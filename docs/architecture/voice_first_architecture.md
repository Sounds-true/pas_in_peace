# Voice-First Architecture
**Голосовой интерфейс как основной способ взаимодействия**

> 🎤 Философия: Говорить проще, чем печатать. Слушать приятнее, чем читать.

---

## 🎯 Концепция

### Voice-First означает:

✅ **Микрофон - первое, что видит пользователь**
✅ **Анимированные волны приглашают говорить**
✅ **Текстовый ввод - запасной вариант** (если нет разрешения / не работает)
✅ **Озвучка по умолчанию включена** (можно отключить кнопкой)
✅ **Голосовые команды everywhere**

---

## 🏗️ Архитектура Системы

### Уровни Voice Interaction

```
┌─────────────────────────────────────┐
│  User Interface Layer               │
│  ┌─────────────────────────────┐   │
│  │  Voice Button (Primary)     │   │
│  │  + Animated Waves           │   │
│  │  + Permission Request       │   │
│  └─────────────────────────────┘   │
│                                      │
│  ┌─────────────────────────────┐   │
│  │  Text Input (Fallback)      │   │
│  │  + Mic Icon (always)        │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  Voice Processing Layer             │
│  ┌────────────┬────────────────┐   │
│  │ STT (🎤→📝) │ TTS (📝→🔊)   │   │
│  │            │                 │   │
│  │ Web Speech │ Web Speech     │   │
│  │ API        │ API            │   │
│  │     OR     │     OR         │   │
│  │ Whisper    │ ElevenLabs     │   │
│  │ (OpenAI)   │                │   │
│  └────────────┴────────────────┘   │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  AI Processing Layer                │
│  ┌─────────────────────────────┐   │
│  │  GPT-4 / Claude             │   │
│  │  + Quest Builder            │   │
│  │  + Content Moderator        │   │
│  │  + Multi-Track Manager      │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  Storage Layer                      │
│  ┌─────────────────────────────┐   │
│  │  PostgreSQL                 │   │
│  │  + Voice Message URLs       │   │
│  │  + Audio Transcripts        │   │
│  │  + TTS Cache                │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
```

---

## 🎤 Voice Button Component (главный элемент)

### Design Spec

```tsx
interface VoiceButtonProps {
  isRecording: boolean;
  isProcessing: boolean;
  onStart: () => void;
  onStop: () => void;
  permission: 'granted' | 'denied' | 'prompt';
  waveAnimation?: boolean;
}

const VoiceButton: React.FC<VoiceButtonProps> = ({
  isRecording,
  isProcessing,
  onStart,
  onStop,
  permission,
  waveAnimation = true
}) => {
  return (
    <div className="voice-button-container">
      {/* Анимированные волны вокруг */}
      {waveAnimation && isRecording && (
        <WaveAnimation />
      )}

      {/* Основная кнопка */}
      <button
        className={`voice-button ${isRecording ? 'recording' : ''} ${isProcessing ? 'processing' : ''}`}
        onClick={isRecording ? onStop : onStart}
        disabled={permission === 'denied' || isProcessing}
      >
        {isProcessing ? (
          <LoadingSpinner />
        ) : isRecording ? (
          <StopIcon size={32} color="var(--accent-error)" />
        ) : (
          <MicrophoneIcon size={32} color="var(--accent-primary)" />
        )}
      </button>

      {/* Permission request tooltip */}
      {permission === 'prompt' && !isRecording && (
        <Tooltip>
          Нажмите и разрешите доступ к микрофону
        </Tooltip>
      )}

      {/* Error state */}
      {permission === 'denied' && (
        <ErrorMessage>
          Микрофон недоступен. Проверьте настройки браузера.
        </ErrorMessage>
      )}
    </div>
  );
};
```

### Wave Animation Component

```tsx
const WaveAnimation: React.FC = () => {
  return (
    <div className="wave-animation">
      {/* Внутренние круги */}
      <div className="wave-ring wave-ring-1" />
      <div className="wave-ring wave-ring-2" />
      <div className="wave-ring wave-ring-3" />

      {/* Пульсирующее свечение */}
      <div className="wave-glow" />
    </div>
  );
};
```

