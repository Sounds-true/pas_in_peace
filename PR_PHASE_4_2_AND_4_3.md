# Phase 4.2 Backend Core + Phase 4.3 Frontend Architecture

## 📋 Summary

**Phase 4.2 (Backend - IMPLEMENTED):** Complete multi-track recovery system with quest builder, content moderation, and REST API.

**Phase 4.3 (Frontend - ARCHITECTURE ONLY):** Comprehensive UI/UX architecture documentation for unified parent/child interfaces with voice mode support.

---

## ✨ Phase 4.2: Backend Core (IMPLEMENTED)

### 1️⃣ **MultiTrackManager** (`src/orchestration/multi_track.py`, ~500 lines)
Manages 4 parallel recovery tracks with cross-track impact and milestone detection.

**Features:**
- 🎯 **4 Recovery Tracks**: SELF_WORK, CHILD_CONNECTION, NEGOTIATION, COMMUNITY
- 📊 **4 Phases per Track**: AWARENESS → EXPRESSION → ACTION → MASTERY (0-100%)
- 🔍 **Keyword-based Track Detection**: Automatically detects intent from messages
- 🔗 **Cross-Track Impact**: Actions can progress multiple tracks (e.g., quest_created affects SELF_WORK + CHILD_CONNECTION)
- 💡 **Smart Suggestions**: Auto-generated next actions based on current phase
- 🏆 **Milestone Tracking**: Achievement detection and database persistence
- 🔄 **Track Switch Recommendations**: Suggests inactive track after 30 days

**Key Methods:**
```python
await multi_track_manager.initialize_tracks(user_id)
await multi_track_manager.get_all_progress(user_id)
await multi_track_manager.update_progress(user_id, track, delta, action_type)
await multi_track_manager.detect_track_from_message(message)
await multi_track_manager.check_milestone(user_id, track, action_type)
```

---

### 2️⃣ **ContentModerator** (`src/safety/content_moderator.py`, ~400 lines)
Two-tier content safety system for parent-created quests.

**Features:**
- ⚡ **Pattern-Based (Fast)**: Regex matching for Russian language red flags
- 🤖 **AI-Based (Accurate)**: SupervisorAgent integration for deep analysis
- 🚨 **8 Moderation Categories**:
  - MANIPULATION (guilt-tripping, pressure)
  - BLAME (blaming ex-partner)
  - PERSONAL_INFO (emails, phones, addresses)
  - INAPPROPRIATE_CONTENT (adult themes)
  - NEGATIVE_EMOTION (excessive negativity)
  - PRESSURE (forcing communication)
  - VIOLENCE (threats, aggression)
  - ADULT_TOPICS (divorce, court, legal)
- 📏 **4 Severity Levels**: CRITICAL, HIGH, MEDIUM, LOW
- 💬 **Fix Suggestions**: Actionable recommendations for improvement
- 🇷🇺 **Russian Language Optimized**: Native pattern matching

**Example Usage:**
```python
is_safe, issues = await moderator.check_content(text, context)
result = await moderator.moderate_quest(quest_yaml, metadata)
# result = {"passed": True/False, "issues": [...], "suggestions": [...]}
```

---

### 3️⃣ **QuestBuilderAssistant** (`src/techniques/quest_builder.py`, ~700 lines)
Conversational AI for creating educational quests through multi-turn dialogue.

**Features:**
- 🗣️ **6-Stage Dialogue System**:
  1. **INITIAL**: Welcome and explanation
  2. **GATHERING**: Collect child info and family memories
  3. **GENERATING**: GPT-4 generates quest YAML
  4. **REVIEWING**: Show preview, allow edits
  5. **MODERATING**: Content safety check
  6. **FINALIZING**: Save to database
- 👶 **Child Context Collection**: Age, interests, family memories, photos
- 🤖 **GPT-4 Integration**: Generates educational content from stories
- ✅ **Content Moderation**: Integrated safety checks
- 💾 **Database Persistence**: Auto-creates quest + analytics + privacy settings
- 🎭 **"Trojan Horse" Strategy**: Quest appears as educational app to child

