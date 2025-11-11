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
import { QuestFlowVisualizer, QuestFlowNode, QuestFlowEdge } from '../../components/QuestFlow/QuestFlowVisualizer';

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

  // Mind map state
  const [mindMapNodes, setMindMapNodes] = useState<QuestFlowNode[]>([]);
  const [mindMapEdges, setMindMapEdges] = useState<QuestFlowEdge[]>([]);
  const [selectedNode, setSelectedNode] = useState<QuestFlowNode | null>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Update mind map as conversation progresses
  useEffect(() => {
    const nodes: QuestFlowNode[] = [];
    const edges: QuestFlowEdge[] = [];

    if (currentStep >= 1) {
      // Start node (always visible)
      nodes.push({
        id: 'start',
        type: 'start',
        position: { x: 250, y: 50 },
        data: {
          title: 'Начало квеста',
          description: questData.childAge ? `Для ребёнка ${questData.childAge} лет` : 'Создаём квест...',
        },
      });
    }

    if (currentStep >= 2 && questData.childInterests && questData.childInterests.length > 0) {
      // Theme node
      nodes.push({
        id: 'theme',
        type: 'question',
        position: { x: 250, y: 180 },
        data: {
          title: 'Тема квеста',
          description: questData.childInterests.join(', '),
        },
      });
      edges.push({ id: 'e-start-theme', source: 'start', target: 'theme' });
    }

    if (currentStep >= 3 && questData.tasks && questData.tasks.length > 0) {
      // Task nodes (spread horizontally)
      const tasksPerRow = 3;
      questData.tasks.forEach((task, index) => {
        const row = Math.floor(index / tasksPerRow);
        const col = index % tasksPerRow;
        const xOffset = col * 200 - ((tasksPerRow - 1) * 200) / 2;

        nodes.push({
          id: `task-${index}`,
          type: task.type === 'reflection' ? 'choice' : task.type === 'question' ? 'question' : 'activity',
          position: { x: 250 + xOffset, y: 320 + row * 150 },
          data: {
            title: task.title,
            description: task.description.substring(0, 60) + '...',
          },
        });

        // Connect first task to theme, others to previous task
        if (index === 0) {
          edges.push({ id: `e-theme-task-${index}`, source: 'theme', target: `task-${index}` });
        } else {
          edges.push({ id: `e-task-${index - 1}-task-${index}`, source: `task-${index - 1}`, target: `task-${index}` });
        }
      });

      if (isComplete) {
        // End node
        nodes.push({
          id: 'end',
          type: 'end',
          position: { x: 250, y: 320 + Math.ceil(questData.tasks.length / tasksPerRow) * 150 },
          data: {
            title: 'Квест завершён!',
            description: `${questData.duration} минут`,
          },
        });
        edges.push({
          id: `e-task-${questData.tasks.length - 1}-end`,
          source: `task-${questData.tasks.length - 1}`,
          target: 'end',
        });
      }
    }

    setMindMapNodes(nodes);
    setMindMapEdges(edges);
  }, [currentStep, questData, isComplete]);

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

  const handleNodeClick = (node: QuestFlowNode) => {
    setSelectedNode(node);
  };

  const handleNodesChange = (updatedNodes: QuestFlowNode[]) => {
    setMindMapNodes(updatedNodes);
  };

  const handleEdgesChange = (updatedEdges: QuestFlowEdge[]) => {
    setMindMapEdges(updatedEdges);
  };

  // Get AI-only messages for chat log
  const aiMessages = messages.filter((m) => m.role === 'assistant');

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
      {/* Fullscreen Mind Map */}
      <div className="fixed inset-0 -mt-20" style={{ paddingTop: '80px' }}>
        <QuestFlowVisualizer
          nodes={mindMapNodes}
          edges={mindMapEdges}
          mode="edit"
          onNodeClick={handleNodeClick}
          onNodesChange={handleNodesChange}
          onEdgesChange={handleEdgesChange}
          className="w-full h-full"
        />
      </div>

      {/* Floating Chat Log (right bottom) */}
      <motion.div
        className="fixed right-6 bottom-32 w-80 h-64 liquid-glass rounded-2xl shadow-2xl z-10 flex flex-col overflow-hidden border border-white/20"
        initial={{ opacity: 0, x: 100 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="p-3 border-b border-white/10 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Wand2 className="w-4 h-4 text-purple-400" />
            <h3 className="text-sm font-bold text-white">AI Действия</h3>
          </div>
          <span className="text-xs text-white/50">
            Шаг {currentStep}/4
          </span>
        </div>

        <div className="flex-1 overflow-y-auto p-3 space-y-2 scrollbar-glass">
          <AnimatePresence>
            {aiMessages.map((message) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                className="text-xs text-white/80 bg-white/5 rounded-lg p-2"
              >
                <span className="text-purple-400 font-medium">AI:</span>{' '}
                {message.content.split('\n')[0].substring(0, 100)}...
              </motion.div>
            ))}
          </AnimatePresence>
          <div ref={messagesEndRef} />
        </div>
      </motion.div>

      {/* Progress bar (top right) */}
      <motion.div
        className="fixed top-24 right-6 liquid-glass rounded-xl p-4 z-10 w-64"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-medium text-white/70">
            Прогресс квеста
          </span>
          <span className="text-xs font-bold text-white">
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
        <div className="mt-2 text-xs text-white/60">
          {mindMapNodes.length} узлов • {mindMapEdges.length} связей
        </div>
      </motion.div>

      {/* Input bar (center bottom) */}
      <motion.div
        className="fixed bottom-6 left-1/2 -translate-x-1/2 w-full max-w-2xl px-6 z-20"
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="liquid-glass rounded-2xl shadow-2xl p-4 border border-white/20">
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
                onClick={() => router.push('/dashboard')}
                className="glass-button bg-purple-500/20 hover:bg-purple-500/30 flex items-center gap-2"
              >
                <Eye className="w-4 h-4" />
                На Dashboard
              </button>
            </div>
          ) : (
            <div className="flex gap-3 items-center">
              {isLoading && (
                <Loader className="w-5 h-5 animate-spin text-purple-400" />
              )}
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Введи свой ответ..."
                disabled={isLoading}
                className="flex-1 bg-white/10 rounded-xl px-4 py-3 text-white placeholder:text-white/50 focus:outline-none focus:ring-2 focus:ring-purple-400/50 disabled:opacity-50"
              />
              <button
                onClick={handleSendMessage}
                disabled={!input.trim() || isLoading}
                className="glass-button bg-purple-500/20 hover:bg-purple-500/30 disabled:opacity-50 disabled:cursor-not-allowed p-3"
              >
                <Send className="w-5 h-5" />
              </button>
            </div>
          )}
        </div>
      </motion.div>

      {/* Node Details Modal */}
      <AnimatePresence>
        {selectedNode && (
          <motion.div
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-30 flex items-center justify-center p-6"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setSelectedNode(null)}
          >
            <motion.div
              className="liquid-glass rounded-2xl shadow-2xl max-w-lg w-full p-6 border border-white/20"
              initial={{ scale: 0.9, y: 20 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.9, y: 20 }}
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-bold text-white">
                  {selectedNode.data.title}
                </h3>
                <button
                  onClick={() => setSelectedNode(null)}
                  className="text-white/50 hover:text-white transition-colors"
                >
                  ✕
                </button>
              </div>

              <div className="space-y-4">
                <div>
                  <span className="text-xs font-semibold text-white/50 uppercase tracking-wider">
                    Тип узла
                  </span>
                  <p className="text-white mt-1 capitalize">{selectedNode.type}</p>
                </div>

                {selectedNode.data.description && (
                  <div>
                    <span className="text-xs font-semibold text-white/50 uppercase tracking-wider">
                      Описание
                    </span>
                    <p className="text-white/80 mt-1 text-sm">
                      {selectedNode.data.description}
                    </p>
                  </div>
                )}

                <div>
                  <span className="text-xs font-semibold text-white/50 uppercase tracking-wider">
                    Связи
                  </span>
                  <div className="mt-2 space-y-1">
                    {mindMapEdges
                      .filter(
                        (e) =>
                          e.source === selectedNode.id ||
                          e.target === selectedNode.id
                      )
                      .map((edge) => (
                        <div
                          key={edge.id}
                          className="text-xs text-white/70 bg-white/5 rounded px-2 py-1"
                        >
                          {edge.source === selectedNode.id ? '→' : '←'}{' '}
                          {edge.source === selectedNode.id
                            ? mindMapNodes.find((n) => n.id === edge.target)
                                ?.data.title
                            : mindMapNodes.find((n) => n.id === edge.source)
                                ?.data.title}
                        </div>
                      ))}
                    {mindMapEdges.filter(
                      (e) =>
                        e.source === selectedNode.id ||
                        e.target === selectedNode.id
                    ).length === 0 && (
                      <p className="text-xs text-white/50">Нет связей</p>
                    )}
                  </div>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
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
