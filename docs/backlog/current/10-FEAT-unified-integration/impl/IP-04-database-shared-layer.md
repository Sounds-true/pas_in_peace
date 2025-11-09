# Implementation Plan: Shared Database Layer

## Смысл и цель задачи

Создать единую database schema которая используется ОБОИМИ проектами (pas_in_peace и inner_edu). Database должна хранить User profiles, Recovery tracking, Creative projects (quests, letters, goals), Child progress (aggregated), и PsychologicalProfile для comprehensive analytics. Обеспечить data consistency, privacy controls, и efficient querying для обоих приложений.

## Архитектура решения

### Database Schema Organization

**Shared Tables** (используются обоими проектами)
- `users` - user profiles с recovery tracking
- `quests` - quest metadata и YAML
- `quest_analytics` - aggregated child progress
- `child_privacy_settings` - что ребенок разрешает шарить
- `creative_projects` - meta-table для всех проектов
- `psychological_profiles` - unified профиль для analytics

**PAS Bot Tables** (только pas_in_peace)
- `messages` - chat history
- `sessions` - therapy sessions
- `letters` - письма родителя
- `goals` - SMART goals
- `metrics_snapshots` - metrics для analytics

**Inner Edu Tables** (только inner_edu)
- `quest_nodes` - детали узлов квеста
- `child_progress` - детальный прогресс (с consent)
- `achievements` - unlocked achievements

### File Structure

```
pas_in_peace/
└── src/storage/
    ├── models.py                    # Extend существующий
    │                               # Add: Quest, CreativeProject,
    │                               # PsychologicalProfile, QuestAnalytics
    ├── database.py                  # Extend существующий
    │                               # Add methods для quest management
    └── migrations/
        └── 2025_11_XX_add_quest_models.py  # Новая миграция

inner_edu/ (допущение - если есть backend)
└── backend/database/
    ├── models.py                    # Import shared models
    └── connection.py                # Connection к shared PostgreSQL
```

## Полный flow работы функционала

### Scenario 1: Quest Creation Flow

1. Parent создает квест через PAS Bot
2. QuestBuilderAssistant собирает данные
3. GPT-4 генерирует YAML
4. Quest сохраняется в `quests` table:
   - quest_id (UUID)
   - creator_id (FK to users)
   - child_name, child_age
   - quest_yaml (Text)
   - status = 'draft'
   - moderation_status = 'pending'
5. CreativeProject record создается:
   - project_type = 'quest'
   - quest_id link
   - status = 'in_progress'
6. RecoveryTrack progress обновляется в `users` table
7. Quest экспортируется в inner_edu

### Scenario 2: Child Plays Quest

1. Child открывает quest в inner_edu app
2. Inner_edu backend читает `quests` table (quest_yaml)
3. Child проходит nodes
4. Progress сохраняется в `quest_analytics` (aggregated):
   - nodes_completed++
   - completion_percentage updated
   - last_played = now()
5. Achievement unlocked -> `child_progress` (если consent)
6. Privacy check: `child_privacy_settings`
7. If sharing enabled -> notifications sent

### Scenario 3: Parent Views Analytics

1. Parent opens web dashboard
2. Frontend query `/api/analytics/child-progress/{quest_id}`
3. Backend reads `quest_analytics`:
   - Только aggregated data
   - NO personal child messages
4. Reads `child_privacy_settings`:
   - Если sharing disabled -> "Child hasn't consented"
5. Return safe analytics to parent

## API и интерфейсы

### Database Models (SQLAlchemy)

**Quest Model**
- Fields: id, quest_id (UUID), creator_id (FK), child_name, child_age, quest_yaml, status, moderation_status, moderation_issues (JSON), created_at, deployed_at
- Relationships: creator (User), analytics (QuestAnalytics), privacy_settings (ChildPrivacySettings), creative_project (CreativeProject)

**CreativeProject Model**
- Fields: id, user_id (FK), project_type (enum), quest_id, letter_id, status, progress (0-100), created_at, completed_at
- Relationships: user (User), quest (Quest), letter (Letter)

**QuestAnalytics Model**
- Fields: id, quest_id (FK), nodes_completed, total_nodes, completion_percentage, educational_progress (JSON), last_played, play_count, child_consented_to_sharing
- Privacy: NO child messages, NO answers, ONLY aggregated metrics

**ChildPrivacySettings Model**
- Fields: id, quest_id (FK unique), share_completion_progress, share_educational_progress, share_play_frequency, updated_at
- Default: все False (privacy-first)

