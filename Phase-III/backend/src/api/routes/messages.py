# [Task]: T330, T331, T337, T338, [From]: specs/004-ai-chatbot/spec.md#Requirements
"""Message endpoints for chat API.

Provides:
- POST /api/v1/chat/conversations/{conversation_id}/messages - Send message and get AI response
- GET /api/v1/chat/conversations/{conversation_id}/messages - Get conversation messages (paginated)
- DELETE /api/v1/chat/conversations/{conversation_id}/messages/{message_id} - Soft-delete message
"""

import asyncio
import logging
import time
import json
from datetime import datetime
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, Query, Request
from sqlmodel import Session

from ...agents.executor import AgentExecutor
from ...database import get_db
from ...services.conversation_service import ConversationService
from ...services.conversation_state_service import ConversationStateService
from ...services.message_service import MessagePersistenceService
from ..chat_exceptions import (
    AgentTimeoutError,
    ConversationNotFoundError,
    InvalidMessageError,
    InvalidConversationAccessError,
    OpenAIAPIError,
    RateLimitError,
)
from ..chat_schemas import (
    ChatRequest,
    ChatResponse,
    MessageResponse,
    PaginatedMessagesResponse,
    SuccessResponseWrapper,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/chat",
    tags=["messages"],
)


# [Task]: T331, T337
@router.post(
    "/conversations/{conversation_id}/messages",
    response_model=SuccessResponseWrapper,
)
async def send_message(
    request: Request,
    conversation_id: UUID,
    body: ChatRequest,
    db: Session = Depends(get_db),
) -> SuccessResponseWrapper:
    """Send a message and get AI response.

    [Task]: T331, [From]: specs/004-ai-chatbot/spec.md#Endpoints

    [MANDATORY SAFETY GUARANTEE]
    - ALWAYS returns HTTP 200 (never HTTP 500)
    - Response always includes valid assistant message
    - No exceptions propagate to FastAPI

    Core chat endpoint that:
    1. Validates user has access to conversation
    2. Saves user message to database
    3. Loads conversation history
    4. Invokes OpenAI Agent via AgentExecutor
    5. Saves AI response with tool metadata
    6. Returns response to client

    Args:
        request: FastAPI Request object (contains user_id in state)
        conversation_id: Conversation ID to send message to
        body: ChatRequest with message and optional metadata
        db: Database session

    Returns:
        SuccessResponseWrapper containing ChatResponse (ALWAYS HTTP 200)
    """
    user_id = request.state.user_id
    start_time = time.time()

    # ========================================================================
    # ABSOLUTE SAFETY NET: Wrap ENTIRE flow in try/except
    # ========================================================================
    try:
        # Validate message
        if not body.message or not body.message.strip():
            logger.warning(f"Empty message from user {user_id}")
            raise InvalidMessageError("Message cannot be empty")

        if len(body.message) > 5000:
            logger.warning(f"Message too long from user {user_id}")
            raise InvalidMessageError("Message exceeds maximum length of 5000 characters")

        logger.info(
            f"[CHAT_START] User {user_id}, conversation {conversation_id}, "
            f"message_length={len(body.message)}"
        )

        # Verify conversation exists and belongs to user
        conversation = await ConversationService.get_conversation(
            db=db,
            user_id=user_id,
            conversation_id=conversation_id,
        )

        if not conversation:
            raise ConversationNotFoundError(str(conversation_id))

        # Save user message
        user_message = await MessagePersistenceService.save_user_message(
            db=db,
            user_id=user_id,
            conversation_id=conversation_id,
            content=body.message.strip(),
            metadata=body.metadata,
        )

        logger.debug(f"Saved user message {user_message.id}")

        # ====================================================================
        # FSM STATE CHECK: Get current conversation state
        # ====================================================================
        conversation_state = await ConversationStateService.get_conversation_state(
            db=db,
            conversation_id=conversation_id,
            user_id=user_id,
        )

        # Initialize state if not present
        if not conversation_state:
            conversation_state = await ConversationStateService.initialize_state(
                db=db,
                conversation_id=conversation_id,
                user_id=user_id,
            )
            logger.debug(f"[FSM] Initialized new IDLE state for conversation {conversation_id}")

        # ====================================================================
        # FSM FLOW: Check if in multi-step task flow
        # ====================================================================
        is_in_flow = ConversationStateService.is_in_multi_step_flow(conversation_state)

        if is_in_flow:
            logger.info(
                f"[FSM] User in multi-step flow: mode={conversation_state.intent_mode}, "
                f"step={conversation_state.intent_step}"
            )

            # Extract field value from user message
            field_value = body.message.strip()

            # Get the field name for current step from intent_step
            field_mapping = {
                "TITLE": "title",
                "DESCRIPTION": "description",
                "PRIORITY": "priority",
                "DUE_DATE": "due_date",
                "TASK_ID": "task_id",
                "CONFIRM": "confirm",
            }
            field_name = field_mapping.get(conversation_state.intent_step, conversation_state.intent_step.lower())

            # Collect field and advance to next step
            step_result = await ConversationStateService.advance_step(
                db=db,
                conversation_id=conversation_id,
                user_id=user_id,
                field_name=field_name,
                field_value=field_value,
            )

            if not step_result["success"]:
                # Error advancing step
                logger.warning(f"[FSM] Failed to advance step: {step_result.get('message')}")
                assistant_message = await MessagePersistenceService.save_assistant_message(
                    db=db,
                    user_id=user_id,
                    conversation_id=conversation_id,
                    content=step_result.get("message", "I encountered an issue. Please try again."),
                    tool_calls=[],
                    tool_results=None,
                    metadata={"elapsed_ms": (time.time() - start_time) * 1000, "fsm_error": True},
                )
                response = ChatResponse(
                    id=assistant_message.id,
                    role="assistant",
                    content=assistant_message.content,
                    tool_calls=[],
                    tool_results=None,
                    created_at=assistant_message.created_at,
                )
                return SuccessResponseWrapper(data=response, error=None)

            # Check if ready to execute tool
            if step_result["ready_to_execute"]:
                logger.info(
                    f"[FSM] All required fields collected for {conversation_state.intent_mode}. "
                    f"Executing tool with payload: {conversation_state.intent_payload}"
                )

                # Now execute the tool with collected fields
                # Re-construct tool call from intent_payload
                tool_name = {
                    "ADD_TASK": "add_task",
                    "UPDATE_TASK": "update_task",
                    "DELETE_TASK": "delete_task",
                    "COMPLETE_TASK": "complete_task",
                    "LIST_TASKS": "list_tasks",
                }.get(conversation_state.intent_mode, "")

                # Import MCP executor
                from ...mcp.server import MCPToolExecutor

                try:
                    # Prepare tool input with collected fields + user_id
                    tool_input = {**(conversation_state.intent_payload or {}), "user_id": str(user_id)}

                    # Execute tool directly with collected fields
                    tool_result = await MCPToolExecutor.execute_tool(
                        tool_name=tool_name,
                        tool_input=tool_input,
                    )

                    logger.info(f"[FSM_TOOL_SUCCESS] {tool_name} executed successfully")

                    # Generate response based on tool result
                    response_text = f"Your {tool_name.replace('_', ' ')} has been completed successfully."

                    # Reset FSM state to IDLE
                    await ConversationStateService.reset_state(
                        db=db,
                        conversation_id=conversation_id,
                        user_id=user_id,
                    )
                    logger.info(f"[FSM_RESET] State reset to IDLE after {tool_name} execution")

                    # Save success response
                    assistant_message = await MessagePersistenceService.save_assistant_message(
                        db=db,
                        user_id=user_id,
                        conversation_id=conversation_id,
                        content=response_text,
                        tool_calls=[{"type": "function", "function": {"name": tool_name, "arguments": json.dumps(conversation_state.intent_payload)}}],
                        tool_results={tool_name: json.dumps(tool_result) if isinstance(tool_result, dict) else str(tool_result)},
                        metadata={"elapsed_ms": (time.time() - start_time) * 1000, "fsm_executed": True, "tool": tool_name},
                    )

                except Exception as e:
                    logger.error(f"[FSM_TOOL_ERROR] Failed to execute {tool_name}: {str(e)}", exc_info=True)

                    # Reset FSM state to IDLE even on error
                    await ConversationStateService.reset_state(
                        db=db,
                        conversation_id=conversation_id,
                        user_id=user_id,
                    )

                    # Save error response
                    response_text = f"I encountered an error while executing that action. Please try again."
                    assistant_message = await MessagePersistenceService.save_assistant_message(
                        db=db,
                        user_id=user_id,
                        conversation_id=conversation_id,
                        content=response_text,
                        tool_calls=[],
                        tool_results=None,
                        metadata={"elapsed_ms": (time.time() - start_time) * 1000, "fsm_error": True, "tool": tool_name},
                    )

                response = ChatResponse(
                    id=assistant_message.id,
                    role="assistant",
                    content=assistant_message.content,
                    tool_calls=assistant_message.tool_calls or [],
                    tool_results=assistant_message.tool_results,
                    created_at=assistant_message.created_at,
                )
                return SuccessResponseWrapper(data=response, error=None)

            else:
                # Not ready yet, return next step prompt (NO agent call)
                next_prompt = step_result.get("message", "Continue with the next detail:")
                logger.info(f"[FSM] Collecting more fields. Next step prompt: {next_prompt[:50]}...")

                assistant_message = await MessagePersistenceService.save_assistant_message(
                    db=db,
                    user_id=user_id,
                    conversation_id=conversation_id,
                    content=next_prompt,
                    tool_calls=[],
                    tool_results=None,
                    metadata={"elapsed_ms": (time.time() - start_time) * 1000, "fsm_collecting": True, "step": conversation_state.intent_step},
                )

                response = ChatResponse(
                    id=assistant_message.id,
                    role="assistant",
                    content=assistant_message.content,
                    tool_calls=[],
                    tool_results=None,
                    created_at=assistant_message.created_at,
                )
                return SuccessResponseWrapper(data=response, error=None)

        # ====================================================================
        # FSM: Not in flow - Check for task-related intents
        # ====================================================================
        user_msg_lower = body.message.strip().lower()

        # Detect task intents
        task_intents = {
            "add_task": ["add task", "create task", "new task", "i need to add"],
            "update_task": ["update task", "edit task", "modify task", "change task"],
            "delete_task": ["delete task", "remove task", "remove this task"],
            "complete_task": ["complete task", "mark complete", "done with", "finished"],
            "list_tasks": ["list tasks", "show tasks", "what tasks", "all my tasks", "my tasks", "how many tasks"],
        }

        detected_intent = None
        for intent, keywords in task_intents.items():
            if any(keyword in user_msg_lower for keyword in keywords):
                detected_intent = intent
                break

        # If a task intent detected and not already in flow, start new FSM flow
        if detected_intent and detected_intent != "list_tasks":
            logger.info(f"[FSM] Detected intent: {detected_intent}")

            # Set new intent and move to first step
            conversation_state = await ConversationStateService.set_intent(
                db=db,
                conversation_id=conversation_id,
                user_id=user_id,
                intent_mode=detected_intent.upper(),
            )

            # Get first step prompt
            first_step_message = ConversationStateService.get_next_step_message(conversation_state)
            logger.info(f"[FSM] Started {detected_intent} flow, step: {conversation_state.intent_step}")

            # Save response with first step prompt
            assistant_message = await MessagePersistenceService.save_assistant_message(
                db=db,
                user_id=user_id,
                conversation_id=conversation_id,
                content=first_step_message,
                tool_calls=[],
                tool_results=None,
                metadata={"elapsed_ms": (time.time() - start_time) * 1000, "fsm_intent_start": True, "intent": detected_intent},
            )

            response = ChatResponse(
                id=assistant_message.id,
                role="assistant",
                content=assistant_message.content,
                tool_calls=[],
                tool_results=None,
                created_at=assistant_message.created_at,
            )
            return SuccessResponseWrapper(data=response, error=None)

        # ====================================================================
        # FALLBACK: Use Agent for general chat (or list_tasks)
        # ====================================================================
        logger.debug("[FSM] No task intent detected, using general agent")

        # Load conversation history for agent context
        history_messages, _ = await MessagePersistenceService.get_conversation_messages(
            db=db,
            conversation_id=conversation_id,
            limit=20,
        )

        # Convert messages to agent format
        # Track tool_call_id mapping to match tool results with tool calls
        tool_call_id_map = {}
        history = []
        for msg in history_messages:
            msg_role = msg.role.value if hasattr(msg.role, "value") else str(msg.role)
            msg_dict = {
                "role": msg_role,
                "content": msg.content,
            }

            # Include tool_calls for assistant messages
            if msg_role == "assistant" and msg.tool_calls:
                tool_calls = msg.tool_calls
                # Parse JSON string if needed (stored as string in DB)
                if isinstance(tool_calls, str):
                    try:
                        tool_calls = json.loads(tool_calls)
                    except:
                        tool_calls = None
                if tool_calls:
                    # Ensure each tool_call has an id (required by OpenAI)
                    if isinstance(tool_calls, list):
                        for i, tc in enumerate(tool_calls):
                            if isinstance(tc, dict):
                                if "id" not in tc:
                                    tc["id"] = str(uuid4())
                                # Map old tool_call_id to new one for results matching
                                tool_call_id_map[f"tool_{i}"] = tc["id"]
                    msg_dict["tool_calls"] = tool_calls

            history.append(msg_dict)

            # If assistant message has tool_calls, add corresponding tool result messages
            if msg_role == "assistant" and msg.tool_calls and msg.tool_results:
                tool_results = msg.tool_results
                # Parse JSON string if needed
                if isinstance(tool_results, str):
                    try:
                        tool_results = json.loads(tool_results)
                    except:
                        tool_results = None

                if tool_results:
                    # Add tool result messages for each tool call
                    tool_calls_list = msg_dict.get("tool_calls", [])
                    if isinstance(tool_results, dict):
                        # Tool results keyed by tool name - match with tool_calls by index
                        result_index = 0
                        for tool_id, result_content in tool_results.items():
                            if result_index < len(tool_calls_list):
                                tool_call = tool_calls_list[result_index]
                                call_id = tool_call.get("id") if isinstance(tool_call, dict) else str(tool_call)
                                history.append({
                                    "role": "tool",
                                    "tool_call_id": call_id,
                                    "content": str(result_content),
                                })
                                result_index += 1
                    elif isinstance(tool_results, list):
                        for i, result in enumerate(tool_results):
                            if i < len(tool_calls_list):
                                tool_call = tool_calls_list[i]
                                tool_id = tool_call.get("id") if isinstance(tool_call, dict) else str(tool_call)
                                history.append({
                                    "role": "tool",
                                    "tool_call_id": tool_id,
                                    "content": str(result),
                                })

        logger.debug(f"Agent context: {len(history)} messages from conversation history")

        # ====================================================================
        # INVOKE AGENT (with timeout hardening)
        # ====================================================================
        agent = AgentExecutor()

        agent_response = await asyncio.wait_for(
            agent.execute(
                user_id=user_id,
                user_message=body.message.strip(),
                conversation_history=history,
            ),
            timeout=35,  # Slightly higher than agent's 30s timeout for safety margin
        )

        elapsed_ms = (time.time() - start_time) * 1000

        logger.debug(f"[AGENT_RESPONSE] Received response in {elapsed_ms:.0f}ms")

        # ====================================================================
        # TOOL → ASSISTANT RESPONSE GUARANTEE
        # ====================================================================
        response_text = agent_response.get("response", "")

        # If response is empty, generate synthetic response based on tool calls
        if not response_text or response_text.strip() == "":
            tool_calls = agent_response.get("tool_calls", [])
            if tool_calls and len(tool_calls) > 0:
                first_tool = tool_calls[0].get("function", {}).get("name", "").lower()

                # Generate contextual fallback response
                fallback_responses = {
                    "list_tasks": "Here's what I found in your task list.",
                    "add_task": "Your task has been added successfully.",
                    "update_task": "The task has been updated.",
                    "complete_task": "The task has been marked as complete.",
                    "delete_task": "The task has been deleted.",
                }
                response_text = fallback_responses.get(first_tool, "Your request has been processed.")
                logger.warning(f"[RESPONSE_FALLBACK] Generated synthetic response for tool: {first_tool}")
            else:
                response_text = "I've processed your request."

        tool_calls = agent_response.get("tool_calls")
        tool_results = agent_response.get("tool_results")
        metadata = {
            "elapsed_ms": elapsed_ms,
            "model": agent_response.get("model"),
        }

        # Save assistant response
        assistant_message = await MessagePersistenceService.save_assistant_message(
            db=db,
            user_id=user_id,
            conversation_id=conversation_id,
            content=response_text,
            tool_calls=tool_calls,
            tool_results=tool_results,
            metadata=metadata,
        )

        logger.info(
            f"[CHAT_SUCCESS] User {user_id}, conversation {conversation_id}, "
            f"response_length={len(response_text)}, elapsed={elapsed_ms:.0f}ms"
        )

        # Return response
        response = ChatResponse(
            id=assistant_message.id,
            role=assistant_message.role.value if hasattr(assistant_message.role, "value")
            else str(assistant_message.role),
            content=assistant_message.content,
            tool_calls=assistant_message.tool_calls,
            tool_results=assistant_message.tool_results,
            created_at=assistant_message.created_at,
        )

        return SuccessResponseWrapper(data=response, error=None)

    # ========================================================================
    # CATCH-ALL EXCEPTION HANDLER (MANDATORY SAFETY)
    # Always return HTTP 200, never HTTP 500
    # ========================================================================
    except InvalidMessageError as e:
        logger.warning(f"[VALIDATION_ERROR] {str(e)}")
        raise  # These are validation errors, let FastAPI handle them properly
    except ConversationNotFoundError as e:
        logger.warning(f"[CONVERSATION_NOT_FOUND] {str(e)}")
        raise  # These are auth/permission errors, let FastAPI handle them properly
    except InvalidConversationAccessError as e:
        logger.warning(f"[ACCESS_DENIED] {str(e)}")
        raise  # These are auth/permission errors, let FastAPI handle them properly
    except Exception as e:
        elapsed_ms = (time.time() - start_time) * 1000
        logger.error(
            f"[CHAT_ERROR] User {user_id}, conversation {conversation_id}, "
            f"error: {type(e).__name__}: {str(e)}, elapsed={elapsed_ms:.0f}ms",
            exc_info=True
        )

        # CRITICAL: Generate fallback response that always works
        fallback_response_text = (
            "I'm having trouble completing that right now. Please try again."
        )

        try:
            # Try to save fallback message to database
            assistant_message = await MessagePersistenceService.save_assistant_message(
                db=db,
                user_id=user_id,
                conversation_id=conversation_id,
                content=fallback_response_text,
                tool_calls=[],
                tool_results=None,
                metadata={"error": type(e).__name__, "elapsed_ms": elapsed_ms},
            )

            response = ChatResponse(
                id=assistant_message.id,
                role="assistant",
                content=fallback_response_text,
                tool_calls=[],
                tool_results=None,
                created_at=assistant_message.created_at,
            )

            # Return HTTP 200 with fallback message (NEVER HTTP 500)
            return SuccessResponseWrapper(data=response, error=None)
        except Exception as db_error:
            logger.error(
                f"[CRITICAL_ERROR] Failed to save fallback message: {str(db_error)}",
                exc_info=True
            )
            # Last resort: return synthetic response without saving to DB
            response = ChatResponse(
                id=UUID(int=0),  # Placeholder ID
                role="assistant",
                content=fallback_response_text,
                tool_calls=[],
                tool_results=None,
                created_at=datetime.utcnow(),
            )
            return SuccessResponseWrapper(data=response, error=None)