```css
/* Анимация волн */
.wave-ring {
  position: absolute;
  width: 100%;
  height: 100%;
  border: 2px solid var(--accent-primary);
  border-radius: 50%;
  opacity: 0;
  animation: wave-expand 2s ease-out infinite;
}

.wave-ring-2 {
  animation-delay: 0.6s;
}

.wave-ring-3 {
  animation-delay: 1.2s;
}

@keyframes wave-expand {
  0% {
    transform: scale(1);
    opacity: 0.6;
  }
  100% {
    transform: scale(2.5);
    opacity: 0;
  }
}

/* Пульсирующее свечение */
.wave-glow {
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: radial-gradient(
    circle,
    rgba(0, 122, 255, 0.3) 0%,
    transparent 70%
  );
  animation: glow-pulse 1.5s ease-in-out infinite;
}

@keyframes glow-pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 0.5;
  }
  50% {
    transform: scale(1.1);
    opacity: 0.8;
  }
}
```

---

## 🔊 Speech-to-Text (STT)

### Web Speech API (основной)

```typescript
class VoiceST

T {
  private recognition: SpeechRecognition | null = null;
  private isListening = false;

  constructor(
    private language: string = 'ru-RU',
    private onResult: (text: string) => void,
    private onError: (error: string) => void
  ) {
    this.initRecognition();
  }

  private initRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      this.onError('Speech Recognition не поддерживается в этом браузере');
      return;
    }

    this.recognition = new SpeechRecognition();
    this.recognition.lang = this.language;
    this.recognition.continuous = false; // Одно высказывание
    this.recognition.interimResults = true; // Показывать промежуточные результаты

    this.recognition.onresult = (event) => {
      const transcript = Array.from(event.results)
        .map(result => result[0].transcript)
        .join('');

      // Финальный результат
      if (event.results[event.results.length - 1].isFinal) {
        this.onResult(transcript);
      }
    };

    this.recognition.onerror = (event) => {
      this.onError(event.error);
    };

    this.recognition.onend = () => {
      this.isListening = false;
    };
  }

  start() {
    if (!this.recognition) {
      this.onError('Recognition не инициализирован');
      return;
    }

    if (this.isListening) return;

    try {
      this.recognition.start();
      this.isListening = true;
    } catch (error) {
      this.onError('Ошибка запуска распознавания');
    }
  }

  stop() {
    if (!this.recognition || !this.isListening) return;

    this.recognition.stop();
    this.isListening = false;
  }
}
```

**Использование:**
```tsx
const [transcript, setTranscript] = useState('');

const voiceSTT = new VoiceSTT(
  'ru-RU',
  (text) => setTranscript(text),
  (error) => console.error(error)
);

// В компоненте
<VoiceButton
  onStart={() => voiceSTT.start()}
  onStop={() => voiceSTT.stop()}
/>
```

### Whisper API (fallback для точности)

```typescript
async function transcribeWithWhisper(audioBlob: Blob): Promise<string> {
  const formData = new FormData();
  formData.append('file', audioBlob, 'audio.wav');
  formData.append('model', 'whisper-1');
  formData.append('language', 'ru');

  const response = await fetch('https://api.openai.com/v1/audio/transcriptions', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${process.env.OPENAI_API_KEY}`
    },
    body: formData
  });

  const data = await response.json();
  return data.text;
}
```

---

## 📢 Text-to-Speech (TTS)

### Web Speech API (основной)

```typescript
class VoiceTTS {
  private synth = window.speechSynthesis;
  private voice: SpeechSynthesisVoice | null = null;

  constructor(private language: string = 'ru-RU') {
    this.loadVoice();
  }

  private loadVoice() {
    const voices = this.synth.getVoices();
    // Ищем русский голос
    this.voice = voices.find(v => v.lang === this.language) || voices[0];
  }

