from fastapi import APIRouter
from .endpoints import products, sales_transactions

router = APIRouter()
router.include_router(products.router, prefix="/products", tags=["products"])
router.include_router(sales_transactions.router, prefix="/sales", tags=["sales"])
