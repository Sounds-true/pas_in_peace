/**
 * Home Page - Redirects to dashboard or login
 */

import { useEffect } from 'react';
import { useRouter } from 'next/router';
import { useUserStore } from '../lib/stores/userStore';

export default function HomePage() {
  const router = useRouter();
  const { isAuthenticated } = useUserStore();

  useEffect(() => {
    // Redirect based on auth status
    if (isAuthenticated) {
      router.replace('/dashboard');
    } else {
      router.replace('/login');
    }
  }, [isAuthenticated, router]);

  // Show loading while redirecting
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <div className="liquid-glass p-8 flex flex-col items-center gap-4">
        <div className="w-16 h-16 border-4 border-blue-400 border-t-transparent rounded-full animate-spin" />
        <p className="text-white text-lg font-medium">Загрузка...</p>
      </div>
    </div>
  );
}
