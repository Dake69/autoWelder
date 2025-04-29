from database.DB import db

users_collection = db["users"]

async def save_user(user_id: int, full_name: str, phone_number: str, region: str):
    user_data = {
        "user_id": user_id,
        "full_name": full_name,
        "phone_number": phone_number,
        "region": region
    }
    await users_collection.update_one({"user_id": user_id}, {"$set": user_data}, upsert=True)

async def get_user(user_id: int):
    return await users_collection.find_one({"user_id": user_id})

async def delete_user(user_id: int):
    await users_collection.delete_one({"user_id": user_id})