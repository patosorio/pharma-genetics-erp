"use client"

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { apiClient } from "@/lib/api-client"
import type { ProductionBatch } from "@/lib/types/cultivation"
import type { PaginatedResponse, ListParams } from "@/lib/types/common"

export function useProductionBatches(params: ListParams = {}) {
  return useQuery({
    queryKey: ["production-batches", params],
    queryFn: () => apiClient.get<PaginatedResponse<ProductionBatch>>("/production-batches/", params),
  })
}

export function useProductionBatch(id: number) {
  return useQuery({
    queryKey: ["production-batches", id],
    queryFn: () => apiClient.get<ProductionBatch>(`/production-batches/${id}/`),
    enabled: !!id,
  })
}

export function useCreateProductionBatch() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: Partial<ProductionBatch>) => apiClient.post<ProductionBatch>("/production-batches/", data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["production-batches"] }),
  })
}

export function useUpdateProductionBatch() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<ProductionBatch> }) =>
      apiClient.patch<ProductionBatch>(`/production-batches/${id}/`, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["production-batches"] }),
  })
}

export function useDeleteProductionBatch() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => apiClient.delete(`/production-batches/${id}/`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["production-batches"] }),
  })
}

export function useCompleteProductionBatch() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => apiClient.post(`/production-batches/${id}/complete_batch/`, {}),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["production-batches"] }),
  })
}
