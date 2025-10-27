import os, sys, asyncio
import logging
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.middlewares.base_db_middleware import DbSessionMiddleware
from app.handlers.main_handlers import router as main_handlers_router
from app.handlers.taskmanage_handlers import router as taskmanage_handlers_router

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()
dp.include_router(main_handlers_router)
dp.include_router(taskmanage_handlers_router)

dp.message.middleware(DbSessionMiddleware())
dp.callback_query.middleware(DbSessionMiddleware())


async def main():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    async with Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML)) as bot:
        await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
