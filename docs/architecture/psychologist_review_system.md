# Psychologist Review System
**Система профессионального ревью квестов психологами**

> 🛡️ Цель: Убедиться, что квесты эмоционально безопасны и терапевтически корректны

---

## 🎯 Концепция

### Зачем нужен психолог?

1. **Emotional Safety**: Проверка на манипуляции, вину, давление
2. **Therapeutic Correctness**: Соответствие принципам IFS/ТРИЗ/CBT
3. **Age Appropriateness**: Подходит ли контент для возраста ребенка
4. **Reveal Timing**: Правильно ли выбраны моменты раскрытия
5. **Trust Badge**: Родители видят "Проверено психологом" → больше доверия

### Как это работает?

```
1. Родитель создает квест
2. Автоматическая модерация (ContentModerator)
3. [ОПЦИОНАЛЬНО] Запрос на психолог-ревью
4. Психолог проходит квест + дает фидбэк
5. Квест получает Badge "✅ Проверено психологом"
6. Фидбэк доступен создателю + сообществу
```

---

## 🏗️ Database Schema

### Новая таблица: psychologist_reviews

```sql
CREATE TABLE psychologist_reviews (
  id SERIAL PRIMARY KEY,

  -- Связи
  quest_id INTEGER NOT NULL REFERENCES quests(id) ON DELETE CASCADE,
  psychologist_id INTEGER NOT NULL REFERENCES users(id),
  parent_id INTEGER NOT NULL REFERENCES users(id),

  -- Статус ревью
  status VARCHAR(50) NOT NULL DEFAULT 'pending',
    -- pending, in_progress, completed, rejected

  -- Результаты
  overall_rating INTEGER CHECK (overall_rating >= 1 AND overall_rating <= 5),
    -- 1-5 звезд
  is_approved BOOLEAN DEFAULT FALSE,

  -- Детальная оценка
  emotional_safety_score INTEGER CHECK (emotional_safety_score >= 1 AND emotional_safety_score <= 5),
  therapeutic_correctness_score INTEGER CHECK (therapeutic_correctness_score >= 1 AND therapeutic_correctness_score <= 5),
  age_appropriateness_score INTEGER CHECK (age_appropriateness_score >= 1 AND age_appropriateness_score <= 5),
  reveal_timing_score INTEGER CHECK (reveal_timing_score >= 1 AND reveal_timing_score <= 5),

  -- Фидбэк
  feedback_text TEXT,
  strengths TEXT[],  -- Что хорошо
  improvements TEXT[], -- Что улучшить
  red_flags TEXT[],  -- Красные флаги (если есть)

  -- Метаданные
  playthrough_duration_minutes INTEGER,
  notes_for_parent TEXT,  -- Приватные заметки для родителя
  notes_for_community TEXT, -- Публичный отзыв

  -- Timestamps
  requested_at TIMESTAMP DEFAULT NOW(),
  started_at TIMESTAMP,
  completed_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),

  -- Индексы
  INDEX idx_quest_review (quest_id),
  INDEX idx_psychologist (psychologist_id),
  INDEX idx_status (status)
);
```

### Обновление таблицы quests

```sql
ALTER TABLE quests ADD COLUMN psychologist_reviewed BOOLEAN DEFAULT FALSE;
ALTER TABLE quests ADD COLUMN psychologist_review_id INTEGER REFERENCES psychologist_reviews(id);
ALTER TABLE quests ADD COLUMN psychologist_rating NUMERIC(2,1); -- Для быстрого доступа
```

---

## 🎖️ Psychologist Badge Component

### Visual Design

