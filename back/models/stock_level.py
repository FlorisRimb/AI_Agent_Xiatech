from beanie import Document, Indexed
from pydantic import Field


class StockLevel(Document):
    sku: Indexed(str, unique=True) = Field(..., description="Product identifier (matches products.sku)")
    stock_on_hand: int = Field(..., ge=0, description="Current quantity in stock")

    class Settings:
        name = "stock_levels"
        use_state_management = True

    class Config:
        json_schema_extra = {
            "example": {
                "sku": "SKU123",
                "stock_on_hand": 150
            }
        }