"""switch embeddings to ollama (vector 768)

Revision ID: b7e3d41f9a20
Revises: 9a4f2c8e6d10
Create Date: 2026-09-15 10:00:00.000000

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b7e3d41f9a20"
down_revision: str | Sequence[str] | None = "9a4f2c8e6d10"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_DIM = 768


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("DROP INDEX IF EXISTS ix_document_chunks_embedding")
    op.execute("TRUNCATE document_chunks")
    op.execute(f"ALTER TABLE document_chunks ALTER COLUMN embedding TYPE vector({_DIM})")
    op.execute(
        "CREATE INDEX ix_document_chunks_embedding "
        "ON document_chunks USING hnsw (embedding vector_cosine_ops)"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP INDEX IF EXISTS ix_document_chunks_embedding")
    op.execute("TRUNCATE document_chunks")
    op.execute("ALTER TABLE document_chunks ALTER COLUMN embedding TYPE vector(1536)")
    op.execute(
        "CREATE INDEX ix_document_chunks_embedding "
        "ON document_chunks USING hnsw (embedding vector_cosine_ops)"
    )