```tsx
interface PsychologistBadgeProps {
  review: PsychologistReview;
  variant?: 'compact' | 'detailed';
  showRating?: boolean;
}

const PsychologistBadge: React.FC<PsychologistBadgeProps> = ({
  review,
  variant = 'compact',
  showRating = true
}) => {
  if (!review || !review.is_approved) {
    return null; // Не показываем, если не одобрено
  }

  return (
    <div className="psychologist-badge">
      {/* Иконка */}
      <CheckShieldIcon className="psychologist-badge-icon" />

      {/* Текст */}
      <span className="psychologist-badge-text">
        {variant === 'compact' ? 'Проверено' : 'Проверено психологом'}
      </span>

      {/* Рейтинг (опционально) */}
      {showRating && (
        <div className="psychologist-badge-rating">
          <StarIcon filled />
          <span>{review.overall_rating}/5</span>
        </div>
      )}

      {/* Tooltip с деталями */}
      <Tooltip>
        <div className="p-4">
          <p className="font-semibold mb-2">Оценка психолога</p>
          <div className="space-y-1 text-sm">
            <div>🛡️ Эмоциональная безопасность: {review.emotional_safety_score}/5</div>
            <div>💚 Терапевтическая корректность: {review.therapeutic_correctness_score}/5</div>
            <div>👶 Соответствие возрасту: {review.age_appropriateness_score}/5</div>
            <div>🎭 Reveal механика: {review.reveal_timing_score}/5</div>
          </div>
          {review.notes_for_community && (
            <p className="mt-3 text-sm italic">
              "{review.notes_for_community}"
            </p>
          )}
        </div>
      </Tooltip>
    </div>
  );
};
```

### CSS (Liquid Glass Style)

```css
.psychologist-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;

  padding: 8px 14px;
  border-radius: 16px;

  background: linear-gradient(
    135deg,
    rgba(52, 199, 89, 0.15) 0%,
    rgba(52, 199, 89, 0.05) 100%
  );
  backdrop-filter: blur(10px);
  border: 1.5px solid var(--accent-success);

  font-size: 14px;
  font-weight: 500;
  color: var(--accent-success);

  cursor: help;
  transition: all 0.3s ease;

  /* Появление */
  animation: badge-appear 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.psychologist-badge:hover {
  background: linear-gradient(
    135deg,
    rgba(52, 199, 89, 0.25) 0%,
    rgba(52, 199, 89, 0.1) 100%
  );
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(52, 199, 89, 0.3);
}

.psychologist-badge-icon {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}

.psychologist-badge-rating {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-left: 4px;

  font-size: 13px;
  font-weight: 600;
}

@keyframes badge-appear {
  0% {
    opacity: 0;
    transform: scale(0.8) translateY(-10px);
  }
  60% {
    transform: scale(1.05) translateY(0);
  }
  100% {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}
```

---

## 🎮 Psychologist Dashboard

### Interface для психолога

```tsx
const PsychologistDashboard: React.FC = () => {
  const [reviews, setReviews] = useState<Review[]>([]);
  const [filter, setFilter] = useState<'pending' | 'in_progress' | 'completed'>('pending');

  return (
    <div className="p-8">
      <h1 className="heading-1 mb-8">Запросы на ревью</h1>

      {/* Фильтры */}
      <div className="flex gap-4 mb-6">
        <FilterButton
          active={filter === 'pending'}
          onClick={() => setFilter('pending')}
          count={reviews.filter(r => r.status === 'pending').length}
        >
          Ожидают
        </FilterButton>

        <FilterButton
          active={filter === 'in_progress'}
          onClick={() => setFilter('in_progress')}
          count={reviews.filter(r => r.status === 'in_progress').length}
        >
          В работе
        </FilterButton>

        <FilterButton
          active={filter === 'completed'}
          onClick={() => setFilter('completed')}
          count={reviews.filter(r => r.status === 'completed').length}
        >
          Завершены
        </FilterButton>
      </div>

      {/* Список квестов */}
      <div className="space-y-4">
        {reviews
          .filter(r => r.status === filter)
          .map(review => (
            <QuestReviewCard
              key={review.id}
              review={review}
              onStart={() => startReview(review.id)}
              onView={() => viewReview(review.id)}
            />
          ))}
      </div>
    </div>
  );
};
```

### Quest Review Card

