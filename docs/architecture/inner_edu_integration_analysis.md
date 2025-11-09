# Inner Edu Architecture Analysis & Integration Report

**Date:** 2025-11-09  
**Analyzed Repository:** https://github.com/Sounds-true/inner_edu  
**Target Integration:** PAS Bot (pas_in_peace) unified platform  

---

## Executive Summary

Inner Edu is a mature educational quest platform with AI-powered quest generation capabilities. The architecture is production-ready with FastAPI backend, React+TypeScript frontend, and PostgreSQL database. Key finding: **Strong alignment with PAS implementation plans (IP-01, IP-02, IP-06)**, but requires careful integration strategy to avoid conflicts.

**Compatibility Score: 8.5/10**

---

## 1. Current Architecture Overview

### 1.1 Backend Stack (Python)

**Framework & Core:**
- FastAPI 0.104.1 (ASGI server with Uvicorn)
- Python 3.11+ required
- SQLAlchemy 2.0.23 ORM with Alembic migrations
- PostgreSQL (asyncpg + psycopg2-binary drivers)

**AI & Integration:**
- OpenAI 1.3.0 (GPT-4 function calling)
- Pydantic 2.5.0 (data validation)
- python-telegram-bot 20.7 (notifications)
- APScheduler 3.10.4 (task scheduling)

**Structure:**
```
backend/
├── api/
│   ├── builder.py       # Quest Builder AI agent endpoints
│   └── quests.py        # Quest CRUD operations
├── database/
│   └── models.py        # SQLAlchemy models
├── quest_builder/
│   └── agent.py         # QuestBuilderAgent (GPT-4)
├── moderation/          # Content safety (not yet implemented)
└── main.py             # FastAPI app initialization
```

**API Endpoints:**
- `POST /api/builder/chat` - AI conversation for quest creation
- `GET /api/builder/session/{id}` - Retrieve session state
- `POST /api/builder/generate_graph` - Force graph generation
- `POST /api/builder/refine_node` - AI node enhancement
- `GET /api/quests/existing` - List approved quests
- `POST /api/quests/load_yaml_quests` - Import YAML quests

**Authentication Status:** ⚠️ **NOT IMPLEMENTED** (commented TODO in main.py)

### 1.2 Frontend Stack (TypeScript)

**Framework & Build:**
- React 18.2.0 with TypeScript 5.3.3
- Vite 5.0.8 (development & build)
- TailwindCSS 3.3.6 (styling)

**State Management:**
- **Zustand 4.4.7** ✅ (matches IP-02 plan)
- No React Router (single-page app currently)
- Axios 1.6.2 (API client)

**Visualization:**
- **React Flow 11.10.1** ✅ (graph-based quest builder)
- Dagre 0.8.5 (graph layout algorithms)

**Structure:**
```
frontend/src/
├── components/
│   └── AIQuestBuilder/
│       ├── index.tsx           # Main quest builder component
│       └── QuestLibrary.tsx    # Quest selection UI
├── types/                      # TypeScript definitions (404 - not found)
├── styles/                     # CSS/styling
├── App.tsx                     # Root component (single user: "test-user-123")
└── main.tsx                    # Entry point
```

**Routing:** ⚠️ No routing library - single component render

**CORS Configuration:**
- `http://localhost:5173` (Vite dev)
- `http://localhost:3000` (alternative)
- Environment variable: `FRONTEND_URL`

### 1.3 Database Schema

**Tables:**

1. **users** (UUID primary key)
   - `telegram_id` (BigInteger, unique, indexed)
   - `child_name` (String)
   - `learning_profile` (JSONB)
   - `created_at` (Timestamp)

2. **quests** (UUID primary key)
   - `author_id` (FK to users)
   - `title` (String)
   - `graph_structure` (JSONB) ← **Primary quest representation**
   - `yaml_content` (Text) ← **YAML export (optional)**
   - `psychological_module`, `location`, `difficulty`, `age_range`
   - `is_public` (Boolean)
   - `moderation_status` (Enum: PENDING, APPROVED, REJECTED)
   - `rating` (Float), `plays_count` (Integer)

3. **quest_builder_sessions** (UUID primary key)
   - `user_id` (FK to users)
   - `conversation_history` (JSONB)
   - `current_stage` (String)
   - `current_graph` (JSONB)
   - `quest_context` (JSONB)

4. **quest_progress** (UUID primary key)
   - `user_id`, `quest_id` (FKs)
   - `current_step` (Integer)
   - `completed` (Boolean)

5. **quest_ratings**, **user_quest_library** (supporting tables)

**Key Insight:** Graph structure is primary; YAML is secondary export format.

