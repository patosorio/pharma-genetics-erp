"use client"

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { apiClient } from "@/lib/api-client"
import type { MotherPlant, Clone, ProductionAssumption } from "@/lib/types/cultivation"
import type { PaginatedResponse, ListParams } from "@/lib/types/common"

// ============ MOTHER PLANTS ============
export function useMotherPlants(params: ListParams = {}) {
  return useQuery({
    queryKey: ["mother-plants", params],
    queryFn: () => apiClient.get<PaginatedResponse<MotherPlant>>("/mother-plants/", params),
  })
}

export function useMotherPlant(id: number) {
  return useQuery({
    queryKey: ["mother-plants", id],
    queryFn: () => apiClient.get<MotherPlant>(`/mother-plants/${id}/`),
    enabled: !!id,
  })
}

export function useCreateMotherPlant() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: Partial<MotherPlant>) => apiClient.post<MotherPlant>("/mother-plants/", data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["mother-plants"] }),
  })
}

export function useUpdateMotherPlant() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<MotherPlant> }) =>
      apiClient.patch<MotherPlant>(`/mother-plants/${id}/`, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["mother-plants"] }),
  })
}

export function useDeleteMotherPlant() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => apiClient.delete(`/mother-plants/${id}/`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["mother-plants"] }),
  })
}

export function useBatchUpdateMotherPlantStatus() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ ids, status }: { ids: number[]; status: string }) =>
      apiClient.post("/mother-plants/batch_update_status/", { ids, status }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["mother-plants"] }),
  })
}

// ============ CLONES ============
export function useClones(params: ListParams = {}) {
  return useQuery({
    queryKey: ["clones", params],
    queryFn: () => apiClient.get<PaginatedResponse<Clone>>("/clones/", params),
  })
}

export function useClone(id: number) {
  return useQuery({
    queryKey: ["clones", id],
    queryFn: () => apiClient.get<Clone>(`/clones/${id}/`),
    enabled: !!id,
  })
}

export function useAvailableClones(params: ListParams = {}) {
  return useQuery({
    queryKey: ["clones", "available", params],
    queryFn: () => apiClient.get<PaginatedResponse<Clone>>("/clones/available/", params),
  })
}

export function useCreateClone() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: Partial<Clone>) => apiClient.post<Clone>("/clones/", data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["clones"] }),
  })
}

export function useUpdateClone() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<Clone> }) =>
      apiClient.patch<Clone>(`/clones/${id}/`, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["clones"] }),
  })
}

export function useDeleteClone() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => apiClient.delete(`/clones/${id}/`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["clones"] }),
  })
}

// ============ PRODUCTION ASSUMPTIONS ============
export function useProductionAssumptions(params: ListParams = {}) {
  return useQuery({
    queryKey: ["production-assumptions", params],
    queryFn: () => apiClient.get<PaginatedResponse<ProductionAssumption>>("/production-assumptions/", params),
  })
}

export function useProductionAssumption(id: number) {
  return useQuery({
    queryKey: ["production-assumptions", id],
    queryFn: () => apiClient.get<ProductionAssumption>(`/production-assumptions/${id}/`),
    enabled: !!id,
  })
}

export function useCreateProductionAssumption() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: Partial<ProductionAssumption>) =>
      apiClient.post<ProductionAssumption>("/production-assumptions/", data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["production-assumptions"] }),
  })
}

export function useUpdateProductionAssumption() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<ProductionAssumption> }) =>
      apiClient.patch<ProductionAssumption>(`/production-assumptions/${id}/`, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["production-assumptions"] }),
  })
}

export function useDeleteProductionAssumption() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => apiClient.delete(`/production-assumptions/${id}/`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["production-assumptions"] }),
  })
}