**PsychologicalProfile Model**
- Fields: id, user_id (FK unique), emotional_trends (JSON), crisis_history (JSON), primary_coping_strategies (JSON), triggers (JSON), communication_style, toxic_patterns (JSON), growth_areas (JSON), quests_created, child_engagement, recommended_techniques (JSON), updated_at
- Purpose: Unified analytics из всех источников

**User Model Extension**
- Add fields: recovery_tracks (JSON), primary_track (String), recovery_week (Int), recovery_day (Int)
- Relationships: quests (Quest), creative_projects (CreativeProject), psychological_profile (PsychologicalProfile)

### DatabaseManager Methods

**Quest Management**
- `create_quest(creator_id, quest_data)` - create new quest
- `get_quest(quest_id)` - retrieve quest by ID
- `update_quest(quest_id, changes)` - update quest fields
- `get_user_quests(user_id)` - all quests by user
- `set_quest_status(quest_id, status)` - update status
- `save_quest_yaml(quest_id, yaml_content)` - save YAML

**Analytics**
- `get_quest_analytics(quest_id)` - aggregated progress
- `update_quest_progress(quest_id, nodes_completed)` - update from inner_edu
- `record_achievement(quest_id, achievement_data)` - child achievement

**Privacy**
- `get_privacy_settings(quest_id)` - child privacy prefs
- `update_privacy_settings(quest_id, settings)` - child updates consent
- `can_share_with_parent(quest_id, data_type)` - check permission

**Creative Projects**
- `create_creative_project(user_id, project_type, linked_id)` - generic project
- `get_all_projects(user_id, filters)` - all projects with filtering
- `update_project_progress(project_id, progress)` - update %

**Psychological Profile**
- `get_or_create_profile(user_id)` - get profile
- `update_profile_emotions(user_id, emotional_data)` - update emotions
- `add_coping_strategy(user_id, strategy)` - record what works
- `get_recommendations(user_id)` - AI recommendations based on profile

## Взаимодействие компонентов

```
PAS Bot Backend
  |
  +---> DatabaseManager
        |
        +---> SQLAlchemy ORM
              |
              v
        PostgreSQL (Shared)
              ^
              |
        SQLAlchemy ORM
        |
  +---> Database Access Layer
  |
Inner Edu Backend

Both access same tables:
  - users
  - quests
  - quest_analytics
  - child_privacy_settings
  - creative_projects

Privacy enforcement:
  - quest_analytics: ONLY aggregated
  - Check child_privacy_settings before returning data
  - NO raw child messages ever stored
```

## Порядок реализации

### Step 1: Schema Design (день 1)

1. Define all new models в models.py
2. Define relationships между моделями
3. Add indexes для performance
4. Add constraints для data integrity

### Step 2: Models Implementation (дни 2-3)

1. Extend User model с recovery tracking fields
2. Create Quest model
3. Create QuestAnalytics model
4. Create ChildPrivacySettings model
5. Create CreativeProject model
6. Create PsychologicalProfile model

### Step 3: Database Migration (день 4)

1. Создать Alembic migration
2. Test migration на dev database
3. Add seed data для testing
4. Document migration steps

### Step 4: DatabaseManager Methods (дни 5-7)

1. Implement quest management methods
2. Implement analytics methods с privacy checks
3. Implement creative projects methods
4. Implement psychological profile methods
5. Unit tests для каждого метода

### Step 5: Privacy Layer (дни 8-9)

1. Implement privacy checking logic
2. Default privacy settings (все False)
3. Privacy enforcement в query methods
4. Audit logging для privacy-sensitive queries

### Step 6: Integration Testing (дни 10-11)

1. Test full quest creation flow
2. Test analytics with/without consent
3. Test concurrent access (PAS + Inner Edu)
4. Test privacy enforcement
5. Performance testing (indexes working?)

### Step 7: Documentation (день 12)

1. ER diagram
2. Table descriptions
3. API documentation
4. Migration guide
5. Privacy policy documentation

## Критичные граничные случаи

**Concurrent updates conflict**
- Use optimistic locking (version field)
- Transaction isolation level SERIALIZABLE
- Retry logic на conflict

**Child revokes consent**
- Immediately hide analytics from parent
- Keep data (не удалять) но не показывать
- Log consent changes

**Quest deleted by parent**
- Soft delete (status = 'deleted')
- Child app продолжает работать
- Analytics preserved для research

**Database migration failure**
- Rollback mechanism
- Backup before migration
- Test migrations на staging first

## Объем работ

### Входит в реализацию

- 6 новых database models
- Extension существующего User model
- Alembic migration
- DatabaseManager methods (20+ methods)
- Privacy enforcement layer
- Indexes для performance
- Foreign key constraints
- Unit tests для CRUD operations
- Documentation

