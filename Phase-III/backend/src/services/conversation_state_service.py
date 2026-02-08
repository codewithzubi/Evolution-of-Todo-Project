"""Conversation State Service - FSM State Management.

Handles conversation-level FSM state for multi-step task flows.
Ensures strict step-based progression without intent mixing.
"""

import logging
from typing import Any, Dict, Optional
from uuid import UUID

from sqlmodel import Session, select

from ..models.conversation_state import ConversationState

logger = logging.getLogger(__name__)


# ============================================================================
# Intent Step Definitions
# ============================================================================

INTENT_STEPS = {
    "ADD_TASK": ["TITLE", "DESCRIPTION", "PRIORITY", "DUE_DATE", "CONFIRM"],
    "UPDATE_TASK": ["TASK_ID", "TITLE", "DESCRIPTION", "PRIORITY", "DUE_DATE", "CONFIRM"],
    "DELETE_TASK": ["TASK_ID", "CONFIRM"],
    "COMPLETE_TASK": ["TASK_ID", "CONFIRM"],
    "LIST_TASKS": [],  # No multi-step flow
}

REQUIRED_FIELDS = {
    "ADD_TASK": ["title"],
    "UPDATE_TASK": ["task_id"],
    "DELETE_TASK": ["task_id"],
    "COMPLETE_TASK": ["task_id"],
}

STEP_PROMPTS = {
    "TITLE": "What would you like to call this task?",
    "DESCRIPTION": "Great! Now describe what this task is about (optional):",
    "PRIORITY": "What priority level? (low, medium, high)",
    "DUE_DATE": "When is this due? (e.g., 2026-02-15)",
    "TASK_ID": "Which task? Please provide the task ID.",
    "CONFIRM": "Ready to proceed?",
}


class ConversationStateService:
    """Manages FSM state for conversations."""

    @staticmethod
    async def get_conversation_state(
        db: Session,
        conversation_id: UUID,
        user_id: UUID,
    ) -> Optional[ConversationState]:
        """Get current FSM state for conversation."""
        statement = select(ConversationState).where(
            ConversationState.conversation_id == conversation_id,
            ConversationState.user_id == user_id,
        )
        # Use execute().scalars() for SQLAlchemy Session compatibility (not SQLModel exec())
        return db.execute(statement).scalars().first()

    @staticmethod
    async def initialize_state(
        db: Session,
        conversation_id: UUID,
        user_id: UUID,
    ) -> ConversationState:
        """Initialize new FSM state (IDLE)."""
        state = ConversationState(
            conversation_id=conversation_id,
            user_id=user_id,
            intent_mode="IDLE",
            intent_step=None,
            intent_payload=None,
        )
        db.add(state)
        db.commit()
        db.refresh(state)
        logger.debug(f"[STATE] Initialized IDLE state for conversation {conversation_id}")
        return state

    @staticmethod
    async def set_intent(
        db: Session,
        conversation_id: UUID,
        user_id: UUID,
        intent_mode: str,
    ) -> ConversationState:
        """Set new intent and move to first step."""
        state = await ConversationStateService.get_conversation_state(db, conversation_id, user_id)

        if not state:
            state = await ConversationStateService.initialize_state(db, conversation_id, user_id)

        # Set new intent
        state.intent_mode = intent_mode
        state.intent_step = INTENT_STEPS.get(intent_mode, [])[0] if INTENT_STEPS.get(intent_mode) else None
        state.intent_payload = {}

        db.add(state)
        db.commit()
        db.refresh(state)

        logger.info(
            f"[STATE_TRANSITION] {conversation_id}: IDLE → {intent_mode} "
            f"(step: {state.intent_step})"
        )
        return state

    @staticmethod
    async def advance_step(
        db: Session,
        conversation_id: UUID,
        user_id: UUID,
        field_name: str,
        field_value: Any,
    ) -> Dict[str, Any]:
        """Advance to next step after collecting field.

        Returns:
            {
                "success": bool,
                "state": ConversationState,
                "message": str,
                "ready_to_execute": bool,  # All required fields collected
            }
        """
        state = await ConversationStateService.get_conversation_state(db, conversation_id, user_id)

        if not state or state.intent_mode == "IDLE":
            return {
                "success": False,
                "state": None,
                "message": "No active task action. Start with 'add task', 'update task', or 'delete task'.",
                "ready_to_execute": False,
            }

        # Update payload with new field
        if not state.intent_payload:
            state.intent_payload = {}

        state.intent_payload[field_name] = field_value
        logger.debug(
            f"[STATE] {state.intent_mode}, step {state.intent_step}: "
            f"collected field '{field_name}' = {field_value}"
        )

        # Check if all required fields collected
        required = REQUIRED_FIELDS.get(state.intent_mode, [])
        missing = [f for f in required if f not in (state.intent_payload or {})]

        if not missing:
            logger.info(
                f"[READY_TO_EXECUTE] {state.intent_mode} with all fields: "
                f"{list(state.intent_payload.keys())}"
            )
            state.intent_step = "CONFIRM"
            db.add(state)
            db.commit()
            db.refresh(state)

            return {
                "success": True,
                "state": state,
                "message": "All required fields collected. Ready to proceed.",
                "ready_to_execute": True,
            }

        # Move to next step
        current_steps = INTENT_STEPS.get(state.intent_mode, [])
        if state.intent_step in current_steps:
            current_idx = current_steps.index(state.intent_step)
            next_step = current_steps[current_idx + 1] if current_idx + 1 < len(current_steps) else "CONFIRM"
            state.intent_step = next_step

        db.add(state)
        db.commit()
        db.refresh(state)

        next_prompt = STEP_PROMPTS.get(state.intent_step, "")

        return {
            "success": True,
            "state": state,
            "message": next_prompt,
            "ready_to_execute": False,
        }

    @staticmethod
    async def reset_state(
        db: Session,
        conversation_id: UUID,
        user_id: UUID,
    ) -> ConversationState:
        """Reset FSM state to IDLE after successful action."""
        state = await ConversationStateService.get_conversation_state(db, conversation_id, user_id)

        if state:
            state.intent_mode = "IDLE"
            state.intent_step = None
            state.intent_payload = None

            db.add(state)
            db.commit()
            db.refresh(state)

            logger.info(f"[STATE_RESET] {conversation_id}: → IDLE")

        return state

    @staticmethod
    def is_in_multi_step_flow(state: Optional[ConversationState]) -> bool:
        """Check if conversation is in active multi-step flow."""
        return state is not None and state.intent_mode != "IDLE"

    @staticmethod
    def get_next_step_message(state: ConversationState) -> str:
        """Get prompt for next step."""
        if state.intent_step:
            return STEP_PROMPTS.get(state.intent_step, "Continue with the next detail:")
        return "What would you like to do?"
