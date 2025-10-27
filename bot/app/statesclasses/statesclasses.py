from aiogram.fsm.state import State, StatesGroup


class NewTask(StatesGroup):
    text = State()


class WeatherLoc(StatesGroup):
    location = State()


class NewFile(StatesGroup):
    file = State()


class CurrRate(StatesGroup):
    text = State()
