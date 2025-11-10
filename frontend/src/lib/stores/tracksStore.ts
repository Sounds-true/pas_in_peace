/**
 * Tracks Store - Recovery tracks state management
 *
 * Handles:
 * - 4 recovery tracks (SELF_WORK, CHILD_CONNECTION, NEGOTIATION, COMMUNITY)
 * - Track progress
 * - Primary track selection
 * - Milestones
 */

import { create } from 'zustand';
import type { RecoveryTrack } from '../types';

interface TracksState {
  // State
  tracks: RecoveryTrack[];
  primaryTrackId: string | null;
  isLoading: boolean;

  // Actions
  setTracks: (tracks: RecoveryTrack[]) => void;
  updateTrack: (trackId: string, updates: Partial<RecoveryTrack>) => void;
  setPrimaryTrack: (trackId: string) => void;
  completeMilestone: (trackId: string, milestoneId: string) => void;
  setLoading: (loading: boolean) => void;

  // Selectors
  getPrimaryTrack: () => RecoveryTrack | null;
  getTrackById: (trackId: string) => RecoveryTrack | undefined;
}

export const useTracksStore = create<TracksState>((set, get) => ({
  // Initial state
  tracks: [],
  primaryTrackId: null,
  isLoading: false,

  // Actions
  setTracks: (tracks) =>
    set({
      tracks,
      primaryTrackId: tracks.find((t) => t.isPrimary)?.id || null,
      isLoading: false,
    }),

  updateTrack: (trackId, updates) =>
    set((state) => ({
      tracks: state.tracks.map((track) =>
        track.id === trackId ? { ...track, ...updates } : track
      ),
    })),

  setPrimaryTrack: (trackId) =>
    set((state) => ({
      tracks: state.tracks.map((track) => ({
        ...track,
        isPrimary: track.id === trackId,
      })),
      primaryTrackId: trackId,
    })),

  completeMilestone: (trackId, milestoneId) =>
    set((state) => ({
      tracks: state.tracks.map((track) => {
        if (track.id !== trackId) return track;

        const updatedMilestones = track.milestones.map((m) =>
          m.id === milestoneId
            ? { ...m, completed: true, completedAt: new Date().toISOString() }
            : m
        );

        const milestonesCompleted = updatedMilestones.filter(
          (m) => m.completed
        ).length;

        return {
          ...track,
          milestones: updatedMilestones,
          milestonesCompleted,
          progress: Math.round(
            (milestonesCompleted / track.milestonesTotal) * 100
          ),
          lastActivityAt: new Date().toISOString(),
        };
      }),
    })),

  setLoading: (loading) =>
    set({
      isLoading: loading,
    }),

  // Selectors
  getPrimaryTrack: () => {
    const state = get();
    return state.tracks.find((t) => t.isPrimary) || null;
  },

  getTrackById: (trackId) => {
    const state = get();
    return state.tracks.find((t) => t.id === trackId);
  },
}));