---

## 2. Quest System Deep Dive

### 2.1 Quest Graph Structure (Graph → YAML)

**Node Types:**

1. **StartNode** (green circle)
   - `title`, `description`
   - Entry point

2. **QuestStepNode** (blue rectangle)
   - `character` (NPC guide)
   - `location` (game world zone)
   - `psychological_method` (e.g., "Feynman Technique")
   - `dialogue` (character speech)

3. **ChoiceNode** (yellow diamond)
   - Branching logic
   - Options with routing to next nodes

4. **RealityBridgeNode** (purple hexagon)
   - Real-world tasks
   - `deadline`, `reminder_settings`

5. **EndNode** (red circle)
   - Completion message
   - Experience points reward

**Graph Representation:**
```javascript
{
  "title": "Quest Name",
  "nodes": [
    {
      "id": "node-1",
      "type": "start",
      "position": {"x": 100, "y": 100},
      "data": {"title": "...", "description": "..."}
    },
    // ...
  ],
  "edges": [
    {
      "id": "edge-1",
      "source": "node-1",
      "target": "node-2",
      "label": "Continue",
      "animated": true
    }
  ]
}
```

### 2.2 Quest YAML Format (Execution Format)

**Example from:** `src/data/quests/tower_confusion/quest_01_simple_words.yaml`

```yaml
quest_id: tower_quest_01_simple_words
title: "Объясни простыми словами"
module: module_15_metacognition
location: tower_confusion
difficulty: easy
age_range: "10-14"
estimated_time_minutes: 10

learning_profile_impact:
  understanding_meaning: high
  memory: low
  attention: medium
  motivation: medium

steps:
  - step_id: 1
    type: input_text
    prompt: "Выбери сложное слово из учебника"
    validation:
      min_length: 2
      max_length: 50
    examples:
      - "синтез"
      - "экосистема"
      - "метафора"

  - step_id: 2
    type: choice
    prompt: "Как ты объяснишь это слово пятилетнему ребенку?"
    options:
      - text: "Нарисую картинку или схему"
        score: 1.0
        feedback: "Отлично! Визуальные образы помогают понять сложные идеи"
      - text: "Найду похожее простое слово"
        score: 0.5
        feedback: "Хорошо, но попробуй создать связь с реальным опытом"
      - text: "Использую связь с чем-то знакомым"
        score: 1.0

  - step_id: 3
    type: input_text
    prompt: "Объясни своими словами так, чтобы понял человек, который никогда не слышал это слово"
    validation:
      min_length: 10
      max_length: 200

completion_message: |
  Отлично! Ты только что применил "эффект протеже" - 
  когда мы объясняем, мы лучше понимаем сами.

rewards:
  xp: 10
  learning_profile_changes:
    understanding_meaning: +2
  location_progress:
    tower_confusion: +1

reality_bridge:
  task: "Объясни одно сложное слово однокласснику в течение 48 часов"
  deadline_hours: 48
  reminder_hours: 24
  verification_method: "self_report"

psychological_framework:
  technique: "Feynman Technique"
  research_basis: "Protégé effect demonstrates improved retention through teaching"
```

**Critical Fields:**
- `steps[]` - Sequential tasks with validation
- `type` - `input_text`, `choice`, `reflection`
- `rewards` - XP, learning profile modifications
- `reality_bridge` - Post-quest real-world application
- `psychological_framework` - Therapeutic basis

### 2.3 Quest Builder AI Agent

**File:** `backend/quest_builder/agent.py`

**Conversation Stages:**
1. GREETING
2. COLLECTING_INFO (age, interests, family memories)
3. CLARIFYING
4. GENERATING (GPT-4 function calling)
5. REVIEWING

**GPT-4 Function Schema:**
```python
{
  "name": "generate_quest_graph",
  "parameters": {
    "title": str,
    "nodes": [
      {"id": str, "type": str, "position": {x, y}, "data": dict}
    ],
    "edges": [
      {"id": str, "source": str, "target": str}
    ]
  }
}
```

**⚠️ CRITICAL GAP:** `graph_to_yaml()` method is **NOT IMPLEMENTED**
```python
def graph_to_yaml(self, graph: QuestGraph) -> str:
    # TODO: Convert graph to YAML
    # Needed for compatibility with QuestEngine
    return ""
```

**Moderation:** ContentModerator module exists but not integrated in API flow.

---

## 3. Comparison with PAS Implementation Plans

### 3.1 IP-01: Master Architecture Alignment

