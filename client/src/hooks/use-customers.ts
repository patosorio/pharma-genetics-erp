"use client"

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { apiClient } from "@/lib/api-client"
import type { Customer } from "@/lib/types/sales"
import type { PaginatedResponse, ListParams } from "@/lib/types/common"

export function useCustomers(params: ListParams = {}) {
  return useQuery({
    queryKey: ["customers", params],
    queryFn: () => apiClient.get<PaginatedResponse<Customer>>("/customers/", params),
  })
}

export function useCustomer(id: number) {
  return useQuery({
    queryKey: ["customers", id],
    queryFn: () => apiClient.get<Customer>(`/customers/${id}/`),
    enabled: !!id,
  })
}

export function useCreateCustomer() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: Partial<Customer>) => apiClient.post<Customer>("/customers/", data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["customers"] }),
  })
}

export function useUpdateCustomer() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<Customer> }) =>
      apiClient.patch<Customer>(`/customers/${id}/`, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["customers"] }),
  })
}
