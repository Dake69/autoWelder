from aiogram.fsm.state import State, StatesGroup

class Registration(StatesGroup):
    full_name = State()
    phone_number = State()
    region = State()

class AddCategoryState(StatesGroup):
    waiting_for_category_name = State()

class EditCategoryState(StatesGroup):
    waiting_for_new_name = State()

class AddProductState(StatesGroup):
    waiting_for_name = State()
    waiting_for_category = State()
    waiting_for_price = State()
    waiting_for_stock = State()
    waiting_for_description = State()
    waiting_for_photo = State()

class EditProductState(StatesGroup):
    waiting_for_field = State()
    waiting_for_new_value = State()

class BroadcastForm(StatesGroup):
    message = State()

class ListCategoriesState(StatesGroup):
    viewing_categories = State()