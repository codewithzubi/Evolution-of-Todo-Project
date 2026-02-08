"""Conversation State Model for FSM (Finite State Machine).

Persists multi-step conversation context for task actions.
Ensures strict step-based flow without mixing intents.
"""

import json
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from sqlalchemy import JSON
from sqlmodel import Field, SQLModel


class ConversationState(SQLModel, table=True):
    """Persistent conversation state for FSM.

    Tracks:
    - Current intent (ADD_TASK, UPDATE_TASK, DELETE_TASK, IDLE)
    - Current step in intent flow (TITLE, DESCRIPTION, CONFIRM, etc.)
    - Collected data for the current intent
    """

    __tablename__ = "conversation_states"

    # Primary key - auto-generate UUID
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", index=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)

    # FSM State
    intent_mode: str = Field(
        default="IDLE",
        description="Current intent: IDLE | ADD_TASK | UPDATE_TASK | DELETE_TASK | COMPLETE_TASK",
    )
    intent_step: Optional[str] = Field(
        default=None,
        description="Current step: TITLE | DESCRIPTION | PRIORITY | DUE_DATE | CONFIRM | TASK_ID | etc.",
    )

    # Collected data for current intent (using JSON type from SQLAlchemy)
    intent_payload: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_type=JSON,
        description="Collected fields: {title, description, priority, due_date, task_id, ...}",
    )

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "660e8400-e29b-41d4-a716-446655440001",
                "intent_mode": "ADD_TASK",
                "intent_step": "DESCRIPTION",
                "intent_payload": {
                    "title": "Buy groceries",
                },
            }
        }
