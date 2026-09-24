"""app_users + chunk visibility

Revision ID: c59f835656fb
Revises: b7e3d41f9a20
Create Date: 2026-09-23 15:11:56.170068

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c59f835656fb"
down_revision: str | Sequence[str] | None = "b7e3d41f9a20"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "app_users",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("username", sa.String(64), nullable=False),
        sa.Column("full_name", sa.String(128), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", sa.String(32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_app_users_username"), "app_users", ["username"], unique=True)

    op.add_column(
        "document_chunks",
        sa.Column("visibility", sa.String(32), nullable=False, server_default="public"),
    )
    op.create_index(op.f("ix_document_chunks_visibility"), "document_chunks", ["visibility"], unique=False)
    op.alter_column("document_chunks", "visibility", server_default=None)


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "document_chunks",
        "visibility",
        existing_type=sa.String(length=32),
        server_default="public",
    )
    op.drop_index(op.f("ix_document_chunks_visibility"), table_name="document_chunks")
    op.drop_column("document_chunks", "visibility")

    op.drop_index(op.f("ix_app_users_username"), table_name="app_users")
    op.drop_table("app_users")
