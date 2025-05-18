import os
import io
import requests
from PIL import Image
from telegram import Update, ReplyKeyboardRemove, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    filters,
    ContextTypes,
)

# 1) Читаем токены из окружения (TELEGRAM_TOKEN и HF_INFER_TOKEN задаются в Render → Environment)
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
HF_INFER_TOKEN = os.environ["HF_INFER_TOKEN"]

# 2) Настройки Hugging Face Inference API
MODEL_ID = "artificialguybr/LogoRedmond-LogoLoraForSDXL-V2"
API_URL  = f"https://api-inference.huggingface.co/models/{MODEL_ID}"
HEADERS  = {"Authorization": f"Bearer {HF_INFER_TOKEN}"}

# 3) Состояния для ConversationHandler
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

    name, style, colors = (
        context.user_data["name"],
        context.user_data["style"],
        context.user_data["colors"],
    )
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
        img = Image.open(io.BytesIO(resp.content))
        img.save("logo.png")
        with open("logo.png", "rb") as f:
