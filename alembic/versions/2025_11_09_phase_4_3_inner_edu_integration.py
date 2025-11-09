"""phase_4_3_inner_edu_integration

Revision ID: phase_4_3_integration
Revises: unified_integration
Create Date: 2025-11-09

Phase 4.3: Inner Edu Integration
- Add graph_structure to Quest model (primary storage for inner_edu compatibility)
- Add User.mode field (EDUCATIONAL vs THERAPEUTIC)
- Add Quest.psychologist_reviewed and related fields
- Create QuestBuilderSession, UserQuestLibrary, QuestProgress, QuestRating tables
- Extend Quest with inner_edu metadata (psychological_module, location, age_range, is_public, rating)
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'phase_4_3_integration'
down_revision: Union[str, None] = 'unified_integration'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add inner_edu integration features to existing pas_in_peace schema."""

    # 1. Extend User table with mode field
    op.execute("""
        CREATE TYPE usermode AS ENUM ('educational', 'therapeutic')
    """)
    op.add_column('users', sa.Column('mode', sa.Enum('educational', 'therapeutic', name='usermode'),
                                      nullable=True, server_default='educational'))
    op.add_column('users', sa.Column('parent_name', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('learning_profile', sa.JSON(), nullable=True))

    # 2. Extend Quest table with inner_edu fields
    # Add graph_structure as primary storage (JSONB)
    op.add_column('quests', sa.Column('graph_structure', sa.JSON(), nullable=True))

    # Add metadata fields
    op.add_column('quests', sa.Column('psychological_module', sa.String(100), nullable=True))
    op.add_column('quests', sa.Column('location', sa.String(100), nullable=True))
    op.add_column('quests', sa.Column('age_range', sa.String(20), nullable=True))

    # Public quest marketplace
    op.add_column('quests', sa.Column('is_public', sa.Boolean(), nullable=True, server_default='false'))
    op.add_column('quests', sa.Column('rating', sa.Float(), nullable=True, server_default='0.0'))
    op.add_column('quests', sa.Column('plays_count', sa.Integer(), nullable=True, server_default='0'))

    # Psychologist review system (Phase 4.3)
    op.add_column('quests', sa.Column('psychologist_reviewed', sa.Boolean(), nullable=True, server_default='false'))
    op.add_column('quests', sa.Column('psychologist_review_id', sa.Integer(), nullable=True))
    op.add_column('quests', sa.Column('reviewed_at', sa.DateTime(), nullable=True))

    # Reveal analytics (Phase 4.3)
    op.add_column('quests', sa.Column('reveal_count', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('quests', sa.Column('last_reveal_at', sa.DateTime(), nullable=True))

    # Create index on psychological_module for filtering
    op.create_index('ix_quests_psychological_module', 'quests', ['psychological_module'])
    op.create_index('ix_quests_is_public', 'quests', ['is_public'])

    # 3. Create psychologist_reviews table
    op.create_table(
        'psychologist_reviews',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('quest_id', sa.Integer(), nullable=False),
        sa.Column('reviewer_name', sa.String(255), nullable=True),
        sa.Column('reviewer_credentials', sa.String(500), nullable=True),

        # Four rating scales (1-5 each)
        sa.Column('emotional_safety_score', sa.Integer(), nullable=False),
        sa.Column('therapeutic_correctness_score', sa.Integer(), nullable=False),
        sa.Column('age_appropriateness_score', sa.Integer(), nullable=False),
        sa.Column('reveal_timing_score', sa.Integer(), nullable=False),

        # Overall assessment
        sa.Column('overall_score', sa.Float(), nullable=True),
        sa.Column('is_approved', sa.Boolean(), nullable=True, server_default='false'),

        # Detailed feedback
        sa.Column('strengths', sa.Text(), nullable=True),
        sa.Column('concerns', sa.Text(), nullable=True),
        sa.Column('recommendations', sa.Text(), nullable=True),
        sa.Column('modification_notes', sa.Text(), nullable=True),

        # Review metadata
        sa.Column('review_duration_minutes', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('reviewed_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),

        sa.ForeignKeyConstraint(['quest_id'], ['quests.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('quest_id')  # One review per quest
    )
    op.create_index('ix_psychologist_reviews_is_approved', 'psychologist_reviews', ['is_approved'])
    op.create_index('ix_psychologist_reviews_reviewed_at', 'psychologist_reviews', ['reviewed_at'])

    # Add FK from quests to psychologist_reviews
    op.create_foreign_key(
        'fk_quests_psychologist_review',
        'quests', 'psychologist_reviews',
        ['psychologist_review_id'], ['id'],
        ondelete='SET NULL'
    )

    # 4. Create quest_builder_sessions table (from inner_edu)
    op.create_table(
        'quest_builder_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),

        # AI conversation history
        sa.Column('conversation_history', sa.JSON(), nullable=True, server_default='[]'),

        # Dialog stage
        sa.Column('current_stage', sa.String(50), nullable=True, server_default='greeting'),

        # Current graph being built
        sa.Column('current_graph', sa.JSON(), nullable=True),

        # Quest context
        sa.Column('quest_context', sa.JSON(), nullable=True),

        # Timestamps
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),

        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_quest_builder_sessions_user_created', 'quest_builder_sessions',
                    ['user_id', 'created_at'])

    # 5. Create user_quest_library table (inner_edu marketplace)
    op.create_table(
        'user_quest_library',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('quest_id', sa.Integer(), nullable=False),
        sa.Column('added_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),

        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['quest_id'], ['quests.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_user_quest_library_user_quest', 'user_quest_library',
                    ['user_id', 'quest_id'], unique=True)

    # 6. Create quest_progress table (child completion tracking)
    op.create_table(
        'quest_progress',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('quest_id', sa.Integer(), nullable=False),

        # Progress tracking
        sa.Column('current_step', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('completed', sa.Boolean(), nullable=True, server_default='false'),

        # Session tracking
        sa.Column('session_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('total_time_minutes', sa.Float(), nullable=True, server_default='0.0'),

        # Timestamps
        sa.Column('started_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('last_played_at', sa.DateTime(), nullable=True),

        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['quest_id'], ['quests.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_quest_progress_user_quest', 'quest_progress',
                    ['user_id', 'quest_id'], unique=True)
    op.create_index('ix_quest_progress_last_played', 'quest_progress', ['last_played_at'])

    # 7. Create quest_ratings table (public marketplace ratings)
    op.create_table(
        'quest_ratings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('quest_id', sa.Integer(), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=False),  # 1-5 stars
        sa.Column('review_text', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),

        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['quest_id'], ['quests.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_quest_ratings_user_quest', 'quest_ratings',
                    ['user_id', 'quest_id'], unique=True)

    # 8. Create user_tracks table (NEW for Phase 4.3 - separate from recovery_tracks JSON)
    op.create_table(
        'user_tracks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),

        # Track type
        sa.Column('track_type', sa.Enum('self_work', 'child_connection', 'negotiation', 'community',
                                        name='recoverytrack'), nullable=False),

        # Current phase
        sa.Column('current_phase', sa.Enum('awareness', 'expression', 'action', 'mastery',
                                           name='trackphase'), nullable=True, server_default='awareness'),

        # Progress tracking
        sa.Column('completion_percentage', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('weeks_active', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('days_active', sa.Integer(), nullable=True, server_default='0'),

        # Activity tracking
        sa.Column('total_activities', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('completed_activities', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('last_activity_at', sa.DateTime(), nullable=True),

        # Timestamps
        sa.Column('started_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),

        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_user_tracks_user_track', 'user_tracks',
                    ['user_id', 'track_type'], unique=True)


def downgrade() -> None:
    """Remove inner_edu integration features."""

    # Drop new tables in reverse order
    op.drop_index('ix_user_tracks_user_track', table_name='user_tracks')
    op.drop_table('user_tracks')

    op.drop_index('ix_quest_ratings_user_quest', table_name='quest_ratings')
    op.drop_table('quest_ratings')

    op.drop_index('ix_quest_progress_last_played', table_name='quest_progress')
    op.drop_index('ix_quest_progress_user_quest', table_name='quest_progress')
    op.drop_table('quest_progress')

    op.drop_index('ix_user_quest_library_user_quest', table_name='user_quest_library')
    op.drop_table('user_quest_library')

    op.drop_index('ix_quest_builder_sessions_user_created', table_name='quest_builder_sessions')
    op.drop_table('quest_builder_sessions')

    op.drop_constraint('fk_quests_psychologist_review', 'quests', type_='foreignkey')
    op.drop_index('ix_psychologist_reviews_reviewed_at', table_name='psychologist_reviews')
    op.drop_index('ix_psychologist_reviews_is_approved', table_name='psychologist_reviews')
    op.drop_table('psychologist_reviews')

    # Remove Quest extensions
    op.drop_index('ix_quests_is_public', table_name='quests')
    op.drop_index('ix_quests_psychological_module', table_name='quests')
    op.drop_column('quests', 'last_reveal_at')
    op.drop_column('quests', 'reveal_count')
    op.drop_column('quests', 'reviewed_at')
    op.drop_column('quests', 'psychologist_review_id')
    op.drop_column('quests', 'psychologist_reviewed')
    op.drop_column('quests', 'plays_count')
    op.drop_column('quests', 'rating')
    op.drop_column('quests', 'is_public')
    op.drop_column('quests', 'age_range')
    op.drop_column('quests', 'location')
    op.drop_column('quests', 'psychological_module')
    op.drop_column('quests', 'graph_structure')

    # Remove User extensions
    op.drop_column('users', 'learning_profile')
    op.drop_column('users', 'parent_name')
    op.drop_column('users', 'mode')
    op.execute('DROP TYPE usermode')

    # Drop enums for user_tracks
    op.execute('DROP TYPE trackphase')
    op.execute('DROP TYPE recoverytrack')
