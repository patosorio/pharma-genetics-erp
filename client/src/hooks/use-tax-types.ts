"use client"

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { apiClient } from "@/lib/api-client"
import type { TaxType } from "@/lib/types/core"
import type { PaginatedResponse, ListParams } from "@/lib/types/common"

export function useTaxTypes(params: ListParams = {}) {
  return useQuery({
    queryKey: ["tax-types", params],
    queryFn: () => apiClient.get<PaginatedResponse<TaxType>>("/tax-types/", params),
  })
}

export function useCreateTaxType() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: Partial<TaxType>) => apiClient.post<TaxType>("/tax-types/", data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["tax-types"] }),
  })
}

export function useUpdateTaxType() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<TaxType> }) =>
      apiClient.patch<TaxType>(`/tax-types/${id}/`, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["tax-types"] }),
  })
}
