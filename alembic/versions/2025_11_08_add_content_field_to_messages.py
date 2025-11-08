"""add_content_field_to_messages

Revision ID: add_content_field
Revises: 3c885b504dad
Create Date: 2025-11-08

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_content_field'
down_revision: Union[str, None] = '3c885b504dad'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add content field to messages table for storing actual message text."""
    # Add content column (nullable first to avoid errors on existing rows)
    op.add_column('messages', sa.Column('content', sa.Text(), nullable=True))

    # Update existing rows to have empty string as content
    op.execute("UPDATE messages SET content = '' WHERE content IS NULL")

    # Make content non-nullable
    op.alter_column('messages', 'content', nullable=False)

    # Add index for faster history queries
    op.create_index('idx_messages_user_created', 'messages', ['user_id', 'created_at'])


def downgrade() -> None:
    """Remove content field from messages table."""
    op.drop_index('idx_messages_user_created', table_name='messages')
    op.drop_column('messages', 'content')
