from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


async def get_main_kb():
    keyboard = [
        [InlineKeyboardButton(text="Создать задачу", callback_data="add_task")],
        [InlineKeyboardButton(text="Показать активные задачи", callback_data="active_tasks")],
        [InlineKeyboardButton(text="Показать все задачи", callback_data="all_tasks")],
        [InlineKeyboardButton(text="Получить погоду", callback_data="get_weather")],
        [InlineKeyboardButton(text="Изменить локацию и получить погоду", callback_data="change_location")],
        [InlineKeyboardButton(text="Получить инфу о файле", callback_data="upload_file")],
        [InlineKeyboardButton(text="Получить курсы валют", callback_data="get_rates")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)