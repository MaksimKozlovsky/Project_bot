import logging
import os
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import aiogram.utils.markdown as md
import requests
from aiogram.dispatcher.filters.state import StatesGroup, State
from services.json_to_text import convert_to_text_order, convert_to_text_position
from services.service import bot_service
from services.state import CoffeeState
from aiogram import Bot, Dispatcher, executor, types
import json
from dotenv import load_dotenv
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton, ParseMode


load_dotenv()
bot = Bot(token=os.environ['BOT_TOKEN'])
logging.basicConfig(level=logging.INFO)
dp = Dispatcher(bot, storage=MemoryStorage())


async def startup(_):
    bot_service.check_availability()


# -------------------------------------------------------------------------------------------------------------------


@dp.message_handler(state='*', commands='stop')
@dp.message_handler(Text(equals='отмена', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info('Cancelling state %r', current_state)
    # Cancel state and inform user about it
    await state.finish()


# -------------------------------------------------------------------------------------------------------------------


@dp.callback_query_handler(Text(contains="return"), state="*")
async def return_handler(callback: types.CallbackQuery, state: FSMContext):
    await start_command(callback.message)
    await state.finish()
    await callback.answer("Начальная страница")
    await callback.message.delete()

# ---------------------------------------------------------------------------------------------------------------------


@dp.message_handler(commands=['start'])
async def start_command(msg: types.Message):
    button = types.InlineKeyboardMarkup(row_width=1)
    button.add(types.InlineKeyboardButton('Сделать заказ', callback_data='order'))
    await msg.answer('Добро пожаловать в кофейню "CoffeeIn"', reply_markup=button)


@dp.callback_query_handler(Text(contains='order'))
async def start_order(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(CoffeeState.client_name.state)
    await callback.message.answer('Как вас зовут')


@dp.message_handler(state=CoffeeState.client_name)
async def get_name(msg: types.Message, state: FSMContext):
    await state.update_data(client_name=msg.text)
    await msg.answer('Коментарий к заказу\n(время или другие пожелания)')
    await state.set_state(CoffeeState.comment)


@dp.message_handler(state=CoffeeState.comment)
async def get_comment(msg: types.Message, state: FSMContext):
    await state.update_data(comment=msg.text)
    await state.set_state(CoffeeState.delivery)
    button = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button.add("Самовынос", "Доставка в бизнес-центре")
    button.add("Доставка Яндекс такси")
    await msg.answer("Выберите способ доставки", reply_markup=button)


@dp.message_handler(state=CoffeeState.delivery)
async def get_delivery(msg: types.Message, state: FSMContext):
    await state.update_data(delivery=msg.text)
    await state.set_state(CoffeeState.menu)
    button = types.InlineKeyboardMarkup(row_width=1)
    button.add(types.InlineKeyboardButton('Полистать меню', callback_data='menu'))
    button.add(types.InlineKeyboardButton("Вернуться в начало", callback_data="return"))
    await msg.answer('Меню', reply_markup=button)


@dp.callback_query_handler(Text(equals='menu'), state=CoffeeState.menu)
async def display_menu(callback: types.CallbackQuery, state: FSMContext):
    menu_response = bot_service.get_menu()
    button = types.InlineKeyboardMarkup(row_width=1)

    for menu in menu_response:
        button.row(types.InlineKeyboardButton(f"{menu['position_name']} {menu['price']}",
                                              callback_data=f"get_position:{menu['id']}"))

    button.add(types.InlineKeyboardButton("Вернуться в начало", callback_data="return"))
    await state.set_state(CoffeeState.position)
    await callback.message.edit_text('Выбирайте:', reply_markup=button)
    await callback.answer('Меню')


@dp.callback_query_handler(Text(contains='get_position'), state=CoffeeState.position)
async def display_position(callback: types.CallbackQuery, state: FSMContext):
    position_id = int(callback.data.split(':')[-1])
    position_name = bot_service.get_position(position_id)['position_name']

    await state.update_data(position_name=position_name)
    await state.set_state(CoffeeState.qty)
    await callback.answer('Введите колличество', show_alert=True)
    await callback.message.delete()


@dp.message_handler(state=CoffeeState.qty)
async def choose_qty(msg: types.Message, state: FSMContext):
    await state.update_data(qty=msg.text)
    await state.set_state(CoffeeState.menu)

    button = types.InlineKeyboardMarkup(row_width=1)
    button .add(types.InlineKeyboardButton('Добавить в заказ', callback_data='menu'))
    button .add(types.InlineKeyboardButton('Сформировать заказ', callback_data='make_order'))
    button.add(types.InlineKeyboardButton("Вернуться в начало", callback_data="return"))
    await msg.answer('Добавить или Сформировать', reply_markup=button)


@dp.callback_query_handler(Text(contains='menu'), state=CoffeeState.menu)
async def add_position(callback: types.CallbackQuery, state: FSMContext):

    await callback.message.delete()


@dp.callback_query_handler(Text(equals='make_order'), state=CoffeeState.menu)
async def total_bill(callback: types.CallbackQuery, state: FSMContext):

    data = await state.get_data()
#    await bot_service.add_new_order(data)
    await callback.message.answer(f"Имя: {data['client_name']}\n"
                     f"Коментарий: {data['comment']}\n"
                     f"Доставка: {data['delivery']}\n"
                     f"Позиция: {data['position_name']}\n"
                     f"Колличество: {data['qty']}")
    await bot_service.add_new_order(data)
    await callback.message.delete()
    await state.finish()

# ----------------------------- отдача -------------------------------------------------------------
# {
#         #     "client_name": "123",
#         #     "comment": "weqewqeq",
#         #     "delivery": "eqweqwew",
#         #     "positions": [
#         #         {'Americano': 1
#         #         '2': 3,
#         #         '3': 2,
#         #         }
#
# -------------------------------------------------------------------------------------------------------------------
executor.start_polling(dp, skip_updates=True, on_startup=startup)
