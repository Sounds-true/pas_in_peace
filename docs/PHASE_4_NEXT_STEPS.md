# Phase 4 Next Steps - Action Plan

**Date**: 2025-11-10
**Session**: Post-merge verification
**Status**: 🟡 Dependencies installing, planning next steps

---

## ✅ Completed This Session

### 1. Environment Setup ✅
- [x] OpenAI API key configured in `.env`
- [x] inner_edu repository cloned to `/home/user/inner_edu`
- [x] Dependencies installation started (torch, transformers - in progress)

### 2. Repository Structure Analysis ✅

#### pas_in_peace (Backend 100% complete)
- All Phase 4.1, 4.2, 4.3 backend code implemented
- Graph ↔ YAML converters ready
- ContentModerator with AI integration
- Integration tests created
- Migrations ready to apply

#### inner_edu (Separate educational platform)
**Structure**:
```
/home/user/inner_edu/
├── backend/
│   ├── api/
│   ├── quest_builder/
│   ├── moderation/
│   └── database/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── AIQuestBuilder/ (index.tsx, QuestLibrary.tsx)
│   │   ├── types/
│   │   └── styles/
│   ├── vite.config.ts
│   └── package.json
├── src/                # Telegram bot modules
│   ├── bot/
│   ├── core/
│   ├── game/
│   └── orchestration/
└── docs/
    └── modules/        # 23 психологических модулей
```

**Key Finding**: ❌ **Liquid Glass components NOT found in inner_edu**

This confirms our analysis: Frontend Phase 4.3 = 0% (needs to be created)

---

## 📊 Current Status Summary

### pas_in_peace Backend: ✅ 100%

**Phase 4.1**: Database Layer ✅
- 6 models + User extensions
- Privacy enforcement
- Migrations ready

**Phase 4.2**: Backend Core ✅
- MultiTrackManager (4 tracks, 4 phases)
- QuestBuilderAssistant (6-stage FSM)
- ContentModerator (pattern + AI)

**Phase 4.3 Backend**: inner_edu Integration ✅
- Quest Builder Agent
- Graph ↔ YAML converters
- API endpoints
- Integration tests

### inner_edu Frontend: ❌ 0%

**Missing**:
- Liquid Glass component library (5 components)
- React Flow mind map integration
- Voice-First UI components
- Psychologist Review Dashboard
- Public Marketplace UI
- Privacy Consent UI

---

## 🎯 Immediate Next Steps

### Step 1: Finish Dependency Installation ⏳
**Status**: In progress (torch ~4GB, transformers ~2GB)

**ETA**: 5-10 minutes

**When complete**:
```bash
pip list | grep -E "torch|transformers|langchain"
```

---

### Step 2: Apply Database Migrations ⚠️ CRITICAL

**Prerequisites**:
- PostgreSQL running
- DATABASE_URL configured

**Commands**:
```bash
cd /home/user/pas_in_peace

# Check current state
alembic current

# Show pending migrations
alembic history

# Apply all migrations
alembic upgrade head

# Verify
alembic current
# Should show: phase_4_3_integration (head)
```

**Expected Result**:
- 6 new tables created (psychologist_reviews, quest_builder_sessions, etc.)
- Quest table extended (graph_structure, psychological_module, etc.)
- User table extended (mode, parent_name, learning_profile)

---

### Step 3: Run Integration Tests

**Basic smoke test**:
```bash
cd /home/user/pas_in_peace

# Run our new integration tests
pytest tests/integration/test_quest_creation_flow.py -v

# Run multi-track tests
pytest tests/integration/test_multi_track_integration.py -v
```

**Full test suite**:
```bash
# Run all integration tests
pytest tests/integration/ -v

# Run with coverage
pytest tests/integration/ -v --cov=src --cov-report=html
```

**Expected Results**:
- Graph to YAML conversion tests pass
- Quest creation E2E flow passes
- Multi-track integration tests pass
- Content moderation tests pass

---

### Step 4: Manual Testing with OpenAI API

**Test Quest Builder Assistant**:
```python
# Create test_quest_manual.py
import asyncio
from src.techniques.quest_builder import QuestBuilderAssistant
from src.storage.database import DatabaseManager
from src.safety.content_moderator import ContentModerator

async def test_manual():
    db = DatabaseManager()
    await db.initialize()

    moderator = ContentModerator()
    quest_builder = QuestBuilderAssistant(
        db_manager=db,
        content_moderator=moderator
    )

    context = {"user_id": 1, "quest_context": None}

    # Stage 1: Initial
    result = await quest_builder.apply(
        user_message="Хочу создать квест для дочери",
        context=context
    )
    print(f"Bot: {result.response}")

    # Stage 2: Gathering info
    result = await quest_builder.apply(
        user_message="Маша, 9 лет, любит математику и котов",
        context=context
    )
    print(f"Bot: {result.response}")

    # Continue conversation...

asyncio.run(test_manual())
```