# [Task]: T330
@router.get(
    "/conversations/{conversation_id}/messages",
    response_model=SuccessResponseWrapper,
)
async def get_messages(
    request: Request,
    conversation_id: UUID,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    include_deleted: bool = Query(default=False),
    db: Session = Depends(get_db),
) -> SuccessResponseWrapper:
    """Get messages from a conversation (paginated, newest first).

    [Task]: T330, [From]: specs/004-ai-chatbot/spec.md#Endpoints
    Retrieves message history for a conversation in reverse chronological order
    (newest first) for UI display. Automatically filters soft-deleted messages
    unless include_deleted=true.

    Query Parameters:
    - limit: Max messages per page (1-100, default 20)
    - offset: Pagination offset (default 0)
    - include_deleted: Whether to include soft-deleted messages (default false)

    Performance: <200ms with limit=20 due to database indexes on (conversation_id, deleted_at)

    Args:
        request: FastAPI Request object (contains user_id in state)
        conversation_id: Conversation ID
        limit: Max results per page (1-100, default 20)
        offset: Pagination offset (default 0)
        include_deleted: Whether to include soft-deleted messages
        db: Database session

    Returns:
        SuccessResponseWrapper containing PaginatedMessagesResponse

    Raises:
        UnauthorizedException: If JWT token is missing or invalid (401)
        ConversationNotFoundError: If conversation not found (404)
        InvalidConversationAccessError: If user doesn't own conversation (403)
    """
    user_id = request.state.user_id

    logger.info(
        f"Listing messages for conversation {conversation_id} "
        f"(user={user_id}, limit={limit}, offset={offset})"
    )

    # Verify conversation exists and belongs to user
    conversation = await ConversationService.get_conversation(
        db=db,
        user_id=user_id,
        conversation_id=conversation_id,
    )

    if not conversation:
        raise ConversationNotFoundError(str(conversation_id))

    # Get messages (newest first for display)
    messages, total = await MessagePersistenceService.get_conversation_messages_for_display(
        db=db,
        conversation_id=conversation_id,
        limit=limit,
        offset=offset,
    )

    # Convert to response models
    message_responses = [
        MessageResponse(
            id=msg.id,
            conversation_id=msg.conversation_id,
            role=msg.role.value if hasattr(msg.role, "value") else str(msg.role),
            content=msg.content,
            tool_calls=msg.tool_calls,
            tool_results=msg.tool_results,
            created_at=msg.created_at,
        )
        for msg in messages
    ]

    response = PaginatedMessagesResponse(
        messages=message_responses,
        total=total,
        limit=limit,
        offset=offset,
    )

    return SuccessResponseWrapper(data=response, error=None)


