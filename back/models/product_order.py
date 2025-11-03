from beanie import Document, Indexed
from pydantic import Field
from datetime import datetime

class ProductOrder(Document):
    order_id: Indexed(str, unique=True) = Field(..., description="Unique product order ID")
    sku: Indexed(str) = Field(..., description="Product identifier (matches products.sku)")
    order_date: datetime = Field(default_factory=datetime.utcnow, description="Date and time when the order was placed")
    quantity: int = Field(..., ge=1, description="Quantity ordered")

    class Settings:
        name = "product_orders"
        use_state_management = True

    class Config:
        json_schema_extra = {
            "example": {
                "order_id": "ORD-20251028-001",
                "sku": "SKU123",
                "order_date": "2025-10-28T10:30:00Z",
                "quantity": 10
            }
        }