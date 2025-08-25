from aiogram import F, Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import orm_add_product
from filters.chat_types import ChatTypeFilter, IsAdmin
from keyboards.reply import get_keyboard

admin_router = Router()
admin_router.message.filter(ChatTypeFilter(['private']), IsAdmin())

ADMIN_KB = get_keyboard(
    'Добавить товар',
    'Изменить товар',
    'Удалить товар',
    'Я так, просто посмотреть зашел',
    placeholder='Выберете действие',
    sizes=(2, 1, 1)
)


@admin_router.message(Command('admin'))
async def add_product(message: types.Message):
    await message.answer('Что хотите сделать?', reply_markup=ADMIN_KB)


@admin_router.message(F.text == 'Я так, просто посмотреть зашел')
async def starring_at_product(message: types.Message):
    await message.answer('Ок, вот список товаров ⬆️')


@admin_router.message(F.text == 'Изменить товар')
async def change_product(message: types.Message):
    await message.answer('Ок, вот список товаров ⬆️')


@admin_router.message(F.text == 'Удалить товар')
async def delete_product(message: types.Message):
    await message.answer('Выберете товар(ы) для удаления ⬆️')


# Машина состояний (FSM)
class AddProduct(StatesGroup):
    # Шаги состояний
    name = State()
    description = State()
    price = State()
    image = State()

    texts = {
        'AddProduct:name': 'Введите название заново:',
        'AddProduct:description': 'Введите описание заново:',
        'AddProduct:price': 'Введите стоимость заново:',
        'AddProduct:image': 'Этот стейт последний, поэтому...'
    }


#  Становимся в состояние ожидания ввода name
@admin_router.message(StateFilter(None), F.text == 'Добавить товар')
async def add_product(message: types.Message, state: FSMContext):
    await message.answer('Введите название товара', reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(AddProduct.name)


@admin_router.message(StateFilter('*'), Command('отмена'))
@admin_router.message(StateFilter('*'), F.text.casefold() == 'отмена')
async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.clear()
    await message.answer('Действия отменены', reply_markup=ADMIN_KB)


@admin_router.message(StateFilter('*'), Command('назад'))
@admin_router.message(StateFilter('*'), F.text.casefold() == 'назад')
async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state == AddProduct.name:
        await message.answer('Предыдущего шага нет, введите название товара или напишите "отмена"')
        return

    previous = None
    for step in AddProduct.__all_states__:
        if step.state == current_state:
            await state.set_state(previous)
            await message.answer(f'Ок, вы вернулись к прошлому шагу\n{AddProduct.texts[previous.state]}')
            return
        previous = step


@admin_router.message(AddProduct.name, F.text)
async def add_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer('Введите описание товара')
    await state.set_state(AddProduct.description)


@admin_router.message(AddProduct.name)
async def add_name(message: types.Message):
    await message.answer('Вы ввели недопустимые данные, введите текст названия товара')


@admin_router.message(AddProduct.description, F.text)
async def add_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer('Введите стоимость товара')
    await state.set_state(AddProduct.price)


@admin_router.message(AddProduct.price, F.text)
async def add_price(message: types.Message, state: FSMContext):
    await state.update_data(price=message.text)
    await message.answer('Загрузите изображение товара')
    await state.set_state(AddProduct.image)


# Хендлер для отлова некорректных ввода для состояния price
@admin_router.message(AddProduct.price)
async def add_price(message: types.Message):
    await message.answer('Вы ввели недопустимые данные, введите стоимость товара')


# Ловим данные для состояния image и потом выходим из состояний
@admin_router.message(AddProduct.image, F.photo)
async def add_image(message: types.Message, state: FSMContext, session: AsyncSession):
    await state.update_data(image=message.photo[-1].file_id)
    data = await state.get_data()

    try:
        await orm_add_product(session, data)
        await message.answer('Товар добавлен', reply_markup=ADMIN_KB)
        await state.clear()
    except Exception as e:
        await message.answer(f'Ошибка:\n{str(e)}\nОбратитесь к программеру, он опять денег хочет',
                             reply_markup=ADMIN_KB)
        await state.clear()


@admin_router.message(AddProduct.image)
async def add_image(message: types.Message):
    await message.answer('Отправьте фото пищи')
