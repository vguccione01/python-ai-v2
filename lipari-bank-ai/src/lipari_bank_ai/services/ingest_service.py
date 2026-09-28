from logging import getLogger
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from lipari_bank_ai.db.models import DocumentChunk
from lipari_bank_ai.lib.chunking import chunk_text
from lipari_bank_ai.llm.embedding_client import EmbeddingClient

logger = getLogger(__name__)


class IngestService:
    def __init__(self, session: AsyncSession, embedding_client: EmbeddingClient) -> None:
        self.session = session
        self.embedding_client = embedding_client

    async def document_exists(self, document_id: str) -> bool:
        stmt = select(func.count()).select_from(DocumentChunk).where(
            DocumentChunk.document_id == document_id
        )
        return (await self.session.execute(stmt)).scalar_one() > 0

    async def ingest_document(
        self,
        document_id: str,
        content: str,
        visibility: str,
        metadata: dict[str, Any] | None = None,
    ) -> int:
        # Idempotente: se il documento è già in DB non lo si duplica.
        # Per re-ingestire un documento aggiornato l'utente deve prima cancellarlo a mano.
        if await self.document_exists(document_id):
            logger.info("ingest_skipped_documento_presente", extra={"document_id": document_id})
            return 0

        # Ho tutti documenti markdown con paragrafi separati da ## quindi non ho bisogno di overlap
        chunks = chunk_text(content, chunk_size=500, overlap=0)
        if not chunks:
            return 0

        embeddings = await self.embedding_client.embed(chunks)

        for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings, strict=True)):
            db_chunk = DocumentChunk(
                document_id=document_id,
                chunk_index=idx,
                content=chunk,
                embedding=embedding,
                chunk_metadata=metadata or {},
                visibility=visibility
            )
            self.session.add(db_chunk)

        await self.session.commit()
        return len(chunks)