| Component | Inner Edu Status | IP-01 Requirement | Compatibility |
|-----------|------------------|-------------------|---------------|
| FastAPI Backend | ✅ Implemented | ✅ Required | 100% |
| PostgreSQL + SQLAlchemy | ✅ Implemented | ✅ Required | 100% |
| Shared Database | ⚠️ Separate schema | Must merge schemas | 70% (migration needed) |
| Telegram OAuth | ❌ Not implemented | ✅ Required | 0% (must add) |
| API Gateway | ❌ No gateway | Single entry point | 50% (can use FastAPI) |
| WebSocket Support | ⚠️ Mentioned, not implemented | Quest creation dialogue | 30% (must implement) |

**Schema Conflicts:**

**Inner Edu `users` table:**
- `telegram_id` (BigInteger)
- `child_name` (String)
- `learning_profile` (JSONB)

**PAS `users` table:**
- `telegram_id` (String(100))
- `current_state` (Enum)
- `therapy_phase` (Enum)
- `emotional_score` (Float)
- `context` (JSON)

**Merge Strategy Required:** 
- Rename inner_edu `users` → `quest_users` or `children`
- PAS `users` → `parents`
- Add `ParentChildRelationship` table
- Shared `telegram_users` table for auth

### 3.2 IP-02: Web Interface Alignment

| Component | Inner Edu Status | IP-02 Requirement | Compatibility |
|-----------|------------------|-------------------|---------------|
| React 18 + TypeScript | ✅ Implemented | ✅ Required | 100% |
| Zustand (state mgmt) | ✅ Implemented | ✅ Required | 100% |
| TailwindCSS | ✅ Implemented | ✅ Required | 100% |
| Next.js App Router | ❌ Uses Vite | ⚠️ IP-02 specifies Next.js | 50% (framework mismatch) |
| React Query | ❌ Not installed | ✅ Required for caching | 0% (must add) |
| Routing | ❌ No router | Need ParentDashboard pages | 0% (must add React Router or migrate to Next.js) |

**Naming Conflicts:**

1. **AIQuestBuilder component exists** in inner_edu
   - IP-02 plans to extend it with `ConversationalMode.tsx` ✅ Compatible
   
2. **No ParentDashboard** in inner_edu
   - Current: Single-user quest builder
   - IP-02: Multi-section dashboard ✅ Can add without conflict

3. **API Client Pattern:**
   - Inner Edu: Direct Axios calls
   - IP-02: `pasBot.ts` centralized client ⚠️ Must refactor

### 3.3 IP-06: Reveal Mechanics Alignment

| Component | Inner Edu Status | IP-06 Requirement | Compatibility |
|-----------|------------------|-------------------|---------------|
| QuestEngine | ❌ Not in backend | Progressive reveal logic | 0% (must implement) |
| Quest Step System | ✅ YAML format supports | Step-by-step execution | 80% |
| Achievement System | ❌ Not implemented | AchievementPopup, ShareConsent | 0% (must add) |
| Privacy Settings | ❌ Not implemented | ChildPrivacySettings table | 0% (must add) |
| Telegram Notifications | ⚠️ Bot framework installed | Dual-parent notifications | 50% (framework ready) |

**Quest YAML Compatibility:**

Inner Edu YAML format **DOES NOT** include:
- ❌ Reveal phases (NEUTRAL, SUBTLE_CLUES, INVESTIGATION, REVEAL)
- ❌ Clue definitions (photo, location, joke, memory)
- ❌ Achievement definitions
- ❌ Parent notification triggers

**Extension Strategy:**
```yaml
# Add to existing YAML format
reveal_mechanics:
  enabled: true
  phases:
    - phase: NEUTRAL
      nodes: [1, 2, 3]
    - phase: SUBTLE_CLUES
      nodes: [4, 5, 6]
      clues:
        - type: PHOTO
          content: "family_photo_001.jpg"
          reveal_threshold: 0.4

achievements:
  - id: "polynomial_master"
    name: "Polynomial Equations Master"
    trigger_node: 5
    share_with_parents: true
```

---

## 4. Frontend Architecture Details

### 4.1 Component Structure

**AIQuestBuilder (index.tsx):**

**State Management (Hooks):**
```typescript
const [nodes, setNodes, onNodesChange] = useNodesState([]);
const [edges, setEdges, onEdgesChange] = useEdgesState([]);
const [messages, setMessages] = useState<Message[]>([]);
const [sessionId, setSessionId] = useState<string | null>(null);
const [currentStage, setCurrentStage] = useState<string>("greeting");
const [isLoading, setIsLoading] = useState(false);
```

**API Integration:**
```typescript
const response = await axios.post('/api/builder/chat', {
  user_id: userId,
  message: inputMessage,
  session_id: sessionId
});

// Response: { ai_response, session_id, stage, graph? }
```

