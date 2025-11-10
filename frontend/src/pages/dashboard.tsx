/**
 * Dashboard Page - Main application dashboard
 *
 * Protected route - requires authentication
 */

import React from 'react';
import { motion } from 'framer-motion';
import { LogOut, Settings, Sparkles } from 'lucide-react';
import { ProtectedRoute } from '../components/Auth/ProtectedRoute';
import { useUserStore } from '../lib/stores/userStore';
import { useLogout } from '../lib/hooks/useAuth';
import { MultiProgressRing } from '../components/LiquidGlass';

function DashboardContent() {
  const { user } = useUserStore();
  const { mutate: logout, isLoading: isLoggingOut } = useLogout();

  const handleLogout = () => {
    logout();
  };

  // Mock track data for demo
  const mockTracks = [
    { id: 'self', name: 'Работа над собой', progress: 25, color: '#60a5fa' },
    { id: 'child', name: 'Связь с ребёнком', progress: 15, color: '#a78bfa' },
    { id: 'negotiation', name: 'Переговоры', progress: 10, color: '#f472b6' },
    { id: 'community', name: 'Сообщество', progress: 20, color: '#34d399' },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <header className="liquid-glass-hover border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            {/* Logo */}
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-400 to-purple-400 flex items-center justify-center">
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              <h1 className="text-xl font-bold text-white">PAS in Peace</h1>
            </div>

            {/* User info + actions */}
            <div className="flex items-center gap-4">
              {/* User name */}
              {user && (
                <div className="text-right">
                  <p className="text-white font-medium">{user.first_name}</p>
                  {user.username && (
                    <p className="text-white/60 text-sm">@{user.username}</p>
                  )}
                </div>
              )}

              {/* Avatar */}
              {user?.photo_url ? (
                <img
                  src={user.photo_url}
                  alt={user.first_name}
                  className="w-10 h-10 rounded-full border-2 border-white/20"
                />
              ) : (
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-400 to-pink-400 flex items-center justify-center text-white font-bold">
                  {user?.first_name?.[0]?.toUpperCase() || 'U'}
                </div>
              )}

              {/* Settings button */}
              <button
                className="p-2 rounded-lg hover:bg-white/10 transition-colors"
                aria-label="Settings"
              >
                <Settings className="w-5 h-5 text-white/70 hover:text-white" />
              </button>

              {/* Logout button */}
              <button
                onClick={handleLogout}
                disabled={isLoggingOut}
                className="p-2 rounded-lg hover:bg-white/10 transition-colors disabled:opacity-50"
                aria-label="Logout"
              >
                <LogOut className="w-5 h-5 text-white/70 hover:text-white" />
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome section */}
        <motion.div
          className="mb-12"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <h2 className="text-3xl font-bold text-white mb-2">
            Добро пожаловать, {user?.first_name}! 👋
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
          className="grid grid-cols-1 md:grid-cols-3 gap-6"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          {/* Create Quest */}
          <button className="frosted-card hover:scale-105 transition-transform text-left">
            <div className="text-4xl mb-4">✨</div>
            <h4 className="text-xl font-bold text-white mb-2">
              Создать квест
            </h4>
            <p className="text-white/70 text-sm">
              Персонализированный образовательный квест для вашего ребёнка
            </p>
          </button>

          {/* Write Letter */}
          <button className="frosted-card hover:scale-105 transition-transform text-left">
            <div className="text-4xl mb-4">💌</div>
            <h4 className="text-xl font-bold text-white mb-2">
              Написать письмо
            </h4>
            <p className="text-white/70 text-sm">
              Выразите свои чувства через благодарность, извинение или воспоминание
            </p>
          </button>

          {/* Set Goal */}
          <button className="frosted-card hover:scale-105 transition-transform text-left">
            <div className="text-4xl mb-4">🎯</div>
            <h4 className="text-xl font-bold text-white mb-2">
              Поставить цель
            </h4>
            <p className="text-white/70 text-sm">
              Определите следующие шаги на пути восстановления связи
            </p>
          </button>
        </motion.div>

        {/* Coming soon */}
        <motion.div
          className="mt-12 text-center text-white/50"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
        >
          <p>🚧 Dashboard в разработке - скоро добавим больше функций!</p>
        </motion.div>
      </main>
    </div>
  );
}

export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <DashboardContent />
    </ProtectedRoute>
  );
}