  speak(text: string, options?: {
    rate?: number;   // 0.1 - 10 (1 = normal)
    pitch?: number;  // 0 - 2 (1 = normal)
    volume?: number; // 0 - 1 (1 = max)
  }) {
    if (!this.synth) return;

    // Останавливаем предыдущее
    this.synth.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.voice = this.voice;
    utterance.lang = this.language;
    utterance.rate = options?.rate ?? 1;
    utterance.pitch = options?.pitch ?? 1;
    utterance.volume = options?.volume ?? 1;

    this.synth.speak(utterance);
  }

  stop() {
    this.synth.cancel();
  }
}
```

**Использование:**
```tsx
const tts = new VoiceTTS('ru-RU');

// Озвучить ответ AI
useEffect(() => {
  if (aiResponse && autoPlayAudio) {
    tts.speak(aiResponse);
  }
}, [aiResponse]);

// Кнопка отключения озвучки
<button onClick={() => setAutoPlayAudio(!autoPlayAudio)}>
  {autoPlayAudio ? <SpeakerOnIcon /> : <SpeakerOffIcon />}
</button>
```

### ElevenLabs (премиум озвучка)

```typescript
async function generateElevenLabsAudio(text: string): Promise<ArrayBuffer> {
  const response = await fetch('https://api.elevenlabs.io/v1/text-to-speech/voice_id', {
    method: 'POST',
    headers: {
      'Accept': 'audio/mpeg',
      'Content-Type': 'application/json',
      'xi-api-key': process.env.ELEVENLABS_API_KEY
    },
    body: JSON.stringify({
      text,
      model_id: 'eleven_multilingual_v2',
      voice_settings: {
        stability: 0.5,
        similarity_boost: 0.75
      }
    })
  });

  return response.arrayBuffer();
}

// Проигрывание
function playAudio(audioData: ArrayBuffer) {
  const audioContext = new AudioContext();
  audioContext.decodeAudioData(audioData, (buffer) => {
    const source = audioContext.createBufferSource();
    source.buffer = buffer;
    source.connect(audioContext.destination);
    source.start(0);
  });
}
```

---

## 🎮 Voice Commands (голосовые команды)

### Command Parser

```typescript
interface VoiceCommand {
  phrases: string[];  // Варианты фраз
  action: () => void; // Что делать
  description: string; // Для help
}

const voiceCommands: VoiceCommand[] = [
  {
    phrases: ['следующий вопрос', 'далее', 'next'],
    action: () => goToNextNode(),
    description: 'Перейти к следующему заданию'
  },
  {
    phrases: ['повтори', 'еще раз', 'repeat'],
    action: () => repeatLastMessage(),
    description: 'Повторить последнее сообщение'
  },
  {
    phrases: ['подсказка', 'помощь', 'hint'],
    action: () => showHint(),
    description: 'Показать подсказку'
  },
  {
    phrases: ['покажи прогресс', 'мой прогресс', 'progress'],
    action: () => showProgress(),
    description: 'Показать прогресс'
  },
  {
    phrases: ['стоп', 'пауза', 'stop'],
    action: () => pauseQuest(),
    description: 'Остановить квест'
  }
];

