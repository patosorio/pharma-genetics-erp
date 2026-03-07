"use client"

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { apiClient } from "@/lib/api-client"
import type { Payment } from "@/lib/types/sales"
import type { PaginatedResponse, ListParams } from "@/lib/types/common"

export function usePayments(params: ListParams = {}) {
  return useQuery({
    queryKey: ["payments", params],
    queryFn: () => apiClient.get<PaginatedResponse<Payment>>("/payments/", params),
  })
}

export function useRecordSalesInvoicePayment() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({
      invoiceId,
      data,
    }: {
      invoiceId: number
      data: {
        amount: string
        payment_method: string
        payment_date: string
        reference_number?: string
        notes?: string
      }
    }) => apiClient.post<Payment>(`/sales-invoices/${invoiceId}/record_payment/`, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["sales-invoices"] })
      queryClient.invalidateQueries({ queryKey: ["payments"] })
    },
  })
}

export function useMarkSalesInvoiceSent() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => apiClient.post(`/sales-invoices/${id}/mark_sent/`, {}),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["sales-invoices"] }),
  })
}
