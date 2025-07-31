import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor

from config import BOT_TOKEN, NGROK_TUNNEL_URL

# Logging sozlamalari
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Bot va Dispatcher ni ishga tushirish
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# /start handler
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    try:
        await message.reply("Assalomu alaykum! Men sizning botingizman! /help bilan yordam oling.")
        logger.info(f"User {message.from_user.username} /start ni ishlatdi.")
    except Exception as e:
        logger.error(f"/start handler xatosi: {e}")

# /help handler
@dp.message_handler(commands=['help'])
async def send_help(message: types.Message):
    try:
        await message.reply("Bu yerda yordam ma'lumotlari: /start - boshlash uchun.")
        logger.info(f"User {message.from_user.username} /help ni ishlatdi.")
    except Exception as e:
        logger.error(f"/help handler xatosi: {e}")

# Boshqa fayllardan foydalanish uchun Dispatcher ni eksport qilamiz
if __name__ == '__main__':
    executor.start_polling(dp)