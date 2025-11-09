# Implementation Plan: Reveal Mechanics & Achievement Sharing System

## Смысл и цель задачи

Реализовать "Троянский конь" стратегию где ребенок постепенно открывает что квест создал отчужденный родитель. Quest презентуется как образовательное приложение для помощи с уроками, но включает семейные намеки которые ребенок расследует как детектив. Achievement sharing система позволяет ребенку поделиться успехами с ОБОИМИ родителями (neutral notifications) только после explicit consent.

## Архитектура решения

### Структура компонентов

**Inner Edu Frontend** (где играет ребенок)

```
frontend/src/
├── components/
│   ├── QuestEngine/              # Существующий - расширить
│   │   ├── RevealMechanics.tsx   # Новый - progressive disclosure
│   │   ├── ClueDetector.tsx      # Новый - обнаружение намеков
│   │   └── DetectiveLog.tsx      # Новый - журнал расследования
│   ├── AchievementSystem/         # Новый
│   │   ├── AchievementPopup.tsx  # После успеха
│   │   ├── ShareConsent.tsx      # Privacy consent screen
│   │   └── ProgressTracker.tsx   # Визуализация прогресса
│   └── PrivacySettings/           # Новый
│       ├── ConsentManager.tsx    # Управление consent
│       └── DataSharing.tsx       # Что шарится с родителями
```

**Backend (pas_in_peace + inner_edu shared)**

```
src/quest/
├── reveal_engine.py              # Новый - логика reveal
├── clue_generator.py             # Новый - генерация подсказок
└── achievement_notifier.py       # Новый - отправка notifications

src/storage/models.py             # Extend (уже описано в IP-04)
```

### Ключевые концепции

**Reveal Phases** - 4 стадии открытия:

1. **NEUTRAL (0-30%)** - чисто образовательный контент, нет намеков
2. **SUBTLE_CLUES (30-60%)** - семейные фото без текста, знакомые места
3. **INVESTIGATION (60-80%)** - детективные узлы "Who made this?"
4. **REVEAL (80-100%)** - финальный узел где ребенок узнает truth

**Clue Types**:
- PHOTO - семейные фотографии (без текста!)
- LOCATION - знакомые места (парк где гуляли)
- JOKE - семейные шутки или фразы
- MEMORY - reference на совместные воспоминания
- HANDWRITING - элементы почерка родителя (опционально)

**Achievement Sharing Levels**:
- NO_SHARING - default, ничего не шарится
- COMPLETION_ONLY - только % прохождения
- ACHIEVEMENTS - + unlocked достижения
- FULL_PROGRESS - + educational metrics (но БЕЗ personal messages)

## Полный flow работы функционала

### Scenario 1: Progressive Reveal Journey

1. **Phase 1: Neutral Education (nodes 1-3)**
   - Child opens "Math Helper" app on tablet
   - Sees standard educational tasks: "Solve 2+2", "Name planets"
   - NO family references, чисто школьные темы
   - Child успешно проходит узлы
   - Quest engine: current_reveal_phase = NEUTRAL

