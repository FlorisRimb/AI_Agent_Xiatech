from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from models.product import Product
from core.config import settings

async def init_db():
    client = AsyncIOMotorClient(settings.MONGO_URL)
    db = client.get_default_database()

    await init_beanie(database=db, document_models=[
        Product,
    ])

    print(f"Database initialized: {db.name}")