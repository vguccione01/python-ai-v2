from opencode_ai import AsyncOpencode
from opencode_ai.types import TextPart, TextPartInputParam

from lipari_bank_ai.llm.types import LLMResponse, Message


class OpencodeProvider:
    PRICING = {
        "opencode-big-pickle": (0.0, 0.0),  # Big Pickle è gratuito
    }

    def __init__(self, api_key: str, model: str = "opencode-big-pickle") -> None:
        self.client = AsyncOpencode(
            base_url="http://localhost:4096"
        )
        self.model = model

    async def complete(self, messages: list[Message], max_tokens: int = 500) -> LLMResponse:
        # Opencode è stateful e ricorda le conversazioni tramite session ID.
        # Per semplicita al momento ne creiamo sempre una nuova
        session = await self.client.session.create()

        parts = [TextPartInputParam(text=m.content, type="text") for m in messages]

        response = await self.client.session.chat(
            id=session.id,
            model_id="opencode-big-pickle",
            provider_id="opencode/big-pickle",
            parts=parts,
        )

        session_messages = await self.client.session.messages(session.id)
        response_parts = next(
            (
                message.parts
                for message in reversed(session_messages)
                if message.info.id == response.id
            ),
            [],
        )
        text = next(
            (part.text for part in response_parts if isinstance(part, TextPart)),
            "",
        )

        input_tokens = int(response.tokens.input)
        output_tokens = int(response.tokens.output)

        return LLMResponse(
            content=text,
            tokens_used=input_tokens + output_tokens,
            cost_eur=0.0,
            model=self.model,
        )
