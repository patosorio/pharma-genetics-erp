"use client"

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { apiClient } from "@/lib/api-client"
import type { Harvest } from "@/lib/types/cultivation"
import type { PaginatedResponse, ListParams } from "@/lib/types/common"

export function useHarvests(params: ListParams = {}) {
  return useQuery({
    queryKey: ["harvests", params],
    queryFn: () => apiClient.get<PaginatedResponse<Harvest>>("/harvests/", params),
  })
}

export function useHarvest(id: number) {
  return useQuery({
    queryKey: ["harvests", id],
    queryFn: () => apiClient.get<Harvest>(`/harvests/${id}/`),
    enabled: !!id,
  })
}

export function useCreateHarvest() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: Partial<Harvest>) => apiClient.post<Harvest>("/harvests/", data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["harvests"] }),
  })
}

export function useUpdateHarvest() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<Harvest> }) =>
      apiClient.patch<Harvest>(`/harvests/${id}/`, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["harvests"] }),
  })
}