**Run**:
```bash
python test_quest_manual.py
```

**Expected**: Real GPT-4 calls, quest generation

---

## 🚀 Short-Term Goals (This Week)

### Goal 1: Backend Deployment Ready ✅

**Tasks**:
- [x] Code complete
- [ ] Migrations applied
- [ ] Tests passing
- [ ] Manual E2E test successful
- [ ] API endpoints verified

**ETA**: 2-4 hours after dependencies installed

---

### Goal 2: Frontend Development Plan 📝

**Create Liquid Glass Components** (as described in PR):

#### Component 1: GlassButton
```typescript
// /home/user/inner_edu/frontend/src/components/LiquidGlass/GlassButton.tsx

interface GlassButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  variant?: 'primary' | 'secondary';
  size?: 'sm' | 'md' | 'lg';
}

export const GlassButton: React.FC<GlassButtonProps> = ({...}) => {
  return (
    <button
      className="glass-button"
      style={{
        background: 'rgba(255, 255, 255, 0.05)',
        backdropFilter: 'blur(20px)',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        boxShadow: '0 8px 32px rgba(0, 0, 0, 0.12)',
        borderRadius: '12px',
        padding: '12px 24px',
        color: '#fff',
        cursor: 'pointer',
        transition: 'all 0.3s ease'
      }}
      onClick={onClick}
    >
      {children}
    </button>
  );
};
```

#### Component 2: VoiceWaveButton ⭐
```typescript
// Voice-First PRIMARY interaction button with animated waves

import { useEffect, useRef } from 'react';

export const VoiceWaveButton = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  // Canvas animation for voice waves
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    // ... animated wave logic
  }, []);

  return (
    <button className="voice-wave-button">
      <canvas ref={canvasRef} width={80} height={80} />
      <MicrophoneIcon />
    </button>
  );
};
```

#### Components 3-5:
- **GlassCard** - Frosted glass container
- **GlassPanel** - Side panel with gradient
- **ProgressRing** - Circular progress

**Design System** (theme.ts):
```typescript
export const liquidGlassTheme = {
  glass: {
    background: 'rgba(255, 255, 255, 0.05)',
    border: 'rgba(255, 255, 255, 0.1)',
    blur: 'blur(20px)',
    shadow: '0 8px 32px rgba(0, 0, 0, 0.12)'
  },
  voice: {
    primary: '#00A8E8',
    glow: 'rgba(0, 168, 232, 0.4)'
  }
};
```

**ETA**: 2-3 days to create all 5 components

---

### Goal 3: React Flow Integration

**Install dependencies**:
```bash
cd /home/user/inner_edu/frontend
npm install reactflow @xyflow/react
```

**Create MindMapEditor component**:
```typescript
// src/components/QuestMindMap/index.tsx

import ReactFlow, {
  Node, Edge, Controls, Background
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

export const QuestMindMapEditor = () => {
  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);

  return (
    <div style={{ width: '100%', height: '600px' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        fitView
      >
        <Controls />
        <Background />
      </ReactFlow>
    </div>
  );
};
```

**ETA**: 1-2 days

---

## 🎯 Mid-Term Goals (Next 2 Weeks)

### Goal 4: Voice-First UI Implementation

**Web Speech API Integration**:
```typescript
// src/hooks/useVoiceInput.ts

export const useVoiceInput = () => {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');

  const recognition = new (window.SpeechRecognition ||
    window.webkitSpeechRecognition)();

  recognition.lang = 'ru-RU';
  recognition.continuous = false;

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    setTranscript(transcript);
  };

  const startListening = () => {
    setIsListening(true);
    recognition.start();
  };

  return { isListening, transcript, startListening };
};
```

**Whisper API Fallback**:
```typescript
// For better accuracy, fallback to OpenAI Whisper

const transcribeAudio = async (audioBlob: Blob) => {
  const formData = new FormData();
  formData.append('file', audioBlob, 'audio.webm');
  formData.append('model', 'whisper-1');

  const response = await fetch('https://api.openai.com/v1/audio/transcriptions', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${OPENAI_API_KEY}`
    },
    body: formData
  });

  const result = await response.json();
  return result.text;
};
```

**ETA**: 3-4 days

---

### Goal 5: Connect Frontend to Backend

**API Client Setup**:
```typescript
// src/api/questBuilder.ts

