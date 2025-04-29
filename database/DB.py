import motor.motor_asyncio

from config import MONGO_URI

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)

db = client["autoWelder"]

async def test_connection():
    try:
        collections = await db.list_collection_names()
        print(f"✅ Успішно підключено до MongoDB! Колекції: {collections}")
    except Exception as e:
        print(f"❌ Помилка підключення до MongoDB: {e}")