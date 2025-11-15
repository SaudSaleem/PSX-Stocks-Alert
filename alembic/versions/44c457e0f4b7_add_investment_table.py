"""add_investment_table

Revision ID: 44c457e0f4b7
Revises: 23654a9f3b45
Create Date: 2025-11-15 10:53:03.700022

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '44c457e0f4b7'
down_revision: Union[str, None] = '23654a9f3b45'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'investments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('date_added', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_investments_id'), 'investments', ['id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_investments_id'), table_name='investments')
    op.drop_table('investments')
