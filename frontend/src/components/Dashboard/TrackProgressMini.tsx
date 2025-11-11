/**
 * TrackProgressMini - Compact track progress indicator for Sidebar
 *
 * Features:
 * - Inline progress bar
 * - Track icon and name
 * - Current phase indicator
 * - Next milestone preview
 * - Expand on hover for details
 */

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Link from 'next/link';

export interface TrackProgressMiniProps {
  trackId: string;
  trackName: string;
  progress: number; // 0-100
  phase: string;
  nextMilestone?: string;
  color: string;
  icon: string; // emoji
  className?: string;
}

export const TrackProgressMini: React.FC<TrackProgressMiniProps> = ({
  trackId,
  trackName,
  progress,
  phase,
  nextMilestone,
  color,
  icon,
  className = '',
}) => {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <Link href={`/tracks/${trackId}`}>
      <motion.div
        className={`relative p-3 rounded-xl cursor-pointer transition-all ${className}`}
        onHoverStart={() => setIsHovered(true)}
        onHoverEnd={() => setIsHovered(false)}
        whileHover={{ x: 4 }}
        style={{
          background: isHovered
            ? `linear-gradient(135deg, ${color}20, ${color}10)`
            : 'transparent',
        }}
      >
        {/* Compact view */}
        <div className="flex items-center gap-3">
          {/* Icon */}
          <div
            className="w-10 h-10 rounded-lg flex items-center justify-center text-xl"
            style={{
              background: `${color}30`,
              border: `1px solid ${color}50`,
            }}
          >
            {icon}
          </div>

          {/* Info */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between mb-1">
              <h5 className="text-sm font-medium text-white truncate">
                {trackName}
              </h5>
              <span className="text-xs font-bold text-white ml-2">
                {progress}%
              </span>
            </div>

            {/* Progress bar */}
            <div className="h-1.5 bg-white/10 rounded-full overflow-hidden">
              <motion.div
                className="h-full rounded-full"
                style={{ backgroundColor: color }}
                initial={{ width: 0 }}
                animate={{ width: `${progress}%` }}
                transition={{ duration: 0.5, ease: 'easeOut' }}
              />
            </div>
          </div>
        </div>

        {/* Expanded details on hover */}
        <AnimatePresence>
          {isHovered && nextMilestone && (
            <motion.div
              className="mt-2 pt-2 border-t border-white/10"
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.2 }}
            >
              <div className="flex items-start gap-2">
                <span className="text-xs text-white/50">Следующее:</span>
                <p className="text-xs text-white/80 flex-1">{nextMilestone}</p>
              </div>
              <div className="mt-1">
                <span
                  className="text-xs px-2 py-0.5 rounded-full"
                  style={{
                    background: `${color}20`,
                    color: color,
                  }}
                >
                  {phase}
                </span>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </Link>
  );
};

export default TrackProgressMini;
