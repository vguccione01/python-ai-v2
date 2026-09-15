import re
from sqlalchemy.ext.asyncio import AsyncSession

from lipari_bank_ai.db.models import DocumentChunk
from lipari_bank_ai.llm.embedding_client import EmbeddingClient


class IngestService:
    def __init__(self, session: AsyncSession, embedding_client: EmbeddingClient) -> None:
        self.session = session
        self.embedding_client = embedding_client

    async def ingest_document(
        self, document_id: str, content: str, metadata: dict | None = None,
    ) -> int:
        chunks = chunk_text(content, chunk_size=500, overlap=50)
        embeddings = await self.embedding_client.embed(chunks)

        for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings, strict=True)):
            db_chunk = DocumentChunk(
                document_id=document_id,
                chunk_index=idx,
                content=chunk,
                embedding=embedding,
                chunk_metadata=metadata or {},
            )
            self.session.add(db_chunk)

        await self.session.commit()
        return len(chunks)

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """Split text into chunks of ~chunk_size chars with overlap."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        # Try to break at sentence boundary
        if end < len(text):
            # Find nearest `.` `\n` `;`
            for sep in ['. ', '.\n', '? ', '! ']:
                idx = text.rfind(sep, start, end)
                if idx > start + chunk_size // 2:  # at least half-full
                    end = idx + len(sep)
                    break
        chunks.append(text[start:end].strip())
        start = end - overlap
    return [c for c in chunks if c]