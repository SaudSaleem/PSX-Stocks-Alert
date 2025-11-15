"""add_phone_numbers_table

Revision ID: 5529597216ca
Revises: cb7e0d4262a5
Create Date: 2025-11-15 11:19:03.592561

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5529597216ca'
down_revision: Union[str, None] = 'cb7e0d4262a5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'phone_numbers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('phone_number', sa.String(), nullable=False),
        sa.Column('label', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('date_added', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_phone_numbers_id'), 'phone_numbers', ['id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_phone_numbers_id'), table_name='phone_numbers')
    op.drop_table('phone_numbers')
