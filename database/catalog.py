from database.DB import db

category_collection = db["category"]
product_collection = db["product"]

# -------------------- Категорії --------------------

async def create_category(name: str):
    category_data = {
        "name": name
    }
    result = await category_collection.insert_one(category_data)
    return result.inserted_id

async def get_all_categories():
    categories = await category_collection.find().to_list(length=None)
    return categories

async def get_category_by_id(category_id: str):
    category = await category_collection.find_one({"_id": category_id})
    return category

async def update_category(category_id: str, name: str = None):
    update_data = {}
    if name:
        update_data["name"] = name

    result = await category_collection.update_one({"_id": category_id}, {"$set": update_data})
    return result.modified_count

async def delete_category(category_id: str):
    result = await category_collection.delete_one({"_id": category_id})
    return result.deleted_count

# -------------------- Товари --------------------

async def create_product(name: str, category_id: str, price: float, description: str = "", stock: int = 0):
    product_data = {
        "name": name,
        "category_id": category_id,
        "price": price,
        "description": description,
        "stock": stock
    }
    result = await product_collection.insert_one(product_data)
    return result.inserted_id

async def get_all_products():
    products = await product_collection.find().to_list(length=None)
    return products

async def get_products_by_category(category_id: str):
    products = await product_collection.find({"category_id": category_id}).to_list(length=None)
    return products

async def get_product_by_id(product_id: str):
    product = await product_collection.find_one({"_id": product_id})
    return product

async def update_product(product_id: str, name: str = None, price: float = None, description: str = None, stock: int = None):
    update_data = {}
    if name:
        update_data["name"] = name
    if price is not None:
        update_data["price"] = price
    if description:
        update_data["description"] = description
    if stock is not None:
        update_data["stock"] = stock

    result = await product_collection.update_one({"_id": product_id}, {"$set": update_data})
    return result.modified_count

async def delete_product(product_id: str):
    result = await product_collection.delete_one({"_id": product_id})
    return result.deleted_count