/**
 * Projects Page - List of all quests, letters, and goals
 *
 * Protected route - requires authentication
 */

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Filter, Search, Plus } from 'lucide-react';
import { ProtectedRoute } from '../components/Auth/ProtectedRoute';
import { DashboardLayout } from '../components/Dashboard';
import { QuestCard } from '../components/LiquidGlass';

type FilterType = 'all' | 'quest' | 'letter' | 'goal';
type StatusType = 'all' | 'draft' | 'active' | 'completed' | 'moderation';

function ProjectsContent() {
  const [filterType, setFilterType] = useState<FilterType>('all');
  const [filterStatus, setFilterStatus] = useState<StatusType>('all');
  const [searchQuery, setSearchQuery] = useState('');

  // Mock data
  const mockProjects = [
    {
      type: 'quest',
      questId: 'quest_001',
      title: 'Тайна зоопарка',
      description: 'Образовательный квест про животных для Маши',
      childName: 'Маша',
      childAge: 9,
      progress: 45,
      status: 'active' as const,
      nodeCount: 6,
      lastUpdated: new Date('2025-11-09'),
    },
    {
      type: 'quest',
      questId: 'quest_002',
      title: 'Секретный торт',
      description: 'Кулинарное приключение с математикой',
      childName: 'Маша',
      childAge: 9,
      progress: 100,
      status: 'completed' as const,
      nodeCount: 8,
      lastUpdated: new Date('2025-11-08'),
    },
    {
      type: 'quest',
      questId: 'quest_003',
      title: 'Природа вокруг нас',
      description: 'Исследование растений и экосистем',
      childName: 'Маша',
      childAge: 9,
      progress: 0,
      status: 'draft' as const,
      nodeCount: 5,
      lastUpdated: new Date('2025-11-10'),
    },
  ];

  const filteredProjects = mockProjects.filter((project) => {
    if (filterType !== 'all' && project.type !== filterType) return false;
    if (filterStatus !== 'all' && project.status !== filterStatus) return false;
    if (searchQuery && !project.title.toLowerCase().includes(searchQuery.toLowerCase())) {
      return false;
    }
    return true;
  });

  return (
    <DashboardLayout
      title="Мои проекты"
      actions={
        <button className="glass-button bg-blue-500/20 hover:bg-blue-500/30 flex items-center gap-2">
          <Plus className="w-4 h-4" />
          <span className="hidden sm:inline">Создать</span>
        </button>
      }
    >
      {/* Filters */}
      <div className="mb-8 space-y-4">
        {/* Search */}
        <div className="relative">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-white/50" />
          <input
            type="text"
            placeholder="Поиск проектов..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="glass-input pl-12"
          />
        </div>

        {/* Filter buttons */}
        <div className="flex flex-wrap gap-3">
          {/* Type filter */}
          <div className="flex gap-2">
            {(['all', 'quest', 'letter', 'goal'] as FilterType[]).map((type) => (
              <button
                key={type}
                onClick={() => setFilterType(type)}
                className={`
                  px-4 py-2 rounded-lg text-sm font-medium transition-all
                  ${
                    filterType === type
                      ? 'bg-blue-500/30 text-white border border-blue-400/50'
                      : 'bg-white/5 text-white/70 hover:bg-white/10 border border-white/10'
                  }
                `}
              >
                {type === 'all' && 'Все'}
                {type === 'quest' && '✨ Квесты'}
                {type === 'letter' && '💌 Письма'}
                {type === 'goal' && '🎯 Цели'}
              </button>
            ))}
          </div>

          <div className="h-8 w-px bg-white/10" />

          {/* Status filter */}
          <div className="flex gap-2">
            {(['all', 'draft', 'active', 'completed'] as StatusType[]).map((status) => (
              <button
                key={status}
                onClick={() => setFilterStatus(status)}
                className={`
                  px-4 py-2 rounded-lg text-sm font-medium transition-all
                  ${
                    filterStatus === status
                      ? 'bg-purple-500/30 text-white border border-purple-400/50'
                      : 'bg-white/5 text-white/70 hover:bg-white/10 border border-white/10'
                  }
                `}
              >
                {status === 'all' && 'Все статусы'}
                {status === 'draft' && 'Черновики'}
                {status === 'active' && 'Активные'}
                {status === 'completed' && 'Завершённые'}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Results */}
      <div className="mb-6">
        <p className="text-white/60 text-sm">
          Найдено проектов: <span className="text-white font-medium">{filteredProjects.length}</span>
        </p>
      </div>

      {/* Projects grid */}
      {filteredProjects.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredProjects.map((project, index) => (
            <motion.div
              key={project.questId}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
            >
              {project.type === 'quest' && (
                <QuestCard
                  questId={project.questId}
                  title={project.title}
                  description={project.description}
                  childName={project.childName}
                  childAge={project.childAge}
                  progress={project.progress}
                  status={project.status}
                  nodeCount={project.nodeCount}
                  lastUpdated={project.lastUpdated}
                  onClick={() => console.log('Quest clicked:', project.questId)}
                />
              )}
            </motion.div>
          ))}
        </div>
      ) : (
        <motion.div
          className="frosted-card text-center py-16"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <div className="text-6xl mb-4">📭</div>
          <h3 className="text-xl font-bold text-white mb-2">Проекты не найдены</h3>
          <p className="text-white/60 mb-6">
            {searchQuery
              ? 'Попробуйте изменить поисковый запрос'
              : 'Создайте свой первый проект!'}
          </p>
          <button className="glass-button bg-blue-500/20 hover:bg-blue-500/30">
            Создать проект
          </button>
        </motion.div>
      )}
    </DashboardLayout>
  );
}

export default function ProjectsPage() {
  return (
    <ProtectedRoute>
      <ProjectsContent />
    </ProtectedRoute>
  );
}
