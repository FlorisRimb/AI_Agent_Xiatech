from beanie import Document, Indexed
from pydantic import Field
from datetime import datetime
import uuid


class SalesTransaction(Document):
    transaction_id: Indexed(str, unique=True) = Field(default_factory=lambda: f"TXN-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}", description="Unique sales transaction ID")
    sku: Indexed(str) = Field(..., description="Product identifier (matches products.sku)")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Date and time of the sale")
    quantity: int = Field(..., ge=1, description="Quantity sold in this transaction")

    class Settings:
        name = "sales_transactions"
        use_state_management = True

    class Config:
        json_schema_extra = {
            "example": {
                "transaction_id": "TXN-20251028-001",
                "sku": "SKU123",
                "timestamp": "2025-10-28T10:30:00Z",
                "quantity": 5
            }
        }