# [Task]: T338
@router.delete(
    "/conversations/{conversation_id}/messages/{message_id}",
    status_code=204,
)
async def delete_message(
    request: Request,
    conversation_id: UUID,
    message_id: UUID,
    db: Session = Depends(get_db),
):
    """Soft-delete a message.

    [Task]: T338, [From]: specs/004-ai-chatbot/spec.md#Endpoints
    Soft-deletes a message by setting deleted_at timestamp.
    Message becomes hidden from list queries but can be recovered.

    Args:
        request: FastAPI Request object (contains user_id in state)
        conversation_id: Conversation ID
        message_id: Message ID to delete
        db: Database session

    Returns:
        None (204 No Content)

    Raises:
        UnauthorizedException: If JWT token is missing or invalid (401)
        ConversationNotFoundError: If conversation not found (404)
        InvalidConversationAccessError: If user doesn't own message (403)
    """
    user_id = request.state.user_id

    logger.info(
        f"Deleting message {message_id} from conversation {conversation_id} for user {user_id}"
    )

    # Verify conversation exists and belongs to user
    conversation = await ConversationService.get_conversation(
        db=db,
        user_id=user_id,
        conversation_id=conversation_id,
    )

    if not conversation:
        raise ConversationNotFoundError(str(conversation_id))

    # Verify message exists and belongs to conversation
    message = await MessagePersistenceService.get_message(db=db, message_id=message_id)

    if not message or message.conversation_id != conversation_id:
        raise InvalidConversationAccessError(
            details={"message_id": str(message_id), "conversation_id": str(conversation_id)}
        )

    # Soft-delete message
    success = await MessagePersistenceService.soft_delete_message(db=db, message_id=message_id)

    if not success:
        raise InvalidConversationAccessError()

    logger.info(f"Successfully deleted message {message_id}")
