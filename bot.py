import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from diffusers import StableDiffusionPipeline
import torch

# 1) Токен от BotFather
TOKEN = "7395107471:AAGjMeouJcXJ5VFaQb7C0Daxd1fXipOofMI"

# 2) ID модели на Hugging Face
MODEL_ID = "artificialguybr/LogoRedmond-LogoLoraForSDXL-V2"

# 3) Загружаем модель
pipe = StableDiffusionPipeline.from_pretrained(
    MODEL_ID,
    torch_dtype=torch.float16,
    revision="fp16"
).to("cuda" if torch.cuda.is_available() else "cpu")

# 4) Обработчики
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Пришли мне название компании — и я сделаю логотип."
    )

async def gen_logo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = update.message.text
    image = pipe(prompt, height=1024, width=1024).images[0]
    path = "logo.png"
    image.save(path)
    await update.message.reply_photo(photo=open(path, "rb"))

# 5) Запуск бота
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, gen_logo))
    app.run_polling()

if __name__ == "__main__":
    main()
