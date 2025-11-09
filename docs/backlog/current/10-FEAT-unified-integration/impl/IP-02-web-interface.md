# Implementation Plan: Unified Web Interface

## Смысл и цель задачи

Создать единый веб-интерфейс где родитель управляет всеми аспектами recovery journey: письмами, квестами, целями, прогрессом по 4 трекам. Интерфейс должен быть удобнее Telegram бота для сложных задач (редактирование квестов, просмотр аналитики), но интегрироваться с ботом для быстрых уведомлений.

## Архитектура решения

### Структура компонентов

**Расположение в inner_edu репозитории**

```
frontend/src/
├── pages/
│   └── ParentDashboard.tsx          # Главная страница (новая)
├── components/
│   ├── UnifiedDashboard/            # Новая директория
│   │   ├── index.tsx               # Main dashboard layout
│   │   ├── Sidebar.tsx             # Навигация между секциями
│   │   ├── Header.tsx              # Топ-бар с user info
│   │   └── QuickActions.tsx        # Быстрые действия
│   ├── MultiTrackProgress/          # Новая директория
│   │   ├── TrackCard.tsx           # Карточка одного трека
│   │   ├── ProgressBar.tsx         # Визуализация прогресса
│   │   ├── MilestoneList.tsx       # Список достижений
│   │   └── NextActionSuggestion.tsx # AI рекомендации
│   ├── CreativeProjects/            # Новая директория
│   │   ├── ProjectsGrid.tsx        # Grid view всех проектов
│   │   ├── ProjectCard.tsx         # Карточка проекта
│   │   ├── FilterBar.tsx           # Фильтры по типу/статусу
│   │   └── CreateProjectModal.tsx  # Модал создания
│   ├── LetterManager/               # Новая директория
│   │   ├── LetterList.tsx          # Список писем
│   │   ├── LetterEditor.tsx        # Редактор письма
│   │   ├── LetterTypeSelector.tsx  # Выбор типа письма
│   │   └── LetterPreview.tsx       # Preview перед отправкой
│   ├── AIQuestBuilder/              # Существующий, расширить
│   │   ├── index.tsx               # Уже есть
│   │   ├── ConversationalMode.tsx  # Новый - AI диалог
│   │   └── ModerationStatus.tsx    # Новый - статус модерации
│   └── Analytics/                   # Новая директория
│       ├── EmotionalTrends.tsx     # График эмоций
│       ├── ChildProgress.tsx       # Прогресс ребенка (aggregated)
│       └── MetricsDashboard.tsx    # Общие метрики
└── api/
    └── pasBot.ts                    # API client для PAS Bot (новый)
```

### Ключевые паттерны

**State Management**
- Zustand для глобального state (user, tracks, projects)
- React Query для server state (API caching)
- Local storage для UI preferences

**Routing**
- Next.js App Router
- Protected routes (require auth)
- Deep linking для direct access к проектам

**Real-time updates**
- WebSocket для AI quest creation dialogue
- Polling для analytics updates (каждые 30 сек)

## Полный flow работы функционала

### User Journey: От входа до создания квеста

1. **Landing** - пользователь открывает app.innerworldedu.com/parent
2. **Auth** - кнопка "Войти через Telegram" -> OAuth flow
3. **Dashboard Load**:
   - Fetch user data с PAS Bot API
   - Fetch multi-track progress
   - Fetch recent projects
   - Render dashboard за <3s
4. **Explore Interface**:
   - Sidebar показывает секции: Dashboard, Projects, Analytics, Resources
   - Main area показывает 4 track cards с прогрессом
   - Quick actions: "Create Quest", "Write Letter", "Set Goal"
5. **Create Quest Flow**:
   - Клик "Create Quest" -> CreateProjectModal
   - Выбор "Educational Quest for Child"
   - Открывается ConversationalMode компонент
   - WebSocket connection к PAS Bot
   - AI задает вопросы, родитель отвечает
   - Real-time moderation feedback
   - Preview в React Flow
   - Finalize -> квест сохраняется
   - Redirect на Projects page с новым квестом highlighted
6. **Manage Projects**:
   - Grid view всех квестов и писем
   - Filters: "In Progress", "Completed", "Needs Moderation"
   - Клик на квест -> открывается в Quest Builder
   - Клик на письмо -> открывается Letter Editor
   - All changes auto-save каждые 10 секунд

## API и интерфейсы

### PAS Bot API Client (pasBot.ts)

**Authentication**
- `telegramAuth(authData)` - получить JWT token
- `refreshToken()` - обновить token

**Tracks**
- `getTrackProgress()` - получить прогресс по 4 трекам
- `updatePrimaryTrack(trackId)` - изменить главный фокус

**Projects**
- `getProjects(filters)` - список проектов с фильтрацией
- `getProject(id)` - детали проекта
- `createProject(type, data)` - создать новый проект
- `updateProject(id, changes)` - обновить проект
- `deleteProject(id)` - удалить проект

