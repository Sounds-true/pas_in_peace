/**
 * Login Page - Telegram OAuth authentication
 */

import React, { useEffect } from 'react';
import { useRouter } from 'next/router';
import { motion } from 'framer-motion';
import { Heart, Sparkles, Star } from 'lucide-react';
import TelegramAuthButton, {
  CustomTelegramAuthButton,
} from '../components/Auth/TelegramAuthButton';
import { useUserStore } from '../lib/stores/userStore';

export default function LoginPage() {
  const router = useRouter();
  const { isAuthenticated } = useUserStore();

  // Get bot username from env or use placeholder
  const botUsername = process.env.NEXT_PUBLIC_TELEGRAM_BOT_USERNAME || 'pas_in_peace_bot';

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      router.push('/dashboard');
    }
  }, [isAuthenticated, router]);

  const handleAuthSuccess = (user: any) => {
    console.log('Login successful:', user);
    // React Query and Zustand will handle state updates
    // User will be redirected by the useEffect above
  };

  const handleAuthError = (error: Error) => {
    console.error('Login failed:', error);
    // Could show toast notification here
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-4">
      {/* Background decorations */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <motion.div
          className="absolute top-20 left-20 text-blue-400/20"
          animate={{
            y: [0, -20, 0],
            rotate: [0, 10, 0],
          }}
          transition={{
            duration: 6,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        >
          <Heart className="w-24 h-24" />
        </motion.div>

        <motion.div
          className="absolute bottom-20 right-20 text-purple-400/20"
          animate={{
            y: [0, 20, 0],
            rotate: [0, -10, 0],
          }}
          transition={{
            duration: 5,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        >
          <Sparkles className="w-32 h-32" />
        </motion.div>

        <motion.div
          className="absolute top-1/2 left-10 text-pink-400/20"
          animate={{
            scale: [1, 1.2, 1],
            rotate: [0, 180, 360],
          }}
          transition={{
            duration: 8,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        >
          <Star className="w-16 h-16" />
        </motion.div>
      </div>

      {/* Login card */}
      <motion.div
        className="relative z-10 w-full max-w-md"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <div className="frosted-card text-center space-y-8">
          {/* Logo/Title */}
          <div className="space-y-4">
            <motion.div
              className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-gradient-to-br from-blue-400 to-purple-400 shadow-lg"
              animate={{
                scale: [1, 1.05, 1],
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                ease: 'easeInOut',
              }}
            >
              <Heart className="w-10 h-10 text-white fill-white" />
            </motion.div>

            <h1 className="text-4xl font-bold gradient-text">
              PAS in Peace
            </h1>

            <p className="text-white/70 text-lg">
              Восстановление связи с ребёнком
            </p>
          </div>

          {/* Description */}
          <div className="space-y-3 text-white/80">
            <p className="flex items-center justify-center gap-2">
              <Sparkles className="w-5 h-5 text-yellow-400" />
              Персонализированные квесты для детей
            </p>
            <p className="flex items-center justify-center gap-2">
              <Heart className="w-5 h-5 text-pink-400" />
              Письма и воспоминания
            </p>
            <p className="flex items-center justify-center gap-2">
              <Star className="w-5 h-5 text-purple-400" />
              4 трека восстановления
            </p>
          </div>

          {/* Telegram Auth Button */}
          <div className="space-y-4">
            <div className="h-px bg-gradient-to-r from-transparent via-white/20 to-transparent" />

            {/* Official Telegram Widget */}
            <TelegramAuthButton
              botUsername={botUsername}
              onAuthSuccess={handleAuthSuccess}
              onAuthError={handleAuthError}
              buttonSize="large"
              cornerRadius={16}
              className="flex justify-center"
            />

            {/* Alternative: Custom styled button */}
            {/*
            <CustomTelegramAuthButton
              onClick={() => {
                // Could open Telegram bot link directly
                window.open(`https://t.me/${botUsername}?start=auth`, '_blank');
              }}
            />
            */}

            <p className="text-xs text-white/50">
              Войдя, вы соглашаетесь с{' '}
              <a href="/privacy" className="text-blue-400 hover:text-blue-300">
                политикой конфиденциальности
              </a>
            </p>
          </div>
        </div>

        {/* Additional info */}
        <motion.div
          className="mt-8 text-center text-white/60 text-sm"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
        >
          <p>
            Помощь родителям при родительском отчуждении
          </p>
          <p className="mt-2">
            Создано с ❤️ для восстановления связей
          </p>
        </motion.div>
      </motion.div>
    </div>
  );
}
