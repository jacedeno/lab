"""add login_pins table

Revision ID: a3b1c4d5e6f7
Revises: f8525c2d7463
Create Date: 2026-02-24 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a3b1c4d5e6f7'
down_revision = 'f8525c2d7463'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('login_pins',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=200), nullable=False),
    sa.Column('pin_hash', sa.String(length=256), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('expires_at', sa.DateTime(), nullable=False),
    sa.Column('attempts', sa.Integer(), nullable=False),
    sa.Column('used', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('login_pins', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_login_pins_email'), ['email'], unique=False)


def downgrade():
    with op.batch_alter_table('login_pins', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_login_pins_email'))

    op.drop_table('login_pins')
