from fastapi import APIRouter, HTTPException, status
from models.product import Product
from typing import List
from pydantic import BaseModel

router = APIRouter()


class ProductUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    price: float | None = None


@router.post("", response_model=Product, status_code=status.HTTP_201_CREATED)
async def create_product(product: Product):
    """Create a new product."""
    existing = await Product.find_one(Product.sku == product.sku)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Product with SKU {product.sku} already exists"
        )

    await product.insert()
    return product


@router.get("", response_model=List[Product])
async def list_products(category: str | None = None, limit: int = 100):
    """List all products, optionally filtered by category."""
    if category:
        products = await Product.find(Product.category == category).limit(limit).to_list()
    else:
        products = await Product.find_all().limit(limit).to_list()
    return products


@router.get("/{sku}", response_model=Product)
async def get_product(sku: str):
    """Get a product by SKU."""
    product = await Product.find_one(Product.sku == sku)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with SKU {sku} not found"
        )
    return product


@router.put("/{sku}", response_model=Product)
async def update_product(sku: str, update_data: ProductUpdate):
    """Update a product."""
    product = await Product.find_one(Product.sku == sku)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with SKU {sku} not found"
        )

    if update_data.name is not None:
        product.name = update_data.name
    if update_data.category is not None:
        product.category = update_data.category
    if update_data.price is not None:
        product.price = update_data.price

    await product.save()
    return product


@router.delete("/{sku}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(sku: str):
    """Delete a product."""
    product = await Product.find_one(Product.sku == sku)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with SKU {sku} not found"
        )

    await product.delete()