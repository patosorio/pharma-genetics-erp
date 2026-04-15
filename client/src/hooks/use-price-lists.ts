"use client"

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { apiClient } from "@/lib/api-client"
import type { PriceList } from "@/lib/types/sales"
import type { PaginatedResponse, ListParams } from "@/lib/types/common"

export function usePriceLists(params: ListParams = {}) {
  return useQuery({
    queryKey: ["price-lists", params],
    queryFn: () => apiClient.get<PaginatedResponse<PriceList>>("/price-lists/", params),
  })
}

export function useCreatePriceList() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: Partial<PriceList>) => apiClient.post<PriceList>("/price-lists/", data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["price-lists"] }),
  })
}

export function useUpdatePriceList() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<PriceList> }) =>
      apiClient.patch<PriceList>(`/price-lists/${id}/`, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["price-lists"] }),
  })
}

export function useDeletePriceList() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => apiClient.delete(`/price-lists/${id}/`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["price-lists"] }),
  })
}
