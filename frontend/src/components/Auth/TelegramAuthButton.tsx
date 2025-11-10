/**
 * TelegramAuthButton - Telegram Login Widget
 *
 * Features:
 * - Telegram OAuth integration
 * - Automatic script loading
 * - Callback handling
 * - Glass morphism design
 */

import React, { useEffect, useRef } from 'react';
import { useTelegramLogin } from '../../lib/hooks/useAuth';
import type { TelegramAuthData } from '../../lib/types';

export interface TelegramAuthButtonProps {
  botUsername: string; // Your bot username (without @)
  onAuthSuccess?: (user: any) => void;
  onAuthError?: (error: Error) => void;
  buttonSize?: 'large' | 'medium' | 'small';
  cornerRadius?: number;
  requestAccess?: boolean;
  usePic?: boolean;
  lang?: string;
  className?: string;
}

// Declare global Telegram widget
declare global {
  interface Window {
    TelegramLoginWidget?: {
      dataOnauth: (user: TelegramAuthData) => void;
    };
  }
}

export const TelegramAuthButton: React.FC<TelegramAuthButtonProps> = ({
  botUsername,
  onAuthSuccess,
  onAuthError,
  buttonSize = 'large',
  cornerRadius = 20,
  requestAccess = true,
  usePic = true,
  lang = 'ru',
  className = '',
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const { mutate: login, isPending } = useTelegramLogin();

  useEffect(() => {
    // Callback function that Telegram widget will call
    window.TelegramLoginWidget = {
      dataOnauth: (user: TelegramAuthData) => {
        console.log('Telegram auth data received:', user);

        // Call our login mutation
        login(user, {
          onSuccess: (data) => {
            console.log('Login successful:', data);
            onAuthSuccess?.(data.user);
          },
          onError: (error) => {
            console.error('Login failed:', error);
            onAuthError?.(error as Error);
          },
        });
      },
    };

    // Load Telegram widget script
    if (containerRef.current && !document.getElementById('telegram-login-script')) {
      const script = document.createElement('script');
      script.id = 'telegram-login-script';
      script.src = 'https://telegram.org/js/telegram-widget.js?22';
      script.async = true;
      script.setAttribute('data-telegram-login', botUsername);
      script.setAttribute('data-size', buttonSize);
      script.setAttribute('data-radius', cornerRadius.toString());
      script.setAttribute('data-request-access', requestAccess ? 'write' : '');
      script.setAttribute('data-userpic', usePic.toString());
      script.setAttribute('data-lang', lang);
      script.setAttribute('data-onauth', 'TelegramLoginWidget.dataOnauth(user)');

      containerRef.current.appendChild(script);
    }

    return () => {
      // Cleanup
      delete window.TelegramLoginWidget;
    };
  }, [botUsername, buttonSize, cornerRadius, requestAccess, usePic, lang, login]);

  return (
    <div className={`relative ${className}`}>
      {/* Glass container for Telegram button */}
      <div
        ref={containerRef}
        className="liquid-glass inline-flex items-center justify-center p-4"
      />

      {/* Loading overlay */}
      {isPending && (
        <div className="absolute inset-0 flex items-center justify-center bg-black/50 backdrop-blur rounded-2xl">
          <div className="flex flex-col items-center gap-3">
            <div className="w-8 h-8 border-4 border-blue-400 border-t-transparent rounded-full animate-spin" />
            <span className="text-sm text-white font-medium">Вход...</span>
          </div>
        </div>
      )}
    </div>
  );
};

/**
 * Custom styled Telegram auth button (alternative to widget)
 */
export interface CustomTelegramAuthButtonProps {
  onClick: () => void;
  isLoading?: boolean;
  className?: string;
}

export const CustomTelegramAuthButton: React.FC<CustomTelegramAuthButtonProps> = ({
  onClick,
  isLoading = false,
  className = '',
}) => {
  return (
    <button
      onClick={onClick}
      disabled={isLoading}
      className={`
        glass-button
        flex items-center gap-3
        px-6 py-4
        bg-gradient-to-r from-blue-500/20 to-cyan-500/20
        hover:from-blue-500/30 hover:to-cyan-500/30
        disabled:opacity-50 disabled:cursor-not-allowed
        ${className}
      `}
    >
      {/* Telegram icon */}
      <svg
        width="24"
        height="24"
        viewBox="0 0 24 24"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm5.562 8.161l-1.94 9.134c-.146.658-.537.818-1.084.508l-3-2.211-1.446 1.394c-.16.16-.295.295-.605.295l.213-3.053 5.56-5.023c.242-.213-.054-.333-.373-.12l-6.871 4.326-2.962-.924c-.643-.204-.657-.643.136-.953l11.575-4.461c.537-.194 1.006.131.832.95z"
          fill="currentColor"
        />
      </svg>

      {/* Button text */}
      <span className="font-medium">
        {isLoading ? 'Загрузка...' : 'Войти через Telegram'}
      </span>

      {/* Loading spinner */}
      {isLoading && (
        <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
      )}
    </button>
  );
};

export default TelegramAuthButton;
