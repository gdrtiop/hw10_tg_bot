import asyncio

from aiogram import types, Router
from aiogram.filters import Command

router = Router()

@router.message(Command("start"))
async def start(message: types.Message):
    await message.answer('Привет!')