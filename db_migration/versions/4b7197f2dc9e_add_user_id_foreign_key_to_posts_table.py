"""add user_id foreign-key to posts table

Revision ID: 4b7197f2dc9e
Revises: 8e20c6420c93
Create Date: 2023-03-11 22:28:33.782703

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4b7197f2dc9e'
down_revision = '8e20c6420c93'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'posts',
        sa.Column('user_id', sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    )
    pass


def downgrade() -> None:
    op.drop_constraint('posts_user_id_fkey', table_name="posts")
    op.drop_column('posts', 'user_id')
    pass
