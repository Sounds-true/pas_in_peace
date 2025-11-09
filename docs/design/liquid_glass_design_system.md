# Liquid Glass Design System
**Минималистичный Apple-стиль для InnerWorld / PAS**

> 🍎 Философия: Легкость, элегантность, прозрачность, не утомляет взгляд

---

## 🎨 Цветовая Палитра (Unified)

### Основа: Liquid Glass Effect

```css
/* === PRIMARY COLORS (Glassmorphism) === */

/* Прозрачное стекло с blur */
--glass-white: rgba(255, 255, 255, 0.7);
--glass-light: rgba(255, 255, 255, 0.5);
--glass-medium: rgba(255, 255, 255, 0.3);

/* Тонированное стекло */
--glass-blue: rgba(230, 240, 250, 0.6);   /* Едва заметный синий */
--glass-purple: rgba(245, 240, 255, 0.6); /* Едва заметный фиолетовый */
--glass-green: rgba(240, 250, 245, 0.6);  /* Едва заметный зеленый */

/* Градиенты для карточек */
--gradient-glass: linear-gradient(
  135deg,
  rgba(255, 255, 255, 0.8) 0%,
  rgba(240, 245, 255, 0.6) 100%
);

--gradient-glass-hover: linear-gradient(
  135deg,
  rgba(255, 255, 255, 0.9) 0%,
  rgba(240, 245, 255, 0.7) 100%
);
```

### Акцентные Цвета (минимальное использование)

```css
/* === ACCENT COLORS === */

/* Только для важных действий и состояний */
--accent-primary: #007AFF;      /* iOS Blue - кнопки, ссылки */
--accent-success: #34C759;      /* iOS Green - успех, прогресс */
--accent-warning: #FF9500;      /* iOS Orange - внимание */
--accent-error: #FF3B30;        /* iOS Red - ошибки, критично */
--accent-purple: #AF52DE;       /* iOS Purple - special, magic */

/* Приглушенные версии для backgrounds */
--accent-primary-soft: rgba(0, 122, 255, 0.1);
--accent-success-soft: rgba(52, 199, 89, 0.1);
--accent-purple-soft: rgba(175, 82, 222, 0.1);
```

### Текст и Иконки

```css
/* === TEXT COLORS === */

--text-primary: rgba(0, 0, 0, 0.85);    /* Основной текст */
--text-secondary: rgba(0, 0, 0, 0.55);  /* Вторичный */
--text-tertiary: rgba(0, 0, 0, 0.35);   /* Hints, placeholders */
--text-disabled: rgba(0, 0, 0, 0.25);   /* Неактивные элементы */

/* На темном фоне (если dark mode) */
--text-primary-dark: rgba(255, 255, 255, 0.95);
--text-secondary-dark: rgba(255, 255, 255, 0.65);
--text-tertiary-dark: rgba(255, 255, 255, 0.45);
```

### Фоны

```css
/* === BACKGROUNDS === */

/* Главный фон - едва уловимый градиент */
--bg-primary: linear-gradient(
  180deg,
  #FAFBFC 0%,
  #F5F7FA 100%
);

/* Вторичный фон - для модальных окон */
--bg-secondary: rgba(255, 255, 255, 0.95);

/* Overlay для модальных окон */
--bg-overlay: rgba(0, 0, 0, 0.3);
--bg-overlay-heavy: rgba(0, 0, 0, 0.5);
```

### Тени (Soft, Apple-like)

```css
/* === SHADOWS === */

/* Карточки */
--shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.08);
--shadow-md: 0 4px 12px rgba(0, 0, 0, 0.1);
--shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.12);

/* Floating elements */
--shadow-float: 0 12px 32px rgba(0, 0, 0, 0.15);

/* Inner shadow для стекла */
--shadow-glass-inset: inset 0 1px 2px rgba(255, 255, 255, 0.8);
```

---

## 🧱 Компоненты

### Glass Card (базовый элемент)

```css
.glass-card {
  background: var(--gradient-glass);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);

  border: 1px solid rgba(255, 255, 255, 0.8);
  border-radius: 24px; /* Большие радиусы */

  box-shadow:
    var(--shadow-md),
    var(--shadow-glass-inset);

  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.glass-card:hover {
  background: var(--gradient-glass-hover);
  box-shadow: var(--shadow-lg);
  transform: translateY(-2px);
}
```

