"use client"

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { apiClient } from "@/lib/api-client"
import type { InventoryItem, StockMovement } from "@/lib/types/inventory"
import type { PaginatedResponse, ListParams } from "@/lib/types/common"

export function useInventoryItems(params: ListParams = {}) {
  return useQuery({
    queryKey: ["inventory-items", params],
    queryFn: () => apiClient.get<PaginatedResponse<InventoryItem>>("/inventory-items/", params),
  })
}

export function useInventoryItem(id: number) {
  return useQuery({
    queryKey: ["inventory-items", id],
    queryFn: () => apiClient.get<InventoryItem>(`/inventory-items/${id}/`),
    enabled: !!id,
  })
}

export function useCreateInventoryItem() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: Partial<InventoryItem>) => apiClient.post<InventoryItem>("/inventory-items/", data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["inventory-items"] }),
  })
}

export function useUpdateInventoryItem() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<InventoryItem> }) =>
      apiClient.patch<InventoryItem>(`/inventory-items/${id}/`, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["inventory-items"] }),
  })
}

export function useStockMovements(params: ListParams = {}) {
  return useQuery({
    queryKey: ["stock-movements", params],
    queryFn: () => apiClient.get<PaginatedResponse<StockMovement>>("/stock-movements/", params),
  })
}

export function useCreateStockMovement() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: Partial<StockMovement>) => apiClient.post<StockMovement>("/stock-movements/", data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["stock-movements"] })
      queryClient.invalidateQueries({ queryKey: ["inventory-items"] })
    },
  })
}
