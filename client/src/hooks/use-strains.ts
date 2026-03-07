"use client"

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { apiClient } from "@/lib/api-client"
import type { Strain, StrainCategory } from "@/lib/types/genetics"
import type { PaginatedResponse, ListParams } from "@/lib/types/common"

export function useStrains(params: ListParams = {}) {
  return useQuery({
    queryKey: ["strains", params],
    queryFn: () => apiClient.get<PaginatedResponse<Strain>>("/strains/", params),
  })
}

export function useStrain(id: number) {
  return useQuery({
    queryKey: ["strains", id],
    queryFn: () => apiClient.get<Strain>(`/strains/${id}/`),
    enabled: !!id,
  })
}

export function useCreateStrain() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: Partial<Strain>) => apiClient.post<Strain>("/strains/", data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["strains"] }),
  })
}

export function useUpdateStrain() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<Strain> }) =>
      apiClient.patch<Strain>(`/strains/${id}/`, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["strains"] }),
  })
}

export function useStrainCategories(params: ListParams = {}) {
  return useQuery({
    queryKey: ["strain-categories", params],
    queryFn: () => apiClient.get<PaginatedResponse<StrainCategory>>("/strain-categories/", params),
  })
}

export function useCreateStrainCategory() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: Partial<StrainCategory>) => apiClient.post<StrainCategory>("/strain-categories/", data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["strain-categories"] }),
  })
}
