from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def create_admin_panel_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton(text="📂 Категорії", callback_data="admin_categories")],
        [InlineKeyboardButton(text="📦 Товари", callback_data="admin_products")],
        [InlineKeyboardButton(text="⚙️ Налаштування", callback_data="admin_settings")],
        [InlineKeyboardButton(text="🔧 Спец функції", callback_data="admin_special_functions")],
    ])
    return keyboard


def create_categories_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Додати категорію", callback_data="add_category")],
        [InlineKeyboardButton(text="📋 Список категорій", callback_data="list_categories")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_back")]
    ])
    return keyboard


def create_products_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Додати товар", callback_data="add_product")],
        [InlineKeyboardButton(text="📋 Список товарів", callback_data="list_products")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_back")]
    ])
    return keyboard

keyboard_special_functions = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Розсилка повідомлень", callback_data="broadcast_message")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_back")]
    ])

stats_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_back")]
    ])