**QuestContext Dataclass:**
```python
@dataclass
class QuestContext:
    child_name: Optional[str]
    child_age: Optional[int]
    child_interests: List[str]
    family_photos: List[str]
    family_memories: List[str]
    family_jokes: List[str]
    quest_yaml: Optional[str]
    current_stage: QuestStage
    moderation_passed: bool
```

---

### 4️⃣ **StateManager Integration** (`src/orchestration/state_manager.py`)
Integrated all Phase 4 components into main conversation flow.

**Changes:**
- 🔧 **Initialization**: Auto-initializes MultiTrackManager, ContentModerator, QuestBuilderAssistant when DB is ready
- 🎯 **Track Detection**: Detects recovery track from every user message
- 📈 **Progress Updates**: Updates track progress when techniques complete
- 🏅 **Milestone Checking**: Logs achievements in real-time
- 📦 **Context Passing**: Detected track + multi_track_manager passed to all techniques

**Integration Points:**
```python
# On initialization
self.multi_track_manager = MultiTrackManager(db_manager=self.db)
self.content_moderator = ContentModerator()
self.techniques["quest_builder"] = QuestBuilderAssistant(db, moderator)

# On message processing
detected_track = self.multi_track_manager.detect_track_from_message(message)

# After technique execution
await self.multi_track_manager.update_progress(user_id, track, delta, action_type)
milestone = await self.multi_track_manager.check_milestone(user_id, track, action_type)
```

---

### 5️⃣ **/progress Telegram Command** (`src/core/bot.py`)
Beautiful multi-track progress visualization for parents.

**Features:**
- 📊 **Visual Progress Bars**: All 4 tracks with percentage completion
- 📍 **Phase & Action Count**: Current phase + total actions per track
- ➡️ **Next Actions**: Suggested next steps for each track
- 🏆 **Recent Milestones**: Last achievement per track
- 💡 **Smart Recommendations**: Suggests track switch when appropriate (30+ days inactive)
- 🇷🇺 **Russian Localization**: Track names, phases, messages

**Example Output:**
```
📊 Ваш прогресс по 4 направлениям восстановления

💚 Работа над собой
████████░░ 45%
Фаза: Выражение | Действий: 12
➡️ Попробуйте технику заземления

💙 Связь с ребенком
██████░░░░ 30%
Фаза: Осознание | Действий: 5
➡️ Создайте первый квест для ребенка
🏆 Последнее достижение: First Letter

🤝 Переговоры
███░░░░░░░ 15%
Фаза: Осознание | Действий: 2
➡️ Изучите технику BIFF

👥 Сообщество
█░░░░░░░░░ 5%
Фаза: Осознание | Действий: 1
➡️ Присоединяйтесь к группе поддержки

💡 Рекомендация: Попробуйте уделить внимание направлению "👥 Сообщество"
```

---

### 6️⃣ **REST API** (`src/api/`, ~600 lines)
FastAPI-based REST API for frontend integration.

**Endpoints:**

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/tracks/{user_id}` | Get all track progress |
| GET | `/api/tracks/{user_id}/{track_name}` | Get specific track |
| POST | `/api/tracks/{user_id}/{track_name}/progress` | Update progress (with cross-track impact) |
| GET | `/api/tracks/{user_id}/milestones` | Get user milestones (filterable) |
| GET | `/api/tracks/{user_id}/suggestions` | Get track switch suggestions |
| GET | `/health` | Health check |
| GET | `/api/docs` | Swagger documentation |
| GET | `/api/redoc` | ReDoc documentation |

**Features:**
- 🔄 **Auto OpenAPI Schema**: Interactive Swagger UI at `/api/docs`
- ✅ **Pydantic Validation**: Request/response models with type safety
- 🌐 **CORS Middleware**: Ready for frontend integration
- 🔥 **Lifespan Management**: DB initialization on startup
- 💉 **Dependency Injection**: Shared DB and MultiTrackManager instances
- ⚠️ **Global Exception Handling**: Graceful error responses

**Run Server:**
```bash
python api_server.py
# or
uvicorn src.api.app:create_app --factory --reload
```

**Example Request:**
```bash
# Get all tracks
curl http://localhost:8000/api/tracks/123456