function parseVoiceCommand(text: string): VoiceCommand | null {
  const normalizedText = text.toLowerCase().trim();

  for (const command of voiceCommands) {
    if (command.phrases.some(phrase => normalizedText.includes(phrase))) {
      return command;
    }
  }

  return null;
}
```

**Использование:**
```tsx
const handleVoiceInput = (text: string) => {
  // Проверяем, это команда или обычный ввод
  const command = parseVoiceCommand(text);

  if (command) {
    command.action();
    tts.speak(`Выполняю: ${command.description}`);
  } else {
    // Обычный ввод - передаем в AI
    processUserMessage(text);
  }
};
```

---

## 🧩 Интеграция с Quest Builder

### Voice-Driven Quest Creation

```tsx
const QuestBuilderVoice: React.FC = () => {
  const [stage, setStage] = useState<QuestStage>('INITIAL');
  const [context, setContext] = useState<QuestContext>({});
  const [isListening, setIsListening] = useState(false);

  const handleVoiceInput = async (transcript: string) => {
    // Отправляем в AI
    const response = await questBuilderAI.processInput(transcript, context);

    // Озвучиваем ответ
    tts.speak(response.message);

    // Обновляем контекст
    setContext(response.updatedContext);
    setStage(response.nextStage);
  };

  return (
    <div className="glass-card p-8">
      {/* AI Avatar (опционально) */}
      <AIAvatar isThinking={isProcessing} />

      {/* Главная кнопка микрофона */}
      <VoiceButton
        isRecording={isListening}
        onStart={() => {
          setIsListening(true);
          voiceSTT.start();
        }}
        onStop={() => {
          setIsListening(false);
          voiceSTT.stop();
        }}
      />

      {/* Текущий вопрос AI (текст + озвучка) */}
      <div className="mt-6 text-center">
        <p className="body-secondary">
          {getCurrentQuestion(stage)}
        </p>
      </div>

      {/* Transcript (что пользователь сказал) */}
      {transcript && (
        <div className="mt-4 glass-card p-4 bg-accent-primary-soft">
          <p className="caption">Вы сказали:</p>
          <p className="body">{transcript}</p>
        </div>
      )}

      {/* Fallback - текстовый ввод */}
      <button
        className="mt-4 text-accent-primary caption"
        onClick={() => setShowTextInput(true)}
      >
        Или введите текстом
      </button>

      {showTextInput && (
        <div className="mt-4 animate-slide-up">
          <div className="glass-input-with-voice">
            <input
              className="glass-input"
              placeholder="Введите ответ..."
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  handleVoiceInput(e.currentTarget.value);
                }
              }}
            />
            <MicIcon
              className="glass-input-voice-icon"
              onClick={() => setShowTextInput(false)}
            />
          </div>
        </div>
      )}
    </div>
  );
};
```

---

## 🎯 Child Quest Player (Voice Mode)

### Voice-Enabled Quest Gameplay

```tsx
const QuestPlayerVoice: React.FC<{quest: Quest}> = ({quest}) => {
  const [currentNode, setCurrentNode] = useState(quest.nodes[0]);
  const [isListening, setIsListening] = useState(false);

  // Озвучиваем задание при загрузке ноды
  useEffect(() => {
    if (autoPlayAudio) {
      tts.speak(currentNode.challenge);
    }
  }, [currentNode]);

  const handleVoiceAnswer = async (answer: string) => {
    // Проверяем ответ
    const isCorrect = checkAnswer(answer, currentNode.answer);

    if (isCorrect) {
      tts.speak('Правильно! Отлично!');
      // Reveal момент (если есть)
      if (currentNode.reveal) {
        setTimeout(() => {
          tts.speak(currentNode.reveal.message);
        }, 1000);
      }
      // Следующая нода
      setCurrentNode(quest.nodes[currentNode.id + 1]);
    } else {
      tts.speak('Попробуй еще раз');
    }
  };

  return (
    <div className="glass-card p-8">
      {/* Quest Header */}
      <h2 className="heading-2 text-center mb-6">
        {quest.title}
      </h2>

      {/* Current Challenge */}
      <div className="glass-card p-6 bg-glass-blue mb-6">
        <p className="body text-center">
          {currentNode.challenge}
        </p>

        {/* Кнопка "Повторить" */}
        <button
          className="glass-button mt-4 w-full"
          onClick={() => tts.speak(currentNode.challenge)}
        >
          🔊 Повторить задание
        </button>
      </div>

      {/* Voice Input */}
      <VoiceButton
        isRecording={isListening}
        onStart={() => {
          setIsListening(true);
          voiceSTT.start();
        }}
        onStop={() => {
          setIsListening(false);
          voiceSTT.stop();
        }}
      />

      <p className="caption text-center mt-4">
        Скажи ответ вслух
      </p>

      {/* Progress */}
      <div className="mt-8">
        <div className="glass-progress">
          <div
            className="glass-progress-fill"
            style={{width: `${(currentNode.id / quest.nodes.length) * 100}%`}}
          />
        </div>
        <p className="caption text-center mt-2">
          Задание {currentNode.id + 1} из {quest.nodes.length}
        </p>
      </div>
    </div>
  );
};
```

---

## 📊 Voice Analytics

### Сохранение голосовых данных

```typescript
interface VoiceInteraction {
  id: string;
  user_id: number;
  timestamp: Date;
  transcript: string;
  audio_url?: string;  // Опционально - сохраняем аудио
  duration_ms: number;
  language: string;
  confidence: number;  // От STT
  intent?: string;     // Детектированный интент
  command_used?: string;
}

