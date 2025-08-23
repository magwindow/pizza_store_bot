import os
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart

load_dotenv()

bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher()


@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer('Это была команда старт')


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