**Quest Builder**
- `startQuestCreation()` - инициализация WebSocket
- `sendQuestMessage(message)` - отправить сообщение AI
- `getQuestPreview(questId)` - получить YAML preview
- `exportQuest(questId)` - финализировать квест

**Letters**
- `getLetters()` - список писем
- `createLetter(type)` - создать новое письмо
- `updateLetter(id, content)` - обновить письмо
- `sendLetter(id)` - отправить письмо

**Analytics**
- `getEmotionalTrends(period)` - данные для графиков
- `getChildProgress(questId)` - aggregated прогресс ребенка

### React Components Props

**TrackCard**
- `track` - объект RecoveryTrack с progress, milestones
- `isPrimary` - boolean флаг
- `onSetPrimary` - callback для изменения фокуса

**ProjectCard**
- `project` - объект проекта (квест/письмо/цель)
- `onEdit` - callback для редактирования
- `onDelete` - callback для удаления
- `moderationStatus` - статус модерации

**ConversationalMode**
- `questId` - ID создаваемого квеста
- `onComplete` - callback когда квест готов
- `onCancel` - callback для отмены

## Взаимодействие компонентов

```
Browser
  |
  v
Next.js App (SSR)
  |
  +---> Auth Flow -> Telegram OAuth -> JWT Token
  |
  +---> ParentDashboard Page
        |
        v
    UnifiedDashboard Component
        |
        +---> Sidebar (navigation)
        |
        +---> MultiTrackProgress
        |       |
        |       +---> 4x TrackCard
        |
        +---> CreativeProjects
        |       |
        |       +---> ProjectsGrid
        |       |       |
        |       |       +---> Nx ProjectCard
        |       |
        |       +---> CreateProjectModal
        |               |
        |               +---> ConversationalMode (WebSocket)
        |
        +---> Analytics
                |
                +---> EmotionalTrends (Chart.js)
                |
                +---> ChildProgress

All components use:
  - PAS Bot API Client (REST + WebSocket)
  - React Query (caching)
  - Zustand (global state)
```

## Порядок реализации

### Step 1: Setup инфраструктуры (день 1)

1. Добавить pasBot.ts API client
2. Настроить Zustand stores (userStore, projectsStore, tracksStore)
3. Настроить React Query provider
4. Создать protected route HOC

### Step 2: Authentication (день 2)

1. Реализовать TelegramAuthButton компонент
2. OAuth flow с backend
3. JWT token management (storage, refresh)
4. Protected ParentDashboard page

### Step 3: Core Dashboard (дни 3-4)

1. UnifiedDashboard layout (sidebar + main area)
2. Sidebar navigation
3. Header с user info
4. Quick actions панель

### Step 4: Multi-Track Progress (дни 5-6)

1. TrackCard компонент
2. ProgressBar visualization
3. MilestoneList
4. NextActionSuggestion с AI подсказками
5. Track switching logic

### Step 5: Creative Projects (дни 7-8)

1. ProjectsGrid компонент
2. ProjectCard с разными типами
3. FilterBar для фильтрации
4. CreateProjectModal
5. Delete/Archive functionality

### Step 6: Quest Builder Integration (дни 9-11)

1. ConversationalMode компонент (WebSocket)
2. Message bubbles UI
3. Real-time moderation indicators
4. Integration с существующим AIQuestBuilder
5. Preview mode
6. Export flow

### Step 7: Letter Manager (дни 12-13)

1. LetterList компонент
2. LetterEditor (rich text)
3. LetterTypeSelector
4. Letter preview
5. Send/Save functionality

### Step 8: Analytics Dashboard (дни 14-15)

1. EmotionalTrends graph (Chart.js/Recharts)
2. ChildProgress aggregated view
3. MetricsDashboard overview
4. Export analytics feature

### Step 9: Polish & Responsive (дни 16-17)

1. Mobile responsive design
2. Loading states
3. Error handling UI
4. Toast notifications
5. Empty states

## Критичные граничные случаи

**WebSocket connection loss**
- Auto-reconnect с exponential backoff
- Показать "Reconnecting..." indicator
- Не терять введенные сообщения (queue)

**API errors**
- Graceful error messages (не показывать stack trace)
- Retry button для failed requests
- Offline mode detection

**Slow API responses**
- Skeleton loaders для всех компонентов
- Optimistic updates где возможно
- Timeout после 30 секунд

**Browser compatibility**
- Support Chrome, Firefox, Safari (last 2 versions)
- Fallback для WebSocket (long polling)

## Объем работ

### Входит в реализацию

- Unified dashboard layout
- Multi-track progress визуализация
- Creative projects management
- Quest Builder conversational UI
- Letter Manager UI
- Analytics dashboard
- Telegram OAuth integration
- WebSocket для real-time
- Responsive design (desktop + tablet)
- Error handling и loading states

