from fastapi import APIRouter, HTTPException, status
from models.agent_history import AgentHistory
from typing import List
from datetime import datetime

router = APIRouter()


@router.post("", response_model=AgentHistory, status_code=status.HTTP_201_CREATED)
async def create_agent_history(agent_history: AgentHistory):
    """Create a new agent history entry."""
    await agent_history.insert()
    return agent_history


@router.get("", response_model=List[AgentHistory])
async def list_agent_history(type: str | None = None, limit: int = 100):
    """List all agent history entries, optionally filtered by type."""
    if type:
        history = await AgentHistory.find(AgentHistory.type == type).sort(-AgentHistory.timestamp).limit(limit).to_list()
    else:
        history = await AgentHistory.find_all().sort(-AgentHistory.timestamp).limit(limit).to_list()
    return history


@router.get("/{history_id}", response_model=AgentHistory)
async def get_agent_history(history_id: str):
    """Get an agent history entry by ID."""
    history = await AgentHistory.get(history_id)
    if not history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent history with ID {history_id} not found"
        )
    return history


@router.delete("/{history_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent_history(history_id: str):
    """Delete an agent history entry."""
    history = await AgentHistory.get(history_id)
    if not history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent history with ID {history_id} not found"
        )

    await history.delete()
