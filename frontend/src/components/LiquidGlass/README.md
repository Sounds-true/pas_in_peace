# Liquid Glass Components

Красивые, дружелюбные UI компоненты с glass morphism дизайном для платформы PAS in Peace.

## Компоненты

### 1. QuestCard

Карточка квеста с эффектом матового стекла.

**Использование:**

```tsx
import { QuestCard } from '@/components/LiquidGlass';

<QuestCard
  questId="quest_001"
  title="Тайна зоопарка"
  description="Особенное приключение для Маши"
  childName="Маша"
  childAge={9}
  progress={45}
  status="active"
  nodeCount={6}
  lastUpdated={new Date()}
  onClick={() => console.log('Quest clicked!')}
/>
```

**Props:**

- `questId` - уникальный ID квеста
- `title` - название квеста
- `description` - описание (опционально)
- `childName` - имя ребёнка
- `childAge` - возраст ребёнка (1-5 сердечек)
- `progress` - прогресс 0-100
- `status` - статус: 'draft' | 'active' | 'completed' | 'moderation'
- `nodeCount` - количество шагов в квесте
- `lastUpdated` - дата последнего обновления
- `onClick` - callback при клике

**Визуальные особенности:**

- ✨ Glass morphism эффект
- 🎨 Градиенты зависят от статуса
- ❤️ Сердечки показывают возраст ребёнка
- 📊 Анимированный progress bar с shimmer эффектом
- 🌟 Hover анимация

---

### 2. ProgressRing

Круговой индикатор прогресса.

**Использование:**

```tsx
import { ProgressRing } from '@/components/LiquidGlass';

<ProgressRing
  progress={75}
  size={120}
  strokeWidth={8}
  color="#60a5fa"
  label="Завершено"
  showPercentage={true}
  animated={true}
/>
```

**Props:**

- `progress` - прогресс 0-100
- `size` - диаметр в пикселях (по умолчанию 120)
- `strokeWidth` - толщина кольца (по умолчанию 8)
- `color` - цвет прогресса
- `glowColor` - цвет свечения
- `label` - текст под процентами
- `showPercentage` - показывать проценты (по умолчанию true)
- `animated` - анимировать прогресс (по умолчанию true)

**Специальные эффекты:**

- ✨ Sparkle эффект при 100%
- 💫 Glow эффект при завершении
- 🎯 Плавная анимация

---

### 3. MultiProgressRing

Концентрические кольца для отображения нескольких треков.

**Использование:**

```tsx
import { MultiProgressRing } from '@/components/LiquidGlass';

<MultiProgressRing
  tracks={[
    { id: 'self', name: 'Работа над собой', progress: 65, color: '#60a5fa' },
    { id: 'child', name: 'Связь с ребёнком', progress: 45, color: '#a78bfa' },
    { id: 'negotiation', name: 'Переговоры', progress: 30, color: '#f472b6' },
    { id: 'community', name: 'Сообщество', progress: 50, color: '#34d399' },
  ]}
  size={200}
/>
```

**Props:**

- `tracks` - массив треков с:
  - `id` - уникальный ID
  - `name` - название трека
  - `progress` - прогресс 0-100
  - `color` - цвет трека
- `size` - размер компонента (по умолчанию 200)

**Визуальные особенности:**

- 🎨 4 концентрических кольца
- 🌈 Каждый трек свой цвет
- 📊 Легенда под кольцами
- ⏱️ Последовательная анимация треков

---

### 4. VoiceWave

Визуализация голосового ввода.

**Использование:**

```tsx
import { VoiceWave } from '@/components/LiquidGlass';

<VoiceWave
  isRecording={isRecording}
  amplitude={audioAmplitude}
  onToggleRecording={() => setIsRecording(!isRecording)}
  disabled={false}
/>
```

**Props:**

- `isRecording` - идёт ли запись
- `amplitude` - амплитуда звука 0-1
- `onToggleRecording` - callback при клике на микрофон
- `disabled` - отключить кнопку

**Визуальные особенности:**

- 🎤 20 анимированных баров
- 🔴 REC индикатор
- 💫 Pulse эффект при записи
- 🌊 Органичная idle анимация

---

### 5. CompactVoiceWave

Компактная версия для inline использования.

**Использование:**

```tsx
import { CompactVoiceWave } from '@/components/LiquidGlass';

<CompactVoiceWave
  isActive={isListening}
  size="md"
/>
```

**Props:**

