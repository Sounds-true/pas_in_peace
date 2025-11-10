/**
 * QuestCard - Liquid Glass component for displaying quest information
 *
 * Features:
 * - Glass morphism effect (frosted glass with blur)
 * - Subtle animations on hover
 * - Progress indicator
 * - Child-friendly design
 */

import React from 'react';
import { motion } from 'framer-motion';
import { Sparkles, Heart, Star } from 'lucide-react';

export interface QuestCardProps {
  questId: string;
  title: string;
  description?: string;
  childName: string;
  childAge: number;
  progress: number; // 0-100
  status: 'draft' | 'active' | 'completed' | 'moderation';
  nodeCount?: number;
  lastUpdated?: Date;
  onClick?: () => void;
  className?: string;
}

export const QuestCard: React.FC<QuestCardProps> = ({
  questId,
  title,
  description,
  childName,
  childAge,
  progress,
  status,
  nodeCount = 0,
  lastUpdated,
  onClick,
  className = '',
}) => {
  // Status colors with Liquid Glass theme
  const statusConfig = {
    draft: {
      bg: 'from-slate-500/20 to-slate-600/20',
      border: 'border-slate-400/30',
      text: 'Черновик',
      icon: '📝',
    },
    active: {
      bg: 'from-blue-500/20 to-purple-500/20',
      border: 'border-blue-400/30',
      text: 'Активен',
      icon: '✨',
    },
    completed: {
      bg: 'from-green-500/20 to-emerald-500/20',
      border: 'border-green-400/30',
      text: 'Завершён',
      icon: '🎉',
    },
    moderation: {
      bg: 'from-amber-500/20 to-orange-500/20',
      border: 'border-amber-400/30',
      text: 'На проверке',
      icon: '🔍',
    },
  };

  const config = statusConfig[status];

  return (
    <motion.div
      className={`
        relative overflow-hidden rounded-2xl p-6
        bg-gradient-to-br ${config.bg}
        backdrop-blur-xl backdrop-saturate-150
        border ${config.border}
        shadow-lg hover:shadow-2xl
        transition-all duration-300
        cursor-pointer
        ${className}
      `}
      onClick={onClick}
      whileHover={{ scale: 1.02, y: -4 }}
      whileTap={{ scale: 0.98 }}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      {/* Glass shine effect */}
      <div className="absolute inset-0 bg-gradient-to-br from-white/10 via-transparent to-transparent pointer-events-none" />

      {/* Status badge */}
      <div className="flex items-center justify-between mb-4">
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-white/20 backdrop-blur text-sm font-medium">
          <span>{config.icon}</span>
          {config.text}
        </span>

        {/* Hearts for child age (cute touch) */}
        <div className="flex gap-1">
          {Array.from({ length: Math.min(childAge, 5) }).map((_, i) => (
            <Heart
              key={i}
              className="w-3 h-3 text-pink-400 fill-pink-300"
            />
          ))}
        </div>
      </div>

      {/* Title */}
      <h3 className="text-xl font-bold text-white mb-2 line-clamp-2">
        {title}
      </h3>

      {/* Child info */}
      <div className="flex items-center gap-2 mb-3 text-white/80">
        <Sparkles className="w-4 h-4 text-yellow-300" />
        <span className="text-sm font-medium">
          Для {childName}, {childAge} лет
        </span>
      </div>

      {/* Description */}
      {description && (
        <p className="text-sm text-white/70 mb-4 line-clamp-2">
          {description}
        </p>
      )}

      {/* Progress bar */}
      {progress > 0 && (
        <div className="mb-4">
          <div className="flex justify-between items-center mb-1.5">
            <span className="text-xs text-white/60 font-medium">Прогресс</span>
            <span className="text-xs text-white/80 font-bold">{progress}%</span>
          </div>
          <div className="relative h-2 bg-white/10 rounded-full overflow-hidden backdrop-blur">
            <motion.div
              className="absolute inset-y-0 left-0 bg-gradient-to-r from-blue-400 to-purple-400 rounded-full"
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.8, ease: 'easeOut' }}
            >
              {/* Shimmer effect */}
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent animate-shimmer" />
            </motion.div>
          </div>
        </div>
      )}

      {/* Footer meta */}
      <div className="flex items-center justify-between text-xs text-white/50 pt-3 border-t border-white/10">
        <div className="flex items-center gap-3">
          <span className="flex items-center gap-1">
            <Star className="w-3 h-3" />
            {nodeCount} шагов
          </span>
          {lastUpdated && (
            <span>
              {new Date(lastUpdated).toLocaleDateString('ru-RU', {
                day: 'numeric',
                month: 'short',
              })}
            </span>
          )}
        </div>

        {/* Quest ID for parent reference */}
        <span className="font-mono opacity-50 text-[10px]">
          #{questId.slice(0, 8)}
        </span>
      </div>
    </motion.div>
  );
};

// Shimmer animation (add to global CSS)
const shimmerStyles = `
@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}
.animate-shimmer {
  animation: shimmer 2s infinite;
}
`;

export default QuestCard;