**Пример использования:**
```tsx
<div className="glass-card p-6">
  <h2>Multi-Track Progress</h2>
  <ProgressBar />
</div>
```

### Voice Button (главный элемент - Voice-First)

```css
.voice-button {
  /* Круглая кнопка с стеклом */
  width: 80px;
  height: 80px;
  border-radius: 50%;

  background: var(--gradient-glass);
  backdrop-filter: blur(20px);
  border: 2px solid rgba(255, 255, 255, 0.9);

  box-shadow: var(--shadow-float);

  /* Центрируем иконку микрофона */
  display: flex;
  align-items: center;
  justify-content: center;

  cursor: pointer;
  transition: all 0.3s ease;
}

.voice-button:hover {
  transform: scale(1.05);
  box-shadow: var(--shadow-float), 0 0 24px rgba(0, 122, 255, 0.3);
}

.voice-button:active {
  transform: scale(0.98);
}

/* Анимированные волны при записи */
.voice-button.recording {
  animation: pulse-glow 1.5s ease-in-out infinite;
}

@keyframes pulse-glow {
  0%, 100% {
    box-shadow:
      var(--shadow-float),
      0 0 0 0 rgba(0, 122, 255, 0.7),
      0 0 0 0 rgba(0, 122, 255, 0.4);
  }
  50% {
    box-shadow:
      var(--shadow-float),
      0 0 0 20px rgba(0, 122, 255, 0),
      0 0 0 40px rgba(0, 122, 255, 0);
  }
}

/* Волны вокруг кнопки */
.voice-button.recording::before,
.voice-button.recording::after {
  content: '';
  position: absolute;
  width: 100%;
  height: 100%;
  border: 2px solid var(--accent-primary);
  border-radius: 50%;
  animation: wave-ripple 1.5s ease-out infinite;
}

.voice-button.recording::after {
  animation-delay: 0.75s;
}

@keyframes wave-ripple {
  0% {
    transform: scale(1);
    opacity: 0.8;
  }
  100% {
    transform: scale(2);
    opacity: 0;
  }
}
```

**React Component:**
```tsx
<VoiceButton>
  <MicrophoneIcon size={32} color="var(--accent-primary)" />
</VoiceButton>

{/* При записи */}
<VoiceButton className="recording">
  <MicrophoneIcon size={32} color="var(--accent-error)" />
</VoiceButton>
```

### Progress Bar (стеклянный)

```css
.glass-progress {
  width: 100%;
  height: 12px;
  border-radius: 12px;

  /* Фон - едва заметный */
  background: rgba(0, 0, 0, 0.05);
  overflow: hidden;

  position: relative;
}

.glass-progress-fill {
  height: 100%;
  border-radius: 12px;

  /* Градиент прогресса */
  background: linear-gradient(
    90deg,
    var(--accent-primary) 0%,
    var(--accent-purple) 100%
  );

  /* Анимация заполнения */
  transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);

  /* Легкий блик */
  position: relative;
  overflow: hidden;
}

.glass-progress-fill::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 255, 255, 0.4),
    transparent
  );
  animation: shine 2s infinite;
}

@keyframes shine {
  0% { left: -100%; }
  50%, 100% { left: 100%; }
}
```

### Button (минималистичный)

```css
.glass-button {
  padding: 12px 24px;
  border-radius: 16px;

  background: var(--glass-white);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.8);

  font-size: 16px;
  font-weight: 500;
  color: var(--text-primary);

  cursor: pointer;
  transition: all 0.2s ease;

  /* Убираем outline */
  outline: none;
}

.glass-button:hover {
  background: var(--glass-light);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.glass-button:active {
  transform: translateY(0);
  box-shadow: var(--shadow-sm);
}

/* Primary action */
.glass-button-primary {
  background: var(--accent-primary);
  color: white;
  border: none;
}

.glass-button-primary:hover {
  background: #0051D5; /* Darker iOS blue */
  box-shadow: 0 4px 16px rgba(0, 122, 255, 0.3);
}
```

### Input (стеклянный)

