/**
 * SidebarEnhanced - Enhanced navigation with track progress
 *
 * Features:
 * - All original Sidebar features
 * - Track progress indicators
 * - Collapsible sections
 * - Notifications badge
 * - User quick stats
 */

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { motion } from 'framer-motion';
import {
  LayoutDashboard,
  FolderKanban,
  BarChart3,
  BookOpen,
  Sparkles,
  Settings,
  HelpCircle,
  ChevronDown,
  ChevronUp,
  User,
  Heart,
  MessageCircle,
  Users,
} from 'lucide-react';
import { TrackProgressMini } from './TrackProgressMini';

export interface NavItem {
  id: string;
  label: string;
  href: string;
  icon: React.ReactNode;
  badge?: number;
}

export interface SidebarEnhancedProps {
  isOpen: boolean;
  onClose?: () => void;
  className?: string;
}

const navSections: { title: string; items: NavItem[] }[] = [
  {
    title: 'Главное',
    items: [
      {
        id: 'dashboard',
        label: 'Dashboard',
        href: '/dashboard',
        icon: <LayoutDashboard className="w-5 h-5" />,
      },
      {
        id: 'projects',
        label: 'Мои проекты',
        href: '/projects',
        icon: <FolderKanban className="w-5 h-5" />,
        badge: 3,
      },
      {
        id: 'analytics',
        label: 'Аналитика',
        href: '/analytics',
        icon: <BarChart3 className="w-5 h-5" />,
      },
    ],
  },
  {
    title: 'Ресурсы',
    items: [
      {
        id: 'resources',
        label: 'Материалы',
        href: '/resources',
        icon: <BookOpen className="w-5 h-5" />,
      },
      {
        id: 'help',
        label: 'Помощь',
        href: '/help',
        icon: <HelpCircle className="w-5 h-5" />,
      },
    ],
  },
  {
    title: 'Настройки',
    items: [
      {
        id: 'settings',
        label: 'Настройки',
        href: '/settings',
        icon: <Settings className="w-5 h-5" />,
      },
    ],
  },
];

// Mock track data
const mockTracks = [
  {
    trackId: 'self_work',
    trackName: 'Работа над собой',
    progress: 25,
    phase: 'Фаза 2: Основы',
    nextMilestone: 'Медитация 7 дней подряд',
    color: '#60a5fa',
    icon: <User className="w-4 h-4" />,
  },
  {
    trackId: 'child_connection',
    trackName: 'Связь с ребёнком',
    progress: 15,
    phase: 'Фаза 1: Оценка',
    nextMilestone: 'Создать первый квест',
    color: '#a78bfa',
    icon: <Heart className="w-4 h-4" />,
  },
  {
    trackId: 'negotiation',
    trackName: 'Переговоры',
    progress: 10,
    phase: 'Фаза 1: Оценка',
    nextMilestone: 'Первое спокойное письмо',
    color: '#f472b6',
    icon: <MessageCircle className="w-4 h-4" />,
  },
  {
    trackId: 'community',
    trackName: 'Сообщество',
    progress: 20,
    phase: 'Фаза 2: Основы',
    nextMilestone: 'Поддержать 3 родителя',
    color: '#34d399',
    icon: <Users className="w-4 h-4" />,
  },
];

