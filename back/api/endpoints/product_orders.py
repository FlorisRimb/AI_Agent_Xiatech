from fastapi import APIRouter, HTTPException, status
from models.product_order import ProductOrder
from typing import List
from pydantic import BaseModel

router = APIRouter()


class ProductOrderUpdate(BaseModel):
    sku: str | None = None
    quantity: int | None = None
    status: str | None = None

@router.post("", response_model=ProductOrder, status_code=status.HTTP_201_CREATED)
async def create_product_order(order: ProductOrder):
    """Create a new product order."""
    # Validate SKU is not empty
    if not order.sku or not order.sku.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SKU cannot be empty"
        )

    # Validate product exists
    from models.product import Product
    product = await Product.find_one(Product.sku == order.sku.strip())
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with SKU {order.sku} not found"
        )

    await order.insert()
    return order

@router.get("", response_model=List[ProductOrder])
async def list_product_orders(limit: int = 100, status: str | None = None, days: int | None = None):
    """List all product orders."""
    # Build query conditions
    if status and days is not None:
        from datetime import datetime, timedelta
        cutoff_date = datetime.now() - timedelta(days=days)
        orders = await ProductOrder.find(
            ProductOrder.status == status,
            ProductOrder.order_date >= cutoff_date
        ).limit(limit).to_list()
    elif status:
        orders = await ProductOrder.find(ProductOrder.status == status).limit(limit).to_list()
    elif days is not None:
        from datetime import datetime, timedelta
        cutoff_date = datetime.now() - timedelta(days=days)
        orders = await ProductOrder.find(ProductOrder.order_date < cutoff_date).limit(limit).to_list()
    else:
        orders = await ProductOrder.find_all().limit(limit).to_list()
    return orders

@router.get("/{order_id}", response_model=ProductOrder)
async def get_product_order(order_id: str):
    """Get a product order by ID."""
    order = await ProductOrder.find_one(ProductOrder.order_id == order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order {order_id} not found"
        )
    return order

@router.put("/{order_id}", response_model=ProductOrder)
async def update_product_order(
    order_id: str,
    update_data: ProductOrderUpdate
):
    """Update a product order."""
    order = await ProductOrder.find_one(ProductOrder.order_id == order_id)
    if not order:
        print(f"[Orders] Order {order_id} not found for update")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order {order_id} not found"
        )

    if update_data.sku is not None:
        order.sku = update_data.sku
    if update_data.quantity is not None:
        order.quantity = update_data.quantity
    if update_data.status is not None:
        if order.status == "pending" and update_data.status == "completed":
            from models.stock_level import StockLevel
            stock = await StockLevel.find_one(StockLevel.sku == order.sku)
            stock.stock_on_hand += order.quantity
            await stock.save()
        order.status = update_data.status

    await order.save()
    return order

@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product_order(order_id: str):
    """Delete a product order."""
    order = await ProductOrder.find_one(ProductOrder.order_id == order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order {order_id} not found"
        )
    await order.delete()