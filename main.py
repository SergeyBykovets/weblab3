from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

STUDENT_NAME = "Биковець С. В."
STUDENT_GROUP = "ІО-31"
PHONE = "+380939876784"
EMAIL = "bykovets.serhii_io31@edu.kpi.ua"

IT_TECHNOLOGIES = """
• Python, FastAPI
• Git, Linux
• MongoDB / PostgreSQL
• REST API
"""

client = Groq(api_key=GROQ_API_KEY)

main_keyboard = ReplyKeyboardMarkup(
    [
        [KeyboardButton("Студент"), KeyboardButton("IT-технології")],
        [KeyboardButton("Контакти"), KeyboardButton("Prompt AI")],
        [KeyboardButton("Головне меню")],
    ],
    resize_keyboard=True,
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"Вітаю! Це бот студента {STUDENT_NAME} ({STUDENT_GROUP}).\n\n"
        "Обери пункт меню:",
        reply_markup=main_keyboard,
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "Студент":
        await update.message.reply_text(
            f"Студент\n\n"
            f"Прізвище, ініціали: {STUDENT_NAME}\n"
            f"Група: {STUDENT_GROUP}",
            reply_markup=main_keyboard,
        )

    elif text == "IT-технології":
        await update.message.reply_text(
            f"IT-технології\n{IT_TECHNOLOGIES}",
            reply_markup=main_keyboard,
        )

    elif text == "Контакти":
        await update.message.reply_text(
            f"Контакти\n\n"
            f"Телефон: {PHONE}\n"
            f"E-mail: {EMAIL}",
            reply_markup=main_keyboard,
        )

    elif text == "Prompt AI":
        context.user_data["waiting_for_prompt"] = True
        await update.message.reply_text(
            "Напиши своє питання / промпт для AI.\n"
            "Я відповім за допомогою Groq.",
            reply_markup=main_keyboard,
        )

    elif text == "Головне меню":
        context.user_data["waiting_for_prompt"] = False
        await start(update, context)

    elif context.user_data.get("waiting_for_prompt"):
        await update.message.reply_chat_action("typing")
        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "Відповідай українською мовою коротко і по суті.",
                    },
                    {"role": "user", "content": text},
                ],
                model="openai/gpt-oss-20b",
                temperature=0.7,
                max_tokens=1024,
            )
            answer = chat_completion.choices[0].message.content
            await update.message.reply_text(
                f"Відповідь AI:\n\n{answer}",
                reply_markup=main_keyboard,
            )
        except Exception as e:
            await update.message.reply_text(
                f"Помилка при зверненні до AI: {e}",
                reply_markup=main_keyboard,
            )
        finally:
            context.user_data["waiting_for_prompt"] = False

    else:
        await update.message.reply_text(
            "Обери пункт з меню або натисни /start",
            reply_markup=main_keyboard,
        )


def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()