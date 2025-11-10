/**
 * ProgressRing - Circular progress indicator with Liquid Glass aesthetics
 *
 * Features:
 * - Smooth animated circular progress
 * - Glass morphism design
 * - Customizable colors and size
 * - Percentage display in center
 * - Glow effect on completion
 */

import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';

export interface ProgressRingProps {
  progress: number; // 0-100
  size?: number; // diameter in pixels
  strokeWidth?: number;
  color?: string;
  glowColor?: string;
  label?: string;
  showPercentage?: boolean;
  className?: string;
  animated?: boolean;
}

export const ProgressRing: React.FC<ProgressRingProps> = ({
  progress,
  size = 120,
  strokeWidth = 8,
  color = '#60a5fa', // blue-400
  glowColor = '#3b82f6', // blue-500
  label,
  showPercentage = true,
  className = '',
  animated = true,
}) => {
  const [displayProgress, setDisplayProgress] = useState(animated ? 0 : progress);

  // Animate progress on mount/update
  useEffect(() => {
    if (animated) {
      const timer = setTimeout(() => {
        setDisplayProgress(progress);
      }, 100);
      return () => clearTimeout(timer);
    } else {
      setDisplayProgress(progress);
    }
  }, [progress, animated]);

  // Calculate SVG circle properties
  const center = size / 2;
  const radius = center - strokeWidth / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (displayProgress / 100) * circumference;

  // Determine if completed (glow effect)
  const isCompleted = progress >= 100;

  return (
    <div className={`relative inline-flex items-center justify-center ${className}`}>
      {/* Glow effect when completed */}
      {isCompleted && (
        <motion.div
          className="absolute inset-0 rounded-full blur-xl"
          style={{
            background: `radial-gradient(circle, ${glowColor}40, transparent)`,
          }}
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.5, 0.8, 0.5],
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        />
      )}

      <svg
        width={size}
        height={size}
        className="transform -rotate-90"
      >
        {/* Background circle (glass effect) */}
        <circle
          cx={center}
          cy={center}
          r={radius}
          fill="none"
          stroke="rgba(255, 255, 255, 0.1)"
          strokeWidth={strokeWidth}
          className="backdrop-blur"
        />

        {/* Progress circle */}
        <motion.circle
          cx={center}
          cy={center}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={circumference}
          animate={{
            strokeDashoffset: offset,
          }}
          transition={{
            duration: 1,
            ease: 'easeInOut',
          }}
          style={{
            filter: `drop-shadow(0 0 6px ${glowColor}80)`,
          }}
        />

        {/* Inner glow circle */}
        <circle
          cx={center}
          cy={center}
          r={radius - strokeWidth / 2}
          fill="none"
          stroke={color}
          strokeWidth={1}
          opacity={0.2}
          className="backdrop-blur"
        />
      </svg>

      {/* Center content */}
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        {showPercentage && (
          <motion.span
            className="text-2xl font-bold text-white"
            key={displayProgress}
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.3 }}
          >
            {Math.round(displayProgress)}%
          </motion.span>
        )}

        {label && (
          <span className="text-xs text-white/70 font-medium mt-1">
            {label}
          </span>
        )}

        {/* Sparkle effect on completion */}
        {isCompleted && (
          <motion.div
            className="absolute"
            initial={{ scale: 0, rotate: 0 }}
            animate={{
              scale: [0, 1.5, 0],
              rotate: [0, 180, 360],
            }}
            transition={{
              duration: 1,
              ease: 'easeOut',
            }}
          >
            ✨
          </motion.div>
        )}
      </div>
    </div>
  );
};

/**
 * MultiProgressRing - Shows multiple tracks in concentric rings
 * Useful for displaying 4 recovery tracks at once
 */
export interface MultiProgressRingProps {
  tracks: Array<{
    id: string;
    name: string;
    progress: number;
    color: string;
  }>;
  size?: number;
  className?: string;
}

export const MultiProgressRing: React.FC<MultiProgressRingProps> = ({
  tracks,
  size = 200,
  className = '',
}) => {
  const strokeWidth = 12;
  const spacing = 16;

  return (
    <div className={`relative inline-flex items-center justify-center ${className}`}>
      <svg width={size} height={size} className="transform -rotate-90">
        {tracks.map((track, index) => {
          const center = size / 2;
          const radius = center - strokeWidth / 2 - index * spacing;
          const circumference = 2 * Math.PI * radius;
          const offset = circumference - (track.progress / 100) * circumference;

          return (
            <g key={track.id}>
              {/* Background circle */}
              <circle
                cx={center}
                cy={center}
                r={radius}
                fill="none"
                stroke="rgba(255, 255, 255, 0.1)"
                strokeWidth={strokeWidth}
              />

              {/* Progress circle */}
              <motion.circle
                cx={center}
                cy={center}
                r={radius}
                fill="none"
                stroke={track.color}
                strokeWidth={strokeWidth}
                strokeLinecap="round"
                strokeDasharray={circumference}
                strokeDashoffset={circumference}
                animate={{
                  strokeDashoffset: offset,
                }}
                transition={{
                  duration: 1.5,
                  delay: index * 0.2,
                  ease: 'easeInOut',
                }}
                style={{
                  filter: `drop-shadow(0 0 4px ${track.color}80)`,
                }}
              />
            </g>
          );
        })}
      </svg>

      {/* Center label */}
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-sm font-bold text-white/80">Recovery</span>
        <span className="text-xs text-white/60">Progress</span>
      </div>

      {/* Track labels */}
      <div className="absolute -bottom-16 left-1/2 transform -translate-x-1/2 w-full">
        <div className="flex flex-wrap justify-center gap-3">
          {tracks.map((track) => (
            <div
              key={track.id}
              className="flex items-center gap-1.5 text-xs"
            >
              <div
                className="w-2 h-2 rounded-full"
                style={{ backgroundColor: track.color }}
              />
              <span className="text-white/70 font-medium">{track.name}</span>
              <span className="text-white/50">{Math.round(track.progress)}%</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ProgressRing;
