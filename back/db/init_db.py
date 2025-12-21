from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from models.product import Product
from models.sales_transaction import SalesTransaction
from models.stock_level import StockLevel
from models.product_order import ProductOrder
from models.agent_history import AgentHistory
from core.config import settings

async def init_db():
    client = AsyncIOMotorClient(settings.MONGO_URL)
    db = client.get_default_database()

    await init_beanie(database=db, document_models=[
        Product,
        SalesTransaction,
        StockLevel,
        ProductOrder,
        AgentHistory
    ])

    print(f"Database initialized: {db.name}")