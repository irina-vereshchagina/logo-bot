import os
import torch
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from diffusers import DiffusionPipeline

# 1) Токены из окружения
TELEGRAM_TOKEN = os.environ["7395107471:AAGjMeouJcXJ5VFaQb7C0Daxd1fXipOofMI"]
HF_HUB_TOKEN   = os.environ.get("artificialguybr/LogoRedmond-LogoLoraForSDXL-V2")

# 2) Загружаем базовую SDXL-модель
pipe = DiffusionPipeline.from_pretrained(
    "stabilityai/stable-diffusion-xl-base-1.0",
    torch_dtype=torch.float16,
    use_auth_token=HF_HUB_TOKEN,
    trust_remote_code=True
)

# 3) Накатываем LoRA-веса
pipe.load_lora_weights("artificialguybr/LogoRedmond-LogoLoraForSDXL-V2")

# 4) Выбираем устройство
device = "cuda" if torch.cuda.is_available() else "cpu"
pipe = pipe.to(device)


# 5) /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Пришли мне название компании — и я сгенерирую логотип."
    )


# 6) Обработка текста
async def gen_logo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = update.message.text
    result = pipe(prompt, height=1024, width=1024)
    image = result.images[0]
    path = "logo.png"
    image.save(path)
    await update.message.reply_photo(photo=open(path, "rb"))


# 7) Точка входа
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, gen_logo))
    app.run_polling()


if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()
