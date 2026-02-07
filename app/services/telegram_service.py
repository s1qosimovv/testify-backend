import os
import asyncio
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup, Poll
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from app.services.quiz_service import get_quiz_from_memory
from app.models.quiz import Quiz
import threading

from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup, Poll, ReplyKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from app.services.quiz_service import get_quiz_from_memory
from app.models.quiz import Quiz
import threading

class TelegramQuizBot:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.app_url = os.getenv("WEB_APP_URL", "http://localhost:5000") # Production URL needed later
        self.application = None
        self.is_running = False

    async def set_menu_button(self):
        # Set the main bot menu button to open the Web App
        await self.application.bot.set_chat_menu_button(
            menu_button={"type": "web_app", "text": "Ilovani Ochish", "web_app": {"url": self.app_url}}
        )

    async def start_bot(self):
        if not self.token or self.token == "your-telegram-bot-token-here":
            print("Telegram Bot Token topilmadi. Telegram funksiyalari o'chirilgan.")
            return

        self.application = ApplicationBuilder().token(self.token).build()
        
        # Add handlers
        self.application.add_handler(CommandHandler("start", self.start_handler))
        self.application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), self.message_handler))
        
        # Start the bot in the background
        self.is_running = True
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        
        # Set persistent menu button
        try:
            await self.set_menu_button()
        except Exception as e:
            print(f"Menu button o'rnatishda xatolik: {e}")
            
        print("Telegram Bot muvaffaqiyatli ishga tushdi!")

    async def start_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        args = context.args
        
        # Deep link handling (Quiz sharing)
        if args and args[0].startswith("q_"):
            quiz_id = args[0][2:]
            quiz = get_quiz_from_memory(quiz_id)
            
            if not quiz:
                await update.message.reply_text("Kechirasiz, bu quiz topilmadi yoki muddati o'tgan. ❌")
                return

            await update.message.reply_text(
                f"✅ **{quiz.title}** topildi!\n"
                f"Bu quiz {len(quiz.questions)} ta savoldan iborat.\n\n"
                "Tayyor bo'lsangiz, quyida savollarni Quiz (Poll) shaklida yuboraman. Ularni guruhga Forward qilishingiz mumkin."
            )

            for i, q in enumerate(quiz.questions):
                options = [opt for opt in q.options.values()]
                correct_index = list(q.options.keys()).index(q.correct_answer)
                
                await context.bot.send_poll(
                    chat_id=update.effective_chat.id,
                    question=f"{i+1}. {q.question}",
                    options=options,
                    type=Poll.QUIZ,
                    correct_option_id=correct_index,
                    is_anonymous=False,
                    explanation="Testify AI tomonidan tuzildi."
                )
                await asyncio.sleep(0.5)
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
            "Ilovani boshlash uchun tugmani bosing: 👇",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "Men faqat buyruqlarga javob bera olaman. Ilovani ishlash uchun pastdagi 'Ilovani Ochish' tugmasini bosing. 👇"
        )

    def run_in_background(self):
        if not self.token or self.token == "your-telegram-bot-token-here":
            return
            
        def run():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.start_bot())
            loop.run_forever()

        thread = threading.Thread(target=run, daemon=True)
        thread.start()

# Global instance
telegram_bot = TelegramQuizBot()
