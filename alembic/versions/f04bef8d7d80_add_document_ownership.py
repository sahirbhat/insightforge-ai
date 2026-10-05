"""add document ownership

Revision ID: f04bef8d7d80
Revises: 
Create Date: 2026-09-17 05:14:15.019732

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f04bef8d7d80'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        'document_chunks',
        sa.Column('document_id', sa.Integer(), nullable=False)
    )

    op.create_index(
        op.f('ix_document_chunks_document_id'),
        'document_chunks',
        ['document_id'],
        unique=False
    )

    op.create_foreign_key(
        'fk_document_chunks_document_id',
        'document_chunks',
        'documents',
        ['document_id'],
        ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_constraint(
        'fk_document_chunks_document_id',
        'document_chunks',
        type_='foreignkey'
    )

    op.drop_index(
        op.f('ix_document_chunks_document_id'),
        table_name='document_chunks'
    )

    op.drop_column(
        'document_chunks',
        'document_id'
    )