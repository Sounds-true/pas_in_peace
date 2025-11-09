"""add_unified_integration_models

Revision ID: unified_integration
Revises: add_content_field
Create Date: 2025-11-09

Phase 4.1: Unified Integration Database Layer
- Add 6 new models: Quest, CreativeProject, QuestAnalytics, ChildPrivacySettings, PsychologicalProfile, TrackMilestone
- Extend User model with recovery tracking fields
- Add new enums for multi-track system
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'unified_integration'
down_revision: Union[str, None] = 'add_content_field'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add unified integration models and extend User."""

    # 1. Extend users table with recovery tracking fields
    op.add_column('users', sa.Column('recovery_tracks', sa.JSON(), nullable=True, server_default='{}'))
    op.add_column('users', sa.Column('primary_track', sa.String(50), nullable=True, server_default='self_work'))
    op.add_column('users', sa.Column('recovery_week', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('users', sa.Column('recovery_day', sa.Integer(), nullable=True, server_default='0'))

    # 2. Create quests table
    op.create_table(
        'quests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('quest_id', sa.String(200), nullable=False),
        sa.Column('title', sa.String(300), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('child_name', sa.String(100), nullable=True),
        sa.Column('child_age', sa.Integer(), nullable=True),
        sa.Column('child_interests', sa.JSON(), nullable=True, server_default='[]'),
        sa.Column('quest_yaml', sa.Text(), nullable=False),
        sa.Column('total_nodes', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('difficulty_level', sa.String(20), nullable=True),
        sa.Column('family_photos', sa.JSON(), nullable=True, server_default='[]'),
        sa.Column('family_memories', sa.JSON(), nullable=True, server_default='[]'),
        sa.Column('family_jokes', sa.JSON(), nullable=True, server_default='[]'),
        sa.Column('familiar_locations', sa.JSON(), nullable=True, server_default='[]'),
        sa.Column('status', sa.String(50), nullable=True, server_default='draft'),
        sa.Column('moderation_status', sa.String(50), nullable=True, server_default='pending'),
        sa.Column('moderation_issues', sa.JSON(), nullable=True, server_default='[]'),
        sa.Column('moderation_notes', sa.Text(), nullable=True),
        sa.Column('reveal_enabled', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('reveal_threshold_percentage', sa.Float(), nullable=True, server_default='0.8'),
        sa.Column('reveal_message', sa.Text(), nullable=True),
        sa.Column('deployed_to_inner_edu', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('inner_edu_quest_id', sa.String(200), nullable=True),
        sa.Column('deployed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('last_edited', sa.DateTime(), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('quest_id')
    )
    op.create_index('ix_quests_quest_id', 'quests', ['quest_id'])
    op.create_index('ix_quests_inner_edu_quest_id', 'quests', ['inner_edu_quest_id'])

    # 3. Create creative_projects table
    op.create_table(
        'creative_projects',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('project_type', sa.String(50), nullable=False),
        sa.Column('quest_id', sa.Integer(), nullable=True),
        sa.Column('letter_id', sa.Integer(), nullable=True),
        sa.Column('goal_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(20), nullable=True, server_default='active'),
        sa.Column('progress_percentage', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('affects_tracks', sa.JSON(), nullable=True, server_default='[]'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('last_activity', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['quest_id'], ['quests.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['letter_id'], ['letters.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['goal_id'], ['goals.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('quest_id'),
        sa.UniqueConstraint('letter_id'),
        sa.UniqueConstraint('goal_id')
    )
    op.create_index('ix_creative_projects_user_created', 'creative_projects', ['user_id', 'created_at'])

    # 4. Create quest_analytics table
    op.create_table(
        'quest_analytics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('quest_id', sa.Integer(), nullable=False),
        sa.Column('nodes_completed', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('total_nodes', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('completion_percentage', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('educational_progress', sa.JSON(), nullable=True, server_default='{}'),
        sa.Column('achievements_unlocked', sa.JSON(), nullable=True, server_default='[]'),
        sa.Column('difficulty_progression', sa.JSON(), nullable=True, server_default='{}'),
        sa.Column('play_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('last_played', sa.DateTime(), nullable=True),
        sa.Column('total_time_spent_minutes', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('average_session_minutes', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('clues_discovered', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('total_clues', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('reveal_phase', sa.String(50), nullable=True),
        sa.Column('reveal_completed', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('reveal_completed_at', sa.DateTime(), nullable=True),
        sa.Column('child_consented_to_sharing', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('consent_updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('last_updated', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['quest_id'], ['quests.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('quest_id')
    )
    op.create_index('ix_quest_analytics_last_played', 'quest_analytics', ['last_played'])

    # 5. Create child_privacy_settings table
    op.create_table(
        'child_privacy_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('quest_id', sa.Integer(), nullable=False),
        sa.Column('share_completion_progress', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('share_educational_progress', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('share_achievements', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('share_play_frequency', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('notify_both_parents', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('notification_frequency', sa.String(20), nullable=True, server_default='immediate'),
        sa.Column('consent_given_by_child', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('consent_timestamp', sa.DateTime(), nullable=True),
        sa.Column('consent_revoked_at', sa.DateTime(), nullable=True),
        sa.Column('consent_history', sa.JSON(), nullable=True, server_default='[]'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('last_updated', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['quest_id'], ['quests.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('quest_id')
    )

    # 6. Create psychological_profiles table
    op.create_table(
        'psychological_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('emotional_trends', sa.JSON(), nullable=True, server_default='{}'),
        sa.Column('emotional_baseline', sa.Float(), nullable=True, server_default='0.5'),
        sa.Column('emotional_volatility', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('crisis_history', sa.JSON(), nullable=True, server_default='[]'),
        sa.Column('last_crisis_date', sa.DateTime(), nullable=True),
        sa.Column('crisis_frequency', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('coping_strategies', sa.JSON(), nullable=True, server_default='{}'),
        sa.Column('most_effective_technique', sa.String(50), nullable=True),
        sa.Column('triggers', sa.JSON(), nullable=True, server_default='[]'),
        sa.Column('distress_patterns', sa.JSON(), nullable=True, server_default='{}'),
        sa.Column('communication_style', sa.String(50), nullable=True),
        sa.Column('preferred_tone', sa.String(50), nullable=True),
        sa.Column('toxic_patterns', sa.JSON(), nullable=True, server_default='[]'),
        sa.Column('toxicity_trend', sa.String(20), nullable=True),
        sa.Column('last_toxicity_incident', sa.DateTime(), nullable=True),
        sa.Column('growth_areas', sa.JSON(), nullable=True, server_default='[]'),
        sa.Column('progress_notes', sa.Text(), nullable=True),
        sa.Column('recommended_techniques', sa.JSON(), nullable=True, server_default='[]'),
        sa.Column('recommended_resources', sa.JSON(), nullable=True, server_default='[]'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('last_updated', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )

    # 7. Create track_milestones table
    op.create_table(
        'track_milestones',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('track', sa.String(50), nullable=False),
        sa.Column('milestone_type', sa.String(100), nullable=False),
        sa.Column('milestone_name', sa.String(200), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('achievement_context', sa.JSON(), nullable=True, server_default='{}'),
        sa.Column('related_project_id', sa.Integer(), nullable=True),
        sa.Column('related_project_type', sa.String(20), nullable=True),
        sa.Column('achieved_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_track_milestones_track', 'track_milestones', ['track'])
    op.create_index('ix_track_milestones_achieved_at', 'track_milestones', ['achieved_at'])
    op.create_index('ix_track_milestones_user_track', 'track_milestones', ['user_id', 'track'])


def downgrade() -> None:
    """Remove unified integration models and revert User extensions."""

    # Drop tables in reverse order (respecting foreign keys)
    op.drop_index('ix_track_milestones_user_track', table_name='track_milestones')
    op.drop_index('ix_track_milestones_achieved_at', table_name='track_milestones')
    op.drop_index('ix_track_milestones_track', table_name='track_milestones')
    op.drop_table('track_milestones')

    op.drop_table('psychological_profiles')
    op.drop_table('child_privacy_settings')

    op.drop_index('ix_quest_analytics_last_played', table_name='quest_analytics')
    op.drop_table('quest_analytics')

    op.drop_index('ix_creative_projects_user_created', table_name='creative_projects')
    op.drop_table('creative_projects')

    op.drop_index('ix_quests_inner_edu_quest_id', table_name='quests')
    op.drop_index('ix_quests_quest_id', table_name='quests')
    op.drop_table('quests')

    # Remove User extensions
    op.drop_column('users', 'recovery_day')
    op.drop_column('users', 'recovery_week')
    op.drop_column('users', 'primary_track')
    op.drop_column('users', 'recovery_tracks')
