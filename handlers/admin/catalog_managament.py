from aiogram import F, Router, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from bson import ObjectId
import aiogram


from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from database.catalog import *

from keyboards.admin import *

from FSM.all import *

router = Router()

@router.callback_query(F.data == "add_category")
async def start_add_category(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("📝 Введіть назву нової категорії:")
    await state.set_state(AddCategoryState.waiting_for_category_name)
    await callback.answer()

@router.message(AddCategoryState.waiting_for_category_name)
async def process_category_name(message: Message, state: FSMContext):
    category_name = message.text.strip()
    if not category_name:
        await message.answer("❌ Назва категорії не може бути порожньою. Спробуйте ще раз.")
        return

    category_id = await create_category(name=category_name)
    await message.answer(f"✅ Категорію '{category_name}' створено з ID: {category_id}")

    await state.clear()


@router.callback_query(F.data == "list_categories")
async def list_categories_handler(callback: CallbackQuery, state: FSMContext):
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
        [InlineKeyboardButton(text=category["name"], callback_data=f"manage_category_{category['_id']}")]
        for category in current_categories
    ])

    navigation_buttons = []
    if page > 1:
        navigation_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"categories_page_{page - 1}"))
    if page < total_pages:
        navigation_buttons.append(InlineKeyboardButton(text="Вперед ➡️", callback_data=f"categories_page_{page + 1}"))
    if navigation_buttons:
        keyboard.inline_keyboard.append(navigation_buttons)

    keyboard.inline_keyboard.append([InlineKeyboardButton(text="🔙 Назад", callback_data="admin_back")])

    await callback.message.edit_text("📂 Оберіть категорію для управління:", reply_markup=keyboard)
    await state.set_state(ListCategoriesState.viewing_categories)
    await callback.answer()

@router.callback_query(F.data.startswith("categories_page_"), ListCategoriesState.viewing_categories)
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
        [InlineKeyboardButton(text=category["name"], callback_data=f"manage_category_{category['_id']}")]
        for category in current_categories
    ])

    navigation_buttons = []
    if page > 1:
        navigation_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"categories_page_{page - 1}"))
    if page < total_pages:
        navigation_buttons.append(InlineKeyboardButton(text="Вперед ➡️", callback_data=f"categories_page_{page + 1}"))
    if navigation_buttons:
        keyboard.inline_keyboard.append(navigation_buttons)

    keyboard.inline_keyboard.append([InlineKeyboardButton(text="🔙 Назад", callback_data="admin_back")])

    await callback.message.edit_text("📂 Оберіть категорію для управління:", reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data.startswith("manage_category_"), ListCategoriesState.viewing_categories)
async def manage_category_handler(callback: CallbackQuery, state: FSMContext):
    category_id = callback.data.split("_")[-1]
    
    try:
        category_id = ObjectId(category_id)
    except Exception:
        await callback.message.edit_text("❌ Невірний формат ID категорії.")
        await callback.answer()
        return

    category = await get_category_by_id(category_id)
    if not category:
        await callback.message.edit_text("❌ Категорію не знайдено.")
        await callback.answer()
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Змінити назву", callback_data=f"edit_category_{category['_id']}")],
        [InlineKeyboardButton(text="❌ Видалити категорію", callback_data=f"delete_category_{category['_id']}")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="list_categories")]
    ])
    await callback.message.edit_text(
        f"📂 Управління категорією:\n\n"
        f"Назва: {category['name']}\n"
        f"ID: {category['_id']}",
        reply_markup=keyboard
    )
    await callback.answer()

@router.callback_query(F.data.startswith("edit_category_"))
async def start_edit_category(callback: CallbackQuery, state: FSMContext):
    category_id = callback.data.split("_")[-1]

    try:
        category_id = ObjectId(category_id)
    except Exception:
        await callback.message.edit_text("❌ Невірний формат ID категорії.")
        await callback.answer()
        return
    
    await state.update_data(category_id=category_id)
    await callback.message.edit_text("📝 Введіть нову назву для категорії:")
    await state.set_state(EditCategoryState.waiting_for_new_name)
    await callback.answer()

