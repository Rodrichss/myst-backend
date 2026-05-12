"""merge heads

Revision ID: 79c53c58ecc0
Revises: 014ccfc660cc, de31272eeaf2
Create Date: 2026-05-12 15:28:15.285158

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '79c53c58ecc0'
down_revision: Union[str, Sequence[str], None] = ('014ccfc660cc', 'de31272eeaf2')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
