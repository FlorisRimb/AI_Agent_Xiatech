from beanie import Document, Indexed
from pydantic import Field
from typing import Optional
from datetime import datetime
import uuid

class Product(Document):
    sku: Indexed(str, unique=True) = Field(default_factory=lambda: f"SKU-{uuid.uuid4().hex[:6]}", description="Unique product identifier (SKU)")
    name: str = Field(..., description="Product name")
    category: str = Field(..., description="Product category")
    price: float = Field(..., ge=0, description="Product unit price")

    class Settings:
        name = "products"
        use_state_management = True

    class Config:
        json_schema_extra = {
            "example": {
                "sku": "SKU123",
                "name": "Wireless Mouse",
                "category": "Electronics",
                "price": 29.99
            }
        }

