from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

keyboard_main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📂 Каталог товарів", callback_data="catalog")],
    [InlineKeyboardButton(text="👤 Особистий кабінет", callback_data="profile")],
    [InlineKeyboardButton(text="🛒 Кошик", callback_data="cart")]
])