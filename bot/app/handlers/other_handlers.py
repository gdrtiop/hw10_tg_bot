import aiohttp, os
import hashlib

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv

from app.keyboards.keyboards import get_main_kb
from app.statesclasses.statesclasses import NewFile, CurrRate

load_dotenv()

EXCHANGE_API_KEY = os.getenv('EXCHANGE_API_KEY')

router = Router()


@router.callback_query(F.data == "upload_file")
async def file_heandler(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Пришли мне любой файл")
    await state.set_state(NewFile.file)
    await callback.answer()


@router.message(NewFile.file)
async def handle_file(message: Message, state: FSMContext):
    file_obj = (
            message.document
            or (message.photo[-1] if message.photo else None)
            or message.video
            or message.audio
            or message.voice
            or message.animation
    )

    if not file_obj:
        await message.answer("Это не файл.")
        return

    tg_file = await message.bot.get_file(file_obj.file_id)
    file_stream = await message.bot.download_file(tg_file.file_path)
    content = file_stream.read()

    file_name = getattr(file_obj, "file_name", "Без имени")
    file_size = len(content)
    sha256 = hashlib.sha256(content).hexdigest()

    await message.answer(f">Имя файла:{file_name}\nРазмер:{file_size:} байт\n, SHA-256:{sha256}",
                         reply_markup=await get_main_kb())

    await state.clear()


@router.callback_query(F.data == "get_rates")
async def start_rate_input(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer(
        "Введи валюты в формате:\n"
        "USD EUR,RUB\n\n"
        "Где USD — базовая валюта, а EUR,RUB — интересующие валюты."
    )
    await state.set_state(CurrRate.text)


@router.message(CurrRate.text)
async def get_rates(message: Message, state: FSMContext):
    try:
        base, symb = message.text.strip().split(maxsplit=1)
        base = base.upper()
        symb = [s.strip().upper() for s in symb.split(",")]
    except ValueError:
        await message.answer("Неверный Формат. Пример: USD EUR,RUB")
        return

    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://v6.exchangerate-api.com/v6/{EXCHANGE_API_KEY}/latest/{base}") as resp:
            'https://v6.exchangerate-api.com/v6/624889ea8e3b1f61ff815aff/latest/USD'
            if resp.status != 200:
                return None
            data = await resp.json()
            if data.get("result") != "success":
                return None

            rates = data.get("conversion_rates", {})
            filtered_rates = {sym: rates[sym] for sym in symb if sym in rates}

    if not filtered_rates:
        await message.answer("Не удалось получить курсы валют.")
        return

    reply = f"Курсы валют по отношению к {base}:\n"
    for sym, rate in filtered_rates.items():
        reply += f"{sym}: {rate}\n"

    await message.answer(reply)