@router.message(EditCategoryState.waiting_for_new_name)
async def process_edit_category_name(message: Message, state: FSMContext):
    new_name = message.text.strip()
    if not new_name:
        await message.answer("❌ Назва не може бути порожньою. Спробуйте ще раз.")
        return

    data = await state.get_data()
    category_id = data["category_id"]

    try:
        updated_count = await update_category(category_id=category_id, name=new_name)
        if updated_count:
            await message.answer(f"✅ Назву категорії змінено на '{new_name}'.")
        else:
            await message.answer("❌ Категорію не знайдено або назва не змінена.")
    except Exception as e:
        await message.answer(f"❌ Сталася помилка: {e}")

    await state.clear()

@router.callback_query(F.data.startswith("delete_category_"))
async def delete_category_handler(callback: CallbackQuery):
    category_id = callback.data.split("_")[-1]

    try:
        category_id = ObjectId(category_id)
    except Exception:
        await callback.message.edit_text("❌ Невірний формат ID категорії.")
        await callback.answer()
        return
    
    deleted_count = await delete_category(category_id=category_id)
    if deleted_count:
        await callback.message.edit_text("✅ Категорію успішно видалено.")
    else:
        await callback.message.edit_text("❌ Не вдалося видалити категорію.")
    await callback.answer()

@router.callback_query(F.data == "add_product")
async def start_add_product(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("📝 Введіть назву товару:")
    await state.set_state(AddProductState.waiting_for_name)
    await callback.answer()

@router.message(AddProductState.waiting_for_name)
async def process_product_name(message: Message, state: FSMContext):
    product_name = message.text.strip()
    if not product_name:
        await message.answer("❌ Назва товару не може бути порожньою. Спробуйте ще раз.")
        return

    await state.update_data(name=product_name)

    categories = await get_all_categories()
    if not categories:
        await message.answer("❌ Немає доступних категорій. Спочатку створіть категорію.")
        await state.clear()
        return

    per_page = 6
    page = 1
    total_pages = (len(categories) + per_page - 1) // per_page
    start = (page - 1) * per_page
    end = start + per_page
    current_categories = categories[start:end]

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=category["name"], callback_data=f"select_category_{category['_id']}")]
        for category in current_categories
    ])

    navigation_buttons = []
    if page > 1:
        navigation_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"categories_page_{page - 1}"))
    if page < total_pages:
        navigation_buttons.append(InlineKeyboardButton(text="Вперед ➡️", callback_data=f"categories_page_{page + 1}"))
    if navigation_buttons:
        keyboard.inline_keyboard.append(navigation_buttons)

    keyboard.inline_keyboard.append([InlineKeyboardButton(text="🔙 Назад", callback_data="cancel_add_product")])

    await message.answer("📂 Оберіть категорію для товару:", reply_markup=keyboard)
    await state.set_state(AddProductState.waiting_for_category)

@router.callback_query(F.data.startswith("categories_page_"), AddProductState.waiting_for_category)
async def paginate_categories(callback: CallbackQuery, state: FSMContext):
    categories = await get_all_categories()
    if not categories:
        await callback.message.edit_text("❌ Немає доступних категорій. Спочатку створіть категорію.")
        await state.clear()
        return

    page = int(callback.data.split("_")[-1])
    per_page = 6
    total_pages = (len(categories) + per_page - 1) // per_page
    start = (page - 1) * per_page
    end = start + per_page
    current_categories = categories[start:end]

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=category["name"], callback_data=f"select_category_{category['_id']}")]
        for category in current_categories
    ])

    navigation_buttons = []
    if page > 1:
        navigation_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"categories_page_{page - 1}"))
    if page < total_pages:
        navigation_buttons.append(InlineKeyboardButton(text="Вперед ➡️", callback_data=f"categories_page_{page + 1}"))
    if navigation_buttons:
        keyboard.inline_keyboard.append(navigation_buttons)

    keyboard.inline_keyboard.append([InlineKeyboardButton(text="🔙 Назад", callback_data="cancel_add_product")])

    await callback.message.edit_text("📂 Оберіть категорію для товару:", reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data.startswith("select_category_"), AddProductState.waiting_for_category)
