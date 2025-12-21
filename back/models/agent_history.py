from beanie import Document, Indexed
from pydantic import Field
from datetime import datetime, timezone
import uuid
from typing import Literal

class AgentHistory(Document):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Date and time of the history entry")
    response: str = Field(..., description="Agent's response to the user query")
    type: Literal["answer", "tool"] = Field(default="answer", description="Type of the agent interaction")

    class Settings:
        name = "agent_history"
        use_state_management = True

    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2025-10-28T10:30:00Z",
                "response": "The current stock level for SKU123 is 150 units.",
                "type": "answer"
            }
        }