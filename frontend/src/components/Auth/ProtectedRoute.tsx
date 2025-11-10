/**
 * ProtectedRoute - HOC for authentication guard
 *
 * Features:
 * - Checks if user is authenticated
 * - Redirects to login if not authenticated
 * - Shows loading state
 * - Auto-refreshes token if needed
 */

import React, { useEffect } from 'react';
import { useRouter } from 'next/router';
import { useUserStore } from '../../lib/stores/userStore';
import { useCurrentUser } from '../../lib/hooks/useAuth';

export interface ProtectedRouteProps {
  children: React.ReactNode;
  redirectTo?: string;
  loadingComponent?: React.ReactNode;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  redirectTo = '/login',
  loadingComponent,
}) => {
  const router = useRouter();
  const { isAuthenticated, isLoading } = useUserStore();
  const { isLoading: isLoadingUser, error } = useCurrentUser();

  useEffect(() => {
    // If not authenticated and not loading, redirect to login
    if (!isAuthenticated && !isLoading && !isLoadingUser && error) {
      router.push(redirectTo);
    }
  }, [isAuthenticated, isLoading, isLoadingUser, error, router, redirectTo]);

  // Show loading state
  if (isLoading || isLoadingUser) {
    return (
      loadingComponent || (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
          <div className="liquid-glass p-8 flex flex-col items-center gap-4">
            <div className="w-16 h-16 border-4 border-blue-400 border-t-transparent rounded-full animate-spin" />
            <p className="text-white text-lg font-medium">Загрузка...</p>
          </div>
        </div>
      )
    );
  }

  // If not authenticated, show nothing (will redirect)
  if (!isAuthenticated) {
    return null;
  }

  // User is authenticated, show protected content
  return <>{children}</>;
};

/**
 * Higher-Order Component version
 */
export function withAuth<P extends object>(
  Component: React.ComponentType<P>,
  options?: {
    redirectTo?: string;
    loadingComponent?: React.ReactNode;
  }
) {
  return function ProtectedComponent(props: P) {
    return (
      <ProtectedRoute
        redirectTo={options?.redirectTo}
        loadingComponent={options?.loadingComponent}
      >
        <Component {...props} />
      </ProtectedRoute>
    );
  };
}

export default ProtectedRoute;
