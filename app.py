import os
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher

from handlers.user_private import user_private_router

load_dotenv()

bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher()

dp.include_router(user_private_router)


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
