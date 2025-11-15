"""add_transaction_type_to_investments

Revision ID: cb7e0d4262a5
Revises: 44c457e0f4b7
Create Date: 2025-11-15 11:05:13.747206

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cb7e0d4262a5'
down_revision: Union[str, None] = '44c457e0f4b7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('investments', sa.Column('transaction_type', sa.String(), nullable=False, server_default='add'))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('investments', 'transaction_type')
