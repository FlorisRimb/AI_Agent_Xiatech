from fastapi import APIRouter, HTTPException, status
from models.stock_level import StockLevel
from models.product import Product
from models.product_order import ProductOrder
from typing import List
from pydantic import BaseModel

router = APIRouter()


class StockLevelUpdate(BaseModel):
    stock_on_hand: int


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
async def list_stock_levels(
    sku: str | None = None,
    min_stock: int | None = None,
    max_stock: int | None = None,
    limit: int = 100,
    skip: int = 0
):
    """List all stock levels with optional filters."""
    conditions = []

    if sku:
        conditions.append(StockLevel.sku == sku)
    if min_stock is not None:
        conditions.append(StockLevel.stock_on_hand >= min_stock)
    if max_stock is not None:
        conditions.append(StockLevel.stock_on_hand <= max_stock)

    if conditions:
        stocks = await StockLevel.find(*conditions).skip(skip).limit(limit).to_list()
    else:
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
async def update_stock_level(sku: str, update_data: StockLevelUpdate):
    """Update stock level for a product."""
    if update_data.stock_on_hand < 0:
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

    stock.stock_on_hand = update_data.stock_on_hand
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


@router.get("/virtual/all", response_model=List[StockLevel])
async def get_all_virtual_stock():
    """Get all stock levels with virtual stock (including pending orders)"""
    stocks = await StockLevel.find_all().to_list()
    result = []

    for stock in stocks:
        # Récupérer les commandes en attente pour ce produit
        pending_orders = await ProductOrder.find(
            ProductOrder.sku == stock.sku,
            ProductOrder.status == "pending"
        ).to_list()

        virtual_stock = stock.stock_on_hand - sum(order.quantity for order in pending_orders)
        stock_dict = stock.dict()
        stock_dict["virtual_stock"] = virtual_stock
        result.append(StockLevel(**stock_dict))

    return result