import logging
import os
from contextlib import asynccontextmanager

import uvicorn
from aiogram.types import Update
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from start_bot import dp, bot

# config faylini import qilish
try:
    from config import BOT_TOKEN, NGROK_TUNNEL_URL
except ImportError:
    # Agar config.py mavjud bo'lmasa, muhit o'zgaruvchilaridan olish
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    NGROK_TUNNEL_URL = os.environ.get("NGROK_TUNNEL_URL")
    if not all([BOT_TOKEN, NGROK_TUNNEL_URL]):
        raise EnvironmentError("BOT_TOKEN and NGROK_TUNNEL_URL are not set.")

# Logging sozlamalari
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Lifespan menejeri - ilova ishga tushganda va to'xtaganda bajariladigan amallar
@asynccontextmanager
async def lifespan_event(app: FastAPI):
    # Ilova ishga tushganda (startup)
    webhook_url = f"{NGROK_TUNNEL_URL}/{BOT_TOKEN}"
    await bot.set_webhook(webhook_url)
    logger.info(f"Joriy webhook URL: {webhook_url}")
    logger.info("Ilova ishga tushmoqda...")

    yield

    # Ilova to'xtaganda (shutdown)
    await bot.session.close()
    await bot.delete_webhook()
    logger.info("Webhook o'chirildi.")
    logger.info("Bot sessiyasi yopildi.")


# FastAPI ilovasini yaratish va lifespan argumentini o'rnatish
app = FastAPI(lifespan=lifespan_event)


# Webhook uchun handler
@app.post(f"/{BOT_TOKEN}")
async def handle_webhook(request: Request):
    """
    Bu funksiya webhook orqali kelgan yangilanishlarni qabul qilib oladi va
    aiogram dispatcher orqali ularni qayta ishlaydi.
    """
    try:
        data = await request.json()
        logger.info(f"Webhook yangilanishi qabul qilindi (xom lug'at): {data}")
        update = Update(**data)
        bot.set_current(bot)
        await dp.feed_update(bot, update)
        return JSONResponse(status_code=200, content={"status": "ok"})
    except Exception as e:
        logger.error(f"Webhook xatosi: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


# Asosiy URL uchun oddiy javob
@app.get("/")
async def root():
    """
    Asosiy sahifa uchun oddiy GET so'roviga javob qaytaradi.
    """
    return {"message": "Bot faqat Telegram orqali ishlaydi"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, reload=True)