**Layout:**
- Left Panel (350px): Chat interface
- Center Panel (flex): React Flow canvas
- Right Panel: Node editor (mentioned, not implemented)

**Missing Components (per IP-02):**
- ❌ Sidebar navigation
- ❌ Header with user info
- ❌ MultiTrackProgress visualization
- ❌ ProjectsGrid (for managing multiple quests)
- ❌ LetterManager
- ❌ Analytics dashboard

### 4.2 App.tsx Simplicity

```typescript
function App() {
  const [userId] = useState('test-user-123'); // Hardcoded!
  
  return (
    <div style={{ width: '100%', height: '100%' }}>
      <AIQuestBuilder userId={userId} />
    </div>
  );
}
```

**Implication:** Inner Edu frontend is a **single-purpose quest builder tool**, not a full application. IP-02 plans to transform this into a multi-section parent dashboard.

**Migration Path:**
1. Wrap AIQuestBuilder in ParentDashboard layout
2. Add routing (`/quests/builder`, `/letters`, `/analytics`)
3. Add authentication wrapper
4. Integrate PAS Bot API client

---

## 5. Database Schema Integration Strategy

### 5.1 Schema Merge Plan

**Option A: Shared Database, Separate Schemas**
```
postgres://
├── pas_schema/
│   ├── users (parents)
│   ├── sessions
│   ├── messages
│   ├── goals
│   └── letters
└── edu_schema/
    ├── quest_users (children)
    ├── quests
    ├── quest_progress
    └── quest_ratings
```

**Option B: Unified Schema (Recommended)**
```sql
-- Unified users table
CREATE TABLE users (
  id UUID PRIMARY KEY,
  telegram_id VARCHAR(100) UNIQUE,
  user_type VARCHAR(20), -- 'parent', 'child', 'both'
  
  -- PAS fields
  current_state VARCHAR(50),
  therapy_phase VARCHAR(50),
  emotional_score FLOAT,
  
  -- Inner Edu fields
  child_name VARCHAR(100),
  learning_profile JSONB,
  
  created_at TIMESTAMP
);

-- Parent-Child relationship
CREATE TABLE parent_child_relationships (
  id UUID PRIMARY KEY,
  parent_id UUID REFERENCES users(id),
  child_id UUID REFERENCES users(id),
  relationship_type VARCHAR(50), -- 'alienated', 'custodial'
  created_at TIMESTAMP
);

-- Quests (extended for PAS integration)
CREATE TABLE quests (
  id UUID PRIMARY KEY,
  author_id UUID REFERENCES users(id), -- parent who created
  child_id UUID REFERENCES users(id),   -- target child (optional)
  
  -- Existing fields
  title VARCHAR(200),
  graph_structure JSONB,
  yaml_content TEXT,
  
  -- IP-06 additions
  reveal_config JSONB,
  achievements JSONB,
  parent_notification_settings JSONB,
  
  moderation_status VARCHAR(20),
  created_at TIMESTAMP
);
```

### 5.2 Migration Sequence

1. **Phase 1:** Add `user_type` discriminator to existing PAS `users` table
2. **Phase 2:** Create `quest_users` table in PAS database
3. **Phase 3:** Add `parent_child_relationships` table
4. **Phase 4:** Import Inner Edu `quests` schema
5. **Phase 5:** Add IP-06 extensions (reveal_config, achievements)
6. **Phase 6:** Merge user authentication (single Telegram OAuth)

**Alembic Migration Required:** ✅ Both projects use Alembic

---

## 6. API Integration Points

### 6.1 Existing Inner Edu Endpoints → PAS Bot Usage

| Endpoint | Inner Edu Purpose | PAS Integration |
|----------|-------------------|-----------------|
| `POST /api/builder/chat` | AI quest creation | ✅ Use as-is, add auth middleware |
| `GET /api/quests/{id}` | Fetch quest details | ✅ Use in ParentDashboard |
| `POST /api/quests/load_yaml_quests` | Import YAML | ⚠️ Admin only, add auth |
| `POST /api/builder/refine_node` | AI node improvement | ✅ Use in quest editor |

### 6.2 New Endpoints Required (IP-01, IP-02)

**PAS Bot Backend (pas_in_peace/src/api/):**

