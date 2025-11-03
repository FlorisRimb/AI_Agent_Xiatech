from fastapi import APIRouter, HTTPException, status
from models.product_order import ProductOrder
from typing import List

router = APIRouter()

@router.post("", response_model=ProductOrder, status_code=status.HTTP_201_CREATED)
async def create_product_order(order: ProductOrder):
    """Create a new product order."""
    existing = await ProductOrder.find_one(ProductOrder.order_id == order.order_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Order with ID {order.order_id} already exists"
        )
    await order.insert()
    return order

@router.get("", response_model=List[ProductOrder])
async def list_product_orders(limit: int = 100, skip: int = 0):
    """List all product orders."""
    orders = await ProductOrder.find_all().skip(skip).limit(limit).to_list()
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
    sku: str | None = None,
    quantity: int | None = None,
    status: str | None = None
):
    """Update a product order."""
    order = await ProductOrder.find_one(ProductOrder.order_id == order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order {order_id} not found"
        )
    
    if sku is not None:
        order.sku = sku
    if quantity is not None:
        order.quantity = quantity
    if status is not None:
        order.status = status
    
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