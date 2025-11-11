/**
 * Dashboard Page - Main application dashboard with Sidebar
 *
 * Protected route - requires authentication
 */

import React from 'react';
import { motion } from 'framer-motion';
import { Sparkles, Mail, Target } from 'lucide-react';
import { ProtectedRoute } from '../components/Auth/ProtectedRoute';
import { DashboardLayout, QuickActions } from '../components/Dashboard';
import { MultiProgressRing } from '../components/LiquidGlass';
import { useUserStore } from '../lib/stores/userStore';

function DashboardContent() {
  const { user } = useUserStore();

  // Mock track data for demo
  const mockTracks = [
    { id: 'self', name: 'Работа над собой', progress: 25, color: '#60a5fa' },
    { id: 'child', name: 'Связь с ребёнком', progress: 15, color: '#a78bfa' },
    { id: 'negotiation', name: 'Переговоры', progress: 10, color: '#f472b6' },
    { id: 'community', name: 'Сообщество', progress: 20, color: '#34d399' },
  ];

  return (
    <DashboardLayout title="Dashboard">
      {/* Welcome section */}
      <motion.div
        className="mb-12"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h2 className="text-3xl font-bold text-white mb-2">
          Добро пожаловать, {user?.first_name}!
        </h2>
        <p className="text-white/70 text-lg">
          Ваш путь восстановления связи с ребёнком
        </p>
      </motion.div>

      {/* Recovery tracks */}
      <motion.div
        className="mb-12"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
      >
        <div className="frosted-card">
          <h3 className="text-2xl font-bold text-white mb-8 text-center">
            Прогресс по 4 трекам восстановления
          </h3>

          <div className="flex justify-center mb-16">
            <MultiProgressRing tracks={mockTracks} size={280} />
          </div>

          {/* Track descriptions */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {mockTracks.map((track) => (
              <div
                key={track.id}
                className="liquid-glass-hover p-4 text-center cursor-pointer"
              >
                <div
                  className="w-3 h-3 rounded-full mx-auto mb-2"
                  style={{ backgroundColor: track.color }}
                />
                <p className="text-white font-medium text-sm mb-1">
                  {track.name}
                </p>
                <p className="text-white/60 text-xs">
                  {track.progress}% завершено
                </p>
              </div>
            ))}
          </div>
        </div>
      </motion.div>

      {/* Quick actions */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
      >
        <h3 className="text-2xl font-bold text-white mb-6">Быстрые действия</h3>
        <QuickActions />
      </motion.div>

      {/* Recent activity (placeholder) */}
      <motion.div
        className="mt-12"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.3 }}
      >
        <div className="frosted-card">
          <h3 className="text-xl font-bold text-white mb-4">
            Недавняя активность
          </h3>
          <div className="space-y-3">
            {[
              { icon: <Sparkles className="w-5 h-5 text-yellow-400" />, text: 'Создан квест "Тайна зоопарка"', time: '2 часа назад' },
              { icon: <Mail className="w-5 h-5 text-pink-400" />, text: 'Отправлено письмо благодарности', time: 'Вчера' },
              { icon: <Target className="w-5 h-5 text-green-400" />, text: 'Достигнута цель: "Медитация 7 дней"', time: '3 дня назад' },
            ].map((item, index) => (
              <div
                key={index}
                className="flex items-center gap-4 p-3 rounded-lg hover:bg-white/5 transition-colors"
              >
                <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-white/5">
                  {item.icon}
                </div>
                <div className="flex-1">
                  <p className="text-white font-medium text-sm">{item.text}</p>
                  <p className="text-white/50 text-xs">{item.time}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </motion.div>
    </DashboardLayout>
  );
}

export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <DashboardContent />
    </ProtectedRoute>
  );
}
