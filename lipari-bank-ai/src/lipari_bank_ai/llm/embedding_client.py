from openai import AsyncOpenAI

from lipari_bank_ai.config import settings


class EmbeddingClient:
    def __init__(self) -> None:
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.embedding_model

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Batch embed multiple texts."""
        response = await self.client.embeddings.create(
            model=self.model,
            input=texts,
        )
        return [item.embedding for item in response.data]

    async def embed_one(self, text: str) -> list[float]:
        result = await self.embed([text])
        return result[0]