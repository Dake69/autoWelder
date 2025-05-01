from aiogram import F, Router, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from config import *

from FSM.all import BroadcastForm

from database.users import users_collection
from database.catalog import category_collection, product_collection

from keyboards.admin import stats_keyboard, create_admin_panel_keyboard, create_categories_keyboard, create_products_keyboard, keyboard_special_functions

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

@router.callback_query(F.data.startswith("admin_"))
async def handle_admin_panel(callback: CallbackQuery):
    if callback.data == "admin_stats":

        users_count = await users_collection.count_documents({})
        categories_count = await category_collection.count_documents({})
        products_count = await product_collection.count_documents({})

        await callback.message.edit_text(
            f"📊 <b>Статистика</b>\n\n"
            f"👥 <b>Кількість користувачів:</b> {users_count}\n"
            f"📂 <b>Кількість категорій:</b> {categories_count}\n"
            f"📦 <b>Кількість товарів:</b> {products_count}",
            reply_markup=stats_keyboard,
            parse_mode="HTML"
        )
        await callback.answer()
    elif callback.data == "admin_categories":
        await callback.message.edit_text(
            "📂 Управління категоріями:",
            reply_markup=create_categories_keyboard()
        )
    elif callback.data == "admin_products":
        await callback.message.edit_text(
            "📦 Управління товарами:",
            reply_markup=create_products_keyboard()
        )
    elif callback.data == "admin_settings":
        await callback.message.answer("⚙️ Налаштування: \n- Опція 1\n- Опція 2\n...")
    elif callback.data == "admin_exit":
        await callback.message.answer("🔙 Ви вийшли з адмін-панелі.")
    elif callback.data == "admin_special_functions":
        await callback.message.edit_text(
            "🔧 Спеціальні функції:",
            reply_markup=keyboard_special_functions
        )
    elif callback.data == "admin_back":
        await callback.message.edit_text(
            "👮‍♂️ Ласкаво просимо до адмін-панелі!\n\n"
            "Оберіть одну з доступних опцій:",
            reply_markup=create_admin_panel_keyboard()
        )
    await callback.answer()

@router.callback_query(F.data == "broadcast_message")
async def start_broadcast(callback: CallbackQuery, state: FSMContext):
    await state.set_state(BroadcastForm.message)
    await callback.message.edit_text(
        "📢 <b>Розсилка повідомлень</b>\n\n"
        "Введіть текст повідомлення, яке буде надіслано всім користувачам:",
        parse_mode="HTML"
    )
    await callback.answer()

@router.message(BroadcastForm.message)
async def process_broadcast(message: Message, state: FSMContext):
    await state.clear()
    broadcast_text = message.text

    users = await users_collection.find().to_list(length=None)

    if not users:
        await message.answer("❌ <b>Немає користувачів для розсилки.</b>", parse_mode="HTML")
        return

    sent_count = 0
    failed_count = 0

    for user in users:
        try:
            await message.bot.send_message(chat_id=user["user_id"], text=broadcast_text)
            sent_count += 1
        except Exception:
            failed_count += 1

    await message.answer(
        f"✅ <b>Розсилка завершена!</b>\n\n"
        f"Успішно надіслано: {sent_count}\n"
        f"Не вдалося надіслати: {failed_count}",
        parse_mode="HTML",
    )