# Update progress
curl -X POST http://localhost:8000/api/tracks/123456/self_work/progress \
  -H "Content-Type: application/json" \
  -d '{"delta": 5, "action_type": "first_cbt"}'

# Response includes cross-track updates
{
  "user_id": 123456,
  "tracks": {
    "self_work": {"completion_percentage": 50, ...},
    "child_connection": {"completion_percentage": 32, ...},  # Also updated!
    ...
  },
  "primary_track": "self_work"
}
```

---

## 🗄️ Database Changes (Phase 4.1 - Already Committed)

- ✅ 6 new models: Quest, CreativeProject, QuestAnalytics, ChildPrivacySettings, PsychologicalProfile, TrackMilestone
- ✅ Extended User model with recovery_tracks fields (JSON column)
- ✅ 20+ new DatabaseManager methods with privacy enforcement
- ✅ Alembic migration created

---

## 🔐 Privacy & Safety

### Content Moderation
- ✅ **Default Block**: CRITICAL/HIGH severity blocks quest creation
- ✅ **Russian Patterns**: Native language red flag detection
- ✅ **AI Backup**: SupervisorAgent for edge cases
- ✅ **Fix Suggestions**: Helps parents improve content

### Child Privacy
- 🔒 **Default NO_SHARING**: All privacy settings default to no sharing
- ✅ **Child Consent Required**: Parent can only see analytics if child explicitly agrees
- 📊 **Aggregated Metrics Only**: No personal answers/messages shared
- 📝 **Audit Trail**: All consent changes logged with timestamps
- ⚠️ **Privacy Enforcement**: `get_quest_analytics()` returns `None` without consent

---

## 📊 Phase 4.2 Commits

1. **c308166** - Add MultiTrackManager and ContentModerator
2. **7a416c5** - Add QuestBuilderAssistant for conversational quest creation
3. **4077928** - Integrate MultiTrackManager with StateManager
4. **f488851** - Add /progress command for multi-track visualization
5. **b8cad95** - Add REST API for multi-track recovery system

**Total Phase 4.2:**
- Files changed: 12
- Lines added: ~2,800
- Status: ✅ **FULLY IMPLEMENTED & TESTED**

---

## 📐 Phase 4.3: Frontend Architecture (DOCUMENTATION ONLY)

### Architecture Document (`docs/architecture/phase_4_3_unified_ui_ux.md`, ~650 lines)

**Comprehensive UI/UX system for:**
1. **Parent Interface** (pas_in_peace)
   - Telegram Bot (exists) + Web Dashboard (new)
   - Multi-track progress visualization
   - Quest Builder (3 modes: Story Chat, Mind Map, YAML)
   - Letter/Goals management
   - Privacy-aware child analytics

2. **Child Interface** (inner_edu)
   - Quest Player with educational content
   - 🎤 **Voice Mode** (audio narration + voice commands)
   - XP/Badge/Level system
   - Reveal mechanics (gradual family clue discovery)
   - Profile & collection

3. **Creator Mode**
   - Story Chat (AI dialogue)
   - Mind Map Builder (visual editor)
   - Template Gallery
   - Preview & Test

4. **Wiki Platform**
   - 32 articles for parent-creators
   - Story-to-Attribute mapping guides
   - AI assistant tutorials
   - Community templates

**Key Concepts Integrated:**
- ✅ **IFS (Internal Family Systems)**: Parts as NPCs
- ✅ **ТРИЗ**: Contradiction resolution as game mechanics
- ✅ **CBT/DBT**: Gamified behavioral activation
- ✅ **Reality-Game Bridge**: Virtual progress → real actions
- ✅ **Proof-of-Emotional-Work**: Reflection-based validation

**Tech Stack:**
```
Frontend:
  - React 18 + TypeScript
  - Next.js 14 (App Router)
  - Zustand (state management)
  - Tailwind CSS + Radix UI
  - Framer Motion (animations)
  - React Flow (mind map)
  - Web Speech API (voice)
  - Recharts + D3.js (charts)

