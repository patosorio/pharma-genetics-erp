"use client"

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { apiClient } from "@/lib/api-client"
import type { Location } from "@/lib/types/core"
import type { PaginatedResponse, ListParams } from "@/lib/types/common"

export function useLocations(params: ListParams = {}) {
  return useQuery({
    queryKey: ["locations", params],
    queryFn: () => apiClient.get<PaginatedResponse<Location>>("/locations/", params),
  })
}

export function useLocation(id: number) {
  return useQuery({
    queryKey: ["locations", id],
    queryFn: () => apiClient.get<Location>(`/locations/${id}/`),
    enabled: !!id,
  })
}

export function useCreateLocation() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: Partial<Location>) => apiClient.post<Location>("/locations/", data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["locations"] }),
  })
}

export function useUpdateLocation() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<Location> }) =>
      apiClient.patch<Location>(`/locations/${id}/`, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["locations"] }),
  })
}