```css
.glass-input {
  width: 100%;
  padding: 14px 20px;
  border-radius: 16px;

  background: var(--glass-white);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(0, 0, 0, 0.08);

  font-size: 16px;
  color: var(--text-primary);

  transition: all 0.2s ease;
  outline: none;
}

.glass-input::placeholder {
  color: var(--text-tertiary);
}

.glass-input:focus {
  border-color: var(--accent-primary);
  box-shadow:
    var(--shadow-md),
    0 0 0 4px var(--accent-primary-soft);
}

/* С иконкой микрофона */
.glass-input-with-voice {
  padding-right: 52px; /* Место для иконки */
  position: relative;
}

.glass-input-voice-icon {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);

  width: 24px;
  height: 24px;
  cursor: pointer;

  color: var(--accent-primary);
  opacity: 0.6;
  transition: opacity 0.2s ease;
}

.glass-input-voice-icon:hover {
  opacity: 1;
}
```

### Badge (психолог проверил)

```css
.psychologist-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;

  padding: 6px 12px;
  border-radius: 12px;

  background: var(--accent-success-soft);
  border: 1px solid var(--accent-success);

  font-size: 13px;
  font-weight: 500;
  color: var(--accent-success);
}

.psychologist-badge-icon {
  width: 16px;
  height: 16px;
}

/* Анимация появления */
.psychologist-badge {
  animation: badge-appear 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes badge-appear {
  0% {
    opacity: 0;
    transform: scale(0.8) translateY(-10px);
  }
  100% {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}
```

**Пример:**
```tsx
<div className="psychologist-badge">
  <CheckShieldIcon className="psychologist-badge-icon" />
  Проверено психологом
</div>
```

---

## 📱 Типографика (San Francisco Style)

```css
/* === TYPOGRAPHY === */

:root {
  /* Шрифты */
  --font-primary: -apple-system, BlinkMacSystemFont, "SF Pro Display",
                  "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  --font-mono: "SF Mono", Monaco, "Cascadia Code", "Courier New", monospace;

  /* Размеры (fluid) */
  --text-xs: 12px;
  --text-sm: 14px;
  --text-base: 16px;
  --text-lg: 18px;
  --text-xl: 20px;
  --text-2xl: 24px;
  --text-3xl: 32px;
  --text-4xl: 40px;
  --text-5xl: 48px;

  /* Веса */
  --font-regular: 400;
  --font-medium: 500;
  --font-semibold: 600;
  --font-bold: 700;

  /* Line heights */
  --leading-tight: 1.2;
  --leading-normal: 1.5;
  --leading-relaxed: 1.75;
}

/* Заголовки */
h1, .heading-1 {
  font-size: var(--text-4xl);
  font-weight: var(--font-bold);
  line-height: var(--leading-tight);
  letter-spacing: -0.02em; /* Чуть теснее */
  color: var(--text-primary);
}

h2, .heading-2 {
  font-size: var(--text-3xl);
  font-weight: var(--font-semibold);
  line-height: var(--leading-tight);
  letter-spacing: -0.01em;
  color: var(--text-primary);
}

h3, .heading-3 {
  font-size: var(--text-2xl);
  font-weight: var(--font-semibold);
  line-height: var(--leading-normal);
  color: var(--text-primary);
}

/* Body text */
p, .body {
  font-size: var(--text-base);
  font-weight: var(--font-regular);
  line-height: var(--leading-relaxed);
  color: var(--text-primary);
}

.body-secondary {
  color: var(--text-secondary);
}

/* Captions */
.caption {
  font-size: var(--text-sm);
  font-weight: var(--font-regular);
  line-height: var(--leading-normal);
  color: var(--text-tertiary);
}
```

---

## 🎭 Анимации (Плавные, Apple-like)

```css
/* === ANIMATIONS === */

/* Easing functions */
:root {
  --ease-out-expo: cubic-bezier(0.19, 1, 0.22, 1);
  --ease-in-out-circ: cubic-bezier(0.85, 0, 0.15, 1);
  --ease-spring: cubic-bezier(0.4, 0, 0.2, 1);
}

/* Fade in */
@keyframes fade-in {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

/* Slide up */
@keyframes slide-up {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Scale in */
@keyframes scale-in {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

/* Применение */
.animate-fade-in {
  animation: fade-in 0.3s var(--ease-spring);
}

.animate-slide-up {
  animation: slide-up 0.4s var(--ease-out-expo);
}

.animate-scale-in {
  animation: scale-in 0.3s var(--ease-spring);
}
```

---

## 🖼️ Layout Principles

### Spacing (8pt Grid System)

```css
:root {
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-8: 32px;
  --space-10: 40px;
  --space-12: 48px;
  --space-16: 64px;
  --space-20: 80px;
}
```

### Border Radius (большие радиусы)

