/**
 * Mock Auth Page - Testing without backend
 *
 * Bypasses Telegram OAuth and creates mock user session
 */

import React, { useState } from 'react';
import { useRouter } from 'next/router';
import { motion } from 'framer-motion';
import { Heart, Sparkles, LogIn, User } from 'lucide-react';
import { useUserStore } from '../lib/stores/userStore';

export default function MockLoginPage() {
  const router = useRouter();
  const { setUser } = useUserStore();
  const [isLoading, setIsLoading] = useState(false);

  const handleMockLogin = async (userName: string) => {
    setIsLoading(true);

    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 500));

    // Create mock user
    const mockUser = {
      id: Date.now(),
      telegram_id: '123456789',
      first_name: userName,
      username: userName.toLowerCase(),
      photo_url: `https://ui-avatars.com/api/?name=${userName}&background=random`,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      child_name: 'Маша',
      child_age: 9,
      child_interests: ['космос', 'рисование'],
      primary_track: 'self_work',
      notification_enabled: true,
    };

    // Set mock token
    if (typeof window !== 'undefined') {
      localStorage.setItem('auth_token', 'mock_token_' + Date.now());
    }

    // Set user in store
    setUser(mockUser);

    // Redirect to dashboard
    router.push('/dashboard');
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-4">
      {/* Background decorations */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <motion.div
          className="absolute top-20 left-20 text-blue-400/20"
          animate={{ y: [0, -20, 0], rotate: [0, 10, 0] }}
          transition={{ duration: 6, repeat: Infinity, ease: 'easeInOut' }}
        >
          <Heart className="w-24 h-24" />
        </motion.div>

        <motion.div
          className="absolute bottom-20 right-20 text-purple-400/20"
          animate={{ y: [0, 20, 0], rotate: [0, -10, 0] }}
          transition={{ duration: 5, repeat: Infinity, ease: 'easeInOut' }}
        >
          <Sparkles className="w-32 h-32" />
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
          {/* Logo */}
          <div className="space-y-4">
            <motion.div
              className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-gradient-to-br from-blue-400 to-purple-400 shadow-lg"
              animate={{ scale: [1, 1.05, 1] }}
              transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
            >
              <Heart className="w-10 h-10 text-white fill-white" />
            </motion.div>

            <h1 className="text-4xl font-bold gradient-text">PAS in Peace</h1>
            <p className="text-white/70 text-lg">Демо режим</p>
          </div>

          {/* Info */}
          <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-xl p-4">
            <p className="text-yellow-200 text-sm">
              ⚠️ <strong>Mock режим</strong> - для тестирования UI без backend
            </p>
          </div>

          {/* Mock users */}
          <div className="space-y-3">
            <h3 className="text-white font-medium">Войти как:</h3>

            <button
              onClick={() => handleMockLogin('Алексей')}
              disabled={isLoading}
              className="w-full glass-button bg-blue-500/20 hover:bg-blue-500/30 flex items-center justify-center gap-3 py-4"
            >
              <User className="w-5 h-5" />
              <span className="font-medium">Алексей (родитель)</span>
            </button>

            <button
              onClick={() => handleMockLogin('Мария')}
              disabled={isLoading}
              className="w-full glass-button bg-purple-500/20 hover:bg-purple-500/30 flex items-center justify-center gap-3 py-4"
            >
              <User className="w-5 h-5" />
              <span className="font-medium">Мария (родитель)</span>
            </button>

            <button
              onClick={() => handleMockLogin('Иван')}
              disabled={isLoading}
              className="w-full glass-button bg-pink-500/20 hover:bg-pink-500/30 flex items-center justify-center gap-3 py-4"
            >
              <User className="w-5 h-5" />
              <span className="font-medium">Иван (родитель)</span>
            </button>
          </div>

          {/* Note */}
          <div className="pt-4 border-t border-white/10">
            <p className="text-xs text-white/50">
              Это временная страница для тестирования UI.
              <br />
              Для реального входа используйте Telegram OAuth.
            </p>
          </div>

          {/* Link to real login */}
          <a
            href="/login"
            className="inline-flex items-center gap-2 text-sm text-blue-400 hover:text-blue-300"
          >
            <LogIn className="w-4 h-4" />
            Войти через Telegram
          </a>
        </div>
      </motion.div>
    </div>
  );
}