async def process_product_category(callback: CallbackQuery, state: FSMContext):
    category_id = callback.data.split("_")[-1]
    try:
        category_id = ObjectId(category_id)
    except Exception:
        await callback.message.edit_text("❌ Невірний формат ID категорії.")
        await callback.answer()
        return

    category = await get_category_by_id(category_id)
    if not category:
        await callback.message.edit_text("❌ Категорію не знайдено.")
        await callback.answer()
        return

    await state.update_data(category_id=str(category_id))
    await callback.message.edit_text("💰 Введіть ціну товару (у форматі 123.45):")
    await state.set_state(AddProductState.waiting_for_price)
    await callback.answer()

@router.message(AddProductState.waiting_for_price)
async def process_product_price(message: Message, state: FSMContext):
    try:
        price = float(message.text.strip())
        if price <= 0:
            raise ValueError
    except ValueError:
        await message.answer("❌ Невірний формат ціни. Введіть додатне число.")
        return

    await state.update_data(price=price)
    await message.answer("📦 Введіть кількість товару на складі:")
    await state.set_state(AddProductState.waiting_for_stock)

@router.message(AddProductState.waiting_for_stock)
async def process_product_stock(message: Message, state: FSMContext):
    try:
        stock = int(message.text.strip())
        if stock < 0:
            raise ValueError
    except ValueError:
        await message.answer("❌ Невірний формат кількості. Введіть ціле число.")
        return

    await state.update_data(stock=stock)
    await message.answer("📝 Введіть опис товару або пропустіть цей крок, надіславши 'Пропустити':")
    await state.set_state(AddProductState.waiting_for_description)

@router.message(AddProductState.waiting_for_description)
async def process_product_description(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("❌ Будь ласка, введіть текст або надішліть 'Пропустити'.")
        return

    if message.text.lower() == "пропустити":
        description = ""
    else:
        description = message.text.strip()

    await state.update_data(description=description)
    await message.answer("🖼️ Надішліть фото товару або пропустіть цей крок, надіславши 'Пропустити':")
    await state.set_state(AddProductState.waiting_for_photo)

@router.message(AddProductState.waiting_for_photo)
async def process_product_photo(message: Message, state: FSMContext):
    if message.text and message.text.lower() == "пропустити":
        photo = None
    elif message.photo:
        photo = message.photo[-1].file_id
    else:
        await message.answer("❌ Надішліть фото або введіть 'Пропустити'.")
        return

    await state.update_data(photo=photo)

    data = await state.get_data()
    product_id = await create_product(
        name=data["name"],
        category_id=data["category_id"],
        price=data["price"],
        stock=data["stock"],
        description=data["description"],
        photo=data["photo"]
    )

    await message.answer(f"✅ Товар '{data['name']}' створено з ID: {product_id}")
    await state.clear()

@router.callback_query(F.data == "list_products")
async def list_products_by_category(callback: CallbackQuery):
    categories = await get_all_categories()
    if not categories:
        await callback.message.edit_text("❌ Немає доступних категорій.")
        await callback.answer()
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=category["name"], callback_data=f"view_products_{str(category['_id'])}_1")]
        for category in categories
    ])
    keyboard.inline_keyboard.append([InlineKeyboardButton(text="🔙 Назад", callback_data="admin_back")])

    try:
        await callback.message.edit_text("📂 Оберіть категорію для перегляду товарів:", reply_markup=keyboard)
    except aiogram.exceptions.TelegramBadRequest:
        await callback.message.delete()
        await callback.message.answer("📂 Оберіть категорію для перегляду товарів:", reply_markup=keyboard)

    await callback.answer()

@router.callback_query(F.data.startswith("view_products_"))
async def view_products_in_category(callback: CallbackQuery):
    data = callback.data.split("_")
    category_id = data[2]
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
        [InlineKeyboardButton(text=product["name"], callback_data=f"product_{str(product['_id'])}")]
        for product in current_products
    ])

    navigation_buttons = []
    if page > 1:
        navigation_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"view_products_{str(category_id)}_{page - 1}"))
    if end < len(products):
        navigation_buttons.append(InlineKeyboardButton(text="Вперед ➡️", callback_data=f"view_products_{str(category_id)}_{page + 1}"))
    if navigation_buttons:
        keyboard.inline_keyboard.append(navigation_buttons)

    keyboard.inline_keyboard.append([InlineKeyboardButton(text="🔙 Назад", callback_data="list_products")])

    response = f"📦 Список товарів у категорії (Сторінка {page}):\n\n"
    for product in current_products:
        response += (
            f"🔹 <b>{product['name']}</b>\n"
            f"💰 Ціна: {product['price']}\n"
            f"📦 Кількість: {product['stock']}\n\n"
        )

    await callback.message.edit_text(response, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data.startswith("product_"))
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
        f"📦 Кількість: {product['stock']}\n"
        f"📝 Опис: {product['description']}\n"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Змінити товар", callback_data=f"edit_product_{str(product['_id'])}")],
        [InlineKeyboardButton(text="❌ Видалити товар", callback_data=f"delete_product_{str(product['_id'])}")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="list_products")]
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