export const SidebarEnhanced: React.FC<SidebarEnhancedProps> = ({
  isOpen,
  onClose,
  className = '',
}) => {
  const router = useRouter();
  const [tracksExpanded, setTracksExpanded] = useState(true);

  const isActive = (href: string) => {
    return router.pathname === href;
  };

  return (
    <>
      {/* Overlay for mobile */}
      {isOpen && (
        <motion.div
          className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 lg:hidden"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`
          fixed top-0 left-0 h-full z-50 w-80
          lg:static lg:z-0
          transition-transform duration-300
          ${isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
          ${className}
        `}
      >
        <div className="h-full liquid-glass border-r border-white/10 flex flex-col">
          {/* Logo/Brand */}
          <div className="p-6 border-b border-white/10">
            <Link href="/dashboard" className="flex items-center gap-3 group">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-400 to-purple-400 flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform">
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">PAS in Peace</h1>
                <p className="text-xs text-white/60">Восстановление связей</p>
              </div>
            </Link>
          </div>

          {/* Main Navigation + Track Progress */}
          <nav className="flex-1 overflow-y-auto scrollbar-glass p-4 space-y-6">
            {/* Recovery Tracks Section */}
            <div>
              <button
                onClick={() => setTracksExpanded(!tracksExpanded)}
                className="w-full flex items-center justify-between mb-3 px-3 group"
              >
                <h3 className="text-xs font-semibold text-white/50 uppercase tracking-wider">
                  Треки восстановления
                </h3>
                {tracksExpanded ? (
                  <ChevronUp className="w-4 h-4 text-white/50 group-hover:text-white" />
                ) : (
                  <ChevronDown className="w-4 h-4 text-white/50 group-hover:text-white" />
                )}
              </button>

              {tracksExpanded && (
                <motion.div
                  className="space-y-2"
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                >
                  {mockTracks.map((track) => (
                    <TrackProgressMini key={track.trackId} {...track} />
                  ))}
                </motion.div>
              )}
            </div>

            {/* Regular navigation sections */}
            {navSections.map((section) => (
              <div key={section.title}>
                {/* Section title */}
                <h3 className="text-xs font-semibold text-white/50 uppercase tracking-wider mb-3 px-3">
                  {section.title}
                </h3>

                {/* Nav items */}
                <ul className="space-y-1">
                  {section.items.map((item) => {
                    const active = isActive(item.href);

                    return (
                      <li key={item.id}>
                        <Link
                          href={item.href}
                          className={`
                            flex items-center gap-3 px-3 py-2.5 rounded-xl
                            transition-all duration-200
                            ${
                              active
                                ? 'bg-gradient-to-r from-blue-500/20 to-purple-500/20 text-white shadow-lg'
                                : 'text-white/70 hover:text-white hover:bg-white/10'
                            }
                          `}
                        >
                          {/* Icon */}
                          <span
                            className={`
                            ${active ? 'text-blue-400' : 'text-white/70'}
                          `}
                          >
                            {item.icon}
                          </span>

                          {/* Label */}
                          <span className="flex-1 font-medium text-sm">
                            {item.label}
                          </span>

                          {/* Badge */}
                          {item.badge && (
                            <span className="px-2 py-0.5 text-xs font-bold bg-blue-500 text-white rounded-full">
                              {item.badge}
                            </span>
                          )}

                          {/* Active indicator */}
                          {active && (
                            <motion.div
                              className="w-1 h-6 bg-blue-400 rounded-full"
                              layoutId="activeIndicator"
                            />
                          )}
                        </Link>
                      </li>
                    );
                  })}
                </ul>
              </div>
            ))}
          </nav>

          {/* Footer with Quick Stats */}
          <div className="p-4 border-t border-white/10 space-y-3">
            {/* Quick stats */}
            <div className="liquid-glass-hover p-3 rounded-xl">
              <div className="grid grid-cols-3 gap-3 text-center">
                <div>
                  <p className="text-2xl font-bold text-white">3</p>
                  <p className="text-xs text-white/60">Квестов</p>
                </div>
                <div>
                  <p className="text-2xl font-bold text-white">8</p>
                  <p className="text-xs text-white/60">Дней</p>
                </div>
                <div>
                  <p className="text-2xl font-bold text-white">18%</p>
                  <p className="text-xs text-white/60">Прогресс</p>
                </div>
              </div>
            </div>

            {/* Version */}
            <div className="text-center">
              <p className="text-xs text-white/40">v0.2.0 • PAS in Peace</p>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
};

export default SidebarEnhanced;
