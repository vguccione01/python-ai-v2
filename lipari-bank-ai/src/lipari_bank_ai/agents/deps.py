from dataclasses import dataclass
from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from lipari_bank_ai.config import settings
from lipari_bank_ai.db.repos import AccountRepository, MovementRepository
from lipari_bank_ai.db.runs import RunRepository
from lipari_bank_ai.db.session import get_db
from lipari_bank_ai.llm.embedding_client import EmbeddingClient
from lipari_bank_ai.services.alerts import AlertService
from lipari_bank_ai.services.retrieval_service import RetrievalService


@dataclass(frozen=True)
class Deps:
    accounts: AccountRepository
    movements: MovementRepository
    alerts: AlertService
    runs: RunRepository
    retrieval: RetrievalService
    embedder: EmbeddingClient
    openai: AsyncOpenAI          # il client grezzo: `complete` del Giorno 4 non ha i tool
    model: str


@lru_cache
def _openai_client() -> AsyncOpenAI:
    # uno per processo, riusato: il pool di connessioni vive nel client (Giorno 4)
    return AsyncOpenAI(
        api_key="ollama",
        base_url=f"{settings.ollama_url}/v1",
        timeout=120.0
    )


@lru_cache
def _embedder() -> EmbeddingClient:
    # come sopra: una sola connessione HTTP per processo, non una per richiesta
    return EmbeddingClient()


def crea_deps(
    db: AsyncSession, *, embedder: EmbeddingClient | None = None, openai: AsyncOpenAI | None = None
) -> Deps:
    """I servizi su una sessione. La usano l'endpoint e, al Giorno 8, il server MCP."""
    embedder = embedder or _embedder()   # i test li passano; altrimenti, dalla factory
    openai = openai or _openai_client()
    return Deps(
        accounts=AccountRepository(db),
        movements=MovementRepository(db),
        alerts=AlertService(db),
        runs=RunRepository(db),
        retrieval=RetrievalService(db, embedder),
        embedder=embedder,
        openai=openai,
        model=settings.agent_model,
    )

def get_deps(db: Annotated[AsyncSession, Depends(get_db)]) -> Deps:
    return crea_deps(db)
