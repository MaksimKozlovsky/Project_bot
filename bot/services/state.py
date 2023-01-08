from aiogram.dispatcher.filters.state import State, StatesGroup


class CoffeeState(StatesGroup):
    client_name = State()
    comment = State()
    delivery = State()
    menu = State()
    position = State()
    qty = State()

