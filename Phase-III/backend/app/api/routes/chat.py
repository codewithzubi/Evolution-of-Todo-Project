"""Chat API routes for Phase-III conversational todo management.

Endpoints:
- POST /api/chat - Send message to AI chatbot
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from uuid import UUID
from groq import Groq

from app.schemas.chat import ChatRequest, ChatResponse, ChatContext
from app.services.chat_service import ChatService
from app.api.deps import get_session, get_current_user_id
from app.config import get_settings

router = APIRouter(prefix="/api", tags=["chat"])


def get_groq_client() -> Groq:
    """Get Groq client for dependency injection.

    Returns:
        Groq client configured with API key from settings

    Raises:
        HTTPException: 500 if GROQ_API_KEY not configured
    """
    settings = get_settings()

    if not settings.GROQ_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Groq API key not configured"
        )

    return Groq(api_key=settings.GROQ_API_KEY)


@router.post(
    "/chat",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Send message to AI chatbot",
    description="Send a natural language message to the AI chatbot for todo management. "
                "The chatbot can create, view, update, complete, and delete tasks based on user intent."
)
def chat_endpoint(
    request: ChatRequest,
    session: Session = Depends(get_session),
    user_id: UUID = Depends(get_current_user_id),
    groq_client: Groq = Depends(get_groq_client)
) -> ChatResponse:
    """Process a chat message through the AI agent.

    This endpoint:
    1. Validates JWT token and extracts user_id
    2. Gets or creates conversation
    3. Saves user message
    4. Fetches conversation history
    5. Calls Groq agent with MCP tools
    6. Saves assistant response
    7. Returns AI reply

    Args:
        request: ChatRequest with message and optional conversation_id
        session: Database session (injected)
        user_id: User ID from JWT token (injected)
        groq_client: Groq client (injected)

    Returns:
        ChatResponse with AI reply, conversation_id, and metadata

    Raises:
        400: Invalid message format or validation error
        401: Invalid or expired JWT token
        404: Conversation not found or doesn't belong to user
        500: AI service failure or internal error
    """
    try:
        # Validate message content
        if not request.message or len(request.message.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message cannot be empty"
            )

        if len(request.message) > 10000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message cannot exceed 10,000 characters"
            )

        # Initialize chat service
        chat_service = ChatService(db=session, groq_client=groq_client)

        # Process message through AI agent
        result = chat_service.process_message(
            user_id=user_id,
            message=request.message,
            conversation_id=request.conversation_id,
            mcp_tools=None
        )

        # Build response
        return ChatResponse(
            success=True,
            conversation_id=result["conversation_id"],
            response=result["response"],
            timestamp=result["timestamp"],
            tools_used=result["tools_used"],
            context=ChatContext(
                tasks_affected=result["context"]["tasks_affected"],
                operation=result["context"]["operation"]
            )
        )

    except ValueError as e:
        # Handle conversation not found or validation errors
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

    except HTTPException:
        # Re-raise HTTP exceptions (auth, validation)
        raise

    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred processing your request: {str(e)}"
        )
