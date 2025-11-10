/**
 * Sidebar - Navigation component with Liquid Glass design
 *
 * Features:
 * - Multiple sections (Dashboard, Projects, Analytics, Resources)
 * - Active state indicators
 * - Glass morphism design
 * - Smooth animations
 * - Responsive (collapses on mobile)
 */

import React from 'react';
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
} from 'lucide-react';

export interface NavItem {
  id: string;
  label: string;
  href: string;
  icon: React.ReactNode;
  badge?: number;
}

export interface SidebarProps {
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

export const Sidebar: React.FC<SidebarProps> = ({
  isOpen,
  onClose,
  className = '',
}) => {
  const router = useRouter();

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
      <motion.aside
        className={`
          fixed top-0 left-0 h-full z-50
          lg:sticky lg:top-0 lg:z-0
          ${className}
        `}
        initial={false}
        animate={{
          x: isOpen ? 0 : -320,
        }}
        transition={{
          type: 'spring',
          stiffness: 300,
          damping: 30,
        }}
        style={{
          width: '320px',
        }}
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

          {/* Navigation */}
          <nav className="flex-1 overflow-y-auto scrollbar-glass p-4 space-y-6">
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

          {/* Footer */}
          <div className="p-4 border-t border-white/10">
            <div className="liquid-glass-hover p-3 rounded-xl text-center">
              <p className="text-xs text-white/60">
                v0.1.0 • Made with ❤️
              </p>
            </div>
          </div>
        </div>
      </motion.aside>
    </>
  );
};

export default Sidebar;