### Не входит в MVP

- Mobile native apps
- Offline-first capabilities
- Advanced charts (только базовые)
- Video/audio content support
- Collaboration features (share with другим родителем)
- White-label customization
- Internationalization (только русский)

## Допущения

- Next.js 14 с App Router уже настроен в inner_edu
- Telegram OAuth endpoint доступен в PAS Bot
- WebSocket endpoint работает на том же домене (или CORS настроен)
- React Query может использовать JWT token из localStorage
- Chart library (Chart.js или Recharts) может быть добавлена

## Открытые вопросы

1. Какой chart library предпочесть - Chart.js или Recharts?
2. Нужна ли PWA поддержка для offline работы?
3. Как долго хранить JWT token - session only или persistent?
4. Нужен ли dark mode для интерфейса?
5. Где хостить frontend - Vercel, Netlify, или свой сервер?

## Acceptance Criteria

- Родитель может залогиниться через Telegram за <10 секунд
- Dashboard загружается за <3 секунды
- Все 4 трека показывают корректный прогресс
- Можно создать новый проект (квест/письмо) через UI
- Quest Builder dialogue работает real-time через WebSocket
- Moderation warnings показываются inline
- Можно редактировать существующие проекты
- Analytics graphs отображают данные корректно
- UI responsive на планшетах (768px+)
- Все actions логируются для debugging

## Definition of Done

- Все React компоненты покрыты TypeScript types
- API client типизирован
- Основные user flows протестированы вручную
- Error boundaries установлены для каждой major секции
- Loading states для всех async операций
- README с инструкциями по запуску frontend
- Environment variables documented
- Build проходит без warnings

## Минимальные NFR для MVP

**Производительность**
- Initial page load: <3s
- Time to interactive: <5s
- WebSocket latency: <500ms
- API response time: <2s (95th percentile)

**Надежность**
- Auto-save каждые 10 секунд
- WebSocket auto-reconnect
- Graceful degradation если API unavailable

**Браузеры**
- Chrome 100+
- Firefox 100+
- Safari 15+

## Требования безопасности

- JWT token в httpOnly cookie (если возможно) или secure localStorage
- CSRF protection для state-changing operations
- XSS sanitization для user content
- Content Security Policy headers
- No inline scripts
- HTTPS only
- Rate limiting на client side (prevent spam)

## Наблюдаемость

**Логи (browser console в dev)**
- API errors с request/response
- WebSocket connection status changes
- Component render errors

**Metrics (отправка в backend)**
- page_view (counter)
- quest_creation_started (counter)
- project_edited (counter)
- api_call_duration_ms (histogram)

**User Analytics**
- Track button clicks (anonymized)
- Track page views
- Track errors (Sentry)

## Релиз

**Feature Flags (environment variables)**
- `NEXT_PUBLIC_QUEST_BUILDER_ENABLED` - enable quest creation
- `NEXT_PUBLIC_ANALYTICS_ENABLED` - enable analytics tab
- `NEXT_PUBLIC_LETTER_MANAGER_ENABLED` - enable letter management

**Развертывание**
1. Vercel preview deployment для каждого PR
2. Staging: автоматический deploy на stage.innerworldedu.com
3. Production: manual trigger после QA approval

## Откат

**Условия отката**
- Critical bugs в auth flow
- WebSocket не работает для >50% users
- Performance degradation (>10s load time)

**Шаги отката**
1. Revert deployment в Vercel
2. Clear CDN cache
3. Уведомить users в Telegram боте
4. Fallback на Telegram bot для всех функций

## Риски и митигации

- **Риск 1**: WebSocket connection unstable - Митигация: fallback на polling, connection retry logic
- **Риск 2**: Frontend bundle слишком большой - Митигация: code splitting, lazy loading компонентов
- **Риск 3**: Chart library performance issues - Митигация: data downsampling, виртуализация
- **Риск 4**: Mobile UX плохой - Митигация: тестирование на реальных устройствах, responsive design system
- **Риск 5**: CORS issues с API - Митигация: правильная настройка headers, same-origin deployment

## Параметры стека

**Frontend**
- Next.js 14 (App Router)
- React 18
- TypeScript 5.0+
- Zustand (state management)
- React Query (server state)
- TailwindCSS (styling)
- Chart.js или Recharts (graphs)
- React Flow (quest visualization, уже есть)

**Development Tools**
- Vite или Next.js dev server
- ESLint + Prettier
- TypeScript strict mode

**Deployment**
- Vercel (рекомендуется для Next.js)
- или Docker + Nginx для self-hosting

## Самопроверка плана перед выдачей

- ✅ Нет кода (только описание)
- ✅ Заполнены все секции
- ✅ Именование файла: `IP-02-web-interface.md`
- ✅ Описаны существующие и новые компоненты
- ✅ Учтена интеграция с inner_edu
- ✅ Realistic timeline (17 дней)