```python
# web_endpoints.py (new file)

@router.post("/auth/telegram")
async def telegram_auth(auth_data: TelegramAuthData):
    """OAuth via Telegram, return JWT"""
    pass

@router.get("/tracks/progress")
async def get_track_progress(user: User = Depends(get_current_user)):
    """Multi-track recovery progress"""
    pass

@router.get("/projects")
async def get_projects(filters: ProjectFilters, user: User):
    """Unified view: quests + letters + goals"""
    pass

@router.post("/letters")
async def create_letter(letter_data: LetterCreate, user: User):
    """Letter writing (existing PAS functionality)"""
    pass

@router.get("/analytics/child-progress/{quest_id}")
async def get_child_progress(quest_id: UUID, user: User):
    """Aggregated child progress (IP-06)"""
    pass
```

**Integration Pattern:**
```
Frontend (Next.js)
  |
  | → /api/builder/* → Inner Edu backend (quest creation)
  | → /api/tracks/* → PAS Bot backend (recovery progress)
  | → /api/letters/* → PAS Bot backend (letter writing)
  | → /api/analytics/* → Shared analytics service
```

**Reverse Proxy Configuration (Nginx):**
```nginx
location /api/builder/ {
    proxy_pass http://inner_edu_backend:8000;
}

location /api/ {
    proxy_pass http://pas_bot_backend:8001;
}
```

---

## 7. Quest YAML Format Compatibility

### 7.1 Current Inner Edu Format → PAS Bot Generation

**QuestBuilderAssistant (PAS)** will generate quests in Inner Edu YAML format.

**Conversion Flow:**
```
User dialogue (PAS Bot)
  ↓
QuestBuilderAssistant collects context
  ↓
GPT-4 generates graph structure
  ↓
⚠️ graph_to_yaml() (MISSING IN INNER EDU)
  ↓
YAML saved to database
  ↓
Inner Edu app loads YAML for child
```

**Action Required:** Implement `graph_to_yaml()` in Inner Edu backend or PAS Bot.

**Implementation Options:**

**Option A:** Implement in Inner Edu (maintain ownership)
```python
# backend/quest_builder/agent.py

def graph_to_yaml(self, graph: QuestGraph) -> str:
    """Convert ReactFlow graph to Inner Edu YAML format"""
    
    yaml_dict = {
        "quest_id": f"pas_quest_{uuid.uuid4().hex[:8]}",
        "title": graph.title,
        "module": graph.metadata.get("psychological_module"),
        "location": graph.metadata.get("location"),
        "difficulty": graph.metadata.get("difficulty"),
        "steps": []
    }
    
    # Convert nodes to steps
    for node in graph.nodes:
        if node.type == "questStep":
            step = {
                "step_id": node.id,
                "type": node.data.get("step_type", "input_text"),
                "prompt": node.data.get("dialogue"),
                # ... mapping logic
            }
            yaml_dict["steps"].append(step)
    
    return yaml.dump(yaml_dict)
```

**Option B:** Implement in PAS Bot (full control)
- PAS generates YAML directly (bypass graph structure)
- Inner Edu receives YAML via API
- Less dependency on Inner Edu code

**Recommendation:** **Option A** - extend Inner Edu's existing converter to maintain consistency.

### 7.2 YAML Extensions for IP-06 (Reveal Mechanics)

**Required Additions:**
```yaml
# Extend existing YAML format

reveal_mechanics:
  enabled: true
  phases:
    - phase: NEUTRAL
      node_range: [1, 3]
    - phase: SUBTLE_CLUES
      node_range: [4, 6]
      clues:
        - clue_id: "photo_001"
          type: PHOTO
          content_url: "https://cdn.example.com/photos/family_001.jpg"
          hint: "Look at the background..."
    - phase: INVESTIGATION
      node_range: [7, 8]
      detective_mode: true
    - phase: REVEAL
      node_range: [9, 10]
      reveal_message: "Video message from parent"

achievements:
  - achievement_id: "first_level_complete"
    name: "First Steps"
    trigger_node: 3
    share_with_parents: false  # child consent required
  
  - achievement_id: "mystery_solved"
    name: "Detective Master"
    trigger_node: 10
    auto_share: true  # reveal moment

parent_notifications:
  enabled: true
  custodial_parent_id: "user_uuid"  # both parents
  alienated_parent_id: "user_uuid"
  message_template: "neutral"  # no manipulation language
```

**Backend Support Required:**
- RevealEngine class (IP-06) must parse these fields
- AchievementSystem must respect `share_with_parents` consent
- QuestEngine must track `current_phase` in `quest_progress` table

---

## 8. Potential Conflicts & Recommendations

### 8.1 Critical Conflicts

**1. Framework Mismatch: Vite vs Next.js**

**Inner Edu:** Vite + React (SPA)  
**IP-02 Plan:** Next.js 14 App Router (SSR)

**Impact:** High - routing, SSR, build system differences

