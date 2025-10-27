import aiohttp, os

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from dotenv import load_dotenv

from app.keyboards.keyboards import get_main_kb
from app.statesclasses.statesclasses import WeatherLoc
from app.utils.utils import get_coord
from app.database.models import User

load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
router = Router()


@router.callback_query(F.data == "get_weather")
async def get_weather(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    res = await session.execute(select(User).where(User.tg_id == callback.from_user.id))
    user = res.scalar_one_or_none()

    if not user:
        await callback.message.answer(
            "Не могу найти тебя в базе данных(\nНажми /start, чтобы это исправить."
        )
        await callback.answer()
        return

    if user and user.lat and user.lon:
        await send_weather(callback.message, user.lat, user.lon)
    else:
        await callback.message.answer("Введи адрес:")
        await state.set_state(WeatherLoc.location)


@router.message(WeatherLoc.location)
async def save_address(message: Message, state: FSMContext, session: AsyncSession):
    address = message.text
    coords = await get_coord(address)

    if not coords:
        await message.answer("Не удалось определить координаты")
        return

    lat, lon = coords

    res = await session.execute(select(User).where(User.tg_id == message.from_user.id))
    user = res.scalar_one_or_none()
    if user:
        user.lat = lat
        user.lon = lon
        session.add(user)
        await session.commit()

    await message.answer(f"Координаты получены!\nШирота: {lat}\nДолгота: {lon}")
    await send_weather(message, lat, lon)
    await state.clear()


async def send_weather(message, lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric&lang=ru"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                await message.answer("Не удалось получить погоду.")
                return
            data = await resp.json()

            now = data["weather"][0]["description"].capitalize()
            temp = data["main"]["temp"]
            feel = data["main"]["feels_like"]
            loc = data["name"]

            await message.answer(f"Погода в {loc}:\nТемпература: {temp}°C\nОщущается как: {feel}°C\nСейчас: {now}",
                                 reply_markup=await get_main_kb())
