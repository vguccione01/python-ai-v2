from datetime import UTC, datetime

from fastapi import APIRouter

from lipari_bank_ai.types.chat import ChatRequest, ChatResponse
from lipari_bank_ai.types.error import ErrorResponse

router = APIRouter(prefix="/api/ai", tags=["Chat"])


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Send message to AI assistant",
    description="Multi-turn conversation. In G4 collegheremo LLM reale.",
    responses={
        200: {
            "description": "OK",
            "content": {
                "application/json": {
                    "example": ChatResponse(
                        session_id="string",
                        reply="string",
                        tokens_used=10,
                        cost_eur=0.0001,
                        model_used="dummy",
                        created_at="2026-09-04T12:44:59.102021Z",
                    )
                }
            },
        },
        422: {
            "description": "Unprocessable Entity",
            "content": {
                "application/json": {
                    "example": ErrorResponse(
                        timestamp="2026-09-04T12:50:56.542130+00:00",
                        status=422,
                        error="VALIDATION_ERROR",
                        message="Input non valido",
                        path="/api/ai/chat",
                        details=["session_id=Input should be a valid string"],
                    )
                }
            },
        },
        429: {"description": "Rate limit"},
    },
)
async def chat(req: ChatRequest) -> ChatResponse:
    return ChatResponse(
        session_id=req.session_id,
        reply=f"Echo: {req.message}",
        tokens_used=10,
        cost_eur=0.0001,
        model_used="dummy",
        created_at=datetime.now(UTC),
    )