### Не входит в MVP

- Database replication
- Sharding для horizontal scaling
- Advanced caching layer (Redis)
- Full-text search (Elasticsearch)
- Data archival strategy
- GDPR compliance automation
- Backup automation

## Допущения

- PostgreSQL 15+ используется обоими проектами
- SQLAlchemy ORM используется в обоих проектах
- Alembic для migrations в pas_in_peace
- Inner_edu может использовать те же models (или re-define с совместимой схемой)
- Database connection pooling настроен
- SSL connection между app и database

## Открытые вопросы

1. Один PostgreSQL instance или separate databases с replication?
2. Нужна ли separate read replica для analytics queries?
3. Как часто запускать vacuum для performance?
4. Retention policy для старых quest analytics?
5. Backup frequency и retention?

## Acceptance Criteria

- Migration создает все таблицы без ошибок
- Все foreign keys работают
- Privacy settings по умолчанию = все False
- Quest можно создать, прочитать, обновить (CRUD works)
- Analytics queries возвращают только aggregated data
- Privacy enforcement блокирует запрещенные queries
- Concurrent access из PAS и Inner Edu работает без conflicts
- Indexes используются (check EXPLAIN ANALYZE)
- All database operations logged

## Definition of Done

- Alembic migration applied на dev/staging/prod
- All models documented с docstrings
- Foreign keys и indexes созданы
- Privacy layer tested с различными consent scenarios
- Performance benchmarks (>100 qps на quest queries)
- ER diagram в documentation
- Migration rollback tested

## Минимальные NFR для MVP

**Производительность**
- Quest creation: <100ms
- Analytics query: <200ms
- Concurrent connections: до 100
- Query throughput: >100 qps

**Надежность**
- Transaction isolation prevents data corruption
- Foreign key constraints enforce referential integrity
- Automatic connection pool management

**Capacity**
- До 10000 quests
- До 1000 active users
- До 100000 analytics records

## Требования безопасности

- Database credentials только через environment variables
- SSL/TLS для database connections
- Role-based access (pas_bot_user, inner_edu_user)
- Audit logging для privacy-sensitive queries
- Encryption at rest (PostgreSQL feature)
- NO child PII в quest_analytics table
- Sanitize all inputs перед SQL queries (SQLAlchemy защищает)

## Наблюдаемость

**Логи**
- Migration applied/rolled back
- Quest created/updated/deleted
- Privacy settings changed
- Analytics accessed (with consent check result)

**Метрики**
- database_connections_active (gauge)
- query_duration_seconds (histogram per table)
- privacy_checks_total (counter with result)
- quest_creations_total (counter)

**Alerts**
- Connection pool exhausted
- Slow queries (>1s)
- Privacy violation attempt

## Релиз

**Migration Strategy**
1. Apply migration на staging
2. Test all flows
3. Backup production database
4. Apply migration в maintenance window
5. Verify all tables created
6. Monitor performance 24h

**Rollback Plan**
- Alembic downgrade migration prepared
- Database backup для restore
- Feature flags для new code paths

## Откат

**Условия отката**
- Migration failure
- Performance degradation (>2x slower queries)
- Data corruption detected
- Privacy leak discovered

**Шаги отката**
1. Alembic downgrade migration
2. Restore from backup if needed
3. Disable feature flags using new tables
4. Investigate root cause

## Риски и митигации

- **Риск 1**: Migration breaks production - Митигация: test на staging, backup, maintenance window
- **Риск 2**: Privacy leak (child data exposed) - Митигация: strict privacy layer, audit logging
- **Риск 3**: Performance degradation - Митигация: indexes, query optimization, monitoring
- **Риск 4**: Concurrent access conflicts - Митигация: transaction isolation, optimistic locking
- **Риск 5**: Schema mismatch между projects - Митигация: shared models library, versioning

## Параметры стека

**Database**
- PostgreSQL 15+
- Extensions: uuid-ossp (для UUID generation)

**ORM**
- SQLAlchemy 2.0
- Alembic (migrations)

**Connection Pooling**
- asyncpg (async driver)
- Pool size: 20 connections

**Deployment**
- Managed PostgreSQL (AWS RDS / DigitalOcean)
- или Self-hosted с Docker

## Самопроверка плана перед выдачей

- ✅ Нет кода (только schema описание)
- ✅ Все секции заполнены
- ✅ Privacy considerations включены
- ✅ Описаны оба проекта (PAS + Inner Edu)
- ✅ Migration strategy описана
