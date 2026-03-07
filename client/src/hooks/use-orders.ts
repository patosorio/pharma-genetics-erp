"use client"

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { apiClient } from "@/lib/api-client"
import type { Order } from "@/lib/types/sales"
import type { PaginatedResponse, ListParams } from "@/lib/types/common"

export function useOrders(params: ListParams = {}) {
  return useQuery({
    queryKey: ["orders", params],
    queryFn: () => apiClient.get<PaginatedResponse<Order>>("/orders/", params),
  })
}

export function useOrder(id: number) {
  return useQuery({
    queryKey: ["orders", id],
    queryFn: () => apiClient.get<Order>(`/orders/${id}/`),
    enabled: !!id,
  })
}

export function useCreateOrder() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: Partial<Order>) => apiClient.post<Order>("/orders/", data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["orders"] }),
  })
}

export function useUpdateOrder() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<Order> }) =>
      apiClient.patch<Order>(`/orders/${id}/`, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["orders"] }),
  })
}

export function useConfirmOrder() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => apiClient.post<Order>(`/orders/${id}/confirm/`, {}),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["orders"] }),
  })
}

export function useMarkOrderInProduction() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => apiClient.post<Order>(`/orders/${id}/mark_in_production/`, {}),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["orders"] }),
  })
}

export function useMarkOrderReady() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => apiClient.post<Order>(`/orders/${id}/mark_ready/`, {}),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["orders"] }),
  })
}

export function useCancelOrder() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => apiClient.post<Order>(`/orders/${id}/cancel/`, {}),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["orders"] }),
  })
}
