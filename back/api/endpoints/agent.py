from fastapi import APIRouter, HTTPException, status
from models.product import Product
from models.stock_level import StockLevel
from models.sales_transaction import SalesTransaction
from models.product_order import ProductOrder
from typing import List, Dict
from datetime import datetime, timedelta
from pydantic import BaseModel
import subprocess
import json

router = APIRouter()

class OrderItem(BaseModel):
    sku: str
    quantity: int

class OrderProductRequest(BaseModel):
    orders: List[OrderItem] 

class DailySalesRequest(BaseModel):
    sku: str
    days: int = 3

class StockLevelRequest(BaseModel):
    sku: str

@router.get("/products_soon_out_of_stock", response_model=List[Product])
async def get_products_soon_out_of_stock(days: int = 3):
    """Get products that will be out of stock within the next 'days' days."""
    products_soon_out_of_stock = []
    products = await Product.find_all().to_list()
    
    for product in products:
        # Obtenir le niveau de stock actuel
        stock_level = await StockLevel.find_one(StockLevel.sku == product.sku)
        if not stock_level:
            continue
            
        current_stock = stock_level.stock_on_hand
        
        if current_stock < 50:
            products_soon_out_of_stock.append(product)
    
    return products_soon_out_of_stock


@router.post("/order_products", response_model=List[ProductOrder], status_code=status.HTTP_201_CREATED)
async def order_products(request: OrderProductRequest):
    """Create purchase orders for multiple products."""
    orders = []
    for order in request.orders:
        sku = order.sku
        quantity = order.quantity
        product = await Product.find_one(Product.sku == sku)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with SKU {sku} not found"
            )
            
        timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        order_id = f"ORD-{timestamp}-{sku}"
        
        product_order = ProductOrder(
            order_id=order_id,
            sku=sku,
            quantity=quantity,
            order_date=datetime.utcnow()
        )
        await product_order.insert()
        orders.append(product_order)
    return orders
    


# @router.post("/daily_sales_data", response_model=dict)
# async def get_daily_sales_for_product(request: DailySalesRequest) -> dict:
#     """Get daily sales data for a given product over the past 'days' days."""
#     end_date = datetime.utcnow()
#     start_date = end_date - timedelta(days=request.days)
#     sales_data = {}
    
#     for day_offset in range(request.days):
#         day = start_date + timedelta(days=day_offset)
#         next_day = day + timedelta(days=1)
        
#         daily_sales = await SalesTransaction.find(
#             SalesTransaction.sku == request.sku,
#             SalesTransaction.timestamp >= day,
#             SalesTransaction.timestamp < next_day
#         ).to_list()
        
#         total_quantity = sum(sale.quantity for sale in daily_sales)
#         sales_data[day.strftime("%Y-%m-%d")] = total_quantity
    
#     return sales_data


# @router.post("/stock_level", response_model=dict)
# async def get_stock_level_for_product(request: StockLevelRequest) -> dict:
#     """Get current stock levels for a given product."""
#     stock = await StockLevel.find_one(StockLevel.sku == request.sku)
#     if not stock:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Stock level for SKU {request.sku} not found"
#         )
#     return {"sku": request.sku, "stock_on_hand": stock.stock_on_hand}