**Recommendations:**
- **Option A:** Migrate Inner Edu to Next.js (2-3 days work, align with plan)
- **Option B:** Keep Vite, add React Router (faster, but misaligns with IP-02)
- **Option C:** Deploy separately, iframe integration (isolated but clunky)

**Best Choice:** **Option A** - migrate to Next.js for long-term consistency.

**2. User Model Conflict**

**Inner Edu:** `telegram_id` BigInteger  
**PAS Bot:** `telegram_id` String(100)

**Impact:** Medium - database type mismatch

**Recommendation:** Standardize on `String` (Telegram IDs can be 10-19 digits, String is safer).

**3. Authentication Gap**

**Inner Edu:** No auth (hardcoded user)  
**PAS Bot:** Session-based Telegram auth (but not OAuth)

**Impact:** High - must implement OAuth

**Recommendation:** Add Telegram OAuth middleware to both backends:
```python
# middleware/telegram_auth.py

from fastapi import Depends, HTTPException
from jose import jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY)
        user_id = payload.get("user_id")
        return await get_user(user_id)
    except:
        raise HTTPException(status_code=401)
```

### 8.2 Component Naming Conflicts

**None identified.** Inner Edu has minimal components; IP-02 plans to add new ones without overlap.

**Existing Inner Edu Components:**
- `AIQuestBuilder/index.tsx` → Keep, extend with `ConversationalMode.tsx`
- `AIQuestBuilder/QuestLibrary.tsx` → Keep, integrate into `ProjectsGrid`

**New Components (IP-02):**
- `UnifiedDashboard/` → No conflict
- `MultiTrackProgress/` → No conflict
- `LetterManager/` → No conflict
- `Analytics/` → No conflict

### 8.3 State Management Alignment

**Inner Edu:** Zustand (basic usage, local component state)  
**IP-02 Plan:** Zustand + React Query

**Compatibility:** ✅ Perfect alignment

**Action Required:** Install React Query, define stores:
```typescript
// stores/userStore.ts
export const useUserStore = create((set) => ({
  user: null,
  setUser: (user) => set({ user })
}));

// stores/projectsStore.ts
export const useProjectsStore = create((set) => ({
  quests: [],
  letters: [],
  goals: [],
  addQuest: (quest) => set((state) => ({
    quests: [...state.quests, quest]
  }))
}));
```

### 8.4 Database Connection Sharing

**Inner Edu:** Async PostgreSQL (asyncpg)  
**PAS Bot:** Sync PostgreSQL (psycopg2) + async support

**Recommendation:** Use asyncpg for both, share connection pool:
```python
# shared_db.py (new file in pas_in_peace)

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

engine = create_async_engine(
    f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"
)

async def get_db() -> AsyncSession:
    async with AsyncSession(engine) as session:
        yield session
```

---

## 9. Integration Recommendations

### 9.1 Safe Integration Strategy

**Phase 1: Database Layer (Week 1)**
1. ✅ Create unified schema design document
2. ✅ Write Alembic migrations (merge schemas)
3. ✅ Test migrations on staging database
4. ✅ Add `user_type` discriminator (`parent`/`child`)
5. ✅ Create `parent_child_relationships` table

**Phase 2: Backend API Gateway (Week 2)**
1. ✅ Implement Telegram OAuth (shared between backends)
2. ✅ Add authentication middleware to Inner Edu endpoints
3. ✅ Create reverse proxy (Nginx) for unified API
4. ✅ Implement `graph_to_yaml()` converter
5. ✅ Add ContentModerator integration to quest creation flow

**Phase 3: Frontend Migration (Week 3)**
1. ✅ Migrate Inner Edu frontend to Next.js 14
2. ✅ Add React Router or use Next.js App Router
3. ✅ Install React Query
4. ✅ Create `pasBot.ts` API client
5. ✅ Wrap AIQuestBuilder in ParentDashboard layout

**Phase 4: Unified Dashboard (Week 4)**
1. ✅ Implement UnifiedDashboard component
2. ✅ Add Sidebar, Header, QuickActions
3. ✅ Integrate MultiTrackProgress (fetch from PAS Bot)
4. ✅ Create ProjectsGrid (quests + letters + goals)
5. ✅ Add LetterManager (connect to PAS letter writing)

**Phase 5: Reveal Mechanics (Week 5)**
1. ✅ Extend YAML format (reveal_mechanics, achievements)
2. ✅ Implement RevealEngine class (IP-06)
3. ✅ Add RevealMechanics, ClueDetector, DetectiveLog components
4. ✅ Implement AchievementSystem backend
5. ✅ Create AchievementPopup, ShareConsent frontend

