import os
import io
import requests
from PIL import Image
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    filters,
    ContextTypes,
)

# 1) Токены из окружения
TELEGRAM_TOKEN="7395107471:AAGjMeouJcXJ5VFaQb7C0Daxd1fXipOofMI"
HF_HUB_TOKEN="artificialguybr/LogoRedmond-LogoLoraForSDXL-V2"


# 1) Настройки HF Inference API
MODEL_ID = "artificialguybr/LogoRedmond-LogoLoraForSDXL-V2"
API_URL  = f"https://api-inference.huggingface.co/models/{MODEL_ID}"
HEADERS  = {"Authorization": f"Bearer {HF_INFER_TOKEN}"}

# 2) Состояния для ConversationHandler
NAME, STYLE, COLORS = range(3)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "🚀 Давайте начнём! Введите название компании или бренда.",
        reply_markup=ReplyKeyboardRemove()
    )
    return NAME


async def ask_style(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["name"] = update.message.text
    keyboard = [["минимализм", "ретро", "футуризм"], ["другой"]]
    await update.message.reply_text(
        "🎨 Выберите стиль логотипа:",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    )
    return STYLE


async def ask_colors(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["style"] = update.message.text
    await update.message.reply_text(
        "🌈 Укажите предпочтительные цвета (например: синий, белый):",
        reply_markup=ReplyKeyboardRemove()
    )
    return COLORS


async def gen_logo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["colors"] = update.message.text

    # Собираем промпт
    name   = context.user_data["name"]
    style  = context.user_data["style"]
    colors = context.user_data["colors"]
    prompt = f"Logo for {name}, style: {style}, colors: {colors}"

    await update.message.reply_text("⏳ Генерирую логотип…")

    try:
        resp = requests.post(
            API_URL,
            headers=HEADERS,
            json={"inputs": prompt},
            timeout=120
        )
        resp.raise_for_status()

        image = Image.open(io.BytesIO(resp.content))
        image.save("logo.png")

        with open("logo.png", "rb") as img_file:
            await update.message.reply_photo(photo=img_file)

    except Exception as e:
        await update.message.reply_text(f"❗ Ошибка генерации: {e}")

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "❌ Операция отменена.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


async def default_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Пожалуйста, отправьте команду /start, чтобы начать.")

def main() -> None:
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # 3) Конверсация: NAME → STYLE → COLORS
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME:   [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_style)],
            STYLE:  [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_colors)],
            COLORS: [MessageHandler(filters.TEXT & ~filters.COMMAND, gen_logo)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    app.add_handler(conv_handler)

    # 4) Всё, что вне конверсии — просим начать с /start (group=1, после conv_handler)
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, default_response),
        group=1
    )

    app.run_polling()


if __name__ == "__main__":
    main()
