/**
 * TrackCard - Detailed recovery track card
 *
 * Features:
 * - Track progress with ProgressRing
 * - Milestones list with checkboxes
 * - Next action suggestion (AI-powered)
 * - Glass morphism design
 * - Expandable details
 */

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, ChevronUp, CheckCircle2, Circle, Sparkles, TrendingUp } from 'lucide-react';
import { ProgressRing } from '../LiquidGlass';

export interface Milestone {
  id: string;
  title: string;
  description: string;
  completed: boolean;
  completedAt?: string;
}

export interface TrackCardProps {
  id: string;
  name: string;
  description: string;
  color: string;
  progress: number;
  currentPhase: string;
  milestones: Milestone[];
  nextAction?: string;
  isPrimary?: boolean;
  onSetPrimary?: () => void;
  onToggleMilestone?: (milestoneId: string) => void;
  className?: string;
}

export const TrackCard: React.FC<TrackCardProps> = ({
  id,
  name,
  description,
  color,
  progress,
  currentPhase,
  milestones,
  nextAction,
  isPrimary = false,
  onSetPrimary,
  onToggleMilestone,
  className = '',
}) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const completedMilestones = milestones.filter((m) => m.completed).length;
  const totalMilestones = milestones.length;

  return (
    <motion.div
      className={`frosted-card ${className}`}
      layout
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      {/* Header */}
      <div className="flex items-start gap-4 mb-6">
        {/* Progress Ring */}
        <ProgressRing
          progress={progress}
          size={80}
          strokeWidth={6}
          color={color}
          glowColor={color}
          showPercentage={true}
        />

        {/* Track Info */}
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <h3 className="text-xl font-bold text-white">{name}</h3>
            {isPrimary && (
              <span className="px-2 py-0.5 text-xs font-bold bg-yellow-500/20 text-yellow-300 rounded-full border border-yellow-400/30">
                ⭐ Основной
              </span>
            )}
          </div>
          <p className="text-white/70 text-sm mb-2">{description}</p>
          <div className="flex items-center gap-4 text-xs text-white/60">
            <span className="flex items-center gap-1">
              <TrendingUp className="w-3 h-3" />
              Фаза: {currentPhase}
            </span>
            <span>
              {completedMilestones} / {totalMilestones} достижений
            </span>
          </div>
        </div>

        {/* Primary toggle */}
        {!isPrimary && onSetPrimary && (
          <button
            onClick={onSetPrimary}
            className="px-3 py-1.5 text-xs font-medium text-white/70 hover:text-white border border-white/20 hover:border-yellow-400/50 rounded-lg transition-colors"
          >
            Сделать основным
          </button>
        )}
      </div>

      {/* Next Action Suggestion (AI) */}
      {nextAction && (
        <div className="mb-6 p-4 rounded-xl bg-gradient-to-r from-blue-500/10 to-purple-500/10 border border-blue-400/20">
          <div className="flex items-start gap-3">
            <Sparkles className="w-5 h-5 text-yellow-400 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h4 className="text-sm font-semibold text-white mb-1">
                Следующий шаг (AI)
              </h4>
              <p className="text-sm text-white/80">{nextAction}</p>
            </div>
          </div>
        </div>
      )}

      {/* Milestones Summary */}
      <div className="mb-4">
        <div className="flex items-center justify-between">
          <h4 className="text-sm font-semibold text-white">Достижения</h4>
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="flex items-center gap-1 text-xs text-white/70 hover:text-white transition-colors"
          >
            {isExpanded ? (
              <>
                Скрыть <ChevronUp className="w-4 h-4" />
              </>
            ) : (
              <>
                Показать всё <ChevronDown className="w-4 h-4" />
              </>
            )}
          </button>
        </div>

        {/* Progress bar */}
        <div className="mt-3 h-2 bg-white/10 rounded-full overflow-hidden">
          <motion.div
            className="h-full rounded-full"
            style={{ backgroundColor: color }}
            initial={{ width: 0 }}
            animate={{ width: `${(completedMilestones / totalMilestones) * 100}%` }}
            transition={{ duration: 0.8, ease: 'easeOut' }}
          />
        </div>
      </div>

      {/* Milestones List (Expandable) */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="overflow-hidden"
          >
            <div className="space-y-2">
              {milestones.map((milestone) => (
                <motion.button
                  key={milestone.id}
                  onClick={() => onToggleMilestone?.(milestone.id)}
                  className={`
                    w-full flex items-start gap-3 p-3 rounded-lg text-left
                    transition-all duration-200
                    ${
                      milestone.completed
                        ? 'bg-green-500/10 hover:bg-green-500/20 border border-green-400/20'
                        : 'bg-white/5 hover:bg-white/10 border border-white/10'
                    }
                  `}
                  whileHover={{ scale: 1.01 }}
                  whileTap={{ scale: 0.99 }}
                >
                  {/* Checkbox */}
                  {milestone.completed ? (
                    <CheckCircle2 className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
                  ) : (
                    <Circle className="w-5 h-5 text-white/40 flex-shrink-0 mt-0.5" />
                  )}

                  {/* Content */}
                  <div className="flex-1">
                    <h5
                      className={`text-sm font-medium mb-1 ${
                        milestone.completed ? 'text-white line-through' : 'text-white'
                      }`}
                    >
                      {milestone.title}
                    </h5>
                    <p className="text-xs text-white/60">{milestone.description}</p>
                    {milestone.completed && milestone.completedAt && (
                      <p className="text-xs text-green-400/70 mt-1">
                        ✓ Завершено {new Date(milestone.completedAt).toLocaleDateString('ru-RU')}
                      </p>
                    )}
                  </div>
                </motion.button>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

export default TrackCard;
