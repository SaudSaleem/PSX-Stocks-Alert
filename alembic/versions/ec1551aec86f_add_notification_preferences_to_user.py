"""add_notification_preferences_to_user

Revision ID: ec1551aec86f
Revises: 0289c12f53de
Create Date: 2025-11-16 17:42:07.741933

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ec1551aec86f'
down_revision: Union[str, None] = '0289c12f53de'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add notification preference columns to users table
    op.add_column('users', sa.Column('email_notifications_enabled', sa.Boolean(), nullable=True))
    op.add_column('users', sa.Column('whatsapp_notifications_enabled', sa.Boolean(), nullable=True))
    
    # Set default values for existing users
    op.execute("UPDATE users SET email_notifications_enabled = TRUE WHERE email_notifications_enabled IS NULL")
    op.execute("UPDATE users SET whatsapp_notifications_enabled = FALSE WHERE whatsapp_notifications_enabled IS NULL")
    
    # Make columns non-nullable after setting defaults
    op.alter_column('users', 'email_notifications_enabled', nullable=False)
    op.alter_column('users', 'whatsapp_notifications_enabled', nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Remove notification preference columns
    op.drop_column('users', 'whatsapp_notifications_enabled')
    op.drop_column('users', 'email_notifications_enabled')