2. **Phase 2: First Clues (nodes 4-6)**
   - Node 4: Math problem about dinosaurs (child's favorite topic)
   - Background image: слегка знакомый парк (но не очевидно)
   - Child может заметить или нет
   - Node 5: задача про футбол (child's hobby)
   - Node 6: background - семейное фото БЕЗ лиц (только природа)
   - Child: "Это странно... как игра знает что я люблю динозавров?"
   - Quest engine: current_reveal_phase = SUBTLE_CLUES

3. **Phase 3: Investigation Begins (nodes 7-8)**
   - Node 7: explicit detective mission: "Who created this app?"
   - Clues presented: photo gallery, знакомые места, семейная шутка
   - Child активно собирает evidence
   - Detective log opens: "Clues found: 3/10"
   - Child может записывать теории
   - Node 8: более explicit clues (папин почерк, мамина любимая фраза)
   - Quest engine: current_reveal_phase = INVESTIGATION

4. **Phase 4: Revelation (node 9-10)**
   - Node 9: child собрал достаточно clues
   - UI: "You're close to solving the mystery!"
   - Final puzzle combining all clues
   - Node 10: REVEAL
   - Video message from parent (pre-recorded): "Привет, сын! Это я создал эту игру для тебя..."
   - Emotional moment
   - Quest engine: current_reveal_phase = REVEAL
   - Achievement unlocked: "Mystery Solved"

### Scenario 2: Achievement Sharing with Consent

1. **Child completes difficult node**
   - Inner Edu app detects achievement (passed hard math task)
   - AchievementPopup appears: "Great job! You solved polynomial equations!"
   - Stars animation, celebration sound

2. **First-time sharing prompt**
   - App: "Would you like to share your achievements?"
   - Explain screen: "Both your parents can receive notifications about your progress. This is optional."
   - Privacy explanation: "We only share that you completed tasks, NOT your answers or messages"
   - Options:
     - "Yes, share my achievements" → ACHIEVEMENTS level
     - "Only completion %" → COMPLETION_ONLY
     - "No, keep private" → NO_SHARING (default stays)

3. **Child chooses "Share achievements"**
   - Consent saved to ChildPrivacySettings table
   - share_educational_progress = True
   - App: "Thank you! Both parents will receive a message."

4. **Notification sent**
   - AchievementNotifier triggered
   - Message composed (neutral, no manipulation triggers):
     ```
     [Educational App Update]
     Maxim completed "Polynomial Equations" module
     Progress: 65% of current quest
     ```
   - Sent via Telegram to:
     - Alienated parent (creator of quest)
     - Custodial parent (алиенатор) - SAME message
   - NO differentiation, fully neutral

5. **Parent receives notification**
   - Alienated parent (PAS Bot): sees message + link to analytics dashboard
   - Custodial parent: receives via Telegram (если known) or email
   - Both see IDENTICAL content (no favoritism)

### Scenario 3: Child revokes consent

1. Child opens PrivacySettings in app
2. Toggle: "Share achievements with parents" → OFF
3. App: "Are you sure? Your parents won't receive updates anymore."
4. Child confirms
5. Consent updated: share_educational_progress = False
6. Backend immediately stops sending notifications
7. Parents see in dashboard: "Child hasn't consented to sharing progress"
8. NO pressure on child, fully autonomous decision

## API и интерфейсы

### RevealEngine Class

**Методы**

- `calculate_reveal_phase(nodes_completed, total_nodes)` - определить текущую фазу
- `get_clues_for_phase(phase, family_data)` - какие clues показать
- `should_trigger_investigation(progress_percentage)` - когда начать детективный сюжет
- `generate_reveal_node(parent_info, child_info)` - финальный reveal узел
- `is_clue_discovered(clue_id, child_progress)` - ребенок нашел clue?

**RevealPhase Enum**

```python
NEUTRAL = "neutral"           # 0-30%
SUBTLE_CLUES = "subtle_clues" # 30-60%
INVESTIGATION = "investigation" # 60-80%
REVEAL = "reveal"             # 80-100%
```

**Clue TypedDict**

```python
{
  "id": str,                    # unique clue identifier
  "type": ClueType,             # PHOTO, LOCATION, JOKE, MEMORY
  "content": str,               # path to photo or text
  "reveal_threshold": float,    # at what % показать (0.3 = 30%)
  "discovered": bool,           # child нашел?
  "discovered_at": datetime     # когда нашел
}
```

### AchievementNotifier Class

**Методы**

- `notify_achievement(child_id, achievement_data, quest_id)` - отправить notification обоим родителям
- `check_consent(child_id)` - проверить child privacy settings
- `compose_neutral_message(achievement)` - создать neutral сообщение
- `send_to_parents(quest_id, message)` - отправить ОБОИМ родителям
- `log_notification(child_id, parents, sent_status)` - audit log

**Achievement TypedDict**

```python
{
  "achievement_id": str,
  "name": str,                  # "Polynomial Equations Master"
  "description": str,           # "Solved 10 polynomial problems"
  "category": str,              # "math", "logic", "creativity"
  "difficulty": str,            # "easy", "medium", "hard"
  "unlocked_at": datetime,
  "node_id": str                # какой узел квеста
}
```

### Frontend Components API

**RevealMechanics Component**

Props:
- `currentProgress: number` (0-100)
- `clues: Clue[]` - список всех clues
- `onClueDiscovered: (clueId) => void` - callback когда найден
- `revealPhase: RevealPhase` - текущая фаза

State:
- `discoveredClues: Set<string>`
- `detectiveLogOpen: boolean`
- `investigationActive: boolean`

**ShareConsent Component**

Props:
- `onConsentChange: (level: SharingLevel) => void`
- `currentLevel: SharingLevel`
- `isFirstTime: boolean` - показать ли full explanation

Methods:
- `handleConsentUpdate()` - сохранить в backend
- `showPrivacyExplanation()` - detailed info

## Взаимодействие компонентов

```
Child plays quest (Inner Edu App)
  |
  v
QuestEngine.onNodeComplete(node_id)
  |
  +---> RevealEngine.calculate_reveal_phase(progress)
  |       |
  |       +---> If phase changed → trigger UI update
  |       +---> Get clues for new phase
  |       |
  |       v
  |   Render clues in quest nodes
  |
  +---> AchievementSystem.checkForAchievement(node_id)
        |
        +---> If achievement unlocked:
              |
              +---> AchievementPopup.show()
              |
              +---> Check if first-time achievement
                    |
                    +---> If YES: ShareConsent.show()
                    |       |
                    |       +---> Child chooses sharing level
                    |       |
                    |       v
                    |   ConsentManager.updateConsent()
                    |       |
                    |       v
                    |   POST /api/privacy/consent
                    |       |
                    |       v
                    |   ChildPrivacySettings table updated
                    |
                    +---> If consent already given:
                          |
                          +---> AchievementNotifier.notify_achievement()
                                |
                                +---> Check ChildPrivacySettings
                                |
                                +---> If sharing enabled:
                                      |
                                      +---> Compose neutral message
                                      +---> Get both parents (creator + custodial)
                                      +---> Send via Telegram Bot API
                                      +---> Log notification
                                      |
                                      v
                                Both parents receive SAME message
```

## Порядок реализации

### Step 1: Reveal Engine Backend (дни 1-3)

1. Create RevealPhase enum
2. Create Clue TypedDict
3. Implement RevealEngine class
4. Algorithm для calculate_reveal_phase()
5. Clue generation logic
6. Unit tests для всех фаз

### Step 2: Frontend Reveal Components (дни 4-6)

1. RevealMechanics component
2. ClueDetector component (визуализация найденных clues)
3. DetectiveLog component (журнал расследования)
4. Integration с QuestEngine
5. UI/UX для каждой фазы

### Step 3: Achievement System (дни 7-9)

1. Achievement detection logic (inner_edu backend)
2. AchievementPopup component
3. ShareConsent component с privacy explanation
4. ConsentManager integration
5. POST /api/privacy/consent endpoint

### Step 4: Notification System (дни 10-12)

1. AchievementNotifier class
2. Neutral message composer
3. Integration с Telegram Bot API
4. Support для email notifications (custodial parent)
5. Audit logging

### Step 5: Privacy Layer (дни 13-14)

1. ChildPrivacySettings enforcement
2. Consent revocation flow
3. Parent dashboard updates (показать "no consent")
4. Privacy audit logging

### Step 6: Testing (дни 15-17)

1. End-to-end test full reveal flow
2. Test all 4 phases
3. Test consent scenarios (grant, revoke, change level)
4. Test neutral notifications (both parents receive same)
5. UI/UX testing с real users

## Критичные граничные случаи

**Child discovers quest creator early**
- Если ребенок случайно узнал до reveal узла
- Quest продолжает работать normally
- Reveal node все равно показывается (formal acknowledgment)
- Achievement "Early Detective" unlocked

**Custodial parent blocks app**
- Neutral branding помогает избежать
- Но если заблокирован:
  - Quest data preserved
  - Can be installed on другом устройстве
  - Progress синхронизируется (если online)

**Child shares achievement but then revokes**
- Consent revocation immediate
- Previous notifications NOT retracted (уже отправлены)
- Future notifications stopped
- Parents notified: "Child updated privacy settings"

**Reveal too early (bad pacing)**
- If quest слишком короткий, reveal может случиться до 80%
- Fallback: reveal НЕ раньше чем 5 nodes completed
- Minimum quest length: 10 nodes (enforced в QuestBuilder)

**Notification delivery failure**
- Если Telegram API unavailable
- Retry logic: 3 attempts с exponential backoff
- If all fail: queue для позже
- Parent увидит в dashboard но не получит instant notification

## Объем работ

### Входит в реализацию

- RevealEngine class (~300 lines)
- ClueGenerator logic
- 3 frontend components (RevealMechanics, ClueDetector, DetectiveLog) (~500 lines)
- AchievementSystem (~400 lines)
- AchievementNotifier class (~200 lines)
- ShareConsent UI component (~150 lines)
- ConsentManager integration
- Neutral message composer
- Telegram Bot API integration для notifications
- ChildPrivacySettings enforcement
- Privacy audit logging
- Unit tests (~400 lines)
- Integration tests
- UI components styling

### Не входит в MVP

- Advanced clue types (audio, video clues)
- AI-generated reveal narratives (GPT-4 для personalization)
- Social sharing (share achievements с друзьями)
- Gamification (leaderboards, competitive achievements)
- Parent-child messaging через app
- Multi-language reveal content
- Accessibility features (screen reader support для reveal)

## Допущения

- Inner Edu app уже имеет QuestEngine
- Telegram Bot API доступен для notifications
- ChildPrivacySettings table создана (IP-04)
- Quest YAML includes reveal node definitions
- Parent pre-records video message для reveal (or text fallback)
- Both parents имеют Telegram accounts (или email fallback)

## Открытые вопросы

1. Как часто можно отправлять notifications (rate limiting)?
2. Должен ли custodial parent получать notifications даже если блокирует контакт?
3. Нужна ли возможность child pause notifications временно?
4. Что если child хочет шарить только с одним родителем (не обоими)?
5. Как обрабатывать ситуацию если родители в разных time zones?

## Acceptance Criteria

- Quest начинается как neutral educational app (no family references)
- Clues появляются постепенно (30%, 60%, 80% milestones)
- Child может вести detective log и записывать теории
- Reveal node показывается только после 80% completion
- Achievement popup appears после успешного выполнения
- ShareConsent screen показывается первый раз clearly и understandably
- Privacy explanation доступна на детском языке
- Child может revoke consent в любой момент
- Neutral notifications отправляются ОБОИМ родителям
- Messages identical (no differentiation между parents)
- Consent changes logged для audit
- Parent dashboard respects child privacy settings

## Definition of Done

- RevealEngine протестирован на всех 4 фазах
- Frontend components рендерятся correctly
- Achievement detection работает reliably
- Consent flow tested (grant, revoke, change level)
- Notifications отправляются обоим parents
- Message content verified as neutral (no manipulation triggers)
- Privacy enforcement tested
- Audit logs working
- UI/UX reviewed с фокус-группой
- Documentation для reveal mechanics
- Metrics для reveal_phase_reached, achievements_shared, consent_changes

## Минимальные NFR для MVP

**Производительность**
- Reveal phase calculation: <100ms
- Achievement popup render: <500ms
- Notification delivery: <5s
- Consent update: <1s

**Надежность**
- Clue discovery state persistent (не теряется при app restart)
- Notification retry до 3 раз
- Consent changes immediate (no delay)

**Usability**
- Privacy explanation understandable для ages 10+
- Consent flow <3 taps
- Detective log accessible any time

## Требования безопасности

- Child consent required для ANY data sharing
- Default: NO_SHARING (privacy-first)
- Audit log всех consent changes
- NO child messages/answers в notifications (только aggregated)
- Neutral language (prevent custodial parent triggers)
- Clue content sanitized (no PII about custodial parent)
- Rate limiting: max 5 notifications per day
- NO tracking child's emotional responses в shared data

## Наблюдаемость

**Логи**
- reveal_phase_changed (child_id, quest_id, old_phase, new_phase)
- clue_discovered (child_id, clue_id, timestamp)
- achievement_unlocked (child_id, achievement_id)
- consent_changed (child_id, old_level, new_level)
- notification_sent (quest_id, parents, success/failure)

**Метрики**
- reveal_phases_reached (counter per phase)
- clues_discovered_total (counter)
- achievements_unlocked_total (counter)
- consent_grants_total (counter)
- consent_revocations_total (counter)
- notifications_sent_total (counter)
- notification_failures_total (counter)

**Alerts**
- Notification failure rate >10%
- Consent revocation spike (>20% in 24h - может указывать на проблему)
- Reveal phase progression stuck (child не прогрессирует)

## Релиз

**Feature Flags**
- `reveal_mechanics_enabled` - enable progressive reveal
- `achievement_sharing_enabled` - enable sharing system
- `dual_parent_notifications` - send to both parents (vs only creator)
- `strict_privacy_mode` - extra privacy enforcement

**Rollout Plan**
1. Alpha: 5 quests with reveal mechanics tested internally
2. Beta: 20 children play quests, feedback collected
3. GA: gradual 10% → 30% → 100%

## Откат

**Условия отката**
- >30% children confused by detective mechanics
- Privacy leak discovered (child data exposed)
- Notification delivery failures >20%
- Custodial parents complaining about notifications

**Шаги отката**
1. Disable `reveal_mechanics_enabled` flag
2. Quests работают as simple educational apps (no reveal)
3. Disable `achievement_sharing_enabled`
4. Stop all notifications
5. Preserve collected data (не удалять)
6. Investigation root cause

## Риски и митигации

- **Риск 1**: Custodial parent обнаруживает source квеста и блокирует - Митигация: neutral branding, educational focus, delay reveal
- **Риск 2**: Child feels manipulated при reveal - Митигация: gentle reveal, option to stop quest, emphasize educational value
- **Риск 3**: Notifications trigger custodial parent aggression - Митигация: strictly neutral language, educational framing, BOTH parents receive same
- **Риск 4**: Privacy leak (child personal data shared) - Митигация: strict privacy layer, aggregated data only, audit logging
- **Риск 5**: Achievement spam (too many notifications) - Митигация: rate limiting, batch daily digest option

## Параметры стека

**Frontend**
- React 18
- TypeScript 5.0+
- React Flow (quest visualization, existing)
- Framer Motion (achievement animations)

**Backend**
- Python 3.11+ (RevealEngine, AchievementNotifier)
- FastAPI (endpoints)
- SQLAlchemy 2.0 (ChildPrivacySettings)

**Notifications**
- Telegram Bot API (primary)
- Email (fallback для custodial parent)

**Database**
- PostgreSQL 15
- child_privacy_settings table (from IP-04)

## Самопроверка плана перед выдачей

- ✅ Нет кода (только описание)
- ✅ Все секции заполнены
- ✅ Realistic timeline (17 дней)
- ✅ Privacy-first approach
- ✅ "Троянский конь" стратегия described
- ✅ Dual parent notification (neutral)
- ✅ Child consent management
- ✅ Naming: `IP-06-reveal-achievement-system.md`
