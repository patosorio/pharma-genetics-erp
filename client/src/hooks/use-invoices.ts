"use client"

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { apiClient } from "@/lib/api-client"
import type { Invoice } from "@/lib/types/sales"
import type { PaginatedResponse, ListParams } from "@/lib/types/common"

export function useInvoices(params: ListParams = {}) {
  return useQuery({
    queryKey: ["invoices", params],
    queryFn: () => apiClient.get<PaginatedResponse<Invoice>>("/invoices/", params),
  })
}

export function useInvoice(id: number) {
  return useQuery({
    queryKey: ["invoices", id],
    queryFn: () => apiClient.get<Invoice>(`/invoices/${id}/`),
    enabled: !!id,
  })
}

export function useCreateInvoice() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: Partial<Invoice>) => apiClient.post<Invoice>("/invoices/", data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["invoices"] }),
  })
}

export function useUpdateInvoice() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<Invoice> }) =>
      apiClient.patch<Invoice>(`/invoices/${id}/`, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["invoices"] }),
  })
}
