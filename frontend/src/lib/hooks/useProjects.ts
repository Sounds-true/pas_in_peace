/**
 * useProjects - Projects (Quests, Letters, Goals) hooks
 */

import React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../api/client';
import { useProjectsStore } from '../stores/projectsStore';
import type { Project, ProjectType, ProjectStatus } from '../types';

/**
 * Get all projects
 */
export function useProjects(filters?: {
  type?: ProjectType;
  status?: ProjectStatus;
}) {
  const { setProjects, setLoading } = useProjectsStore();

  const query = useQuery({
    queryKey: ['projects', filters],
    queryFn: async () => {
      const projects = await apiClient.getProjects(filters);
      return projects;
    },
    staleTime: 1 * 60 * 1000, // 1 minute
  });

  // Handle side effects with useEffect
  React.useEffect(() => {
    if (query.data) {
      setProjects(query.data);
      setLoading(false);
    }
  }, [query.data, setProjects, setLoading]);

  return query;
}

/**
 * Get single project
 */
export function useProject(projectId: string) {
  return useQuery({
    queryKey: ['projects', projectId],
    queryFn: () => apiClient.getProject(projectId),
    enabled: !!projectId,
  });
}

/**
 * Create project
 */
export function useCreateProject() {
  const queryClient = useQueryClient();
  const { addProject } = useProjectsStore();

  return useMutation({
    mutationFn: (data: Parameters<typeof apiClient.createProject>[0]) =>
      apiClient.createProject(data),
    onSuccess: (newProject) => {
      addProject(newProject);
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    },
  });
}

/**
 * Update project
 */
export function useUpdateProject() {
  const queryClient = useQueryClient();
  const { updateProject } = useProjectsStore();

  return useMutation({
    mutationFn: ({
      id,
      changes,
    }: {
      id: string;
      changes: Partial<Project>;
    }) => apiClient.updateProject(id, changes),
    onSuccess: (updatedProject) => {
      updateProject(updatedProject.id, updatedProject);
      queryClient.invalidateQueries({ queryKey: ['projects'] });
      queryClient.invalidateQueries({ queryKey: ['projects', updatedProject.id] });
    },
  });
}

/**
 * Delete project
 */
export function useDeleteProject() {
  const queryClient = useQueryClient();
  const { removeProject } = useProjectsStore();

  return useMutation({
    mutationFn: (projectId: string) => apiClient.deleteProject(projectId),
    onSuccess: (_, projectId) => {
      removeProject(projectId);
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    },
  });
}

// ========== Quests ==========

/**
 * Get all quests
 */
export function useQuests() {
  return useQuery({
    queryKey: ['quests'],
    queryFn: () => apiClient.getQuests(),
    staleTime: 1 * 60 * 1000,
  });
}

/**
 * Get single quest
 */
export function useQuest(questId: string) {
  return useQuery({
    queryKey: ['quests', questId],
    queryFn: () => apiClient.getQuest(questId),
    enabled: !!questId,
  });
}

/**
 * Create quest
 */
export function useCreateQuest() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: Parameters<typeof apiClient.createQuest>[0]) =>
      apiClient.createQuest(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['quests'] });
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    },
  });
}

/**
 * Update quest
 */
export function useUpdateQuest() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      id,
      changes,
    }: {
      id: string;
      changes: Parameters<typeof apiClient.updateQuest>[1];
    }) => apiClient.updateQuest(id, changes),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['quests'] });
      queryClient.invalidateQueries({ queryKey: ['quests', variables.id] });
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    },
  });
}
