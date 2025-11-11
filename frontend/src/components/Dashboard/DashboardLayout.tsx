/**
 * DashboardLayout - Unified layout with Sidebar and Header
 *
 * Features:
 * - Sidebar navigation (collapsible on mobile)
 * - Header with user info
 * - Responsive design
 * - Glass morphism throughout
 */

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Menu, X, LogOut, Settings, Bell } from 'lucide-react';
import { useRouter } from 'next/router';
import { SidebarEnhanced } from './SidebarEnhanced';
import { useUserStore } from '../../lib/stores/userStore';
import { useLogout } from '../../lib/hooks/useAuth';

export interface DashboardLayoutProps {
  children: React.ReactNode;
  title?: string;
  actions?: React.ReactNode;
}

export const DashboardLayout: React.FC<DashboardLayoutProps> = ({
  children,
  title,
  actions,
}) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { user } = useUserStore();
  const { mutate: logout, isPending: isLoggingOut } = useLogout();
  const router = useRouter();

  const handleLogout = () => {
    logout(undefined, {
      onSuccess: () => {
        router.push('/login');
      },
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex">
      {/* Sidebar */}
      <SidebarEnhanced isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      {/* Main content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <header className="liquid-glass border-b border-white/10 sticky top-0 z-30">
          <div className="px-4 sm:px-6 lg:px-8 py-4">
            <div className="flex items-center justify-between">
              {/* Left: Mobile menu + Title */}
              <div className="flex items-center gap-4">
                {/* Mobile menu button */}
                <button
                  onClick={() => setSidebarOpen(!sidebarOpen)}
                  className="lg:hidden p-2 rounded-lg hover:bg-white/10 transition-colors"
                  aria-label="Toggle menu"
                >
                  {sidebarOpen ? (
                    <X className="w-6 h-6 text-white" />
                  ) : (
                    <Menu className="w-6 h-6 text-white" />
                  )}
                </button>

                {/* Page title */}
                {title && (
                  <h1 className="text-xl font-bold text-white hidden sm:block">
                    {title}
                  </h1>
                )}
              </div>

              {/* Right: Actions + User menu */}
              <div className="flex items-center gap-3">
                {/* Custom actions */}
                {actions}

                {/* Notifications */}
                <button
                  className="p-2 rounded-lg hover:bg-white/10 transition-colors relative"
                  aria-label="Notifications"
                >
                  <Bell className="w-5 h-5 text-white/70 hover:text-white" />
                  {/* Badge */}
                  <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" />
                </button>

                {/* Settings */}
                <button
                  onClick={() => router.push('/settings')}
                  className="p-2 rounded-lg hover:bg-white/10 transition-colors"
                  aria-label="Settings"
                >
                  <Settings className="w-5 h-5 text-white/70 hover:text-white" />
                </button>

                {/* User menu */}
                <div className="flex items-center gap-3 pl-3 border-l border-white/10">
                  {/* User info */}
                  {user && (
                    <div className="text-right hidden sm:block">
                      <p className="text-sm font-medium text-white">
                        {user.first_name}
                      </p>
                      {user.username && (
                        <p className="text-xs text-white/60">@{user.username}</p>
                      )}
                    </div>
                  )}

                  {/* Avatar */}
                  {user?.photo_url ? (
                    <img
                      src={user.photo_url}
                      alt={user.first_name}
                      className="w-10 h-10 rounded-full border-2 border-white/20 hover:border-blue-400/50 transition-colors cursor-pointer"
                    />
                  ) : (
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-400 to-pink-400 flex items-center justify-center text-white font-bold cursor-pointer hover:scale-110 transition-transform">
                      {user?.first_name?.[0]?.toUpperCase() || 'U'}
                    </div>
                  )}

                  {/* Logout */}
                  <button
                    onClick={handleLogout}
                    disabled={isLoggingOut}
                    className="p-2 rounded-lg hover:bg-red-500/20 transition-colors disabled:opacity-50"
                    aria-label="Logout"
                  >
                    <LogOut className="w-5 h-5 text-white/70 hover:text-red-400" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </header>

        {/* Main content area */}
        <main className="flex-1 overflow-y-auto">
          <div className="px-4 sm:px-6 lg:px-8 py-8">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
            >
              {children}
            </motion.div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default DashboardLayout;
