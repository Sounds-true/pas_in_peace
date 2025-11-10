/**
 * useTracks - Recovery tracks hooks
 */

import React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../api/client';
import { useTracksStore } from '../stores/tracksStore';

/**
 * Get all recovery tracks
 */
export function useTracks() {
  const { setTracks, setLoading } = useTracksStore();

  const query = useQuery({
    queryKey: ['tracks'],
    queryFn: async () => {
      const tracks = await apiClient.getTrackProgress();
      return tracks;
    },
    staleTime: 2 * 60 * 1000, // 2 minutes
  });

  // Handle side effects with useEffect
  React.useEffect(() => {
    if (query.data) {
      setTracks(query.data);
      setLoading(false);
    }
  }, [query.data, setTracks, setLoading]);

  return query;
}

/**
 * Get single track
 */
export function useTrack(trackId: string) {
  return useQuery({
    queryKey: ['tracks', trackId],
    queryFn: () => apiClient.getTrack(trackId),
    enabled: !!trackId,
  });
}

/**
 * Update primary track
 */
export function useUpdatePrimaryTrack() {
  const queryClient = useQueryClient();
  const { setPrimaryTrack } = useTracksStore();

  return useMutation({
    mutationFn: (trackId: string) => apiClient.updatePrimaryTrack(trackId),
    onSuccess: (_, trackId) => {
      setPrimaryTrack(trackId);
      queryClient.invalidateQueries({ queryKey: ['tracks'] });
    },
  });
}