```css
:root {
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --radius-xl: 20px;
  --radius-2xl: 24px;
  --radius-full: 9999px; /* Круглые элементы */
}
```

---

## 🌓 Dark Mode (опционально)

```css
@media (prefers-color-scheme: dark) {
  :root {
    /* Инвертированные стекла */
    --glass-white: rgba(20, 20, 25, 0.7);
    --glass-light: rgba(30, 30, 35, 0.5);
    --glass-medium: rgba(40, 40, 45, 0.3);

    /* Фон */
    --bg-primary: linear-gradient(
      180deg,
      #0A0A0F 0%,
      #15151A 100%
    );

    /* Текст */
    --text-primary: var(--text-primary-dark);
    --text-secondary: var(--text-secondary-dark);
    --text-tertiary: var(--text-tertiary-dark);

    /* Тени мягче */
    --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.4);
  }
}
```

---

## 📦 Tailwind CSS Configuration

```js
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        glass: {
          white: 'rgba(255, 255, 255, 0.7)',
          light: 'rgba(255, 255, 255, 0.5)',
          medium: 'rgba(255, 255, 255, 0.3)',
        },
        accent: {
          primary: '#007AFF',
          success: '#34C759',
          warning: '#FF9500',
          error: '#FF3B30',
          purple: '#AF52DE',
        }
      },
      backdropBlur: {
        glass: '20px',
      },
      borderRadius: {
        '2xl': '24px',
        '3xl': '32px',
      },
      boxShadow: {
        glass: '0 4px 12px rgba(0, 0, 0, 0.1), inset 0 1px 2px rgba(255, 255, 255, 0.8)',
      }
    }
  }
}
```

---

## 🎨 Примеры Использования

### Voice-First Interface

```tsx
<div className="glass-card p-8 text-center">
  {/* Главная кнопка микрофона */}
  <VoiceButton
    isRecording={isRecording}
    onClick={startRecording}
  />

  {/* Текст-подсказка */}
  <p className="caption mt-4">
    Нажмите и расскажите о вашем ребенке
  </p>

  {/* Альтернативный ввод (скрыт пока не попросят) */}
  {showTextInput && (
    <div className="mt-6 animate-slide-up">
      <div className="glass-input-with-voice">
        <input
          className="glass-input"
          placeholder="Или введите текст..."
        />
        <MicIcon className="glass-input-voice-icon" />
      </div>
    </div>
  )}
</div>
```

### Quest Card с Badge психолога

```tsx
<div className="glass-card p-6 hover:shadow-lg transition-all">
  <div className="flex justify-between items-start">
    <div>
      <h3 className="heading-3">Тайна старого сада</h3>
      <p className="caption mt-1">8 заданий • 45 минут</p>
    </div>

    {/* Badge психолога */}
    {quest.psychologistApproved && (
      <div className="psychologist-badge">
        <CheckShieldIcon />
        Проверено
      </div>
    )}
  </div>

  {/* Progress */}
  <div className="mt-4">
    <div className="glass-progress">
      <div
        className="glass-progress-fill"
        style={{width: `${quest.progress}%`}}
      />
    </div>
  </div>
</div>
```

### Multi-Track Progress

```tsx
<div className="glass-card p-8">
  <h2 className="heading-2 mb-6">Ваш прогресс</h2>

  {tracks.map(track => (
    <div key={track.id} className="mb-6 last:mb-0">
      <div className="flex justify-between items-center mb-2">
        <span className="body font-medium">{track.icon} {track.name}</span>
        <span className="caption">{track.percentage}%</span>
      </div>

      <div className="glass-progress">
        <div
          className="glass-progress-fill"
          style={{
            width: `${track.percentage}%`,
            background: track.gradient
          }}
        />
      </div>

      <p className="caption mt-2">{track.nextAction}</p>
    </div>
  ))}
</div>
```

---

## ✨ Ключевые Принципы

1. **Минимализм**: Меньше цветов, больше белого пространства
2. **Стекло everywhere**: Все карточки - glassmorphism
3. **Плавность**: Все transitions 0.3s с ease функциями
4. **Большие радиусы**: 16-24px для элементов
5. **Мягкие тени**: Никаких жестких контрастов
6. **Voice-First**: Микрофон - главный элемент UI
7. **Единый стиль**: Одинаковый для родителей и детей

---

**Version**: 1.0.0
**Inspired by**: Apple iOS/macOS, Glassmorphism, Liquid Design
**Status**: 🚀 Ready for Implementation
