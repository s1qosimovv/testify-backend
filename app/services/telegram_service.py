import os
import asyncio
import logging
import threading
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup, Poll, ReplyKeyboardMarkup, WebAppInfo, PollAnswer
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, PollAnswerHandler
from app.services.quiz_service import get_quiz_from_memory
from app.config import settings

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Additional storage for user sessions
USER_SESSIONS_FILE = "user_sessions.json"

def _load_sessions():
    if not os.path.exists(USER_SESSIONS_FILE): return {}
    try:
        with open(USER_SESSIONS_FILE, "r") as f: return json.load(f)
    except: return {}

def _save_session(user_id, quiz_id):
    try:
        sessions = _load_sessions()
        sessions[str(user_id)] = quiz_id
        with open(USER_SESSIONS_FILE, "w") as f: json.dump(sessions, f)
    except: pass

class TelegramQuizBot:
    def __init__(self):
        self.token = settings.TELEGRAM_BOT_TOKEN
        self.app_url = settings.WEB_APP_URL
        self.application = None
        # Track active polls: { poll_id: { "correct_index": int, "chat_id": int, "quiz_id": str } }
        self.active_polls = {}
        # Track results: { (chat_id, quiz_id): { user_id: { "name": str, "score": int, "answers": int } } }
        self.quiz_results = {}

    async def set_menu_button(self):
        """Set the main bot menu button to open the Web App"""
        try:
            await self.application.bot.set_chat_menu_button(
                menu_button={"type": "web_app", "text": "Ilovani Ochish", "web_app": {"url": self.app_url}}
            )
            logger.info("Menu button set successfully")
        except Exception as e:
            logger.error(f"Error setting menu button: {e}")

    async def start_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            if not update.message:
                return

            user_id = update.effective_user.id
            chat_id = update.effective_chat.id
            args = context.args
            logger.info(f"Start command from {user_id} in {update.effective_chat.type} ({chat_id}) with args: {args}")
            
            quiz_id = None
            
            # 1. Check deep link args
            if args and len(args) > 0:
                payload = args[0]
                if payload.startswith("q_"):
                    quiz_id = payload[2:]
                    _save_session(user_id, quiz_id)
                elif payload.startswith("startgroup_q_"):
                    quiz_id = payload[13:]
                    _save_session(user_id, quiz_id)

            # 2. If no args, try to fetch last session
            if not quiz_id:
                sessions = _load_sessions()
                quiz_id = sessions.get(str(user_id))
                logger.debug(f"Fetched session quiz_id for {user_id}: {quiz_id}")

            if quiz_id:
                try:
                    quiz = get_quiz_from_memory(quiz_id)
                    title = getattr(quiz, 'title', 'Yangi Quiz')
                    
                    await update.message.reply_text(
                        f"✅ **{title}** topildi!\n"
                        f"Bu quiz {len(quiz.quiz)} ta savoldan iborat.\n\n"
                        "Savollarni birma-bir yuboryapman... 👇",
                        parse_mode='Markdown'
                    )

                    duration = getattr(quiz, 'time_per_question', 30)
                    
                    # Initialize results for this session
                    session_key = (chat_id, quiz_id)
                    self.quiz_results[session_key] = {}
                    
                    for i, q in enumerate(quiz.quiz):
                        options = [opt for opt in q.options.values()]
                        opt_keys = list(q.options.keys())
                        try:
                            correct_index = opt_keys.index(q.correct_answer)
                        except ValueError:
                            correct_index = 0
                        
                        message = await context.bot.send_poll(
                            chat_id=chat_id,
                            question=f"{i+1}. {q.question}",
                            options=options,
                            type=Poll.QUIZ,
                            correct_option_id=correct_index,
                            is_anonymous=False,
                            open_period=duration,
                            explanation="To'g'ri javobni tanlang."
                        )
                        
                        # Register poll for tracking
                        self.active_polls[message.poll.id] = {
                            "correct_index": correct_index,
                            "chat_id": chat_id,
                            "quiz_id": quiz_id
                        }
                        
                        await asyncio.sleep(duration + 1)
                    
                    # Send Leaderboard
                    results = self.quiz_results.get(session_key, {})
                    if not results:
                        await context.bot.send_message(chat_id=chat_id, text="🏁 Quiz yakunlandi. Hech kim ishtirok etmadi. 🤷‍♂️")
                    else:
                        # Sort by score (descending)
                        sorted_users = sorted(results.values(), key=lambda x: x['score'], reverse=True)
                        
                        leaderboard = "🏆 **QUIZ NATIJALARI** 🏆\n\n"
                        for i, user in enumerate(sorted_users[:10]): # Top 10
                            medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else "👤"
                            leaderboard += f"{medal} {user['name']}: **{user['score']}** / {len(quiz.quiz)}\n"
                        
                        await context.bot.send_message(
                            chat_id=chat_id, 
                            text=leaderboard, 
                            parse_mode='Markdown'
                        )
                    
                    # Cleanup (Optional: keep for a while or delete)
                    # del self.quiz_results[session_key]
                    return
                except Exception as quiz_err:
                    logger.error(f"Quiz loading error: {quiz_err}")
                    await update.message.reply_text(
                        f"❌ Kechirasiz, quizingizni yuklashda xatolik: {str(quiz_err)}\n"
                        "Ehtimol, server yangilangani uchun xotira o'chib ketgan. Iltimos, ilovada yangi quiz yarating."
                    )
                    return
            
            # If still no quiz, show general onboarding
            keyboard = [[InlineKeyboardButton("� Ilovani Ochish", web_app=WebAppInfo(url=self.app_url))]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                "Assalomu alaykum! **Testify AI** botiga xush kelibsiz! ✨\n\n"
                "Sizda hali faol quiz seansi yo'q ekan. Quizingizni boshlash uchun:\n"
                "1. Pastdagi tugma orqali ilovaga kiring.\n"
                "2. Fayl yuklab test yarating.\n"
                "3. Natija ekranidagi 'Guruhda ishlatish' tugmasini bosing.\n\n"
                "Shundan so'ng bu guruhda `/start@TestifyHub_bot` buyrug'i ishlaydi! 👇",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Error in start_handler: {e}")
            try:
                await update.message.reply_text(f"⚠️ Botda texnik xatolik: {str(e)}")
            except: pass

    async def ping_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Pong! 🏓 Bot ishlayapti.")

    async def debug_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        sessions = _load_sessions()
        last_quiz = sessions.get(str(user_id), "Yo'q")
        
        status = (
            f"🔍 **Debug Ma'lumotlari**\n"
            f"User ID: `{user_id}`\n"
            f"Chat ID: `{update.effective_chat.id}`\n"
            f"Oxirgi Quiz: `{last_quiz}`\n"
            f"Aktiv Polls: `{len(self.active_polls)}`\n"
            f"Server holati: ✅ Ishlayapti"
        )
        await update.message.reply_text(status, parse_mode='Markdown')

    async def message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.message and update.effective_chat.type == "private":
            await update.message.reply_text(
                "Men faqat buyruqlarga javob bera olaman. Ilovani ishlash uchun pastdagi 'Ilovani Ochish' tugmasini bosing. 👇"
            )

    async def poll_answer_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Track user answers across multiple polls"""
        answer = update.poll_answer
        poll_id = answer.poll_id
        
        if poll_id in self.active_polls:
            poll_info = self.active_polls[poll_id]
            chat_id = poll_info["chat_id"]
            quiz_id = poll_info["quiz_id"]
            correct_index = poll_info["correct_index"]
            
            session_key = (chat_id, quiz_id)
            user_id = answer.user.id
            user_name = answer.user.full_name
            
            if session_key not in self.quiz_results:
                self.quiz_results[session_key] = {}
            
            if user_id not in self.quiz_results[session_key]:
                self.quiz_results[session_key][user_id] = {
                    "name": user_name,
                    "score": 0,
                    "answers": 0
                }
            
            # Check if answer is correct
            if answer.option_ids and answer.option_ids[0] == correct_index:
                self.quiz_results[session_key][user_id]["score"] += 1
            
            self.quiz_results[session_key][user_id]["answers"] += 1

    def run_in_background(self):
        if not self.token or self.token == "your-telegram-bot-token-here":
            logger.warning("Telegram Bot Token topilmadi. Bot o'chirilgan.")
            return
            
        def run():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                self.application = ApplicationBuilder().token(self.token).build()
                self.application.add_handler(CommandHandler("start", self.start_handler))
                self.application.add_handler(CommandHandler("ping", self.ping_handler))
                self.application.add_handler(CommandHandler("debug", self.debug_handler))
                self.application.add_handler(PollAnswerHandler(self.poll_answer_handler))
                self.application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), self.message_handler))
                
                loop.run_until_complete(self.application.initialize())
                loop.run_until_complete(self.application.start())
                loop.run_until_complete(self.application.updater.start_polling())
                loop.run_until_complete(self.set_menu_button())
                
                logger.info("Telegram Bot polling started successfully")
                loop.run_forever()
            except Exception as e:
                logger.error(f"Critical error in Telegram Bot thread: {e}")

        thread = threading.Thread(target=run, daemon=True)
        thread.start()

# Global instance
telegram_bot = TelegramQuizBot()
