"use client"

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { apiClient } from "@/lib/api-client"
import type { GrowRoom } from "@/lib/types/cultivation"
import type { PaginatedResponse, ListParams } from "@/lib/types/common"

export function useGrowRooms(params: ListParams = {}) {
  return useQuery({
    queryKey: ["grow-rooms", params],
    queryFn: () => apiClient.get<PaginatedResponse<GrowRoom>>("/grow-rooms/", params),
  })
}

export function useGrowRoom(id: number) {
  return useQuery({
    queryKey: ["grow-rooms", id],
    queryFn: () => apiClient.get<GrowRoom>(`/grow-rooms/${id}/`),
    enabled: !!id,
  })
}

export function useCreateGrowRoom() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: Partial<GrowRoom>) => apiClient.post<GrowRoom>("/grow-rooms/", data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["grow-rooms"] }),
  })
}

export function useUpdateGrowRoom() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<GrowRoom> }) =>
      apiClient.patch<GrowRoom>(`/grow-rooms/${id}/`, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["grow-rooms"] }),
  })
}
