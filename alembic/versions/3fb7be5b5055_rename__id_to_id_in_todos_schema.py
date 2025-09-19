"""rename _id to id in todos schema

Revision ID: 3fb7be5b5055
Revises: 1f61df3648a8
Create Date: 2025-09-19 16:12:23.255668

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3fb7be5b5055'
down_revision: Union[str, None] = '1f61df3648a8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
