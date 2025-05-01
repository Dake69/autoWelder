from database.DB import db
from bson import ObjectId

cart_collection = db["cart"]
compileted_orders_collection = db["compileted_orders"]

async def create_cart(user_id: int):
    cart_data = {
        "user_id": user_id,
        "products": [],
        "total_price": 0.0,
        "status": "active",
        "is completed": False
    }
    result = await cart_collection.insert_one(cart_data)
    return result.inserted_id

async def add_product_to_cart(user_id: int, product_id: str):
    temp = await cart_collection.find_one({
        "user_id": user_id,
        "is completed": False
    })

    if temp is None:
        await create_cart(user_id)
        temp = await cart_collection.find_one({
            "user_id": user_id,
            "is completed": False
        })

    if product_id in temp["products"]:
        return {"error": "Цей товар вже в кошику"}

    result = await cart_collection.update_one(
        {"_id": temp["_id"]},
        {"$push": {"products": product_id}}
    )

    return result.modified_count > 0