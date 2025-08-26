from aiogram import types, Router
from aiogram.filters import CommandStart, Command
from sqlalchemy.ext.asyncio import AsyncSession

from filters.chat_types import ChatTypeFilter
from keyboards.inline import get_callback_btns
from handlers.menu_processing import get_menu_content

user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(['private']))


@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message, session: AsyncSession):
    media, reply_markup = await get_menu_content(session, level=0, menu_name='main')
    await message.answer_photo(media.media, caption=media.caption, reply_markup=reply_markup)


@user_private_router.message(Command('help'))
async def about_cmd(message: types.Message):
    await message.answer('Помощь по навигации в боте')



