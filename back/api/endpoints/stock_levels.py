from fastapi import APIRouter, HTTPException, status
from models.stock_level import StockLevel
from models.product import Product
from typing import List

router = APIRouter()


@router.post("", response_model=StockLevel, status_code=status.HTTP_201_CREATED)
async def create_stock_level(stock: StockLevel):
    """Create a new stock level entry."""
    # Vérifier que le produit existe
    product = await Product.find_one(Product.sku == stock.sku)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with SKU {stock.sku} not found"
        )

    # Vérifier que le stock n'existe pas déjà
    existing = await StockLevel.find_one(StockLevel.sku == stock.sku)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stock level for SKU {stock.sku} already exists"
        )

    await stock.insert()
    return stock


@router.get("", response_model=List[StockLevel])
async def list_stock_levels(limit: int = 100, skip: int = 0):
    """List all stock levels."""
    stocks = await StockLevel.find_all().skip(skip).limit(limit).to_list()
    return stocks


@router.get("/{sku}", response_model=StockLevel)
async def get_stock_level(sku: str):
    """Get stock level for a specific product."""
    stock = await StockLevel.find_one(StockLevel.sku == sku)
    if not stock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Stock level for SKU {sku} not found"
        )
    return stock


@router.put("/{sku}", response_model=StockLevel)
async def update_stock_level(sku: str, stock_on_hand: int):
    """Update stock level for a product."""
    if stock_on_hand < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stock quantity must be non-negative"
        )

    stock = await StockLevel.find_one(StockLevel.sku == sku)
    if not stock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Stock level for SKU {sku} not found"
        )

    stock.stock_on_hand = stock_on_hand
    await stock.save()
    return stock


@router.delete("/{sku}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_stock_level(sku: str):
    """Delete stock level for a product."""
    stock = await StockLevel.find_one(StockLevel.sku == sku)
    if not stock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Stock level for SKU {sku} not found"
        )

    await stock.delete()