```tsx
const QuestReviewCard: React.FC<{review: Review}> = ({review}) => {
  return (
    <div className="glass-card p-6 hover:shadow-lg transition-all">
      <div className="flex justify-between items-start">
        <div>
          <h3 className="heading-3">{review.quest.title}</h3>

          <div className="flex gap-4 mt-2 text-sm text-secondary">
            <span>👶 Возраст: {review.quest.child_age} лет</span>
            <span>📝 Заданий: {review.quest.total_nodes}</span>
            <span>⏱️ ~{review.quest.estimated_duration} мин</span>
          </div>

          <div className="mt-3">
            <span className="caption">Создатель:</span>
            <span className="body ml-2">
              Родитель #{review.parent_id}
            </span>
          </div>
        </div>

        {/* Статус */}
        <StatusBadge status={review.status} />
      </div>

      {/* Действия */}
      <div className="flex gap-3 mt-4">
        {review.status === 'pending' && (
          <button
            className="glass-button-primary"
            onClick={() => startReview(review.id)}
          >
            Начать ревью
          </button>
        )}

        {review.status === 'in_progress' && (
          <button
            className="glass-button-primary"
            onClick={() => continueReview(review.id)}
          >
            Продолжить
          </button>
        )}

        {review.status === 'completed' && (
          <button
            className="glass-button"
            onClick={() => viewReview(review.id)}
          >
            Посмотреть отчет
          </button>
        )}

        <button
          className="glass-button"
          onClick={() => previewQuest(review.quest_id)}
        >
          Предпросмотр квеста
        </button>
      </div>
    </div>
  );
};
```

---

## 📝 Review Form

### Форма для заполнения ревью

```tsx
const ReviewForm: React.FC<{questId: number}> = ({questId}) => {
  const [scores, setScores] = useState({
    emotional_safety: 0,
    therapeutic_correctness: 0,
    age_appropriateness: 0,
    reveal_timing: 0
  });

  const [feedback, setFeedback] = useState({
    strengths: [] as string[],
    improvements: [] as string[],
    red_flags: [] as string[],
    notes_for_parent: '',
    notes_for_community: ''
  });

  return (
    <div className="glass-card p-8">
      <h2 className="heading-2 mb-6">Оценка квеста</h2>

      {/* Шкалы оценки */}
      <div className="space-y-6">
        <RatingScale
          label="🛡️ Эмоциональная безопасность"
          description="Нет манипуляций, вины, давления"
          value={scores.emotional_safety}
          onChange={(v) => setScores({...scores, emotional_safety: v})}
        />

        <RatingScale
          label="💚 Терапевтическая корректность"
          description="Соответствует IFS/ТРИЗ/CBT принципам"
          value={scores.therapeutic_correctness}
          onChange={(v) => setScores({...scores, therapeutic_correctness: v})}
        />

        <RatingScale
          label="👶 Соответствие возрасту"
          description="Задания подходят для указанного возраста"
          value={scores.age_appropriateness}
          onChange={(v) => setScores({...scores, age_appropriateness: v})}
        />

        <RatingScale
          label="🎭 Reveal механика"
          description="Раскрытие создателя идет постепенно и безопасно"
          value={scores.reveal_timing}
          onChange={(v) => setScores({...scores, reveal_timing: v})}
        />
      </div>

      {/* Сильные стороны */}
      <div className="mt-8">
        <label className="body font-semibold mb-2 block">
          ✅ Что хорошо в этом квесте?
        </label>
        <TagInput
          tags={feedback.strengths}
          onChange={(tags) => setFeedback({...feedback, strengths: tags})}
          placeholder="Добавить сильную сторону..."
        />
      </div>

      {/* Что улучшить */}
      <div className="mt-6">
        <label className="body font-semibold mb-2 block">
          💡 Что можно улучшить?
        </label>
        <TagInput
          tags={feedback.improvements}
          onChange={(tags) => setFeedback({...feedback, improvements: tags})}
          placeholder="Добавить рекомендацию..."
        />
      </div>

      {/* Красные флаги (если есть) */}
      <div className="mt-6">
        <label className="body font-semibold mb-2 block text-accent-error">
          🚩 Красные флаги (критичные проблемы)
        </label>
        <TagInput
          tags={feedback.red_flags}
          onChange={(tags) => setFeedback({...feedback, red_flags: tags})}
          placeholder="Добавить проблему..."
          variant="error"
        />
      </div>

      {/* Заметки для родителя (приватно) */}
      <div className="mt-8">
        <label className="body font-semibold mb-2 block">
          📝 Заметки для создателя (приватно)
        </label>
        <textarea
          className="glass-input w-full h-32 resize-none"
          placeholder="Детальный фидбэк для родителя..."
          value={feedback.notes_for_parent}
          onChange={(e) => setFeedback({...feedback, notes_for_parent: e.target.value})}
        />
      </div>

      {/* Публичный отзыв */}
      <div className="mt-6">
        <label className="body font-semibold mb-2 block">
          💬 Публичный отзыв (видят все)
        </label>
        <textarea
          className="glass-input w-full h-24 resize-none"
          placeholder="Краткий отзыв для сообщества..."
          value={feedback.notes_for_community}
          onChange={(e) => setFeedback({...feedback, notes_for_community: e.target.value})}
          maxLength={280}
        />
        <p className="caption mt-1">
          {feedback.notes_for_community.length}/280 символов
        </p>
      </div>

      {/* Решение */}
      <div className="flex gap-4 mt-8">
        <button
          className="glass-button-primary flex-1"
          onClick={() => submitReview('approved')}
          disabled={!canApprove()}
        >
          ✅ Одобрить квест
        </button>

        <button
          className="glass-button flex-1"
          onClick={() => submitReview('rejected')}
        >
          ❌ Отклонить
        </button>
      </div>
    </div>
  );
};
```