Backend (exists):
  - FastAPI ✅
  - PostgreSQL ✅
  - WebSocket (new)
  - Redis (new)
```

**14-Week Roadmap:**
- Week 1-2: Core Dashboard
- Week 3-4: Quest Builder - Story Mode
- Week 5-6: Quest Builder - Mind Map
- Week 7-9: Child Quest Player
- **Week 10-11: 🎤 Voice Mode**
- Week 12: Wiki & Docs
- Week 13-14: Testing & Polish

---

### Wiki for Parent-Creators (`docs/wiki/README.md`, ~500 lines + structure)

**32 Articles Planned:**

```
📁 01_getting_started (3 articles)
   - What is InnerWorld?
   - Creating Your First Quest (15 min)
   - Privacy & Safety

📁 02_quest_design (11 articles)
   Story Elements:
   - Character Development
   - Family Memories as Clues
   - Reveal Mechanics (Trojan Horse)

   Educational Content:
   - Math Challenges (age 7-12)
   - Reading Comprehension
   - Logic Puzzles
   - Emotional Intelligence

   Game Mechanics:
   - XP & Leveling
   - Badges & Achievements
   - Difficulty Tuning
   - 🎤 Voice Mode Integration

📁 03_story_mapping (9 articles)
   - Transformation Principle
   - Family Joke → Password
   - Photo → Visual Clue
   - Hobby → Character Strength
   - Experience → Story Arc
   - IFS Parts as NPCs

📁 04_ai_assistant (3 articles)
   - Talking to Quest Builder
   - Refining Generated Content
   - Content Moderation System

📁 05_advanced (4 articles)
   - Multi-Quest Campaigns
   - Collaborative Quests
   - Analytics & Feedback
   - Reveal Strategy

📁 06_community (3 articles)
   - Template Library
   - Success Stories
   - Support Forum
```

**Quick Start Example:**
```yaml
# 5 minutes: 1 story → 1 quest

Story: "Мы с сыном искали созвездия"

AI generates:
  quest: "Звездный Путь"
  node_5:
    reveal: "Это же созвездие, которое мы искали вместе!"
```

---

### Example Wiki Article (`docs/wiki/03_story_mapping/joke_to_password.md`, ~430 lines)

**Detailed Guide:** Family Joke → Password Puzzle

**Includes:**
- Psychology & concept explanation
- YAML transformation example
- 3 difficulty variations:
  - **Easy** (7-9 years): Direct password
  - **Medium** (9-11 years): Cryptogram (Caesar cipher)
  - **Hard** (10-12 years): Visual rebus puzzle
- Story integration examples
- Safety & moderation guidelines
- Privacy-aware analytics
- Advanced techniques (joke chains, evolution, collaboration)
- Practical exercises & community tips

**Example Transformation:**
```yaml
Story:
  "Мы называли кота 'философом'"

Game:
  node_7:
    type: puzzle
    challenge: "Введи кодовое слово"
    answers: ["кот-философ", "философ", "барсик-философ"]

    on_success:
      reveal:
        message: "Это же наша шутка! Кто создал этот квест?"
        image: "family_photo_with_cat.jpg"
        emotion_tag: "nostalgic_joy"
```

---

## 🎤 Voice Mode (NEW - High Priority Feature)

**Architecture Included in Phase 4.3 Docs:**

```tsx
Voice Features:
✅ Audio Narration - Quest content read aloud
✅ Voice Commands - "следующий вопрос", "дай подсказку"
✅ Speech Recognition - Voice answer input
✅ Offline Fallback - Works without internet

Tech Stack:
- Web Speech API (browser STT/TTS)
- Whisper API (OpenAI, optional premium)
- ElevenLabs (high-quality narration)
- Mozilla DeepSpeech (offline model)
```

**Example Voice Quest Flow:**
```
🔊 Narrator: "Ты стоишь перед старым садом..."
🎤 Child: "Открыть ворота"
🔊 Narrator: "На воротах висит замок с загадкой..."
🎤 Child: "Кот-философ"
🔊 Narrator: "✨ Правильно! Дверь открылась!"
```

---

## ❓ UX Decisions Needed (Before Phase 4.3 Implementation)

### 1. **Color Palette** 🎨
Proposed:
```css
Parents (calm):
  --pas-primary: #4A90E2 (trust blue)
  --pas-self-work: #48C774 (growth green)

