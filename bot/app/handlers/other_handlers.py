import aiohttp, os
import hashlib

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from app.keyboards.keyboards import get_main_kb
from app.statesclasses.statesclasses import NewFile, CurrRate

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

    await message.answer(f">Имя файла:{file_name}\n, Размер:{file_size:,} байт\n, SHA-256:{sha256}",
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
        symb = symb.replace(" ", "").upper()
    except ValueError:
        await message.answer("Неверный Формат. Пример: USD EUR,RUB")
        return

    async with aiohttp.ClientSession() as session:
        async with session.get(
                f"https://api.exchangerate.host/latest?base={base}&symb={symb}"
        ) as resp:
            data = await resp.json()

    if "rates" not in data:
        await message.answer("Не удалось получить данные.")
        return

    rates = data["rates"]
    answer = [f"Базовая валюта: {base}"]
    for sym, val in rates.items():
        answer.append(f"{sym}: {val:.4f}")

    await message.answer("\n".join(answer), reply_markup=await get_main_kb())
    await state.clear()