// Сохранение взаимодействия
async function saveVoiceInteraction(
  userId: number,
  transcript: string,
  audioBlob?: Blob
): Promise<void> {
  let audioUrl = null;

  // Если нужно сохранить аудио (для ревью психолога)
  if (audioBlob) {
    audioUrl = await uploadToS3(audioBlob);
  }

  await db.voiceInteractions.create({
    user_id: userId,
    transcript,
    audio_url: audioUrl,
    duration_ms: audioBlob?.size ? calculateDuration(audioBlob) : 0,
    language: 'ru-RU',
    confidence: 0.95, // От STT
  });
}
```

---

## 🔒 Privacy & Permissions

### Permission Flow

```tsx
const VoicePermissionRequest: React.FC = () => {
  const [permission, setPermission] = useState<PermissionState>('prompt');

  const requestPermission = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({audio: true});

      // Успех
      setPermission('granted');

      // Останавливаем stream (он больше не нужен)
      stream.getTracks().forEach(track => track.stop());

    } catch (error) {
      // Отказ
      setPermission('denied');
    }
  };

  if (permission === 'granted') {
    return <VoiceButton />;
  }

  return (
    <div className="glass-card p-8 text-center">
      <MicrophoneIcon size={64} className="mx-auto mb-4 text-accent-primary opacity-50" />

      <h3 className="heading-3 mb-2">
        Разрешите доступ к микрофону
      </h3>

      <p className="body-secondary mb-6">
        Это позволит вам общаться голосом.
        Мы не записываем и не передаем ваши данные.
      </p>

      <button
        className="glass-button-primary"
        onClick={requestPermission}
      >
        Разрешить
      </button>

      <button
        className="glass-button mt-2"
        onClick={() => setShowTextInput(true)}
      >
        Использовать текст
      </button>
    </div>
  );
};
```

---

## 🚀 Implementation Roadmap

### Week 1: Core Voice Components
- [ ] VoiceButton with wave animation
- [ ] Web Speech API integration (STT/TTS)
- [ ] Permission handling
- [ ] Basic voice commands

### Week 2: Quest Builder Voice
- [ ] Voice-driven dialogue
- [ ] AI response synthesis
- [ ] Context extraction from speech
- [ ] Fallback to text

### Week 3: Child Player Voice
- [ ] Voice answer checking
- [ ] Audio narration of challenges
- [ ] Voice commands in quests
- [ ] Progress announcements

### Week 4: Advanced Features
- [ ] Whisper API fallback
- [ ] ElevenLabs premium voices
- [ ] Voice analytics
- [ ] Offline mode (cache TTS)

---

## 📝 Best Practices

### 1. **Always Provide Fallback**
```tsx
{hasVoiceSupport ? <VoiceButton /> : <TextInput />}
```

### 2. **Show Visual Feedback**
```tsx
{isListening && <WaveAnimation />}
{isProcessing && <LoadingSpinner />}
```

### 3. **Handle Errors Gracefully**
```tsx
if (error === 'not-allowed') {
  showMessage('Разрешите доступ к микрофону в настройках');
}
```

### 4. **Cache TTS for Performance**
```typescript
const ttsCache = new Map<string, AudioBuffer>();

async function speakCached(text: string) {
  if (ttsCache.has(text)) {
    playFromCache(text);
  } else {
    const audio = await generateTTS(text);
    ttsCache.set(text, audio);
    playAudio(audio);
  }
}
```

### 5. **Respect User Preferences**
```tsx
const [autoPlay, setAutoPlay] = useLocalStorage('autoplay_audio', true);
const [voiceEnabled, setVoiceEnabled] = useLocalStorage('voice_enabled', true);
```

---

**Status**: 🚀 Ready for Implementation
**Priority**: HIGH (основной функционал)
**Estimated Time**: 4 weeks