### Rating Scale Component

```tsx
const RatingScale: React.FC<{
  label: string;
  description: string;
  value: number;
  onChange: (value: number) => void;
}> = ({label, description, value, onChange}) => {
  return (
    <div className="glass-card p-4">
      <div className="mb-3">
        <p className="body font-semibold">{label}</p>
        <p className="caption">{description}</p>
      </div>

      <div className="flex gap-2">
        {[1, 2, 3, 4, 5].map(score => (
          <button
            key={score}
            className={`
              glass-button w-12 h-12 rounded-full
              ${value === score ? 'bg-accent-primary text-white' : ''}
            `}
            onClick={() => onChange(score)}
          >
            {score}
          </button>
        ))}
      </div>

      {/* Подсказки */}
      <div className="flex justify-between mt-2 text-xs text-tertiary">
        <span>Низко</span>
        <span>Отлично</span>
      </div>
    </div>
  );
};
```

---

## 🔔 Notification System

### Уведомления для родителя

```tsx
// Когда психолог начал ревью
{
  type: 'psychologist_review_started',
  title: 'Ревью начато',
  message: 'Психолог начал проверку квеста "Тайна старого сада"',
  icon: <ClockIcon />,
  link: `/quests/${questId}/review`
}

// Когда ревью завершено
{
  type: 'psychologist_review_completed',
  title: 'Ревью завершено!',
  message: review.is_approved
    ? `Квест одобрен! Рейтинг: ${review.overall_rating}/5 ⭐`
    : 'Квест требует доработки. Смотрите фидбэк.',
  icon: review.is_approved ? <CheckIcon /> : <AlertIcon />,
  link: `/quests/${questId}/review`,
  priority: 'high'
}
```

---

## 📊 DatabaseManager Methods

### Новые методы для работы с ревью

```python
# src/storage/database.py

async def request_psychologist_review(
    self,
    quest_id: int,
    psychologist_id: int,
    parent_id: int
) -> PsychologistReview:
    """Создать запрос на ревью."""
    review = PsychologistReview(
        quest_id=quest_id,
        psychologist_id=psychologist_id,
        parent_id=parent_id,
        status='pending',
        requested_at=datetime.utcnow()
    )
    db_session.add(review)
    await db_session.commit()
    return review

async def get_pending_reviews(
    self,
    psychologist_id: int
) -> List[PsychologistReview]:
    """Получить ожидающие ревью для психолога."""
    result = await db_session.execute(
        select(PsychologistReview)
        .where(PsychologistReview.psychologist_id == psychologist_id)
        .where(PsychologistReview.status == 'pending')
        .order_by(PsychologistReview.requested_at.asc())
    )
    return result.scalars().all()

async def submit_psychologist_review(
    self,
    review_id: int,
    scores: Dict[str, int],
    feedback: Dict[str, Any],
    is_approved: bool
) -> PsychologistReview:
    """Отправить завершенное ревью."""
    review = await db_session.get(PsychologistReview, review_id)

    review.status = 'completed'
    review.completed_at = datetime.utcnow()
    review.is_approved = is_approved

    # Scores
    review.emotional_safety_score = scores['emotional_safety']
    review.therapeutic_correctness_score = scores['therapeutic_correctness']
    review.age_appropriateness_score = scores['age_appropriateness']
    review.reveal_timing_score = scores['reveal_timing']

    # Overall rating (среднее)
    review.overall_rating = sum(scores.values()) // len(scores)

    # Feedback
    review.strengths = feedback['strengths']
    review.improvements = feedback['improvements']
    review.red_flags = feedback['red_flags']
    review.notes_for_parent = feedback['notes_for_parent']
    review.notes_for_community = feedback['notes_for_community']

    await db_session.commit()

    # Обновить квест
    if is_approved:
        quest = await db_session.get(Quest, review.quest_id)
        quest.psychologist_reviewed = True
        quest.psychologist_review_id = review.id
        quest.psychologist_rating = review.overall_rating
        await db_session.commit()

    return review

async def get_quest_review(
    self,
    quest_id: int
) -> Optional[PsychologistReview]:
    """Получить ревью для квеста."""
    result = await db_session.execute(
        select(PsychologistReview)
        .where(PsychologistReview.quest_id == quest_id)
        .where(PsychologistReview.status == 'completed')
        .order_by(PsychologistReview.completed_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()
```

