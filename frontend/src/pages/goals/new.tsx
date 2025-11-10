/**
 * Goals Manager Page - Set and track recovery goals
 *
 * Protected route - requires authentication
 */

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Save,
  ArrowLeft,
  Target,
  Calendar,
  Flag,
  CheckCircle,
  Plus,
  X,
  Brain,
  Heart,
  MessageCircle,
  Users,
  Sparkles,
} from 'lucide-react';
import { useRouter } from 'next/router';
import { ProtectedRoute } from '../../components/Auth/ProtectedRoute';
import { DashboardLayout } from '../../components/Dashboard';

type TrackType = 'self-care' | 'child-bond' | 'negotiation' | 'community';
type GoalDifficulty = 'easy' | 'medium' | 'hard';

interface Milestone {
  id: string;
  title: string;
  description: string;
  deadline?: string;
}

interface GoalData {
  track: TrackType;
  title: string;
  description: string;
  difficulty: GoalDifficulty;
  deadline: string;
  milestones: Milestone[];
  isRecurring: boolean;
  reminderEnabled: boolean;
}

function GoalsManagerContent() {
  const router = useRouter();
  const [selectedTrack, setSelectedTrack] = useState<TrackType | null>(null);
  const [goalData, setGoalData] = useState<GoalData>({
    track: 'self-care',
    title: '',
    description: '',
    difficulty: 'medium',
    deadline: '',
    milestones: [],
    isRecurring: false,
    reminderEnabled: true,
  });
  const [newMilestone, setNewMilestone] = useState('');

  const tracks = [
    {
      type: 'self-care' as TrackType,
      name: 'Работа над собой',
      emoji: '🧘',
      icon: <Brain className="w-6 h-6" />,
      color: 'blue',
      description: 'Эмоциональное благополучие и саморазвитие',
      exampleGoals: [
        'Медитировать 10 минут каждый день',
        'Вести дневник эмоций',
        'Посетить 5 сессий с психологом',
      ],
    },
    {
      type: 'child-bond' as TrackType,
      name: 'Связь с ребёнком',
      emoji: '❤️',
      icon: <Heart className="w-6 h-6" />,
      color: 'purple',
      description: 'Восстановление эмоциональной связи',
      exampleGoals: [
        'Создать 3 персонализированных квеста',
        'Написать письмо благодарности',
        'Записать видео-воспоминание',
      ],
    },
    {
      type: 'negotiation' as TrackType,
      name: 'Переговоры',
      emoji: '🤝',
      icon: <MessageCircle className="w-6 h-6" />,
      color: 'pink',
      description: 'Коммуникация с другим родителем',
      exampleGoals: [
        'Составить предложение о графике встреч',
        'Провести медиацию',
        'Установить правила общения',
      ],
    },
    {
      type: 'community' as TrackType,
      name: 'Сообщество',
      emoji: '👥',
      icon: <Users className="w-6 h-6" />,
      color: 'green',
      description: 'Поддержка других родителей',
      exampleGoals: [
        'Присоединиться к группе поддержки',
        'Поделиться опытом в сообществе',
        'Помочь другому родителю',
      ],
    },
  ];

  const handleAddMilestone = () => {
    if (!newMilestone.trim()) return;

    const milestone: Milestone = {
      id: Date.now().toString(),
      title: newMilestone,
      description: '',
    };

    setGoalData({
      ...goalData,
      milestones: [...goalData.milestones, milestone],
    });
    setNewMilestone('');
  };

  const handleRemoveMilestone = (id: string) => {
    setGoalData({
      ...goalData,
      milestones: goalData.milestones.filter((m) => m.id !== id),
    });
  };

  const handleSelectTrack = (track: TrackType) => {
    setSelectedTrack(track);
    setGoalData({ ...goalData, track });
  };

  const handleSave = () => {
    // TODO: Save to backend
    router.push('/analytics');
  };

  if (!selectedTrack) {
    return (
      <DashboardLayout
        title="Поставить цель"
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
          {/* Header */}
          <motion.div
            className="text-center mb-12"
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <div className="text-6xl mb-4">🎯</div>
            <h2 className="text-3xl font-bold text-white mb-2">
              Выберите трек восстановления
            </h2>
            <p className="text-white/70">
              Создайте цель для одного из 4 треков
            </p>
          </motion.div>

          {/* Track selection */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {tracks.map((track, index) => (
              <motion.button
                key={track.type}
                onClick={() => handleSelectTrack(track.type)}
                className="frosted-card text-left hover:scale-105 transition-all group"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                whileHover={{ y: -4 }}
              >
                <div className="flex items-center gap-4 mb-4">
                  <div
                    className={`
                    w-16 h-16 rounded-2xl flex items-center justify-center text-3xl
                    ${track.color === 'blue' && 'bg-blue-500/20'}
                    ${track.color === 'purple' && 'bg-purple-500/20'}
                    ${track.color === 'pink' && 'bg-pink-500/20'}
                    ${track.color === 'green' && 'bg-green-500/20'}
                    group-hover:scale-110 transition-transform
                  `}
                  >
                    {track.emoji}
                  </div>
                  <div className="flex-1">
                    <h3 className="text-xl font-bold text-white mb-1 group-hover:text-blue-400 transition-colors">
                      {track.name}
                    </h3>
                    <p className="text-sm text-white/70">{track.description}</p>
                  </div>
                </div>

                {/* Example goals */}
                <div className="space-y-2">
                  <p className="text-xs font-medium text-white/50 uppercase tracking-wider">
                    Примеры целей:
                  </p>
                  {track.exampleGoals.map((goal, i) => (
                    <div key={i} className="flex items-start gap-2 text-sm text-white/70">
                      <CheckCircle className="w-4 h-4 flex-shrink-0 mt-0.5 text-green-400" />
                      <span>{goal}</span>
                    </div>
                  ))}
                </div>
              </motion.button>
            ))}
          </div>
        </div>
      </DashboardLayout>
    );
  }

  const currentTrack = tracks.find((t) => t.type === selectedTrack);

  return (
    <DashboardLayout
      title={`Цель: ${currentTrack?.name}`}
      actions={
        <div className="flex gap-2">
          <button
            onClick={handleSave}
            className="glass-button bg-blue-500/20 hover:bg-blue-500/30 flex items-center gap-2"
          >
            <Save className="w-4 h-4" />
            Сохранить
          </button>
        </div>
      }
    >
      <div className="max-w-4xl mx-auto">
        {/* Track indicator */}
        <motion.div
          className="frosted-card mb-6 flex items-center gap-4"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="text-4xl">{currentTrack?.emoji}</div>
          <div className="flex-1">
            <h3 className="text-lg font-bold text-white">{currentTrack?.name}</h3>
            <p className="text-sm text-white/70">{currentTrack?.description}</p>
          </div>
          <button
            onClick={() => setSelectedTrack(null)}
            className="glass-button bg-white/10 hover:bg-white/20 text-sm"
          >
            Изменить трек
          </button>
        </motion.div>

        {/* Goal form */}
        <motion.div
          className="space-y-6"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          {/* Title */}
          <div className="frosted-card">
            <label className="block text-sm font-medium text-white/70 mb-2 flex items-center gap-2">
              <Target className="w-4 h-4 text-blue-400" />
              Название цели
            </label>
            <input
              type="text"
              value={goalData.title}
              onChange={(e) =>
                setGoalData({ ...goalData, title: e.target.value })
              }
              placeholder="Например: Медитировать каждый день в течение недели"
              className="w-full bg-white/5 rounded-xl px-4 py-3 text-white placeholder:text-white/50 focus:outline-none focus:ring-2 focus:ring-blue-400/50"
            />
          </div>

          {/* Description */}
          <div className="frosted-card">
            <label className="block text-sm font-medium text-white/70 mb-2">
              Описание (необязательно)
            </label>
            <textarea
              value={goalData.description}
              onChange={(e) =>
                setGoalData({ ...goalData, description: e.target.value })
              }
              rows={4}
              placeholder="Опишите, что вы хотите достичь и почему это важно для вас..."
              className="w-full bg-white/5 rounded-xl px-4 py-3 text-white placeholder:text-white/50 focus:outline-none focus:ring-2 focus:ring-blue-400/50 resize-none"
            />
          </div>

          {/* Difficulty and deadline */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Difficulty */}
            <div className="frosted-card">
              <label className="block text-sm font-medium text-white/70 mb-3 flex items-center gap-2">
                <Flag className="w-4 h-4 text-purple-400" />
                Сложность
              </label>
              <div className="space-y-2">
                {(['easy', 'medium', 'hard'] as GoalDifficulty[]).map((diff) => (
                  <button
                    key={diff}
                    onClick={() => setGoalData({ ...goalData, difficulty: diff })}
                    className={`
                      w-full text-left px-4 py-3 rounded-lg transition-all
                      ${
                        goalData.difficulty === diff
                          ? 'bg-purple-500/20 text-white ring-2 ring-purple-400'
                          : 'bg-white/5 text-white/70 hover:bg-white/10'
                      }
                    `}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-medium">
                        {diff === 'easy' && '🟢 Лёгкая'}
                        {diff === 'medium' && '🟡 Средняя'}
                        {diff === 'hard' && '🔴 Сложная'}
                      </span>
                      {goalData.difficulty === diff && (
                        <CheckCircle className="w-5 h-5 text-purple-400" />
                      )}
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* Deadline */}
            <div className="frosted-card">
              <label className="block text-sm font-medium text-white/70 mb-3 flex items-center gap-2">
                <Calendar className="w-4 h-4 text-cyan-400" />
                Срок выполнения
              </label>
              <input
                type="date"
                value={goalData.deadline}
                onChange={(e) =>
                  setGoalData({ ...goalData, deadline: e.target.value })
                }
                className="w-full bg-white/5 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-blue-400/50"
              />
              <p className="text-xs text-white/50 mt-2">
                Выберите реалистичный срок для достижения цели
              </p>
            </div>
          </div>

          {/* Milestones */}
          <div className="frosted-card">
            <div className="flex items-center justify-between mb-4">
              <label className="text-sm font-medium text-white/70 flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-yellow-400" />
                Этапы (милестоуны)
              </label>
              <span className="text-xs text-white/50">
                {goalData.milestones.length} этапов
              </span>
            </div>

            {/* Milestone list */}
            <AnimatePresence>
              {goalData.milestones.length > 0 && (
                <div className="space-y-2 mb-4">
                  {goalData.milestones.map((milestone, index) => (
                    <motion.div
                      key={milestone.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: 20 }}
                      className="flex items-center gap-3 bg-white/5 rounded-lg p-3 group"
                    >
                      <span className="text-blue-400 font-bold text-sm">
                        #{index + 1}
                      </span>
                      <span className="flex-1 text-white text-sm">
                        {milestone.title}
                      </span>
                      <button
                        onClick={() => handleRemoveMilestone(milestone.id)}
                        className="opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-red-500/20 rounded"
                      >
                        <X className="w-4 h-4 text-red-400" />
                      </button>
                    </motion.div>
                  ))}
                </div>
              )}
            </AnimatePresence>

            {/* Add milestone */}
            <div className="flex gap-2">
              <input
                type="text"
                value={newMilestone}
                onChange={(e) => setNewMilestone(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') handleAddMilestone();
                }}
                placeholder="Добавить этап..."
                className="flex-1 bg-white/5 rounded-lg px-3 py-2 text-white placeholder:text-white/50 focus:outline-none focus:ring-2 focus:ring-blue-400/50 text-sm"
              />
              <button
                onClick={handleAddMilestone}
                className="glass-button bg-blue-500/20 hover:bg-blue-500/30 p-2"
              >
                <Plus className="w-4 h-4" />
              </button>
            </div>
            <p className="text-xs text-white/50 mt-2">
              Разбейте цель на маленькие шаги для более легкого достижения
            </p>
          </div>

          {/* Settings */}
          <div className="frosted-card space-y-4">
            <h4 className="text-sm font-medium text-white/70 mb-4">
              Настройки цели
            </h4>

            {/* Recurring */}
            <div className="flex items-center justify-between">
              <div>
                <h5 className="text-white font-medium">Повторяющаяся цель</h5>
                <p className="text-sm text-white/60">
                  Автоматически создавать новую цель после завершения
                </p>
              </div>
              <button
                onClick={() =>
                  setGoalData({
                    ...goalData,
                    isRecurring: !goalData.isRecurring,
                  })
                }
                className={`
                  relative w-12 h-6 rounded-full transition-colors
                  ${goalData.isRecurring ? 'bg-blue-500' : 'bg-white/20'}
                `}
              >
                <motion.div
                  className="absolute top-1 w-4 h-4 rounded-full bg-white"
                  animate={{
                    left: goalData.isRecurring ? '28px' : '4px',
                  }}
                  transition={{ type: 'spring', stiffness: 500, damping: 30 }}
                />
              </button>
            </div>

            {/* Reminders */}
            <div className="flex items-center justify-between pt-4 border-t border-white/10">
              <div>
                <h5 className="text-white font-medium">Напоминания</h5>
                <p className="text-sm text-white/60">
                  Получать уведомления о прогрессе
                </p>
              </div>
              <button
                onClick={() =>
                  setGoalData({
                    ...goalData,
                    reminderEnabled: !goalData.reminderEnabled,
                  })
                }
                className={`
                  relative w-12 h-6 rounded-full transition-colors
                  ${goalData.reminderEnabled ? 'bg-purple-500' : 'bg-white/20'}
                `}
              >
                <motion.div
                  className="absolute top-1 w-4 h-4 rounded-full bg-white"
                  animate={{
                    left: goalData.reminderEnabled ? '28px' : '4px',
                  }}
                  transition={{ type: 'spring', stiffness: 500, damping: 30 }}
                />
              </button>
            </div>
          </div>

          {/* Save button */}
          <button
            onClick={handleSave}
            disabled={!goalData.title}
            className="w-full glass-button bg-gradient-to-r from-blue-500/20 to-purple-500/20 hover:from-blue-500/30 hover:to-purple-500/30 disabled:opacity-50 disabled:cursor-not-allowed py-4 text-lg font-medium flex items-center justify-center gap-2"
          >
            <Save className="w-5 h-5" />
            Сохранить цель
          </button>
        </motion.div>
      </div>
    </DashboardLayout>
  );
}

export default function GoalsManagerPage() {
  return (
    <ProtectedRoute>
      <GoalsManagerContent />
    </ProtectedRoute>
  );
}
