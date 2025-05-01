import datetime

from aiogram import F, Router, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext


from FSM.all import Registration

from keyboards.reg import create_regions_inline_keyboard, keyboard_to_main

from database.users import save_user, get_user

from config import *

router = Router()

@router.message(CommandStart())
async def send_welcome(message: Message, state: FSMContext):
    user = await get_user(message.from_user.id)
    if user:
        await message.answer(
            f"👋 Вітаємо назад, {user['full_name']}! 🚗\n\n"
            "Ви вже зареєстровані в нашому інтернет-магазині автозапчастин. 🛠️\n"
            f"📞 Ваш номер телефону: {user['phone_number']}\n"
            f"📍 Ваша область проживання: {user['region']}\n\n"
            "🛒 Ви можете переглядати наш каталог автозапчастин!",
            reply_markup=keyboard_to_main
        )
        return

    await message.answer(
        "👋 Вітаємо в інтернет-магазині автозапчастин! 🚗\n\n"
        "Для початку роботи, будь ласка, зареєструйтесь.\n"
        "📋 Введіть своє повне ім'я (ПІБ):"
    )
    await state.set_state(Registration.full_name)

@router.message(Registration.full_name)
async def ask_phone_number(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text)

    contact_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📞 Надіслати номер телефону", request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await message.answer(
        "✅ Дякуємо! Тепер надішліть свій номер телефону, натиснувши кнопку нижче:",
        reply_markup=contact_keyboard
    )
    await state.set_state(Registration.phone_number)


@router.message(Registration.phone_number, F.contact)
async def ask_region(message: Message, state: FSMContext):
    if message.contact and message.contact.phone_number:
        await state.update_data(phone_number=message.contact.phone_number)

        regions_keyboard = create_regions_inline_keyboard(page=1)
        await message.answer(
            "📍 Чудово! Тепер виберіть область, у якій ви проживаєте:",
            reply_markup=regions_keyboard
        )
        await state.set_state(Registration.region)
    else:
        await message.answer("⚠️ Будь ласка, скористайтесь кнопкою для надсилання номера телефону.")

@router.callback_query(F.data.startswith("page_") | F.data.startswith("r_"))
async def handle_region_pagination(callback: CallbackQuery, state: FSMContext):
    if callback.data.startswith("page_"):
        page = int(callback.data.split("_")[1])
        keyboard = create_regions_inline_keyboard(page=page)
        await callback.message.edit_reply_markup(reply_markup=keyboard)
        await callback.answer()
    elif callback.data.startswith("r_"):
        region_index = int(callback.data.split("_")[1]) - 1
        regions = [
            "Вінницька", "Волинська", "Дніпропетровська", "Донецька",
            "Житомирська", "Закарпатська", "Запорізька", "Івано-Франківська",
            "Київська", "Кіровоградська", "Луганська", "Львівська",
            "Миколаївська", "Одеська", "Полтавська", "Рівненська",
            "Сумська", "Тернопільська", "Харківська", "Херсонська",
            "Хмельницька", "Черкаська", "Чернівецька", "Чернігівська"
        ]
        selected_region = regions[region_index]
        await state.update_data(region=selected_region)


        user_data = await state.get_data()


        try:
            await save_user(callback.from_user.id,
                               full_name=user_data['full_name'],
                               phone_number=user_data['phone_number'],
                               region=user_data['region'])
        except Exception as e:
            await callback.message.answer("❌ Помилка збереження даних користувача. Спробуйте ще раз.")
            return


        await callback.message.edit_text(
            f"🎉 Дякуємо за реєстрацію, {user_data['full_name']}! 🛠️\n\n"
            f"📞 Ваш номер телефону: {user_data['phone_number']}\n"
            f"📍 Ваша область проживання: {user_data['region']}\n\n"
            "🛒 Тепер ви можете переглядати наш каталог автозапчастин!",
            reply_markup=keyboard_to_main
        )
        await state.clear()
        await callback.answer()