from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def create_regions_inline_keyboard(page: int = 1, per_page: int = 8):
    regions = [
        "Вінницька", "Волинська", "Дніпропетровська", "Донецька",
        "Житомирська", "Закарпатська", "Запорізька", "Івано-Франківська",
        "Київська", "Кіровоградська", "Луганська", "Львівська",
        "Миколаївська", "Одеська", "Полтавська", "Рівненська",
        "Сумська", "Тернопільська", "Харківська", "Херсонська",
        "Хмельницька", "Черкаська", "Чернівецька", "Чернігівська"
    ]

    start = (page - 1) * per_page
    end = start + per_page
    current_regions = regions[start:end]

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=region, callback_data=f"r_{i}")] for i, region in enumerate(current_regions, start=start + 1)
    ])

    navigation_buttons = []
    if page > 1:
        navigation_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"page_{page - 1}"))
    if end < len(regions):
        navigation_buttons.append(InlineKeyboardButton(text="Вперед ➡️", callback_data=f"page_{page + 1}"))
    if navigation_buttons:
        keyboard.inline_keyboard.append(navigation_buttons)

    return keyboard