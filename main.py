import asyncio
import logging

from aiogram import Bot, Dispatcher
import asyncio
from aiogram import Bot, Dispatcher
from config import TOKEN
from handlers.reg import router as reg_router
from handlers.admin.admin_panel import router as admin_router
from database.DB import test_connection

async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    await test_connection()
    dp.include_router(reg_router)
    dp.include_router(admin_router)

    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())