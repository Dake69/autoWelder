from aiogram import F, Router, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from bson import ObjectId
import aiogram

from database.catalog import get_all_categories, get_products_by_category, get_product_by_id
from database.cart import add_product_to_cart

router = Router()

@router.callback_query(F.data == "catalog")
async def handle_catalog_query(callback: CallbackQuery):
    categories = await get_all_categories()
    if not categories:
        await callback.message.edit_text("❌ Немає жодної категорії.")
        await callback.answer()
        return

    per_page = 6
    page = 1
    total_pages = (len(categories) + per_page - 1) // per_page
    start = (page - 1) * per_page
    end = start + per_page
    current_categories = categories[start:end]

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=category["name"], callback_data=f"check_category_{category['_id']}_1")]
        for category in current_categories
    ])

    navigation_buttons = []
    if page > 1:
        navigation_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"catalog_page_{page - 1}"))
    if page < total_pages:
        navigation_buttons.append(InlineKeyboardButton(text="Вперед ➡️", callback_data=f"catalog_page_{page + 1}"))
    if navigation_buttons:
        keyboard.inline_keyboard.append(navigation_buttons)

    keyboard.inline_keyboard.append([InlineKeyboardButton(text="🔙 Назад", callback_data="start")])


    try:
        await callback.message.edit_text(
            "🛒🔍 Оберіть категорію пошуку автозапчастин 🔧🚗",
            reply_markup=keyboard
        )
    except aiogram.exceptions.TelegramBadRequest:
        await callback.message.delete()
        await callback.message.answer(
            "🛒🔍 Оберіть категорію пошуку автозапчастин 🔧🚗",
            reply_markup=keyboard
        )
    await callback.answer()

@router.callback_query(F.data.startswith("catalog_page_"))
async def paginate_categories(callback: CallbackQuery, state: FSMContext):
    categories = await get_all_categories()
    if not categories:
        await callback.message.edit_text("❌ Немає жодної категорії.")
        await callback.answer()
        return

    page = int(callback.data.split("_")[-1])
    per_page = 6
    total_pages = (len(categories) + per_page - 1) // per_page
    start = (page - 1) * per_page
    end = start + per_page
    current_categories = categories[start:end]

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=category["name"], callback_data=f"check_category_{category['_id']}_1")]
        for category in current_categories
    ])

    navigation_buttons = []
    if page > 1:
        navigation_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"categories_page_{page - 1}"))
    if page < total_pages:
        navigation_buttons.append(InlineKeyboardButton(text="Вперед ➡️", callback_data=f"categories_page_{page + 1}"))
    if navigation_buttons:
        keyboard.inline_keyboard.append(navigation_buttons)

    keyboard.inline_keyboard.append([InlineKeyboardButton(text="🔙 Назад", callback_data="start")])

    await callback.message.edit_text(
        "🛒🔍 Оберіть категорію пошуку автозапчастин 🔧🚗",
        reply_markup=keyboard
    )

    await callback.answer()

@router.callback_query(F.data.startswith("check_category_"))
async def view_products_in_category(callback: CallbackQuery):
    data = callback.data.split("_")
    category_id = data[2]
    print(category_id, callback.data)
    page = int(data[3])

    try:
        category_id = ObjectId(category_id)
    except Exception:
        await callback.message.edit_text("❌ Невірний формат ID категорії.")
        await callback.answer()
        return

    products = await get_products_by_category(str(category_id))
    if not products:
        await callback.message.edit_text("❌ У цій категорії немає товарів.")
        await callback.answer()
        return

    per_page = 6
    start = (page - 1) * per_page
    end = start + per_page
    current_products = products[start:end]

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=product["name"], callback_data=f"checkproduct_{str(product['_id'])}")]
        for product in current_products
    ])

    navigation_buttons = []
    if page > 1:
        navigation_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"view_products_{str(category_id)}_{page - 1}"))
    if end < len(products):
        navigation_buttons.append(InlineKeyboardButton(text="Вперед ➡️", callback_data=f"view_products_{str(category_id)}_{page + 1}"))
    if navigation_buttons:
        keyboard.inline_keyboard.append(navigation_buttons)

    keyboard.inline_keyboard.append([InlineKeyboardButton(text="🔙 Назад", callback_data="catalog")])

    response = f"📦 Список товарів у категорії (Сторінка {page}):\n\n"
    for product in current_products:
        response = f"📦 <b>Список товарів у категорії</b> (сторінка {page}):\n\n"

    for i, product in enumerate(products, start=1):
        response += (
            f"{i}. <b>{product['name']}</b>\n"
            f"   💰 Ціна: <i>{product['price']}</i>\n"
            f"-----------------------------------\n"
        )
    response += "\n\nВиберіть товар для детальної інформації."

    await callback.message.edit_text(response, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data.startswith("checkproduct_"))
async def view_product_details(callback: CallbackQuery):
    product_id = callback.data.split("_")[-1]
    product = await get_product_by_id(product_id)
    if not product:
        await callback.message.edit_text("❌ Товар не знайдено.")
        await callback.answer()
        return

    response = (
        f"🔹 <b>{product['name']}</b>\n"
        f"💰 Ціна: {product['price']}\n"
        f"📝 Опис: {product['description']}\n"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Додати у кошик", callback_data=f"add_to_cart_{product_id}")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="catalog")]
    ])

    if product.get("photo"):
        await callback.message.delete()
        await callback.message.answer_photo(
            photo=product["photo"],
            caption=response,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    else:
        await callback.message.edit_text(
            text=response,
            reply_markup=keyboard,
            parse_mode="HTML"
        )

    await callback.answer()

@router.callback_query(F.data.startswith("add_to_cart_"))
async def add_to_cart(callback: CallbackQuery):
    product_id = callback.data.split("_")[-1]
    user_id = callback.from_user.id

    success = await add_product_to_cart(user_id, product_id)
    if success != {"error": "Цей товар вже в кошику"}:
        await callback.answer("✅ Товар успішно додано у кошик!")
    else:
        await callback.answer("❌ Не вдалося додати товар у кошик.(Можливо він вже там)")