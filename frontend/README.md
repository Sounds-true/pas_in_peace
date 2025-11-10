# PAS in Peace - Frontend

Красивый, дружелюбный интерфейс для платформы поддержки родителей при родительском отчуждении.

## 🎨 Liquid Glass Design System

Наш дизайн основан на концепции **Liquid Glass** - современном подходе с эффектами матового стекла, плавными анимациями и органичными формами.

### Ключевые принципы:

1. **Glass Morphism** - полупрозрачные элементы с эффектом размытия
2. **Smooth Animations** - плавные переходы и анимации (Framer Motion)
3. **Child-Friendly** - тёплые цвета, милые детали (сердечки, эмодзи)
4. **Accessibility First** - keyboard navigation, ARIA labels, semantic HTML

## 🚀 Быстрый старт

### Установка зависимостей

```bash
cd frontend
npm install
```

### Запуск dev сервера

```bash
npm run dev
```

Откройте [http://localhost:3000](http://localhost:3000) в браузере.

### Просмотр компонентов

Демо страница со всеми компонентами: [http://localhost:3000/demo](http://localhost:3000/demo)

## 📦 Компоненты

### Liquid Glass Components

Находятся в `src/components/LiquidGlass/`:

- **QuestCard** - карточка квеста с glass эффектом
- **ProgressRing** - круговой индикатор прогресса
- **MultiProgressRing** - концентрические кольца для 4 треков
- **VoiceWave** - визуализация голосового ввода
- **CompactVoiceWave** - компактная версия для inline
- **VoiceVisualizer** - круговая визуализация с liquid эффектом

Подробная документация: [src/components/LiquidGlass/README.md](src/components/LiquidGlass/README.md)

## 🎯 Структура проекта

```
frontend/
├── src/
│   ├── components/
│   │   └── LiquidGlass/          # Базовые компоненты
│   │       ├── QuestCard.tsx
│   │       ├── ProgressRing.tsx
│   │       ├── VoiceWave.tsx
│   │       ├── index.ts
│   │       └── README.md
│   ├── pages/
│   │   ├── _app.tsx              # Next.js app entry
│   │   └── demo.tsx              # Demo page
│   └── styles/
│       └── globals.css           # Global styles + utilities
├── package.json
├── tsconfig.json
├── tailwind.config.js
├── next.config.js
└── README.md
```

## 🛠 Технологии

- **Next.js 14** - React framework
- **TypeScript** - type safety
- **Tailwind CSS** - utility-first CSS
- **Framer Motion** - animations
- **Lucide React** - icons

### Планируется добавить:

- Zustand - state management
- React Query - server state
- WebSocket - real-time communication
- React Flow - quest visualization

## 🎨 Цветовая палитра

### Primary Colors

- **Blue**: `#60a5fa` (blue-400) - основной цвет
- **Purple**: `#a78bfa` (purple-400) - вторичный
- **Pink**: `#f472b6` (pink-400) - акценты
- **Green**: `#34d399` (green-400) - успех

### Status Colors

- **Draft**: Slate gradient
- **Active**: Blue-Purple gradient
- **Completed**: Green gradient
- **Moderation**: Amber-Orange gradient

### Glass Effects

- Background: `rgba(255, 255, 255, 0.1)`
- Border: `rgba(255, 255, 255, 0.2)`
- Backdrop blur: `16px` + saturation `150%`

## 📝 Примеры использования

### Quest Card

```tsx
import { QuestCard } from '@/components/LiquidGlass';

<QuestCard
  questId="quest_001"
  title="Тайна зоопарка"
  childName="Маша"
  childAge={9}
  progress={45}
  status="active"
  nodeCount={6}
  onClick={() => console.log('Clicked!')}
/>
```

### Progress Ring

```tsx
import { ProgressRing } from '@/components/LiquidGlass';

<ProgressRing
  progress={75}
  color="#60a5fa"
  label="Завершено"
/>
```

### Voice Wave

```tsx
import { VoiceWave } from '@/components/LiquidGlass';

<VoiceWave
  isRecording={isRecording}
  amplitude={amplitude}
  onToggleRecording={toggleRecording}
/>
```

## 🧪 Тестирование

```bash
# Type check
npm run type-check

# Lint
npm run lint

# Build
npm run build
```

## 🚀 Деплой

### Vercel (рекомендуется)

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel
```

### Docker

```bash
# Build image
docker build -t pas-frontend .

# Run container
docker run -p 3000:3000 pas-frontend
```

## 🔧 Environment Variables

Создайте `.env.local`:

```bash
# API endpoints
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000

# Feature flags
NEXT_PUBLIC_QUEST_BUILDER_ENABLED=true
NEXT_PUBLIC_ANALYTICS_ENABLED=true
NEXT_PUBLIC_LETTER_MANAGER_ENABLED=true
```

## 📚 Дополнительные ресурсы

- [Next.js Documentation](https://nextjs.org/docs)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [Framer Motion](https://www.framer.com/motion/)
- [React Flow](https://reactflow.dev/)

## 🤝 Contributing

1. Создайте feature branch (`git checkout -b feature/amazing-feature`)
2. Commit изменения (`git commit -m 'Add amazing feature'`)
3. Push в branch (`git push origin feature/amazing-feature`)
4. Откройте Pull Request

## 📄 License

MIT License - see LICENSE file for details

---

## ✨ Текущий статус

**Фаза 1: Liquid Glass Components** ✅ ЗАВЕРШЕНА

- ✅ QuestCard с glass morphism
- ✅ ProgressRing с анимациями
- ✅ MultiProgressRing для 4 треков
- ✅ VoiceWave с real-time визуализацией
- ✅ CompactVoiceWave для inline использования
- ✅ VoiceVisualizer с liquid эффектом
- ✅ Demo page со всеми компонентами
- ✅ Global styles и utilities
- ✅ TailwindCSS конфигурация

**Следующие шаги:**

- [ ] Setup infrastructure (API client, Zustand, React Query)
- [ ] Authentication flow (Telegram OAuth)
- [ ] UnifiedDashboard layout
- [ ] MultiTrackProgress visualization
- [ ] Quest Builder conversational UI
- [ ] Letter Manager
- [ ] Analytics Dashboard

---

Made with ❤️ for parents reconnecting with their children
