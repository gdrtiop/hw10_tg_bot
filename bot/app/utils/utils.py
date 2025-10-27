import math
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

ONE_PAGE_ACTIVE = 5
ONE_PAGE_PASSIVE = 10


def page_task_active_generator(data, page):
    pages = max(1, math.ceil(len(data) / ONE_PAGE_ACTIVE))
    strt = (page - 1) * ONE_PAGE_ACTIVE
    now_data = data[strt:strt + ONE_PAGE_ACTIVE]

    ans = 'Твои задачи:\n'
    keyboard_list = []
    for num, task in enumerate(now_data, start=strt+1):
        ans = ans + f'{num}. {task.text}\n'

        keyboard_list.append([
            InlineKeyboardButton(
                text=task.text[:20] + ('...' if len(task.text) > 20 else ''),
                callback_data=f'done_{task.id}_page_{page}',
            )]
        )
    ans = ans + 'Если уже что-то сделал, то отметь это:'

    if page == 1 and pages > 1:
        keyboard_list.append([InlineKeyboardButton(text="Вперёд ▶️", callback_data=f"pageactive_{page + 1}")])
    elif 1 < page < pages:
        keyboard_list.append([
            InlineKeyboardButton(text="◀️ Назад", callback_data=f"pageactive_{page - 1}"),
            InlineKeyboardButton(text="Вперёд ▶️", callback_data=f"pageactive_{page + 1}")
        ])
    elif page == pages and pages > 1:
        keyboard_list.append([InlineKeyboardButton(text="◀️ Назад", callback_data=f"pageactive_{page - 1}")])
    keyboard_list.append([InlineKeyboardButton(text=f"Стр. {page}/{pages}", callback_data=f"pageactive_{page}")])

    keyboard_list.append([InlineKeyboardButton(text="Вернуться в меню", callback_data="menu")])

    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_list)

    return ans, keyboard


def page_task_all_generator(data, page):
    all_tasks = len(data)
    pages = max(1, all_tasks // ONE_PAGE_PASSIVE + (1 if all_tasks % ONE_PAGE_PASSIVE != 0 else 0))
    strt = (page - 1) * ONE_PAGE_PASSIVE
    now_data = data[strt:strt + ONE_PAGE_PASSIVE]

    ans = 'Твои задачи:\n'
    for num, task in enumerate(now_data, start=strt + 1):
        stat = '✅ Выполнена' if task.done else '❌ Не выполнена'
        create = task.created_at.strftime('%Y-%m-%d %H:%M')
        ans += f"{num}. {task.text}\nСтатус: {stat}\nСоздано: {create}\n\n"

    keyboard_list = []

    if page == 1 and pages > 1:
        keyboard_list.append([InlineKeyboardButton(text="Вперёд ▶️", callback_data=f"pageall_{page + 1}")])
    elif 1 < page < pages:
        keyboard_list.append([
            InlineKeyboardButton(text="◀️ Назад", callback_data=f"pageall_{page - 1}"),
            InlineKeyboardButton(text="Вперёд ▶️", callback_data=f"pageall_{page + 1}")
        ])
    elif page == pages and pages > 1:
        keyboard_list.append([InlineKeyboardButton(text="◀️ Назад", callback_data=f"pageall_{page - 1}")])
    keyboard_list.append([InlineKeyboardButton(text=f"Стр. {page}/{pages}", callback_data=f"pageall_{page}")])

    keyboard_list.append([InlineKeyboardButton(text="Вернуться в меню", callback_data="menu")])

    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_list)

    return ans, keyboard
