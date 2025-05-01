from aiogram import F, Router, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from bson import ObjectId
import aiogram

from keyboards.users import keyboard_main

from database.cart import create_cart

router = Router()

@router.callback_query(F.data == "start")
async def start_handler(callback: CallbackQuery):
    welcome_text = (
        "👋 <b>Ласкаво просимо до магазину автозапчастин!</b>\n\n"
        "🔧 У нас ви знайдете широкий вибір автозапчастин для вашого автомобіля.\n\n"
        "🚗 <b>Що ви можете зробити зараз?</b>\n"
        "1️⃣ Переглянути <b>каталог товарів</b> і знайти потрібні запчастини.\n"
        "2️⃣ Перейти до <b>особистого кабінету</b>, щоб переглянути ваші дані та історію замовлень.\n"
        "3️⃣ Перевірити <b>кошик</b> і оформити замовлення.\n\n"
        "Оберіть одну з опцій нижче, щоб почати!"
    )

    await create_cart(callback.from_user.id)

    await callback.message.edit_text(welcome_text, reply_markup=keyboard_main, parse_mode="HTML")

@router.callback_query(F.data == "cart")
async def cart_handler(callback: CallbackQuery):
    await callback.message.edit_text(
        "🛒 <b>Ваш кошик</b>\n\n"
        "Тут ви можете переглянути ваші вибрані товари та оформити замовлення.",
        reply_markup=keyboard_main,
        parse_mode="HTML"
    )
    await callback.answer()