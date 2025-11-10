/**
 * VoiceWave - Animated voice wave visualization
 *
 * Features:
 * - Real-time voice amplitude visualization
 * - Liquid, organic wave animation
 * - Glass morphism design
 * - Idle state animation
 * - Recording state with pulsing effect
 */

import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Mic, MicOff } from 'lucide-react';

export interface VoiceWaveProps {
  isRecording?: boolean;
  amplitude?: number; // 0-1, voice amplitude
  onToggleRecording?: () => void;
  disabled?: boolean;
  className?: string;
}

export const VoiceWave: React.FC<VoiceWaveProps> = ({
  isRecording = false,
  amplitude = 0,
  onToggleRecording,
  disabled = false,
  className = '',
}) => {
  const [idleAmplitudes, setIdleAmplitudes] = useState<number[]>([]);

  // Generate idle wave animation
  useEffect(() => {
    if (!isRecording) {
      const interval = setInterval(() => {
        setIdleAmplitudes(
          Array.from({ length: 20 }, () => Math.random() * 0.3 + 0.1)
        );
      }, 100);
      return () => clearInterval(interval);
    }
  }, [isRecording]);

  // Number of wave bars
  const barCount = 20;
  const bars = Array.from({ length: barCount });

  return (
    <div className={`relative ${className}`}>
      {/* Main container with glass effect */}
      <div className="relative rounded-3xl overflow-hidden bg-gradient-to-br from-blue-500/20 to-purple-500/20 backdrop-blur-xl border border-white/20 shadow-2xl">
        {/* Wave visualization */}
        <div className="flex items-center justify-center gap-1 px-8 py-6 h-32">
          {bars.map((_, index) => {
            // Calculate bar height based on amplitude or idle animation
            const centerDistance = Math.abs(index - barCount / 2) / (barCount / 2);
            const baseHeight = isRecording
              ? amplitude * (1 - centerDistance * 0.5)
              : (idleAmplitudes[index] || 0.2) * (1 - centerDistance * 0.3);

            return (
              <motion.div
                key={index}
                className="w-1 rounded-full bg-gradient-to-t from-blue-400 via-purple-400 to-pink-400"
                style={{
                  filter: 'drop-shadow(0 0 4px rgba(59, 130, 246, 0.6))',
                }}
                animate={{
                  height: `${baseHeight * 100}%`,
                }}
                transition={{
                  duration: isRecording ? 0.1 : 0.3,
                  ease: 'easeOut',
                }}
              />
            );
          })}
        </div>

        {/* Recording indicator */}
        <AnimatePresence>
          {isRecording && (
            <motion.div
              className="absolute top-2 right-2 flex items-center gap-1.5 px-2 py-1 rounded-full bg-red-500/80 backdrop-blur"
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
            >
              <motion.div
                className="w-2 h-2 rounded-full bg-white"
                animate={{
                  opacity: [1, 0.3, 1],
                }}
                transition={{
                  duration: 1,
                  repeat: Infinity,
                  ease: 'easeInOut',
                }}
              />
              <span className="text-xs font-medium text-white">REC</span>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Microphone button */}
        <div className="flex justify-center pb-6">
          <motion.button
            onClick={onToggleRecording}
            disabled={disabled}
            className={`
              relative p-4 rounded-full
              ${isRecording
                ? 'bg-red-500/80 hover:bg-red-600/80'
                : 'bg-blue-500/80 hover:bg-blue-600/80'
              }
              backdrop-blur-lg border-2 border-white/30
              shadow-lg hover:shadow-2xl
              transition-all duration-200
              disabled:opacity-50 disabled:cursor-not-allowed
            `}
            whileHover={!disabled ? { scale: 1.1 } : {}}
            whileTap={!disabled ? { scale: 0.95 } : {}}
          >
            {/* Pulse effect when recording */}
            {isRecording && (
              <motion.div
                className="absolute inset-0 rounded-full bg-red-400/40"
                animate={{
                  scale: [1, 1.5, 1],
                  opacity: [0.5, 0, 0.5],
                }}
                transition={{
                  duration: 1.5,
                  repeat: Infinity,
                  ease: 'easeOut',
                }}
              />
            )}

            {isRecording ? (
              <MicOff className="w-6 h-6 text-white relative z-10" />
            ) : (
              <Mic className="w-6 h-6 text-white relative z-10" />
            )}
          </motion.button>
        </div>
      </div>

      {/* Helper text */}
      <motion.p
        className="text-center text-sm text-white/60 mt-3"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
      >
        {isRecording
          ? '🎤 Говорите...'
          : 'Нажмите на микрофон чтобы начать'}
      </motion.p>
    </div>
  );
};

/**
 * CompactVoiceWave - Smaller version for inline use
 */
export interface CompactVoiceWaveProps {
  isActive?: boolean;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export const CompactVoiceWave: React.FC<CompactVoiceWaveProps> = ({
  isActive = false,
  size = 'md',
  className = '',
}) => {
  const barCount = size === 'sm' ? 5 : size === 'md' ? 8 : 12;
  const bars = Array.from({ length: barCount });

  const heights = {
    sm: 'h-4',
    md: 'h-6',
    lg: 'h-8',
  };

  return (
    <div className={`inline-flex items-center gap-0.5 ${heights[size]} ${className}`}>
      {bars.map((_, index) => (
        <motion.div
          key={index}
          className="w-0.5 rounded-full bg-gradient-to-t from-blue-400 to-purple-400"
          animate={{
            height: isActive
              ? [`${20 + Math.random() * 80}%`, `${20 + Math.random() * 80}%`]
              : '20%',
          }}
          transition={{
            duration: 0.3,
            repeat: isActive ? Infinity : 0,
            repeatType: 'reverse',
            ease: 'easeInOut',
          }}
        />
      ))}
    </div>
  );
};

/**
 * VoiceVisualizer - Circular voice visualizer with liquid animation
 */
export interface VoiceVisualizerProps {
  amplitude: number; // 0-1
  size?: number;
  className?: string;
}

export const VoiceVisualizer: React.FC<VoiceVisualizerProps> = ({
  amplitude,
  size = 100,
  className = '',
}) => {
  const points = 32; // Number of points in the circle
  const angleStep = (Math.PI * 2) / points;
  const baseRadius = size / 3;

  // Generate path for liquid circle
  const generatePath = () => {
    const pathPoints = Array.from({ length: points }).map((_, i) => {
      const angle = angleStep * i;
      const noise = Math.sin(angle * 3 + Date.now() / 500) * amplitude * 10;
      const radius = baseRadius + noise;
      const x = size / 2 + Math.cos(angle) * radius;
      const y = size / 2 + Math.sin(angle) * radius;
      return { x, y };
    });

    // Create smooth curve using quadratic bezier
    let path = `M ${pathPoints[0].x} ${pathPoints[0].y}`;
    for (let i = 0; i < pathPoints.length; i++) {
      const current = pathPoints[i];
      const next = pathPoints[(i + 1) % pathPoints.length];
      const controlX = (current.x + next.x) / 2;
      const controlY = (current.y + next.y) / 2;
      path += ` Q ${current.x} ${current.y} ${controlX} ${controlY}`;
    }
    path += ' Z';
    return path;
  };

  const [path, setPath] = useState(generatePath());

  useEffect(() => {
    const interval = setInterval(() => {
      setPath(generatePath());
    }, 50);
    return () => clearInterval(interval);
  }, [amplitude]);

  return (
    <svg
      width={size}
      height={size}
      className={`${className}`}
    >
      <defs>
        <radialGradient id="voiceGradient" cx="50%" cy="50%">
          <stop offset="0%" stopColor="#60a5fa" stopOpacity="0.8" />
          <stop offset="50%" stopColor="#a78bfa" stopOpacity="0.6" />
          <stop offset="100%" stopColor="#ec4899" stopOpacity="0.4" />
        </radialGradient>
        <filter id="glow">
          <feGaussianBlur stdDeviation="4" result="coloredBlur" />
          <feMerge>
            <feMergeNode in="coloredBlur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>

      <motion.path
        d={path}
        fill="url(#voiceGradient)"
        filter="url(#glow)"
        animate={{ d: path }}
        transition={{ duration: 0.05 }}
      />
    </svg>
  );
};

export default VoiceWave;