@router.callback_query(F.data.startswith("edit_product_"))
async def start_edit_product(callback: CallbackQuery, state: FSMContext):
    """
    Обробник для початку редагування товару.
    """
    product_id = callback.data.split("_")[-1]
    product = await get_product_by_id(product_id)
    if not product:
        await callback.message.edit_text("❌ Товар не знайдено.")
        await callback.answer()
        return

    await state.update_data(product_id=product_id)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Назва", callback_data="edit_field_name")],
        [InlineKeyboardButton(text="Ціна", callback_data="edit_field_price")],
        [InlineKeyboardButton(text="Кількість", callback_data="edit_field_stock")],
        [InlineKeyboardButton(text="Опис", callback_data="edit_field_description")],
        [InlineKeyboardButton(text="Фото", callback_data="edit_field_photo")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data=f"product_{product_id}")]
    ])

    try:
        await callback.message.edit_text("🛠️ Оберіть поле для редагування:", reply_markup=keyboard)
    except aiogram.exceptions.TelegramBadRequest:
        await callback.message.delete()
        await callback.message.answer("🛠️ Оберіть поле для редагування:", reply_markup=keyboard)

    await state.set_state(EditProductState.waiting_for_field)
    await callback.answer()

@router.callback_query(EditProductState.waiting_for_field)
async def choose_field_to_edit(callback: CallbackQuery, state: FSMContext):
    field = callback.data.split("_")[-1]
    await state.update_data(field=field)

    if field == "photo":
        await callback.message.edit_text("🖼️ Надішліть нове фото для товару:")
    else:
        await callback.message.edit_text("📝 Введіть нове значення для вибраного поля:")

    await state.set_state(EditProductState.waiting_for_new_value)
    await callback.answer()

@router.message(EditProductState.waiting_for_new_value)
async def process_new_value(message: Message, state: FSMContext):
    data = await state.get_data()
    product_id = data["product_id"]
    field = data["field"]

    if field == "photo":
        if not message.photo:
            await message.answer("❌ Надішліть фото.")
            return
        new_value = message.photo[-1].file_id
    else:
        new_value = message.text.strip()
        if not new_value:
            await message.answer("❌ Значення не може бути порожнім. Спробуйте ще раз.")
            return

    updated_count = await update_product(product_id=product_id, **{field: new_value})
    if updated_count:
        await message.answer(f"✅ Поле '{field}' успішно оновлено.")
    else:
        await message.answer("❌ Не вдалося оновити товар.")

    await state.clear()

@router.callback_query(F.data.startswith("delete_product_"))
async def delete_product(callback: CallbackQuery):
    product_id = callback.data.split("_")[-1]
    try:
        deleted_count = await delete_product_by_id(product_id)
        try:
            if deleted_count:
                await callback.message.edit_text("✅ Товар успішно видалено.")
            else:
                await callback.message.edit_text("❌ Не вдалося видалити товар. Можливо, його вже немає.")
        except aiogram.exceptions.TelegramBadRequest:
            await callback.message.delete()
            if deleted_count:
                await callback.message.answer("✅ Товар успішно видалено.")
            else:
                await callback.message.answer("❌ Не вдалося видалити товар. Можливо, його вже немає.")
    except Exception as e:
        try:
            await callback.message.edit_text(f"❌ Сталася помилка: {e}")
        except aiogram.exceptions.TelegramBadRequest:   
            await callback.message.delete()
            await callback.message.answer(f"❌ Сталася помилка: {e}")

    await callback.answer()