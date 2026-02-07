import os
import asyncio
import logging
import threading
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup, Poll, ReplyKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from app.services.quiz_service import get_quiz_from_memory
from app.models.quiz import Quiz

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TelegramQuizBot:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.app_url = os.getenv("WEB_APP_URL", "https://s1qosimovv.github.io/testify-frontend/")
        self.application = None
        self.is_running = False

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

            args = context.args
            logger.info(f"Start command received in {update.effective_chat.type} with args: {args}")
            
            # Deep link handling (Quiz sharing)
            if args and args[0].startswith("q_"):
                quiz_id = args[0][2:]
                quiz = get_quiz_from_memory(quiz_id)
                
                if not quiz:
                    await update.message.reply_text(
                        "Kechirasiz, bu quiz topilmadi yoki muddati o'tgan. ❌\n"
                        "Ilova yangilangan bo'lishi mumkin. Iltimos, quizingizni qayta yaratib ko'ring."
                    )
                    return

                await update.message.reply_text(
                    f"✅ **{quiz.title}** topildi!\n"
                    f"Bu quiz {len(quiz.quiz)} ta savoldan iborat.\n\n"
                    "Savollarni birma-bir Quiz (Poll) shaklida yuboryapman... 👇",
                    parse_mode='Markdown'
                )

                for i, q in enumerate(quiz.quiz):
                    options = [opt for opt in q.options.values()]
                    # Map the correct answer (usually A, B, C, D) to its index
                    opt_keys = list(q.options.keys())
                    try:
                        correct_index = opt_keys.index(q.correct_answer)
                    except ValueError:
                        correct_index = 0 # Fallback
                    
                    try:
                        await context.bot.send_poll(
                            chat_id=update.effective_chat.id,
                            question=f"{i+1}. {q.question}",
                            options=options,
                            type=Poll.QUIZ,
                            correct_option_id=correct_index,
                            is_anonymous=False,
                            explanation="To'g'ri javobni tanlang."
                        )
                        await asyncio.sleep(0.3)
                    except Exception as poll_error:
                        logger.error(f"Error sending poll {i}: {poll_error}")
                        await update.message.reply_text(f"Savol {i+1} ni yuborishda xatolik: {poll_error}")
                return

            # Regular Start / Onboarding
            keyboard = [
                [InlineKeyboardButton("🚀 Ilovani Ochish", web_app=WebAppInfo(url=self.app_url))],
                [InlineKeyboardButton("📖 Yo'riqnoma", callback_data="help"), InlineKeyboardButton("📢 Kanalimiz", url="https://t.me/testify_news")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                "Assalomu alaykum! **Testify AI** botiga xush kelibsiz! ✨\n\n"
                "Mening yordamimda siz:\n"
                "1️⃣ PDF yoki boshqa matnlardan darrov Quiz yaratishingiz\n"
                "2️⃣ Bilimingizni sinashingiz\n"
                "3️⃣ Quizlarni guruhlarda o'tkazishingiz mumkin.\n\n"
                "Ilovani boshlash uchun pastdagi tugmani bosing: 👇",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Error in start_handler: {e}")

    async def message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.message and update.effective_chat.type == "private":
            await update.message.reply_text(
                "Men faqat buyruqlarga javob bera olaman. Ilovani ishlash uchun pastdagi 'Ilovani Ochish' tugmasini bosing. 👇"
            )

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
                self.application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), self.message_handler))
                
                # Start bot persistent setup
                loop.run_until_complete(self.application.initialize())
                loop.run_until_complete(self.application.start())
                loop.run_until_complete(self.application.updater.start_polling())
                loop.run_until_complete(self.set_menu_button())
                
                logger.info("Telegram Bot polling started successfully in background thread")
                loop.run_forever()
            except Exception as e:
                logger.error(f"Critical error in Telegram Bot thread: {e}")

        thread = threading.Thread(target=run, daemon=True)
        thread.start()

# Global instance
telegram_bot = TelegramQuizBot()
