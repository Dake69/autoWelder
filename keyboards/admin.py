from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def create_admin_panel_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton(text="👥 Користувачі", callback_data="admin_users")],
        [InlineKeyboardButton(text="⚙️ Налаштування", callback_data="admin_settings")],
    ])
    return keyboard