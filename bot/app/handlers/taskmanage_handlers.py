import math

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.keyboards.keyboards import get_main_kb
from app.statesclasses.statesclasses import NewTask
from app.database.models import User, Task
from app.utils.utils import page_task_active_generator, page_task_all_generator, ONE_PAGE_ACTIVE
from app.handlers.main_handlers import get_menu

router = Router()


@router.callback_query(F.data == "add_task")
async def adding_task(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    res = await session.execute(select(User).where(User.tg_id == callback.from_user.id))
    user = res.scalar_one_or_none()

    if not user:
        await callback.message.answer(
            "Не могу найти тебя в базе данных(\nНажми /start, чтобы это исправить."
        )
        await callback.answer()
        return

    await state.set_state(NewTask.text)
    await callback.message.answer('Введи текст задачи:')
    await callback.answer()


@router.message(NewTask.text)
async def save_task(message: Message, state: FSMContext, session: AsyncSession):
    text = message.text

    if len(text) > 100:
        await message.answer(f"Бот поддерживает текст задач до 100 символов. У тебя {len(text)}.\nПопробуй ещё раз:")
        return

    await state.update_data(text=text)

    data = await state.get_data()
    new_task = Task(
        author=message.from_user.id,
        text=data['text'],
    )

    session.add(new_task)
    await session.commit()
    main_kb = await get_main_kb()
    await message.answer('✅ Задача успешно добавлена', reply_markup=main_kb)
    await state.clear()


@router.callback_query(F.data == 'active_tasks')
async def show_active_tasks(callback: CallbackQuery, session: AsyncSession):
    res = await session.execute(select(User).where(User.tg_id == callback.from_user.id))
    user = res.scalar_one_or_none()

    if not user:
        await callback.message.answer(
            "Не могу найти тебя в базе данных(\nНажми /start, чтобы это исправить."
        )
        await callback.answer()
        return

    res = await session.execute(
        select(Task).join(User).where(User.tg_id == callback.from_user.id, Task.done == False).order_by(
            Task.created_at.desc()))
    data = res.scalars().all()

    if not data:
        await callback.message.answer('У тебя нету не выполненных задач')
        await get_menu(callback)
        await callback.answer()
        return

    ans, keyboard = page_task_active_generator(data, 1)
    await callback.message.answer(ans, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith('pageactive_'))
async def task_page(callback: CallbackQuery, session: AsyncSession):
    page = int(callback.data.split('_')[1])
    res = await session.execute(select(User).where(User.tg_id == callback.from_user.id))
    user = res.scalar_one_or_none()

    if not user:
        await callback.message.answer(
            "Не могу найти тебя в базе данных(\nНажми /start, чтобы это исправить."
        )
        await callback.answer()
        return

    res = await session.execute(
        select(Task).join(User).where(User.tg_id == callback.from_user.id, Task.done == False).order_by(
            Task.created_at.desc()))
    data = res.scalars().all()

    ans, keyboard = page_task_active_generator(data, page)
    await callback.message.answer(ans, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith('done_'))
async def task_done(callback: CallbackQuery, session: AsyncSession):
    task_id = int(callback.data.split('_')[1])
    page = int(callback.data.split('_')[3])
    res = await session.execute(select(Task).where(Task.id == task_id))
    task = res.scalar_one_or_none()

    task.done = True
    session.add(task)
    await session.commit()
    await callback.answer("Задача выполнена ✅")

    res = await session.execute(
        select(Task).join(User).where(User.tg_id == callback.from_user.id, Task.done == False).order_by(
            Task.created_at.desc()))
    data = res.scalars().all()

    if not data:
        await callback.message.edit_text('У тебя нету не выполненных задач')
        await get_menu(callback)
        await callback.answer()
        return

    total_pages = max(1, math.ceil(len(data) / ONE_PAGE_ACTIVE))
    if page > total_pages:
        page = total_pages
    ans, keyboard = page_task_active_generator(data, page)
    await callback.message.edit_text(ans, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == 'all_tasks')
async def show_all_tasks(callback: CallbackQuery, session: AsyncSession):
    res = await session.execute(select(User).where(User.tg_id == callback.from_user.id))
    user = res.scalar_one_or_none()

    if not user:
        await callback.message.answer(
            "Не могу найти тебя в базе данных(\nНажми /start, чтобы это исправить."
        )
        await callback.answer()
        return
    res = await session.execute(
        select(Task).join(User).where(User.tg_id == callback.from_user.id).order_by(
            Task.created_at.desc()))
    data = res.scalars().all()

    if not data:
        await callback.message.answer('У тебя нет задач')
        await get_menu(callback)
        await callback.answer()
        return

    ans, keyboard = page_task_all_generator(data, 1)
    await callback.message.answer(ans, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith('pageall_'))
async def alltasks_page(callback: CallbackQuery, session: AsyncSession):
    page = int(callback.data.split('_')[1])

    res = await session.execute(
        select(Task).join(User).where(User.tg_id == callback.from_user.id).order_by(
            Task.created_at.desc()))
    data = res.scalars().all()

    ans, keyboard = page_task_all_generator(data, page)
    await callback.message.edit_text(ans, reply_markup=keyboard)
    await callback.answer()