**Phase 6: Testing & Polish (Week 6)**
1. ✅ End-to-end test: parent creates quest → child plays → achievement shared
2. ✅ Test all 4 reveal phases
3. ✅ Test privacy consent flows
4. ✅ Performance optimization (API caching, bundle size)
5. ✅ Security audit (auth, moderation, PII protection)

### 9.2 Deployment Architecture

**Recommended Setup:**

```
┌─────────────────────────────────────────────────────────────┐
│                      Nginx Reverse Proxy                    │
│                  (SSL termination, routing)                 │
└─────────────────────────────────────────────────────────────┘
                             │
                ┌────────────┴────────────┐
                │                         │
        ┌───────▼───────┐         ┌──────▼──────┐
        │   Next.js     │         │  API Gateway│
        │  Frontend     │         │  (FastAPI)  │
        │ (Port 3000)   │         │  (Port 8000)│
        └───────────────┘         └──────┬──────┘
                                         │
                        ┌────────────────┼────────────────┐
                        │                │                │
                ┌───────▼────────┐ ┌────▼─────┐ ┌────────▼────────┐
                │ Inner Edu      │ │ PAS Bot  │ │ Shared Services │
                │ Quest Builder  │ │ Backend  │ │ (moderation,    │
                │ (FastAPI)      │ │(FastAPI) │ │  analytics)     │
                └────────────────┘ └──────────┘ └─────────────────┘
                        │                │                │
                        └────────────────┼────────────────┘
                                         │
                              ┌──────────▼──────────┐
                              │   PostgreSQL DB     │
                              │  (Unified Schema)   │
                              └─────────────────────┘
```

**Docker Compose Configuration:**
```yaml
services:
  frontend:
    image: nextjs-app
    ports: ["3000:3000"]
  
  api_gateway:
    image: api-gateway
    ports: ["8000:8000"]
    environment:
      - INNER_EDU_URL=http://inner_edu:8001
      - PAS_BOT_URL=http://pas_bot:8002
  
  inner_edu:
    image: inner-edu-backend
    ports: ["8001:8001"]
  
  pas_bot:
    image: pas-bot-backend
    ports: ["8002:8002"]
  
  postgres:
    image: postgres:15
    volumes: ["./data:/var/lib/postgresql/data"]
```

### 9.3 Feature Flag Strategy

**Environment Variables:**
```bash
# Feature flags (toggle during rollout)
QUEST_BUILDER_ENABLED=true
REVEAL_MECHANICS_ENABLED=false  # Phase 5
ACHIEVEMENT_SHARING_ENABLED=false  # Phase 5
DUAL_PARENT_NOTIFICATIONS=false  # Phase 5

# API endpoints
INNER_EDU_BACKEND_URL=http://localhost:8001
PAS_BOT_BACKEND_URL=http://localhost:8002

# Database
POSTGRES_URL=postgresql://user:pass@localhost:5432/unified_db
```

**Frontend Feature Flags (useFeatureFlags hook):**
```typescript
export const useFeatureFlags = () => {
  return {
    questBuilderEnabled: process.env.NEXT_PUBLIC_QUEST_BUILDER_ENABLED === 'true',
    revealMechanicsEnabled: process.env.NEXT_PUBLIC_REVEAL_MECHANICS_ENABLED === 'true',
    // ...
  };
};

// Usage
const { questBuilderEnabled } = useFeatureFlags();
{questBuilderEnabled && <AIQuestBuilder />}
```

---

## 10. Open Questions & Decisions Needed

### 10.1 Critical Decisions

1. **Monorepo or Separate Repos?**
   - Option A: Merge both into monorepo (`unified-platform/`)
   - Option B: Keep separate, share database + API gateway
   - **Recommendation:** Option B (phased integration, less risk)

2. **Next.js Migration Timeline?**
   - Migrate Inner Edu frontend now (aligns with IP-02)
   - Or keep Vite, add routing (faster but technical debt)
   - **Recommendation:** Migrate during Phase 3 (Week 3)

3. **Quest Ownership Model?**
   - Quests belong to parent (creator)?
   - Or separate "child account" with privacy?
   - **Recommendation:** Parent creates, child accesses via privacy-protected link

4. **Moderation Flow?**
   - Synchronous (block quest creation if toxic)?
   - Asynchronous (queue for review)?
   - **Recommendation:** Synchronous for PAS (prevent harmful content), async for minor edits

5. **WebSocket vs Polling for AI Dialogue?**
   - IP-02 specifies WebSocket
   - Inner Edu currently uses REST polling
   - **Recommendation:** Implement WebSocket in Phase 2 (better UX)

