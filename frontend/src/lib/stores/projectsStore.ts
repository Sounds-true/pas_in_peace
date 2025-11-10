/**
 * Projects Store - Quests, Letters, Goals state management
 *
 * Handles:
 * - All user projects (quests, letters, goals)
 * - Filtering and sorting
 * - CRUD operations
 */

import { create } from 'zustand';
import type { Project, ProjectType, ProjectStatus } from '../types';

interface ProjectsState {
  // State
  projects: Project[];
  isLoading: boolean;
  filters: {
    type?: ProjectType;
    status?: ProjectStatus;
  };

  // Actions
  setProjects: (projects: Project[]) => void;
  addProject: (project: Project) => void;
  updateProject: (projectId: string, updates: Partial<Project>) => void;
  removeProject: (projectId: string) => void;
  setFilters: (filters: Partial<ProjectsState['filters']>) => void;
  setLoading: (loading: boolean) => void;

  // Selectors
  getFilteredProjects: () => Project[];
  getProjectById: (projectId: string) => Project | undefined;
  getProjectsByType: (type: ProjectType) => Project[];
  getProjectsByStatus: (status: ProjectStatus) => Project[];
}

export const useProjectsStore = create<ProjectsState>((set, get) => ({
  // Initial state
  projects: [],
  isLoading: false,
  filters: {},

  // Actions
  setProjects: (projects) =>
    set({
      projects,
      isLoading: false,
    }),

  addProject: (project) =>
    set((state) => ({
      projects: [project, ...state.projects],
    })),

  updateProject: (projectId, updates) =>
    set((state) => ({
      projects: state.projects.map((project) =>
        project.id === projectId
          ? {
              ...project,
              ...updates,
              updatedAt: new Date().toISOString(),
            }
          : project
      ),
    })),

  removeProject: (projectId) =>
    set((state) => ({
      projects: state.projects.filter((p) => p.id !== projectId),
    })),

  setFilters: (filters) =>
    set((state) => ({
      filters: { ...state.filters, ...filters },
    })),

  setLoading: (loading) =>
    set({
      isLoading: loading,
    }),

  // Selectors
  getFilteredProjects: () => {
    const state = get();
    let filtered = state.projects;

    if (state.filters.type) {
      filtered = filtered.filter((p) => p.type === state.filters.type);
    }

    if (state.filters.status) {
      filtered = filtered.filter((p) => p.status === state.filters.status);
    }

    // Sort by updatedAt descending
    return filtered.sort(
      (a, b) =>
        new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
    );
  },

  getProjectById: (projectId) => {
    const state = get();
    return state.projects.find((p) => p.id === projectId);
  },

  getProjectsByType: (type) => {
    const state = get();
    return state.projects.filter((p) => p.type === type);
  },

  getProjectsByStatus: (status) => {
    const state = get();
    return state.projects.filter((p) => p.status === status);
  },
}));
