/**
 * useAuth - Authentication hooks
 *
 * Provides:
 * - Login with Telegram
 * - Logout
 * - Current user query
 * - Token refresh
 */

import React from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../api/client';
import { useUserStore } from '../stores/userStore';
import type { TelegramAuthData } from '../types';

/**
 * Get current user
 */
export function useCurrentUser() {
  const { setUser, setLoading } = useUserStore();

  const query = useQuery({
    queryKey: ['user', 'me'],
    queryFn: async () => {
      const user = await apiClient.getCurrentUser();
      return user;
    },
    retry: false,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  // Handle side effects with useEffect instead of callbacks
  React.useEffect(() => {
    if (query.data) {
      setUser(query.data);
      setLoading(false);
    } else if (query.error) {
      setUser(null);
      setLoading(false);
    }
  }, [query.data, query.error, setUser, setLoading]);

  return query;
}

/**
 * Login with Telegram
 */
export function useTelegramLogin() {
  const queryClient = useQueryClient();
  const { setUser } = useUserStore();

  return useMutation({
    mutationFn: (authData: TelegramAuthData) => apiClient.telegramAuth(authData),
    onSuccess: (data) => {
      setUser(data.user);
      queryClient.setQueryData(['user', 'me'], data.user);
      // Invalidate all queries to refetch with new auth
      queryClient.invalidateQueries({ queryKey: [] });
    },
  });
}

/**
 * Logout
 */
export function useLogout() {
  const queryClient = useQueryClient();
  const { logout } = useUserStore();

  return useMutation({
    mutationFn: () => apiClient.logout(),
    onSuccess: () => {
      logout();
      // Clear all query cache
      queryClient.clear();
    },
  });
}

/**
 * Refresh token
 */
export function useRefreshToken() {
  return useMutation({
    mutationFn: () => apiClient.refreshToken(),
  });
}

/**
 * Update user profile
 */
export function useUpdateUser() {
  const queryClient = useQueryClient();
  const { updateUser } = useUserStore();

  return useMutation({
    mutationFn: (updates: Parameters<typeof apiClient.updateUser>[0]) =>
      apiClient.updateUser(updates),
    onSuccess: (updatedUser) => {
      updateUser(updatedUser);
      queryClient.setQueryData(['user', 'me'], updatedUser);
    },
  });
}
