"use client"

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { apiClient } from "@/lib/api-client"
import type { SalesInvoice } from "@/lib/types/sales"
import type { PaginatedResponse, ListParams } from "@/lib/types/common"

export function useInvoices(params: ListParams = {}) {
  return useQuery({
    queryKey: ["sales-invoices", params],
    queryFn: () => apiClient.get<PaginatedResponse<SalesInvoice>>("/sales-invoices/", params),
  })
}

export function useInvoice(id: number) {
  return useQuery({
    queryKey: ["sales-invoices", id],
    queryFn: () => apiClient.get<SalesInvoice>(`/sales-invoices/${id}/`),
    enabled: !!id,
  })
}

export function useCreateInvoice() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: Partial<SalesInvoice>) => apiClient.post<SalesInvoice>("/sales-invoices/", data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["sales-invoices"] }),
  })
}

export function useUpdateInvoice() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<SalesInvoice> }) =>
      apiClient.patch<SalesInvoice>(`/sales-invoices/${id}/`, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["sales-invoices"] }),
  })
}
