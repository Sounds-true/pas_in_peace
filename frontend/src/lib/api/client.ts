/**
 * API Client for PAS Bot Backend
 *
 * Handles all HTTP requests to the backend API with:
 * - JWT token management
 * - Request/response interceptors
 * - Error handling
 * - TypeScript types
 */

import type {
  User,
  Quest,
  RecoveryTrack,
  Project,
  Letter,
  AnalyticsData,
} from '../types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000';

class APIClient {
  private baseURL: string;
  private token: string | null = null;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
    // Load token from localStorage if available
    if (typeof window !== 'undefined') {
      this.token = localStorage.getItem('auth_token');
    }
  }

  /**
   * Set authentication token
   */
  setToken(token: string) {
    this.token = token;
    if (typeof window !== 'undefined') {
      localStorage.setItem('auth_token', token);
    }
  }

  /**
   * Clear authentication token
   */
  clearToken() {
    this.token = null;
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token');
    }
  }

  /**
   * Make HTTP request
   */
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string>),
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    const url = `${this.baseURL}${endpoint}`;

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({
          message: response.statusText,
        }));
        throw new APIError(error.message || 'Request failed', response.status, error);
      }

      return await response.json();
    } catch (error) {
      if (error instanceof APIError) {
        throw error;
      }
      throw new APIError(
        error instanceof Error ? error.message : 'Network error',
        0,
        error
      );
    }
  }

  /**
   * GET request
   */
  async get<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'GET' });
  }

  /**
   * POST request
   */
  async post<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  /**
   * PUT request
   */
  async put<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  /**
   * DELETE request
   */
  async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'DELETE' });
  }

  // ========== Authentication ==========

  /**
   * Authenticate with Telegram
   */
  async telegramAuth(authData: {
    id: number;
    first_name: string;
    username?: string;
    photo_url?: string;
    auth_date: number;
    hash: string;
  }): Promise<{ token: string; user: User }> {
    const response = await this.post<{ token: string; user: User }>(
      '/api/auth/telegram',
      authData
    );
    this.setToken(response.token);
    return response;
  }

  /**
   * Refresh authentication token
   */
  async refreshToken(): Promise<{ token: string }> {
    const response = await this.post<{ token: string }>('/api/auth/refresh');
    this.setToken(response.token);
    return response;
  }

  /**
   * Logout
   */
  async logout(): Promise<void> {
    await this.post('/api/auth/logout');
    this.clearToken();
  }

  // ========== User ==========

  /**
   * Get current user
   */
  async getCurrentUser(): Promise<User> {
    return this.get<User>('/api/user/me');
  }

  /**
   * Update user profile
   */
  async updateUser(data: Partial<User>): Promise<User> {
    return this.put<User>('/api/user/me', data);
  }

  // ========== Recovery Tracks ==========

  /**
   * Get all recovery tracks with progress
   */
  async getTrackProgress(): Promise<RecoveryTrack[]> {
    return this.get<RecoveryTrack[]>('/api/tracks');
  }

  /**
   * Update primary track focus
   */
  async updatePrimaryTrack(trackId: string): Promise<void> {
    return this.put('/api/tracks/primary', { trackId });
  }

  /**
   * Get track details
   */
  async getTrack(trackId: string): Promise<RecoveryTrack> {
    return this.get<RecoveryTrack>(`/api/tracks/${trackId}`);
  }

  // ========== Projects (Quests + Letters) ==========

  /**
   * Get all projects with optional filters
   */
  async getProjects(filters?: {
    type?: 'quest' | 'letter' | 'goal';
    status?: 'draft' | 'active' | 'completed' | 'moderation';
  }): Promise<Project[]> {
    const params = new URLSearchParams(filters as any);
    return this.get<Project[]>(`/api/projects?${params}`);
  }

  /**
   * Get project by ID
   */
  async getProject(id: string): Promise<Project> {
    return this.get<Project>(`/api/projects/${id}`);
  }

  /**
   * Create new project
   */
  async createProject(data: {
    type: 'quest' | 'letter' | 'goal';
    title: string;
    data: any;
  }): Promise<Project> {
    return this.post<Project>('/api/projects', data);
  }

  /**
   * Update project
   */
  async updateProject(id: string, changes: Partial<Project>): Promise<Project> {
    return this.put<Project>(`/api/projects/${id}`, changes);
  }

  /**
   * Delete project
   */
  async deleteProject(id: string): Promise<void> {
    return this.delete(`/api/projects/${id}`);
  }

  // ========== Quests ==========

  /**
   * Get all quests
   */
  async getQuests(): Promise<Quest[]> {
    return this.get<Quest[]>('/api/quests');
  }

  /**
   * Get quest by ID
   */
  async getQuest(id: string): Promise<Quest> {
    return this.get<Quest>(`/api/quests/${id}`);
  }

  /**
   * Create new quest
   */
  async createQuest(data: {
    title: string;
    description?: string;
    childName: string;
    childAge: number;
    yaml?: string;
  }): Promise<Quest> {
    return this.post<Quest>('/api/quests', data);
  }

  /**
   * Update quest
   */
  async updateQuest(id: string, changes: Partial<Quest>): Promise<Quest> {
    return this.put<Quest>(`/api/quests/${id}`, changes);
  }

  /**
   * Get quest preview (YAML to graph)
   */
  async getQuestPreview(questId: string): Promise<any> {
    return this.get(`/api/quests/${questId}/preview`);
  }

  /**
   * Export quest (finalize)
   */
  async exportQuest(questId: string): Promise<{ yaml: string }> {
    return this.post(`/api/quests/${questId}/export`);
  }

  // ========== Quest Builder (WebSocket) ==========

  /**
   * Start quest creation dialogue
   * Returns WebSocket connection
   */
  startQuestCreation(questId: string): WebSocket {
    const wsURL = `${WS_URL}/ws/quest-builder/${questId}?token=${this.token}`;
    const ws = new WebSocket(wsURL);

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    ws.onclose = () => {
      console.log('WebSocket closed');
    };

    return ws;
  }

  /**
   * Send message to quest builder
   */
  sendQuestMessage(ws: WebSocket, message: string): void {
    if (ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: 'message', content: message }));
    }
  }

  // ========== Letters ==========

  /**
   * Get all letters
   */
  async getLetters(): Promise<Letter[]> {
    return this.get<Letter[]>('/api/letters');
  }

  /**
   * Create new letter
   */
  async createLetter(type: string): Promise<Letter> {
    return this.post<Letter>('/api/letters', { type });
  }

  /**
   * Update letter
   */
  async updateLetter(id: string, content: string): Promise<Letter> {
    return this.put<Letter>(`/api/letters/${id}`, { content });
  }

  /**
   * Send letter
   */
  async sendLetter(id: string): Promise<void> {
    return this.post(`/api/letters/${id}/send`);
  }

  // ========== Analytics ==========

  /**
   * Get emotional trends
   */
  async getEmotionalTrends(period: '7d' | '30d' | '90d'): Promise<AnalyticsData> {
    return this.get<AnalyticsData>(`/api/analytics/trends?period=${period}`);
  }

  /**
   * Get child progress for quest
   */
  async getChildProgress(questId: string): Promise<any> {
    return this.get(`/api/analytics/quests/${questId}/progress`);
  }
}

/**
 * Custom API Error
 */
export class APIError extends Error {
  status: number;
  data: any;

  constructor(message: string, status: number, data?: any) {
    super(message);
    this.name = 'APIError';
    this.status = status;
    this.data = data;
  }
}

// Export singleton instance
export const apiClient = new APIClient(API_URL);

export default apiClient;
