"""create users table

Revision ID: 8e20c6420c93
Revises: a71220084e73
Create Date: 2023-03-11 22:12:48.950007

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8e20c6420c93'
down_revision = 'a71220084e73'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, nullable=False, primary_key=True),
        sa.Column('uuid', sa.String, nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('username', sa.String, nullable=False),
        sa.Column('email', sa.String, unique=True, nullable=False),
        sa.Column('firstname', sa.String, nullable=False),
        sa.Column('lastname', sa.String, nullable=False),
        sa.Column('password', sa.String, nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()'))
    )
    pass


def downgrade() -> None:
    op.drop_table('users')
    pass