---

## 🌐 Community Features

### Quest Gallery с фильтром "Проверено психологом"

```tsx
const QuestGallery: React.FC = () => {
  const [filter, setFilter] = useState({
    psychologistReviewed: false,
    minRating: 0,
    ageRange: [7, 12]
  });

  return (
    <div>
      {/* Фильтры */}
      <div className="glass-card p-4 mb-6">
        <div className="flex gap-4 items-center">
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={filter.psychologistReviewed}
              onChange={(e) => setFilter({...filter, psychologistReviewed: e.target.checked})}
            />
            <span className="body">Только проверенные психологом</span>
          </label>

          <select
            className="glass-input"
            value={filter.minRating}
            onChange={(e) => setFilter({...filter, minRating: +e.target.value})}
          >
            <option value={0}>Любой рейтинг</option>
            <option value={4}>⭐ 4+</option>
            <option value={5}>⭐ 5</option>
          </select>
        </div>
      </div>

      {/* Квесты */}
      <div className="grid grid-cols-3 gap-6">
        {quests
          .filter(q => !filter.psychologistReviewed || q.psychologist_reviewed)
          .filter(q => !filter.minRating || q.psychologist_rating >= filter.minRating)
          .map(quest => (
            <QuestCard key={quest.id} quest={quest} />
          ))}
      </div>
    </div>
  );
};
```

---

## 📈 Analytics & Metrics

### Для психолога

```typescript
interface PsychologistStats {
  total_reviews: number;
  completed_reviews: number;
  average_rating_given: number;
  approval_rate: number; // % одобренных квестов
  average_review_time_hours: number;
}
```

### Для родителей

```typescript
interface QuestWithReview {
  quest: Quest;
  review?: PsychologistReview;
  community_rating?: number; // От других родителей
}
```

---

## 🚀 Implementation Plan

### Week 1: Database & Backend
- [ ] Create psychologist_reviews table
- [ ] Add DatabaseManager methods
- [ ] Update Quest model
- [ ] API endpoints for reviews

### Week 2: Psychologist Dashboard
- [ ] Dashboard UI
- [ ] Quest preview
- [ ] Review form
- [ ] Submit review

### Week 3: Parent Integration
- [ ] Request review button
- [ ] View review results
- [ ] Psychologist Badge component
- [ ] Notification system

### Week 4: Community Features
- [ ] Quest gallery with filter
- [ ] Public reviews display
- [ ] Rating aggregation
- [ ] Analytics dashboard

---

## 💡 Future Enhancements

1. **Psychologist Marketplace**: Родители выбирают психолога
2. **Paid Reviews**: Премиум ревью за деньги
3. **Video Feedback**: Психолог записывает видео-фидбэк
4. **Group Reviews**: Несколько психологов проверяют сложный квест
5. **AI Pre-Review**: GPT предварительно оценивает перед психологом

---

**Status**: 🚧 Ready for Implementation
**Dependencies**: Phase 4.2 (Database), Phase 4.3 (UI Components)
**Priority**: MEDIUM-HIGH (важно для доверия)
