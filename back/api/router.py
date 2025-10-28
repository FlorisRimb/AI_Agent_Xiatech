from fastapi import APIRouter
from .endpoints import products

router = APIRouter()
router.include_router(products.router, prefix="/products", tags=["products"])