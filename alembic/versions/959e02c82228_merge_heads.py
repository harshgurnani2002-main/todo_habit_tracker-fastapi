"""merge heads

Revision ID: 959e02c82228
Revises: 3fb7be5b5055, 954ed4a764a1
Create Date: 2025-09-19 18:55:28.347752

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '959e02c82228'
down_revision: Union[str, None] = ('3fb7be5b5055', '954ed4a764a1')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