const API_BASE = 'http://localhost:8000';

export const questBuilderAPI = {
  async sendMessage(sessionId: string, message: string) {
    const response = await fetch(`${API_BASE}/api/quest-builder/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, message })
    });
    return response.json();
  },

  async getSession(sessionId: string) {
    const response = await fetch(`${API_BASE}/api/quest-builder/session/${sessionId}`);
    return response.json();
  },

  async generateGraph(sessionId: string) {
    const response = await fetch(`${API_BASE}/api/quest-builder/generate_graph`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId })
    });
    return response.json();
  }
};
```

**WebSocket Integration** (optional for real-time):
```typescript
// For real-time updates during quest generation

const ws = new WebSocket('ws://localhost:8000/ws/quest-builder');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'graph_update') {
    setNodes(data.nodes);
    setEdges(data.edges);
  }
};
```

**ETA**: 2-3 days

---

## 🎯 Long-Term Goals (Weeks 3-4)

### Goal 6: Psychologist Review Dashboard

**Features**:
- List of pending quests
- 4-scale rating system (emotional safety, therapeutic correctness, age appropriateness, reveal timing)
- Approval/rejection workflow
- Feedback text areas

**Components**:
- `ReviewList.tsx`
- `ReviewCard.tsx`
- `RatingScale.tsx` (1-5 stars)
- `FeedbackForm.tsx`

**ETA**: 3-4 days

---

### Goal 7: Public Marketplace

**Features**:
- Browse approved quests
- Filter by: psychological_module, age_range, location, rating
- Search by title/description
- Add to personal library
- Rate quests (1-5 stars)

**Components**:
- `QuestMarketplace.tsx`
- `QuestCard.tsx`
- `FilterPanel.tsx`
- `SearchBar.tsx`

**ETA**: 3-4 days

---

### Goal 8: Privacy Consent UI

**Features**:
- Child consent flow (age-appropriate language)
- Parent notification settings
- Granular sharing controls (completion %, achievements, play frequency)
- Audit trail visualization

**Components**:
- `ConsentFlow.tsx` - Step-by-step wizard
- `PrivacyDashboard.tsx` - Settings overview
- `NotificationSettings.tsx` - Parent notifications

**ETA**: 2-3 days

---

## 📈 Success Metrics

### Phase 4 Backend Completion
- [x] All code written
- [ ] Migrations applied
- [ ] Tests passing (target: 100%)
- [ ] Manual E2E test successful
- [ ] API endpoints verified
- [ ] Documentation complete

### Phase 4 Frontend Completion (Target)
- [ ] Liquid Glass components (5/5)
- [ ] React Flow integration
- [ ] Voice-First UI working
- [ ] Backend API connected
- [ ] Psychologist Review Dashboard
- [ ] Public Marketplace
- [ ] Privacy Consent UI

**Overall Target**: 2-4 weeks for full Phase 4 completion

---

## 🚧 Blockers & Risks

### Current Blockers
1. ⏳ **Dependencies installation** - In progress (~5-10 min remaining)
2. ⚠️ **PostgreSQL** - May need to start/configure database
3. ⚠️ **Database migrations** - Need to apply before testing

### Potential Risks
1. **OpenAI API rate limits** - Monitor usage during testing
2. **Database connection** - May need Docker Compose for PostgreSQL
3. **Frontend build issues** - inner_edu may need npm install

---

## 💡 Recommendations

### Immediate Priority
1. ✅ Wait for pip install to complete
2. ⚡ Start PostgreSQL (if not running)
3. ⚡ Apply migrations
4. ⚡ Run integration tests
5. ⚡ Manual E2E test with real OpenAI

### Short-Term Focus
- **This week**: Backend deployment ready
- **Next week**: Start Liquid Glass components

### Long-Term Strategy
- Frontend development in parallel with backend deployment
- Iterative releases: MVP → Features → Polish
- User testing with real parents/children (small group)

---

## 📚 Documentation Needed

### Technical Docs
- [ ] API documentation (OpenAPI/Swagger)
- [ ] Quest Builder user guide
- [ ] Psychologist review guidelines
- [ ] Privacy policy updates

### User Guides
- [ ] Parent: How to create a quest
- [ ] Child: How to play quests
- [ ] Psychologist: Review process

---

**Status**: Ready to proceed with migrations and testing once dependencies complete!

**Next Action**: Monitor pip install → Apply migrations → Run tests

