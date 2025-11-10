/**
 * Resources Page - Educational materials and guides
 *
 * Protected route - requires authentication
 */

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  BookOpen,
  Video,
  FileText,
  Headphones,
  Download,
  ExternalLink,
  Search,
  Filter,
  Heart,
  Brain,
  Users,
  MessageCircle,
} from 'lucide-react';
import { ProtectedRoute } from '../components/Auth/ProtectedRoute';
import { DashboardLayout } from '../components/Dashboard';

type ResourceType = 'article' | 'video' | 'audio' | 'guide' | 'all';
type CategoryType = 'self-care' | 'child-bond' | 'negotiation' | 'community' | 'all';

function ResourcesContent() {
  const [filterType, setFilterType] = useState<ResourceType>('all');
  const [filterCategory, setFilterCategory] = useState<CategoryType>('all');
  const [searchQuery, setSearchQuery] = useState('');

  // Mock resources data
  const mockResources = [
    {
      id: '1',
      title: 'Эмоциональная регуляция для родителей',
      description: 'Практические техники управления эмоциями в сложных ситуациях',
      type: 'article' as const,
      category: 'self-care' as const,
      duration: '15 мин',
      author: 'Психолог Анна Иванова',
      thumbnail: '🧘',
      downloads: 1234,
      rating: 4.8,
    },
    {
      id: '2',
      title: 'Как восстановить связь с ребёнком',
      description: 'Видео-курс по восстановлению доверия и эмоциональной связи',
      type: 'video' as const,
      category: 'child-bond' as const,
      duration: '45 мин',
      author: 'Семейный психолог',
      thumbnail: '❤️',
      downloads: 2156,
      rating: 4.9,
    },
    {
      id: '3',
      title: 'Медитация для внутреннего покоя',
      description: 'Аудио-практика для снижения тревожности и стресса',
      type: 'audio' as const,
      category: 'self-care' as const,
      duration: '20 мин',
      author: 'Инструктор медитации',
      thumbnail: '🎧',
      downloads: 3421,
      rating: 4.7,
    },
    {
      id: '4',
      title: 'Руководство по конструктивным переговорам',
      description: 'Полное руководство по коммуникации с другим родителем',
      type: 'guide' as const,
      category: 'negotiation' as const,
      duration: '30 мин',
      author: 'Медиатор семейных споров',
      thumbnail: '🤝',
      downloads: 987,
      rating: 4.6,
    },
    {
      id: '5',
      title: 'Поддержка в родительском сообществе',
      description: 'Как найти и получить помощь от других родителей',
      type: 'article' as const,
      category: 'community' as const,
      duration: '10 мин',
      author: 'Координатор группы поддержки',
      thumbnail: '👥',
      downloads: 756,
      rating: 4.5,
    },
    {
      id: '6',
      title: 'Техники активного слушания',
      description: 'Видео о том, как слышать и понимать своего ребёнка',
      type: 'video' as const,
      category: 'child-bond' as const,
      duration: '25 мин',
      author: 'Детский психолог',
      thumbnail: '💬',
      downloads: 1543,
      rating: 4.8,
    },
  ];

  // Filter resources
  const filteredResources = mockResources.filter((resource) => {
    if (filterType !== 'all' && resource.type !== filterType) return false;
    if (filterCategory !== 'all' && resource.category !== filterCategory) return false;
    if (
      searchQuery &&
      !resource.title.toLowerCase().includes(searchQuery.toLowerCase()) &&
      !resource.description.toLowerCase().includes(searchQuery.toLowerCase())
    ) {
      return false;
    }
    return true;
  });

  return (
    <DashboardLayout title="Материалы">
      {/* Header with search */}
      <motion.div
        className="mb-8"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h2 className="text-3xl font-bold text-white mb-2">
          Образовательные материалы 📚
        </h2>
        <p className="text-white/70 mb-6">
          Статьи, видео и аудио для поддержки на пути восстановления
        </p>

        {/* Search */}
        <div className="relative">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-white/50" />
          <input
            type="text"
            placeholder="Поиск материалов..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full frosted-card pl-12 pr-4 py-3 text-white placeholder:text-white/50 focus:outline-none focus:ring-2 focus:ring-blue-400/50"
          />
        </div>
      </motion.div>

      {/* Filters */}
      <motion.div
        className="mb-8 space-y-4"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        {/* Type filter */}
        <div>
          <div className="flex items-center gap-2 mb-3">
            <Filter className="w-4 h-4 text-white/70" />
            <span className="text-sm font-medium text-white/70">Тип материала:</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {(['all', 'article', 'video', 'audio', 'guide'] as ResourceType[]).map(
              (type) => (
                <button
                  key={type}
                  onClick={() => setFilterType(type)}
                  className={`
                    px-4 py-2 rounded-lg text-sm font-medium transition-all
                    ${
                      filterType === type
                        ? 'bg-blue-500/30 text-white shadow-lg'
                        : 'bg-white/5 text-white/70 hover:bg-white/10'
                    }
                  `}
                >
                  {type === 'all' && '📋 Все'}
                  {type === 'article' && '📄 Статьи'}
                  {type === 'video' && '🎥 Видео'}
                  {type === 'audio' && '🎧 Аудио'}
                  {type === 'guide' && '📖 Руководства'}
                </button>
              )
            )}
          </div>
        </div>

        {/* Category filter */}
        <div>
          <div className="flex items-center gap-2 mb-3">
            <Filter className="w-4 h-4 text-white/70" />
            <span className="text-sm font-medium text-white/70">Категория:</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {(
              ['all', 'self-care', 'child-bond', 'negotiation', 'community'] as CategoryType[]
            ).map((category) => (
              <button
                key={category}
                onClick={() => setFilterCategory(category)}
                className={`
                  px-4 py-2 rounded-lg text-sm font-medium transition-all flex items-center gap-2
                  ${
                    filterCategory === category
                      ? 'bg-purple-500/30 text-white shadow-lg'
                      : 'bg-white/5 text-white/70 hover:bg-white/10'
                  }
                `}
              >
                {category === 'all' && (
                  <>
                    <BookOpen className="w-4 h-4" /> Все
                  </>
                )}
                {category === 'self-care' && (
                  <>
                    <Brain className="w-4 h-4" /> Работа над собой
                  </>
                )}
                {category === 'child-bond' && (
                  <>
                    <Heart className="w-4 h-4" /> Связь с ребёнком
                  </>
                )}
                {category === 'negotiation' && (
                  <>
                    <MessageCircle className="w-4 h-4" /> Переговоры
                  </>
                )}
                {category === 'community' && (
                  <>
                    <Users className="w-4 h-4" /> Сообщество
                  </>
                )}
              </button>
            ))}
          </div>
        </div>
      </motion.div>

      {/* Resources grid */}
      {filteredResources.length > 0 ? (
        <motion.div
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          {filteredResources.map((resource, index) => (
            <motion.div
              key={resource.id}
              className="frosted-card group hover:scale-105 transition-all cursor-pointer"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 * index }}
            >
              {/* Thumbnail */}
              <div className="text-6xl mb-4 text-center">{resource.thumbnail}</div>

              {/* Type badge */}
              <div className="flex items-center gap-2 mb-3">
                {resource.type === 'article' && (
                  <span className="px-2 py-1 text-xs font-medium bg-blue-500/20 text-blue-300 rounded-lg flex items-center gap-1">
                    <FileText className="w-3 h-3" /> Статья
                  </span>
                )}
                {resource.type === 'video' && (
                  <span className="px-2 py-1 text-xs font-medium bg-purple-500/20 text-purple-300 rounded-lg flex items-center gap-1">
                    <Video className="w-3 h-3" /> Видео
                  </span>
                )}
                {resource.type === 'audio' && (
                  <span className="px-2 py-1 text-xs font-medium bg-pink-500/20 text-pink-300 rounded-lg flex items-center gap-1">
                    <Headphones className="w-3 h-3" /> Аудио
                  </span>
                )}
                {resource.type === 'guide' && (
                  <span className="px-2 py-1 text-xs font-medium bg-green-500/20 text-green-300 rounded-lg flex items-center gap-1">
                    <BookOpen className="w-3 h-3" /> Руководство
                  </span>
                )}
                <span className="text-xs text-white/60">{resource.duration}</span>
              </div>

              {/* Title and description */}
              <h3 className="text-lg font-bold text-white mb-2 group-hover:text-blue-400 transition-colors">
                {resource.title}
              </h3>
              <p className="text-sm text-white/70 mb-4 line-clamp-2">
                {resource.description}
              </p>

              {/* Author */}
              <p className="text-xs text-white/50 mb-4">{resource.author}</p>

              {/* Stats */}
              <div className="flex items-center justify-between text-xs text-white/60 mb-4">
                <div className="flex items-center gap-1">
                  <Download className="w-3 h-3" />
                  <span>{resource.downloads}</span>
                </div>
                <div className="flex items-center gap-1">
                  <span>⭐</span>
                  <span>{resource.rating}</span>
                </div>
              </div>

              {/* Actions */}
              <div className="flex gap-2">
                <button className="flex-1 glass-button bg-blue-500/20 hover:bg-blue-500/30 text-sm flex items-center justify-center gap-2">
                  <ExternalLink className="w-4 h-4" />
                  Открыть
                </button>
                <button className="glass-button bg-white/10 hover:bg-white/20 p-2">
                  <Download className="w-4 h-4" />
                </button>
              </div>
            </motion.div>
          ))}
        </motion.div>
      ) : (
        <motion.div
          className="frosted-card text-center py-12"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <div className="text-6xl mb-4">🔍</div>
          <h3 className="text-xl font-bold text-white mb-2">
            Материалы не найдены
          </h3>
          <p className="text-white/70">
            Попробуйте изменить фильтры или поисковый запрос
          </p>
        </motion.div>
      )}
    </DashboardLayout>
  );
}

export default function ResourcesPage() {
  return (
    <ProtectedRoute>
      <ResourcesContent />
    </ProtectedRoute>
  );
}