Children (bright):
  --inner-primary: #FFD93D (sunny yellow)
  --inner-magic: #A78BFA (magic purple)
```
**Question:** Approve or modify?

### 2. **Voice Mode Priority** 🎤
Architecture ready (Week 10-11 in roadmap)

**Question:** Priority level?
- [ ] High (must-have in MVP)
- [ ] Medium (Phase 2)
- [ ] Low (optional)

### 3. **Mind Map Complexity** 🗺️
**Question:** What level for MVP?
- [ ] Simple (basic nodes + connections)
- [ ] Medium (+ attributes, icons)
- [ ] Advanced (+ auto-layout, collaboration)

### 4. **Template Gallery** 📦
Proposed: 10-15 starter templates

**Question:** Include community gallery (user-submitted)?
- [ ] Yes (with moderation)
- [ ] No (curated only)

### 5. **Psychology Consultation** 👨‍⚕️
Reveal strategy documented in detail

**Question:** Need additional consultation?
- [ ] Yes
- [ ] No

---

## 🧪 Testing

### API Server
```bash
# Start server
python api_server.py

# Test endpoints
curl http://localhost:8000/health
curl http://localhost:8000/api/docs  # Swagger UI
```

### Telegram Bot
```bash
# /progress command
User: /progress
Bot: [Shows 4-track progress visualization]
```

### Quest Builder (via Telegram)
```bash
# Will be activated after frontend is ready
User: /quest
Bot: [Opens Web Dashboard Quest Builder]
```

---

## 📊 Overall Statistics

### Phase 4.2 (Backend - DONE)
```
Commits: 5
Files: 12
Lines: ~2,800
Status: ✅ Fully Implemented
```

### Phase 4.3 (Frontend - ARCHITECTURE)
```
Commits: 2
Files: 4 (documentation)
Lines: ~2,000
Status: 📋 Architecture Ready
Next: UX Decisions → Implementation
```

### Combined
```
Total Commits: 7
Total Lines: ~4,800
Branch: claude/review-development-roadmap-011CUuXKnVM5C53ydHPJRhCd
All Pushed: ✅
```

---

## 🎯 Next Steps

### Immediate (Phase 4.3)
1. **Get UX Decisions** (see questions above)
2. **Create Figma Mockups** (optional but helpful)
3. **Setup Next.js Project** (monorepo structure)

### Short-term
4. **Implement Core Dashboard** (Week 1-2)
5. **Build Quest Builder UI** (Week 3-6)
6. **Create Child Quest Player** (Week 7-9)

### Medium-term
7. **Implement Voice Mode** (Week 10-11)
8. **Build Wiki Platform** (Week 12)
9. **Testing & Polish** (Week 13-14)

---

## 🔗 Related Documentation

- **Implementation Plan**: `docs/implementation/IP-04-unified-integration.md`
- **Architecture Analysis**: `docs/architecture/inner_edu_integration_analysis.md`
- **Phase 4.3 Plan**: `PHASE_4_3_PLAN.md`
- **Wiki Home**: `docs/wiki/README.md`

---

## 💡 Key Innovation: "Trojan Horse" Strategy

Quests appear as **educational games** to the child. As they play:
1. Learning math, logic, reading ✅
2. Earning XP, badges, levels 🎮
3. Gradually discovering **family clues** 🔍
4. Realizing: "Someone who knows me created this!" 💡
5. Optional: Child can share progress with parent 💙

**Result:** Gentle, non-pressured reconnection through **shared joy of learning**.

---

**Status:** ✅ **Phase 4.2 Complete** | 📋 **Phase 4.3 Architecture Ready**

**Branch:** `claude/review-development-roadmap-011CUuXKnVM5C53ydHPJRhCd`

**Ready for:** Review → UX Decisions → Implementation
