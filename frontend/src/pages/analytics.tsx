/**
 * Analytics Page - Progress analytics and insights
 *
 * Protected route - requires authentication
 */

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  TrendingUp,
  TrendingDown,
  Calendar,
  Activity,
  Heart,
  Mail,
  Target,
} from 'lucide-react';
import { ProtectedRoute } from '../components/Auth/ProtectedRoute';
import { DashboardLayout, TrackCard } from '../components/Dashboard';
import { ProgressRing } from '../components/LiquidGlass';

type PeriodType = '7d' | '30d' | '90d';

function AnalyticsContent() {
  const [period, setPeriod] = useState<PeriodType>('30d');

  // Mock analytics data
  const stats = {
    questsCreated: 5,
    questsCompleted: 2,
    lettersSent: 8,
    goalsAchieved: 12,
    totalTimeSpent: 420, // minutes
    avgEngagement: 78,
  };

  const mockTracks = [
    {
      id: 'self',
      name: 'Работа над собой',
      description: 'Эмоциональное благополучие и саморазвитие',
      color: '#60a5fa',
      progress: 65,
      currentPhase: 'Фаза 3: Активная работа',
      milestones: [
        {
          id: 'm1',
          title: 'Начать медитацию',
          description: '7 дней подряд по 10 минут',
          completed: true,
          completedAt: '2025-11-05',
        },
        {
          id: 'm2',
          title: 'Вести дневник эмоций',
          description: 'Записывать свои чувства каждый день',
          completed: true,
          completedAt: '2025-11-08',
        },
        {
          id: 'm3',
          title: 'Консультация психолога',
          description: 'Первая сессия с психологом',
          completed: false,
        },
      ],
      nextAction: 'Запланируйте первую консультацию с психологом на этой неделе',
      isPrimary: true,
    },
    {
      id: 'child',
      name: 'Связь с ребёнком',
      description: 'Восстановление эмоциональной связи',
      color: '#a78bfa',
      progress: 45,
      currentPhase: 'Фаза 2: Фундамент',
      milestones: [
        {
          id: 'm4',
          title: 'Создать первый квест',
          description: 'Персонализированный квест для ребёнка',
          completed: true,
          completedAt: '2025-11-09',
        },
        {
          id: 'm5',
          title: 'Отправить письмо',
          description: 'Написать письмо благодарности',
          completed: true,
          completedAt: '2025-11-08',
        },
        {
          id: 'm6',
          title: 'Записать видео',
          description: 'Короткое видео с воспоминанием',
          completed: false,
        },
      ],
      nextAction: 'Запишите короткое видео (1-2 минуты) с тёплым воспоминанием о совместном времени',
    },
    {
      id: 'negotiation',
      name: 'Переговоры',
      description: 'Коммуникация с другим родителем',
      color: '#f472b6',
      progress: 30,
      currentPhase: 'Фаза 2: Фундамент',
      milestones: [
        {
          id: 'm7',
          title: 'Анализ ситуации',
          description: 'Понять позиции и интересы',
          completed: true,
          completedAt: '2025-11-06',
        },
        {
          id: 'm8',
          title: 'Подготовить предложение',
          description: 'Составить конструктивное предложение',
          completed: false,
        },
      ],
      nextAction: 'Составьте письменное предложение о графике встреч с ребёнком',
    },
    {
      id: 'community',
      name: 'Сообщество',
      description: 'Поддержка других родителей',
      color: '#34d399',
      progress: 50,
      currentPhase: 'Фаза 2: Фундамент',
      milestones: [
        {
          id: 'm9',
          title: 'Присоединиться к группе',
          description: 'Найти группу поддержки',
          completed: true,
          completedAt: '2025-11-07',
        },
        {
          id: 'm10',
          title: 'Поделиться опытом',
          description: 'Рассказать свою историю',
          completed: false,
        },
      ],
      nextAction: 'Поделитесь своим опытом в группе поддержки - это поможет и вам, и другим родителям',
    },
  ];

  // Mock emotional trends data
  const emotionalTrends = [
    { date: '04.11', mood: 'neutral', score: 50 },
    { date: '05.11', mood: 'happy', score: 70 },
    { date: '06.11', mood: 'sad', score: 40 },
    { date: '07.11', mood: 'happy', score: 75 },
    { date: '08.11', mood: 'happy', score: 80 },
    { date: '09.11', mood: 'neutral', score: 65 },
    { date: '10.11', mood: 'happy', score: 85 },
  ];

  return (
    <DashboardLayout
      title="Аналитика"
      actions={
        <div className="flex gap-2">
          {(['7d', '30d', '90d'] as PeriodType[]).map((p) => (
            <button
              key={p}
              onClick={() => setPeriod(p)}
              className={`
                px-3 py-1.5 rounded-lg text-sm font-medium transition-all
                ${
                  period === p
                    ? 'bg-blue-500/30 text-white'
                    : 'bg-white/5 text-white/70 hover:bg-white/10'
                }
              `}
            >
              {p === '7d' && '7 дней'}
              {p === '30d' && '30 дней'}
              {p === '90d' && '90 дней'}
            </button>
          ))}
        </div>
      }
    >
      {/* Overview Stats */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-12">
        <StatCard
          icon={<Activity className="w-5 h-5" />}
          label="Квесты создано"
          value={stats.questsCreated}
          trend={+20}
          color="blue"
        />
        <StatCard
          icon={<Target className="w-5 h-5" />}
          label="Квесты завершено"
          value={stats.questsCompleted}
          trend={+50}
          color="green"
        />
        <StatCard
          icon={<Mail className="w-5 h-5" />}
          label="Писем отправлено"
          value={stats.lettersSent}
          trend={+10}
          color="pink"
        />
        <StatCard
          icon={<Target className="w-5 h-5" />}
          label="Целей достигнуто"
          value={stats.goalsAchieved}
          trend={+25}
          color="purple"
        />
        <StatCard
          icon={<Calendar className="w-5 h-5" />}
          label="Время (мин)"
          value={stats.totalTimeSpent}
          trend={+15}
          color="cyan"
        />
        <StatCard
          icon={<Heart className="w-5 h-5" />}
          label="Вовлечённость"
          value={`${stats.avgEngagement}%`}
          trend={+8}
          color="red"
        />
      </div>

      {/* Emotional Trends Chart */}
      <motion.div
        className="frosted-card mb-12"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <h3 className="text-xl font-bold text-white mb-6">Эмоциональные тренды</h3>

        {/* Simple bar chart */}
        <div className="space-y-4">
          {emotionalTrends.map((day, index) => (
            <div key={index} className="flex items-center gap-4">
              <span className="text-sm text-white/60 w-16">{day.date}</span>
              <div className="flex-1 h-8 bg-white/5 rounded-lg overflow-hidden">
                <motion.div
                  className="h-full rounded-lg flex items-center px-3"
                  style={{
                    backgroundColor:
                      day.mood === 'happy'
                        ? '#34d399'
                        : day.mood === 'sad'
                        ? '#f472b6'
                        : '#60a5fa',
                  }}
                  initial={{ width: 0 }}
                  animate={{ width: `${day.score}%` }}
                  transition={{ duration: 0.8, delay: index * 0.1 }}
                >
                  <span className="text-xs font-medium text-white">
                    {day.score}%
                  </span>
                </motion.div>
              </div>
              <span className="text-2xl">
                {day.mood === 'happy' && '😊'}
                {day.mood === 'sad' && '😔'}
                {day.mood === 'neutral' && '😐'}
              </span>
            </div>
          ))}
        </div>
      </motion.div>

      {/* Recovery Tracks Progress */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <h3 className="text-2xl font-bold text-white mb-6">
          Прогресс по трекам восстановления
        </h3>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {mockTracks.map((track) => (
            <TrackCard
              key={track.id}
              {...track}
              onToggleMilestone={(milestoneId) => {
                console.log('Toggle milestone:', milestoneId);
              }}
            />
          ))}
        </div>
      </motion.div>
    </DashboardLayout>
  );
}

// Stat Card Component
interface StatCardProps {
  icon: React.ReactNode;
  label: string;
  value: number | string;
  trend?: number;
  color: string;
}

const StatCard: React.FC<StatCardProps> = ({ icon, label, value, trend, color }) => {
  const colorClasses = {
    blue: 'from-blue-500/20 to-blue-600/20 border-blue-400/30',
    green: 'from-green-500/20 to-green-600/20 border-green-400/30',
    pink: 'from-pink-500/20 to-pink-600/20 border-pink-400/30',
    purple: 'from-purple-500/20 to-purple-600/20 border-purple-400/30',
    cyan: 'from-cyan-500/20 to-cyan-600/20 border-cyan-400/30',
    red: 'from-red-500/20 to-red-600/20 border-red-400/30',
  };

  return (
    <motion.div
      className={`frosted-card bg-gradient-to-br ${colorClasses[color as keyof typeof colorClasses]}`}
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
    >
      <div className="flex items-center justify-between mb-2">
        <div className="text-white/70">{icon}</div>
        {trend !== undefined && (
          <div
            className={`flex items-center gap-1 text-xs font-medium ${
              trend > 0 ? 'text-green-400' : 'text-red-400'
            }`}
          >
            {trend > 0 ? (
              <TrendingUp className="w-3 h-3" />
            ) : (
              <TrendingDown className="w-3 h-3" />
            )}
            {Math.abs(trend)}%
          </div>
        )}
      </div>
      <div className="text-2xl font-bold text-white mb-1">{value}</div>
      <div className="text-xs text-white/60">{label}</div>
    </motion.div>
  );
};

export default function AnalyticsPage() {
  return (
    <ProtectedRoute>
      <AnalyticsContent />
    </ProtectedRoute>
  );
}
