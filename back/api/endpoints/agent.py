from fastapi import APIRouter, HTTPException, status
from models.product import Product
from models.stock_level import StockLevel
from models.sales_transaction import SalesTransaction
from models.product_order import ProductOrder
from typing import List
from datetime import datetime, timedelta
from pydantic import BaseModel

router = APIRouter()

class OrderProductRequest(BaseModel):
    sku: str
    quantity: int

class DailySalesRequest(BaseModel):
    sku: str
    days: int = 3

class StockLevelRequest(BaseModel):
    sku: str

@router.get("/products_soon_out_of_stock", response_model=List[Product])
async def get_products_soon_out_of_stock(days: int = 3):
    """Get products that will be out of stock within the next 'days' days."""
    products_soon_out_of_stock = []
    threshold_date = datetime.utcnow() + timedelta(days=days)
    products = await Product.find_all().to_list()
    for product in products:
        transactions = await SalesTransaction.find(
            SalesTransaction.sku == product.sku,
            SalesTransaction.timestamp >= datetime.utcnow() - timedelta(days=days)
        ).to_list()
        total_sold = sum(tr.quantity for tr in transactions)

        stock_level = await StockLevel.find_one(StockLevel.sku == product.sku)
        if stock_level:
            projected_stock = stock_level.stock_on_hand - total_sold
            if projected_stock <= 0:
                products_soon_out_of_stock.append(product)            
    
    return products_soon_out_of_stock


@router.post("/order_product", response_model=ProductOrder, status_code=status.HTTP_201_CREATED)
async def order_products(request: OrderProductRequest):
    """Create product orders for the given sku with quantity."""
    print(f"Creating order for SKU {request.sku} with quantity {request.quantity}")
    
    product = await Product.find_one(Product.sku == request.sku)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with SKU {request.sku} not found"
        )
        
    order = ProductOrder(
        order_id=f"order_{request.sku}_{int(datetime.utcnow().timestamp())}",
        sku=request.sku,
        quantity=request.quantity,
        order_date=datetime.utcnow(),
    )
    await order.insert()
    
    return order


@router.post("/daily_sales_data", response_model=dict)
async def get_daily_sales_for_product(request: DailySalesRequest) -> dict:
    """Get daily sales data for a given product over the past 'days' days."""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=request.days)
    sales_data = {}
    
    for day_offset in range(request.days):
        day = start_date + timedelta(days=day_offset)
        next_day = day + timedelta(days=1)
        
        daily_sales = await SalesTransaction.find(
            SalesTransaction.sku == request.sku,
            SalesTransaction.timestamp >= day,
            SalesTransaction.timestamp < next_day
        ).to_list()
        
        total_quantity = sum(sale.quantity for sale in daily_sales)
        sales_data[day.strftime("%Y-%m-%d")] = total_quantity
    
    return sales_data


@router.post("/stock_level", response_model=dict)
async def get_stock_level_for_product(request: StockLevelRequest) -> dict:
    """Get current stock levels for a given product."""
    stock = await StockLevel.find_one(StockLevel.sku == request.sku)
    if not stock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Stock level for SKU {request.sku} not found"
        )
    return {"sku": request.sku, "stock_on_hand": stock.stock_on_hand}