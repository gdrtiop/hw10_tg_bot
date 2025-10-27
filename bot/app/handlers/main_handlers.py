from aiogram import F, types, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User
from app.keyboards.keyboards import get_main_kb

router = Router()


@router.message(Command("start"))
async def start(message: types.Message, session: AsyncSession):
    result = await session.execute(select(User).where(User.tg_id == message.from_user.id))
    user = result.scalar_one_or_none()

    if not user:
        new_user = User(tg_id=message.from_user.id)
        session.add(new_user)
        await session.commit()

    await message.answer("Привет! \nЧтобы узнать, что я могу нажми /help.", reply_markup=await get_main_kb())


@router.message(Command("help"))
async def start(message: types.Message):
    await message.answer("Благодаря мне ты можешь управлять своими задачами, отслеживать пагоду, получать информацию "
                         "о файле и получать курс валют.", reply_markup=await get_main_kb())


@router.callback_query(F.data == "menu")
async def get_menu(callback: CallbackQuery):
    main_kb = await get_main_kb()
    await callback.message.answer("📋 МЕНЮ", reply_markup=main_kb)
    await callback.answer()