- `isActive` - активна ли визуализация
- `size` - размер: 'sm' | 'md' | 'lg'

---

### 6. VoiceVisualizer

Круговая визуализация голоса с liquid эффектом.

**Использование:**

```tsx
import { VoiceVisualizer } from '@/components/LiquidGlass';

<VoiceVisualizer
  amplitude={audioAmplitude}
  size={100}
/>
```

**Props:**

- `amplitude` - амплитуда 0-1
- `size` - размер в пикселях

**Визуальные особенности:**

- 🌊 Жидкая анимация
- 🎨 Радиальный градиент
- ✨ Glow эффект

---

## Установка зависимостей

```bash
cd frontend
npm install
```

Требуемые пакеты:
- `framer-motion` - анимации
- `lucide-react` - иконки
- `tailwindcss` - стили

---

## TailwindCSS Configuration

Добавьте в `tailwind.config.js`:

```js
module.exports = {
  theme: {
    extend: {
      backdropBlur: {
        xs: '2px',
      },
      animation: {
        shimmer: 'shimmer 2s infinite',
      },
      keyframes: {
        shimmer: {
          '0%': { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(100%)' },
        },
      },
    },
  },
  plugins: [],
};
```

---

## Примеры использования

### Dashboard с треками

```tsx
import { MultiProgressRing, QuestCard } from '@/components/LiquidGlass';

export default function Dashboard() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-8">
      <div className="max-w-6xl mx-auto">
        {/* Multi-track progress */}
        <div className="flex justify-center mb-12">
          <MultiProgressRing
            tracks={[
              { id: 'self', name: 'Работа над собой', progress: 65, color: '#60a5fa' },
              { id: 'child', name: 'Связь с ребёнком', progress: 45, color: '#a78bfa' },
              { id: 'negotiation', name: 'Переговоры', progress: 30, color: '#f472b6' },
              { id: 'community', name: 'Сообщество', progress: 50, color: '#34d399' },
            ]}
            size={240}
          />
        </div>

        {/* Quest cards grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <QuestCard
            questId="quest_001"
            title="Тайна зоопарка"
            description="Приключение про жирафов и котиков"
            childName="Маша"
            childAge={9}
            progress={45}
            status="active"
            nodeCount={6}
          />
          {/* More cards... */}
        </div>
      </div>
    </div>
  );
}
```

### Voice interface

```tsx
import { VoiceWave } from '@/components/LiquidGlass';
import { useState } from 'react';

export default function VoiceInterface() {
  const [isRecording, setIsRecording] = useState(false);
  const [amplitude, setAmplitude] = useState(0);

  const handleToggle = () => {
    setIsRecording(!isRecording);
    // Start/stop audio capture...
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 to-purple-900 flex items-center justify-center p-8">
      <VoiceWave
        isRecording={isRecording}
        amplitude={amplitude}
        onToggleRecording={handleToggle}
      />
    </div>
  );
}
```

---

## Дизайн-система

### Цветовая палитра

**Primary (Blue-Purple)**
- `from-blue-500/20 to-purple-500/20` - основной градиент
- `border-blue-400/30` - границы

**Status colors**
- Draft: `from-slate-500/20`
- Active: `from-blue-500/20`
- Completed: `from-green-500/20`
- Moderation: `from-amber-500/20`

**Glass effect**
- `backdrop-blur-xl` - матовое стекло
- `backdrop-saturate-150` - насыщенность
- `bg-white/10` - полупрозрачный фон

### Типография

- Заголовки: `font-bold text-white`
- Текст: `text-white/70`
- Метаданные: `text-white/50 text-xs`

### Анимации

- Hover: `scale: 1.02, y: -4`
- Tap: `scale: 0.98`
- Duration: `0.3s` для UI, `1-2s` для progress

---

## Accessibility

Все компоненты поддерживают:
- ✅ Keyboard navigation
- ✅ ARIA labels
- ✅ Focus states
- ✅ Screen readers (через semantic HTML)

---

## Performance

Оптимизации:
- 🚀 Framer Motion с hardware acceleration
- 🎯 React.memo для предотвращения rerenders
- 💾 CSS containment для изоляции layouts
- ⚡ Lazy loading для тяжёлых компонентов

---

## Browser Support

- Chrome 100+
- Firefox 100+
- Safari 15+
- Edge 100+

Требуется поддержка:
- CSS `backdrop-filter`
- SVG animations
- CSS Grid/Flexbox
