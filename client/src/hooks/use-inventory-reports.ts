"use client"

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { apiClient } from "@/lib/api-client"
import type {
  InventoryAlert,
  InventoryAdjustment,
  InventorySummaryByStrain,
  InventorySummaryByLocation,
  InventoryAgingReport,
} from "@/lib/types/inventory"
import type { PaginatedResponse, ListParams } from "@/lib/types/common"

// Inventory Alerts
export function useInventoryAlerts(params: ListParams = {}) {
  return useQuery({
    queryKey: ["inventory-alerts", params],
    queryFn: () => apiClient.get<PaginatedResponse<InventoryAlert>>("/inventory-alerts/", params),
  })
}

export function useLowStockAlerts() {
  return useQuery({
    queryKey: ["inventory-alerts", "low-stock"],
    queryFn: () => apiClient.get<InventoryAlert[]>("/inventory-alerts/low_stock/"),
  })
}

export function useCreateInventoryAlert() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: Partial<InventoryAlert>) => apiClient.post<InventoryAlert>("/inventory-alerts/", data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["inventory-alerts"] }),
  })
}

export function useUpdateInventoryAlert() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<InventoryAlert> }) =>
      apiClient.patch<InventoryAlert>(`/inventory-alerts/${id}/`, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["inventory-alerts"] }),
  })
}

export function useDeleteInventoryAlert() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => apiClient.delete(`/inventory-alerts/${id}/`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["inventory-alerts"] }),
  })
}

// Inventory Adjustments
export function useInventoryAdjustments(params: ListParams = {}) {
  return useQuery({
    queryKey: ["inventory-adjustments", params],
    queryFn: () => apiClient.get<PaginatedResponse<InventoryAdjustment>>("/inventory-adjustments/", params),
  })
}

export function useCreateInventoryAdjustment() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: Partial<InventoryAdjustment>) =>
      apiClient.post<InventoryAdjustment>("/inventory-adjustments/", data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["inventory-adjustments"] })
      queryClient.invalidateQueries({ queryKey: ["stock-movements"] })
    },
  })
}

// Inventory Summary Reports
export function useInventorySummaryByStrain(location_id?: number) {
  return useQuery({
    queryKey: ["inventory-summary", "by-strain", location_id],
    queryFn: () =>
      apiClient.get<InventorySummaryByStrain[]>("/inventory/summary/by_strain/", location_id ? { location_id } : {}),
  })
}

export function useInventorySummaryByLocation() {
  return useQuery({
    queryKey: ["inventory-summary", "by-location"],
    queryFn: () => apiClient.get<InventorySummaryByLocation[]>("/inventory/summary/by_location/"),
  })
}

export function useInventoryAgingReport(params: { strain_id?: number; location_id?: number } = {}) {
  return useQuery({
    queryKey: ["inventory-summary", "aging", params],
    queryFn: () => apiClient.get<InventoryAgingReport[]>("/inventory/summary/aging/", params),
  })
}

export function useInventoryValue(params: { strain_id?: number; location_id?: number } = {}) {
  return useQuery({
    queryKey: ["inventory-summary", "value", params],
    queryFn: () => apiClient.get<{ total_value: string }>("/inventory/summary/value/", params),
  })
}
