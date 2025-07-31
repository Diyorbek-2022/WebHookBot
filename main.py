import logging  # Loglash uchun kutubxona
import os

from aiogram import types, Bot
from aiogram.dispatcher.dispatcher import Dispatcher
from fastapi import FastAPI
import uvicorn  # FastAPI ilovasini ishga tushirish uchun

from bot import bot, dp
from config import TELEGRAM_BOT_TOKEN, NGROK_TUNNEL_URL

# Loglashni sozlash: INFO darajasidagi xabarlarni ko'rsatadi
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# FastAPI ilovasini yaratish
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Bot faqat Telegram orqali ishlaydi | https://t.me/tvbsfdgiejqiwoslsdkd_bot"}


# Webhook yo'li va URL manzilini belgilash
WEBHOOK_PATH = f"/bot/{TELEGRAM_BOT_TOKEN}"
WEBHOOK_URL = f"{NGROK_TUNNEL_URL}{WEBHOOK_PATH}"


@app.on_event("startup")
async def on_startup():
    """
    Ilova ishga tushganda webhookni sozlash.
    Agar webhook allaqachon to'g'ri o'rnatilgan bo'lsa, qayta o'rnatmaydi.
    """
    logger.info("Ilova ishga tushmoqda...")
    try:
        # Telegramdan joriy webhook ma'lumotlarini olish
        current_webhook_info = await bot.get_webhook_info()
        logger.info(f"Joriy webhook URL: {current_webhook_info.url}")

        # Agar joriy webhook URL bizning URLga mos kelmasa, uni yangilash
        if current_webhook_info.url != WEBHOOK_URL:
            await bot.set_webhook(url=WEBHOOK_URL)
            logger.info(f"Webhook muvaffaqiyatli o'rnatildi: {WEBHOOK_URL}")
        else:
            logger.info(f"Webhook allaqachon o'rnatilgan va to'g'ri: {WEBHOOK_URL}")
    except Exception as e:
        logger.error(f"Webhookni o'rnatishda xato yuz berdi: {e}")
        # Xato yuz berganda webhookni o'chirishga urinish, keyingi urinish uchun toza holat yaratish
        try:
            await bot.delete_webhook()
            logger.info("Xato tufayli webhook o'chirildi.")
        except Exception as delete_e:
            logger.error(f"Webhookni o'chirishda xato yuz berdi: {delete_e}")


@app.post(WEBHOOK_PATH)
async def handle_webhook(update: dict):
    """
    Telegramdan kelgan webhook yangilanishlarini qabul qilish va qayta ishlash.
    FastAPI avtomatik ravishda JSON so'rovini lug'atga aylantiradi.
    """
    logger.info(f"Webhook yangilanishi qabul qilindi (xom lug'at): {update}")
    try:
        # Kelgan xom lug'atni aiogramning Update obyektiga aylantirish
        telegram_update = types.Update(**update)
        logger.info(f"Aiogram Update obyektiga o'tkazildi. Update ID: {telegram_update.update_id}")

        # Dispatcher va Bot obyektlarini joriy kontekstga o'rnatish
        # Bu aiogramning ichki mexanizmlari to'g'ri ishlashi uchun muhim
        Dispatcher.set_current(dp)
        Bot.set_current(bot)

        # Yangilanishni aiogram dispatcher orqali qayta ishlash
        await dp.process_update(telegram_update)
        logger.info("Yangilanish aiogram dispatcher tomonidan qayta ishlandi.")
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Yangilanishni qayta ishlashda xato yuz berdi: {e}", exc_info=True)
        # Xato yuz berganda Telegramga xato statusini qaytarish
        return {"status": "error", "message": str(e)}, 500


@app.on_event("shutdown")
async def on_shutdown():
    """
    Ilova o'chirilganda bot sessiyasini yopish va webhookni o'chirish.
    """
    logger.info("Ilova o'chirilmoqda...")
    try:
        # Rivojlanish paytida webhookni o'chirish yaxshi amaliyotdir
        # eski webhook URLlari bilan bog'liq muammolarni oldini olish uchun.
        await bot.delete_webhook()
        logger.info("Webhook o'chirildi.")
    except Exception as e:
        logger.error(f"Webhookni o'chirishda xato yuz berdi: {e}")

    await dp.bot.get_session().close()  # Yangi usul
    logger.info("Bot sessiyasi yopildi.")


# Bu qism faqatgina main.py faylini to'g'ridan-to'g'ri ishga tushirganda ishlaydi.
# Odatda FastAPI ilovalari "uvicorn main:app --reload" buyrug'i bilan ishga tushiriladi.
# if __name__ == "__main__":
#     logger.info("Uvicorn to'g'ridan-to'g'ri ishga tushirilmoqda...")
#     uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    logger.info("Uvicorn to'g'ridan-to'g'ri ishga tushirilmoqda...")
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)