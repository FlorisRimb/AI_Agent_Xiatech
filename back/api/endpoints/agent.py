from fastapi import APIRouter, HTTPException, status
from models.product import Product
from models.stock_level import StockLevel
from models.sales_transaction import SalesTransaction
from models.product_order import ProductOrder
from typing import List
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/products_soon_out_of_stock", response_model=List[Product])
async def get_products_soon_out_of_stock(days: int = 3):
    """Get products that will be out of stock within the next 'days' days."""
    products_soon_out_of_stock = []
    threshold_date = datetime.utcnow() + timedelta(days=days)
    products = await Product.find_all().to_list()
    for product in products:
        transactions = await SalesTransaction.find(
            SalesTransaction.sku == product.sku,
            SalesTransaction.timestamp >= datetime.utcnow() - timedelta(days=days))
            .to_list()
        total_sold = sum(tr.quantity for tr in transactions)

        stock_level = await StockLevel.find_one(StockLevel.sku == product.sku)
        if stock_level:
            projected_stock = stock_level.quantity - total_sold
            if projected_stock <= 0:
                products_soon_out_of_stock.append(product)            
    
    return products_soon_out_of_stock


@router.post("/order_product", response_model=ProductOrder, status_code=status.HTTP_201_CREATED)
async def order_product(sku: str, quantity: int):
    """Create a product order for restocking."""
    product = await Product.find_one(Product.sku == sku)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with SKU {sku} not found"
        )
    
    product_order = ProductOrder(
        sku=sku,
        quantity=quantity,
        order_date=datetime.utcnow()
    )
    await product_order.insert()
    return product_order


