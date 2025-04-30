from aiogram import F, Router, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from config import *

from keyboards.admin import create_admin_panel_keyboard

router = Router()

@router.message(Command('admin'))
async def admin_panel(message: Message):
    for admin in MAIN_ADMINS:
        if message.from_user.id == admin:
            await message.answer(
            "👮‍♂️ Ласкаво просимо до адмін-панелі!\n\n"
            "Оберіть одну з доступних опцій:",
            reply_markup=create_admin_panel_keyboard()
            )
            return
    else:
        await message.answer(
            "❌ Ви не маєте доступу до адмін-панелі."
        )

