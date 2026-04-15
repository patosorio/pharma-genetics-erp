"use client"

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { apiClient } from "@/lib/api-client"
import type { Currency } from "@/lib/types/core"
import type { PaginatedResponse, ListParams } from "@/lib/types/common"

export function useCurrencies(params: ListParams = {}) {
  return useQuery({
    queryKey: ["currencies", params],
    queryFn: () => apiClient.get<PaginatedResponse<Currency>>("/currencies/", params),
  })
}

export function useCreateCurrency() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: Partial<Currency>) => apiClient.post<Currency>("/currencies/", data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["currencies"] }),
  })
}

export function useUpdateCurrency() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<Currency> }) =>
      apiClient.patch<Currency>(`/currencies/${id}/`, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["currencies"] }),
  })
}
