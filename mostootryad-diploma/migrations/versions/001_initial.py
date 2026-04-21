"""Initial migration with all models

Revision ID: 001_initial
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum types
    user_role_enum = sa.Enum('ADMIN', 'ENGINEER', 'WORKER', 'VIEWER', name='user_roles')
    user_role_enum.create(op.get_bind())
    
    act_status_enum = sa.Enum('DRAFT', 'PENDING_APPROVAL', 'APPROVED', 'REJECTED', 'ARCHIVED', name='act_statuses')
    act_status_enum.create(op.get_bind())
    
    approval_status_enum = sa.Enum('PENDING', 'APPROVED', 'REJECTED', name='approval_statuses')
    approval_status_enum.create(op.get_bind())
    
    audit_action_enum = sa.Enum('CREATE', 'UPDATE', 'DELETE', 'LOGIN', 'LOGOUT', name='audit_actions')
    audit_action_enum.create(op.get_bind())

    # Users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('role', user_role_enum, nullable=False, server_default='WORKER'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )

    # Construction objects table
    op.create_table('construction_objects',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='active'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )

    # Work types table
    op.create_table('work_types',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=True),
        sa.Column('unit', sa.String(length=50), nullable=False),
        sa.Column('default_price', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )

    # Acts table
    op.create_table('acts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('number', sa.String(length=50), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('construction_object_id', sa.Integer(), nullable=False),
        sa.Column('work_type_id', sa.Integer(), nullable=False),
        sa.Column('volume', sa.Numeric(precision=10, scale=3), nullable=False),
        sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('total', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('status', act_status_enum, nullable=False, server_default='DRAFT'),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['construction_object_id'], ['construction_objects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['work_type_id'], ['work_types.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('number')
    )
    op.create_index(op.f('ix_acts_construction_object_id'), 'acts', ['construction_object_id'], unique=False)
    op.create_index(op.f('ix_acts_created_by'), 'acts', ['created_by'], unique=False)
    op.create_index(op.f('ix_acts_work_type_id'), 'acts', ['work_type_id'], unique=False)

    # Approvals table
    op.create_table('approvals',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('act_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('status', approval_status_enum, nullable=False, server_default='PENDING'),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['act_id'], ['acts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_approvals_act_id'), 'approvals', ['act_id'], unique=False)
    op.create_index(op.f('ix_approvals_user_id'), 'approvals', ['user_id'], unique=False)

    # Attachments table
    op.create_table('attachments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('original_filename', sa.String(length=255), nullable=True),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('file_size', sa.BigInteger(), nullable=True),
        sa.Column('mime_type', sa.String(length=100), nullable=True),
        sa.Column('act_id', sa.Integer(), nullable=True),
        sa.Column('uploaded_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['act_id'], ['acts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['uploaded_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_attachments_act_id'), 'attachments', ['act_id'], unique=False)
    op.create_index(op.f('ix_attachments_uploaded_by'), 'attachments', ['uploaded_by'], unique=False)

    # Audit log table
    op.create_table('audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('action', audit_action_enum, nullable=False),
        sa.Column('entity_type', sa.String(length=50), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=True),
        sa.Column('old_values', sa.JSON(), nullable=True),
        sa.Column('new_values', sa.JSON(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_audit_logs_user_id'), 'audit_logs', ['user_id'], unique=False)
    op.create_index(op.f('ix_audit_logs_entity_type'), 'audit_logs', ['entity_type'], unique=False)
    op.create_index(op.f('ix_audit_logs_entity_id'), 'audit_logs', ['entity_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_audit_logs_entity_id'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_entity_type'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_user_id'), table_name='audit_logs')
    op.drop_table('audit_logs')
    
    op.drop_index(op.f('ix_attachments_uploaded_by'), table_name='attachments')
    op.drop_index(op.f('ix_attachments_act_id'), table_name='attachments')
    op.drop_table('attachments')
    
    op.drop_index(op.f('ix_approvals_user_id'), table_name='approvals')
    op.drop_index(op.f('ix_approvals_act_id'), table_name='approvals')
    op.drop_table('approvals')
    
    op.drop_index(op.f('ix_acts_work_type_id'), table_name='acts')
    op.drop_index(op.f('ix_acts_created_by'), table_name='acts')
    op.drop_index(op.f('ix_acts_construction_object_id'), table_name='acts')
    op.drop_table('acts')
    
    op.drop_table('work_types')
    op.drop_table('construction_objects')
    op.drop_table('users')
    
    # Drop enum types
    sa.Enum(name='audit_actions').drop(op.get_bind())
    sa.Enum(name='approval_statuses').drop(op.get_bind())
    sa.Enum(name='act_statuses').drop(op.get_bind())
    sa.Enum(name='user_roles').drop(op.get_bind())
