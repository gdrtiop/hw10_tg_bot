from aiogram.fsm.state import State, StatesGroup


class NewTask(StatesGroup):
    text = State()