### 10.2 Technical Questions

1. How to handle quest versioning (parent edits after child starts)?
   - **Answer:** Create new version, keep child on old version until completion

2. Should custodial parent receive notifications even if blocking contact?
   - **Answer:** Yes (neutral educational framing), unless legal order prohibits

3. Rate limiting for quest creation (prevent abuse)?
   - **Answer:** 5 quests/hour per user (IP-01 spec)

4. Child privacy: what if child is under 13 (COPPA compliance)?
   - **Answer:** Parent consent required, no direct child data collection

---

## 11. Risk Assessment

### 11.1 High Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Schema migration data loss | Medium | Critical | Test on staging, backup production |
| Auth integration breaks existing PAS Bot | Medium | High | Feature flag, gradual rollout |
| Next.js migration delays timeline | High | Medium | Allocate extra week, or use Vite fallback |
| graph_to_yaml() conversion errors | High | High | Unit tests, validate against Inner Edu parser |
| Custodial parent identifies quest source | Medium | Critical | Neutral branding, delay reveal to 80%+ |

### 11.2 Medium Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Performance issues (N+1 queries) | Medium | Medium | Database indexing, API caching |
| WebSocket connection unstable | Medium | Medium | Fallback to polling, retry logic |
| Moderation false positives (block valid content) | Medium | Medium | Manual review queue, user feedback |
| CORS issues between frontends | Low | Medium | Nginx proxy, correct headers |

### 11.3 Low Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| React Flow version incompatibility | Low | Low | Pin versions in package.json |
| Timezone issues (notifications) | Low | Low | Store UTC, convert on client |
| Bundle size too large | Low | Low | Code splitting, lazy loading |

---

## 12. Conclusion & Next Steps

### 12.1 Summary

**Inner Edu is a solid foundation** for the unified PAS platform:
- ✅ Mature quest builder with AI generation
- ✅ React + TypeScript + Zustand (aligns with IP-02)
- ✅ PostgreSQL + SQLAlchemy (compatible with PAS)
- ⚠️ Missing authentication, routing, and reveal mechanics (planned in IP-01, IP-02, IP-06)

**Integration Feasibility:** **HIGH** (8.5/10)

**Critical Path:**
1. Implement `graph_to_yaml()` converter ← **BLOCKER**
2. Add Telegram OAuth ← **BLOCKER**
3. Migrate to Next.js or add routing ← **High Priority**
4. Merge database schemas ← **High Priority**
5. Implement reveal mechanics ← **Phase 5**

### 12.2 Immediate Action Items

**Week 1:**
- [ ] Clone Inner Edu repository to local environment
- [ ] Set up test database with merged schema
- [ ] Write Alembic migration for user model unification
- [ ] Implement `graph_to_yaml()` in Inner Edu backend

**Week 2:**
- [ ] Add JWT authentication middleware to Inner Edu API
- [ ] Create Nginx reverse proxy configuration
- [ ] Test PAS Bot ↔ Inner Edu API communication
- [ ] Implement WebSocket support for quest dialogue

**Week 3:**
- [ ] Migrate Inner Edu frontend to Next.js (or add React Router)
- [ ] Create ParentDashboard layout
- [ ] Build `pasBot.ts` API client
- [ ] Integrate AIQuestBuilder into dashboard

### 12.3 Success Metrics

**Technical:**
- [ ] All API endpoints respond < 2 seconds
- [ ] Quest creation success rate > 95%
- [ ] Zero authentication bypasses (security audit)
- [ ] Database migration with zero data loss

**User Experience:**
- [ ] Parent can create quest in < 15 minutes
- [ ] Child reveal mechanics work in 80%+ of quests
- [ ] Achievement sharing consent flow < 3 taps
- [ ] Both parents receive identical notifications

### 12.4 Final Recommendation

**Proceed with integration** following the 6-phase plan:

1. **Database Layer** (Week 1) - Low risk, high value
2. **API Gateway** (Week 2) - Medium risk, enables frontend work
3. **Frontend Migration** (Week 3) - High effort, aligns with plan
4. **Unified Dashboard** (Week 4) - User-facing value
5. **Reveal Mechanics** (Week 5) - Core PAS functionality
6. **Testing & Polish** (Week 6) - Quality assurance

**Total Estimated Timeline:** 6 weeks  
**Team Required:** 1 full-stack developer + 1 frontend specialist  
**Budget Impact:** Minimal (no new services, reuse infrastructure)

---

**Document Version:** 1.0  
**Last Updated:** 2025-11-09  
**Author:** Architecture Analysis Agent  
**Status:** Ready for Review
