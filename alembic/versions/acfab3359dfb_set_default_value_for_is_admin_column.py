"""set default value for is_admin column

Revision ID: acfab3359dfb
Revises: cfc72d1b0cfb
Create Date: 2025-09-15 23:30:21.146013

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'acfab3359dfb'
down_revision: Union[str, None] = 'cfc72d1b0cfb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Set default value for existing rows and make column non-nullable
    op.execute("UPDATE users SET is_admin = false WHERE is_admin IS NULL")
    op.alter_column('users', 'is_admin', server_default=sa.text('false'))


def downgrade() -> None:
    # Remove default value
    op.alter_column('users', 'is_admin', server_default=None)
