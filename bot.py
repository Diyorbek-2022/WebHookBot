from random import shuffle

from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

from config import TELEGRAM_BOT_TOKEN

predict = [
    'Вижу на канал ты подпишешься!',
    'Bugun senga omad kulib boqadi!',
    "Bugun sen webhookni qanday ishlatishni o'rganasan!"
]

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    print("URAAAAAAAAAAAAA!!!!!!!!!!!!")
    shuffle(predict)
    await message.answer(f"{message.from_user.full_name}, {predict[0]}")

@dp.message_handler(commands=['help'])
async def help(message: types.Message):
    await message.answer(f"{message.from_user.full_name}, {predict[1]}")

# if __name__ == '__main__':
#     executor.start_polling(dp)