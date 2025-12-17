from fastapi import APIRouter
from .endpoints import agent_history, products, sales_transactions, stock_levels, product_orders

router = APIRouter()
router.include_router(products.router, prefix="/products", tags=["products"])
router.include_router(sales_transactions.router, prefix="/sales", tags=["sales"])
router.include_router(stock_levels.router, prefix="/stocks", tags=["stocks"])
router.include_router(product_orders.router, prefix="/orders", tags=["orders"])
router.include_router(agent_history.router, prefix="/agent", tags=["agent"])
