import os
import torch
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from diffusers import DiffusionPipeline

# 1) Токен от BotFather
TOKEN = "7395107471:AAGjMeouJcXJ5VFaQb7C0Daxd1fXipOofMI"

# 2) ID модели на Hugging Face
MODEL_ID = "artificialguybr/LogoRedmond-LogoLoraForSDXL-V2"

# Загружаем базовую SDXL-модель и накатываем на неё LoRA-веса
pipe = DiffusionPipeline.from_pretrained(
    "stabilityai/stable-diffusion-xl-base-1.0",
    torch_dtype=torch.float16,
    use_auth_token=HF_HUB_TOKEN,
    trust_remote_code=True
)
pipe.load_lora_weights("artificialguybr/LogoRedmond-LogoLoraForSDXL-V2")

# Переводим модель на GPU, если доступно, иначе на CPU
device = "cuda" if torch.cuda.is_available() else "cpu"
pipe = pipe.to(device)

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Пришли мне название компании — и я сгенерирую логотип."
    )

# Обработчик любого текстового сообщения
async def gen_logo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = update.message.text
    result = pipe(prompt, height=1024, width=1024)
    image = result.images[0]
    path = "logo.png"
    image.save(path)
    await update.message.reply_photo(photo=open(path, "rb"))

# Точка входа
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, gen_logo))
    app.run_polling()

if __name__ == "__main__":
    main()
