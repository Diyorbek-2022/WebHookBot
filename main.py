import os
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from bot import dp, bot  # bot.py dan Dispatcher va Bot ni import qilamiz
from config import NGROK_TUNNEL_URL, BOT_TOKEN

# Logging sozlamalari
logger = logging.getLogger(__name__)

# FastAPI ilovasi
app = FastAPI()

# Webhook uchun handler
@app.post(f"/bot/{BOT_TOKEN}")
async def handle_webhook(request: Request):
    try:
        update = await request.json()
        logger.info(f"Webhook yangilanishi qabul qilindi (xom lug'at): {update}")
        await dp.process_update(update)
        return JSONResponse(status_code=200, content={"status": "ok"})
    except Exception as e:
        logger.error(f"Webhook xatosi: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

# Ilova ishga tushganda webhook ni o'rnatish
async def on_startup():
    webhook_url = f"{NGROK_TUNNEL_URL}/bot/{bot.token}"
    await bot.set_webhook(webhook_url)
    logger.info(f"Joriy webhook URL: {webhook_url}")
    logger.info("Ilova ishga tushmoqda...")

# Ilova to'xtaganda webhook ni o'chirish
async def on_shutdown():
    await bot.delete_webhook()
    await dp.bot.get_session().close()
    logger.info("Webhook o'chirildi.")
    logger.info("Bot sessiyasi yopildi.")

# Asosiy URL uchun oddiy javob
@app.get("/")
async def root():
    return {"message": "Bot faqat Telegram orqali ishlaydi | https://t.me/tvbsfdgiejqiwoslsdkd_bot"}

# Startup va shutdown hodisalarini ulash
@app.on_event("startup")
async def startup_event():
    await on_startup()

@app.on_event("shutdown")
async def shutdown_event():
    await on_shutdown()

if __name__ == "__main__":
    # Portni environment o'zgaruvchidan olish
    port = int(os.environ.get("PORT", 8000))
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port, reload=True)