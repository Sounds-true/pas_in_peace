/**
 * Quest Builder Page - Conversational quest creation
 *
 * Protected route - requires authentication
 */

import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Send,
  Sparkles,
  Loader,
  CheckCircle,
  ArrowLeft,
  Save,
  Eye,
  Wand2,
} from 'lucide-react';
import { useRouter } from 'next/router';
import { ProtectedRoute } from '../../components/Auth/ProtectedRoute';
import { DashboardLayout } from '../../components/Dashboard';

interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
}

interface QuestData {
  title?: string;
  description?: string;
  childAge?: number;
  childInterests?: string[];
  questType?: 'educational' | 'game' | 'emotional';
  difficulty?: 'easy' | 'medium' | 'hard';
  duration?: number; // minutes
  tasks?: Array<{
    title: string;
    description: string;
    type: 'question' | 'activity' | 'reflection';
  }>;
}

function QuestBuilderContent() {
  const router = useRouter();
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content:
        'Привет! Я помогу тебе создать персонализированный квест для твоего ребёнка. Давай начнём с простого вопроса: сколько лет твоему ребёнку?',
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [questData, setQuestData] = useState<QuestData>({});
  const [currentStep, setCurrentStep] = useState(1);
  const [isComplete, setIsComplete] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Simulate AI conversation
  const handleSendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    // Simulate AI processing
    await new Promise((resolve) => setTimeout(resolve, 1500));

    // Generate AI response based on current step
    let aiResponse = '';
    let nextQuestData = { ...questData };

    if (currentStep === 1) {
      // Age question
      const age = parseInt(input);
      if (!isNaN(age)) {
        nextQuestData.childAge = age;
        aiResponse = `Отлично! ${age} лет - замечательный возраст.\n\nТеперь расскажи, что интересует твоего ребёнка? Например: космос, динозавры, рисование, музыка, спорт...`;
        setCurrentStep(2);
      } else {
        aiResponse =
          'Пожалуйста, укажи возраст числом, например: 7 или 10.';
      }
    } else if (currentStep === 2) {
      // Interests question
      const interests = input
        .split(/[,;]/)
        .map((i) => i.trim())
        .filter((i) => i);
      nextQuestData.childInterests = interests;
      // Quest is always hybrid (educational + game + emotional)
      nextQuestData.questType = 'educational'; // We use this as default but quest includes all types
      aiResponse = `Замечательно! Очень интересные темы.\n\nЯ создам комбинированный квест с элементами обучения, игры и эмоциональной связи.\n\nКакой уровень сложности?\n\n**1** - Лёгкий (15-20 минут)\n**2** - Средний (30-40 минут)  \n**3** - Сложный (60+ минут)\n\nНапиши цифру 1, 2 или 3.`;
      setCurrentStep(3);
    } else if (currentStep === 3) {
      // Difficulty - extract first digit from input
      const digitMatch = input.match(/[123]/);
      const digit = digitMatch ? digitMatch[0] : null;

      const difficultyMap: Record<string, 'easy' | 'medium' | 'hard'> = {
        '1': 'easy',
        '2': 'medium',
        '3': 'hard',
        лёгкий: 'easy',
        легкий: 'easy',
        средний: 'medium',
        сложный: 'hard',
      };
      const difficulty = digit ? difficultyMap[digit] : difficultyMap[input.toLowerCase().trim()];
      if (difficulty) {
        nextQuestData.difficulty = difficulty;
        nextQuestData.duration =
          difficulty === 'easy' ? 20 : difficulty === 'medium' ? 35 : 60;

        // Generate quest based on collected data
        const mainInterest = nextQuestData.childInterests?.[0] || 'Исследователь';
        nextQuestData.title = `Приключение "${mainInterest}"`;
        nextQuestData.description = `Комбинированный квест для ребёнка ${nextQuestData.childAge} лет с элементами обучения, игры и эмоциональной связи. Темы: ${
          nextQuestData.childInterests?.join(', ') || 'интересы'
        }`;

        // Generate sample tasks (hybrid: education + game + emotional)
        nextQuestData.tasks = [
          {
            title: `Открытие`,
            description: `Расскажи папе, что ты уже знаешь о ${mainInterest}? Что тебе в этом нравится больше всего?`,
            type: 'question',
          },
          {
            title: `Исследование`,
            description: `Давай вместе узнаем 3 новых факта о ${mainInterest}! Ты можешь найти их в книгах, интернете или спросить у меня.`,
            type: 'activity',
          },
          {
            title: `Творчество`,
            description: `Придумай и нарисуй (или опиши) свою историю про ${mainInterest}. Можно добавить волшебство!`,
            type: 'activity',
          },
          {
            title: `Игровой челлендж`,
            description: `Мини-игра: Представь что ты учитель и расскажи мне про ${mainInterest} за 2 минуты. Можно показывать жестами!`,
            type: 'activity',
          },
          {
            title: `Размышление вместе`,
            description: `Что тебе понравилось больше всего? Чему ты научился? Давай обсудим вместе с папой.`,
            type: 'reflection',
          },
        ];

        aiResponse = `Потрясающе! Я создал для тебя комбинированный квест.\n\n**${nextQuestData.title}**\n\n${nextQuestData.description}\n\nКвест включает ${nextQuestData.tasks.length} заданий (образование + игра + эмоции):\n${nextQuestData.tasks.map((t, i) => `${i + 1}. ${t.title}`).join('\n')}\n\nПримерное время: ${nextQuestData.duration} минут\n\nТы можешь сохранить квест, посмотреть детали или создать новый!`;
        setIsComplete(true);
        setCurrentStep(4);
      } else {
        aiResponse =
          'Пожалуйста, выбери уровень сложности (1, 2 или 3).';
      }
    }

    setQuestData(nextQuestData);

    const assistantMessage: Message = {
      id: (Date.now() + 1).toString(),
      role: 'assistant',
      content: aiResponse,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, assistantMessage]);
    setIsLoading(false);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleSaveQuest = () => {
    // TODO: Save quest to backend
    router.push('/projects');
  };

  return (
    <DashboardLayout
      title="Создание квеста"
      actions={
        <button
          onClick={() => router.push('/dashboard')}
          className="glass-button bg-white/10 hover:bg-white/20 flex items-center gap-2"
        >
          <ArrowLeft className="w-4 h-4" />
          Назад
        </button>
      }
    >
      <div className="max-w-4xl mx-auto">
        {/* Progress */}
        <motion.div
          className="frosted-card mb-6"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm font-medium text-white/70">
              Шаг {Math.min(currentStep, 4)} из 4
            </span>
            <span className="text-sm font-medium text-white">
              {Math.min((currentStep / 4) * 100, 100).toFixed(0)}%
            </span>
          </div>
          <div className="h-2 bg-white/10 rounded-full overflow-hidden">
            <motion.div
              className="h-full bg-gradient-to-r from-blue-500 to-purple-500"
              initial={{ width: 0 }}
              animate={{ width: `${Math.min((currentStep / 4) * 100, 100)}%` }}
              transition={{ duration: 0.5 }}
            />
          </div>
        </motion.div>

        {/* Chat container */}
        <div className="frosted-card flex flex-col h-[600px]">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4 scrollbar-glass">
            <AnimatePresence initial={false}>
              {messages.map((message) => (
                <motion.div
                  key={message.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  className={`flex ${
                    message.role === 'user' ? 'justify-end' : 'justify-start'
                  }`}
                >
                  <div
                    className={`
                    max-w-[80%] rounded-2xl px-4 py-3
                    ${
                      message.role === 'user'
                        ? 'bg-blue-500/30 text-white'
                        : 'bg-white/10 text-white'
                    }
                  `}
                  >
                    {message.role === 'assistant' && (
                      <div className="flex items-center gap-2 mb-2">
                        <Wand2 className="w-4 h-4 text-purple-400" />
                        <span className="text-xs font-medium text-purple-400">
                          AI-Ассистент
                        </span>
                      </div>
                    )}
                    <p className="text-sm whitespace-pre-wrap leading-relaxed">
                      {message.content}
                    </p>
                    <span className="text-xs text-white/50 mt-2 block">
                      {message.timestamp.toLocaleTimeString('ru-RU', {
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </span>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>

            {/* Loading indicator */}
            {isLoading && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex justify-start"
              >
                <div className="bg-white/10 rounded-2xl px-4 py-3">
                  <div className="flex items-center gap-2">
                    <Loader className="w-4 h-4 animate-spin text-purple-400" />
                    <span className="text-sm text-white/70">
                      Обрабатываю...
                    </span>
                  </div>
                </div>
              </motion.div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input area */}
          <div className="border-t border-white/10 p-4">
            {isComplete ? (
              <div className="flex gap-3">
                <button
                  onClick={handleSaveQuest}
                  className="flex-1 glass-button bg-blue-500/20 hover:bg-blue-500/30 flex items-center justify-center gap-2"
                >
                  <Save className="w-4 h-4" />
                  Сохранить квест
                </button>
                <button
                  onClick={() => router.push('/quest-builder/preview')}
                  className="glass-button bg-purple-500/20 hover:bg-purple-500/30 flex items-center gap-2"
                >
                  <Eye className="w-4 h-4" />
                  Посмотреть
                </button>
              </div>
            ) : (
              <div className="flex gap-3">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Напиши свой ответ..."
                  disabled={isLoading}
                  className="flex-1 bg-white/5 rounded-xl px-4 py-3 text-white placeholder:text-white/50 focus:outline-none focus:ring-2 focus:ring-blue-400/50 disabled:opacity-50"
                />
                <button
                  onClick={handleSendMessage}
                  disabled={!input.trim() || isLoading}
                  className="glass-button bg-blue-500/20 hover:bg-blue-500/30 disabled:opacity-50 disabled:cursor-not-allowed p-3"
                >
                  <Send className="w-5 h-5" />
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Quest preview (if complete) */}
        {isComplete && questData.tasks && (
          <motion.div
            className="frosted-card mt-6"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <div className="flex items-center gap-2 mb-4">
              <CheckCircle className="w-5 h-5 text-green-400" />
              <h3 className="text-xl font-bold text-white">
                Квест готов!
              </h3>
            </div>

            <div className="space-y-4">
              <div>
                <h4 className="text-lg font-bold text-white mb-2">
                  {questData.title}
                </h4>
                <p className="text-white/70 text-sm mb-4">
                  {questData.description}
                </p>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                <div className="frosted-card">
                  <span className="text-white/60">Возраст</span>
                  <p className="text-white font-medium">{questData.childAge} лет</p>
                </div>
                <div className="frosted-card">
                  <span className="text-white/60">Тип</span>
                  <p className="text-white font-medium">
                    {questData.questType === 'educational'
                      ? 'Образовательный'
                      : questData.questType === 'game'
                      ? 'Игровой'
                      : 'Эмоциональный'}
                  </p>
                </div>
                <div className="frosted-card">
                  <span className="text-white/60">Сложность</span>
                  <p className="text-white font-medium">
                    {questData.difficulty === 'easy'
                      ? 'Лёгкий'
                      : questData.difficulty === 'medium'
                      ? 'Средний'
                      : 'Сложный'}
                  </p>
                </div>
                <div className="frosted-card">
                  <span className="text-white/60">Время</span>
                  <p className="text-white font-medium">{questData.duration} мин</p>
                </div>
              </div>

              <div>
                <h5 className="text-white font-medium mb-3">
                  Задания ({questData.tasks.length})
                </h5>
                <div className="space-y-2">
                  {questData.tasks.map((task, index) => (
                    <div
                      key={index}
                      className="bg-white/5 rounded-lg p-3 hover:bg-white/10 transition-colors"
                    >
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-blue-400 font-bold">#{index + 1}</span>
                        <h6 className="text-white font-medium">{task.title}</h6>
                        <span className="ml-auto text-xs px-2 py-1 rounded-full bg-purple-500/20 text-purple-300">
                          {task.type === 'question'
                            ? 'Вопрос'
                            : task.type === 'activity'
                            ? 'Активность'
                            : 'Рефлексия'}
                        </span>
                      </div>
                      <p className="text-sm text-white/70">{task.description}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </div>
    </DashboardLayout>
  );
}

export default function QuestBuilderPage() {
  return (
    <ProtectedRoute>
      <QuestBuilderContent />
    </ProtectedRoute>
  );
}
