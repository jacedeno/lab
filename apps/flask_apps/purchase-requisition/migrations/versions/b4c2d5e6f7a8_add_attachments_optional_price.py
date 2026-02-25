"""add attachments table and make price optional

Revision ID: b4c2d5e6f7a8
Revises: a3b1c4d5e6f7
Create Date: 2026-02-24 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b4c2d5e6f7a8'
down_revision = 'a3b1c4d5e6f7'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('attachments',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('requisition_id', sa.Integer(), nullable=False),
    sa.Column('filename', sa.String(length=255), nullable=False),
    sa.Column('content_type', sa.String(length=100), nullable=False),
    sa.Column('data', sa.LargeBinary(), nullable=False),
    sa.Column('size', sa.Integer(), nullable=False),
    sa.Column('uploaded_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['requisition_id'], ['purchase_requisitions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

    with op.batch_alter_table('requisition_items', schema=None) as batch_op:
        batch_op.alter_column('price',
               existing_type=sa.Float(),
               nullable=True)


def downgrade():
    with op.batch_alter_table('requisition_items', schema=None) as batch_op:
        batch_op.alter_column('price',
               existing_type=sa.Float(),
               nullable=False)

    op.drop_table('attachments')
