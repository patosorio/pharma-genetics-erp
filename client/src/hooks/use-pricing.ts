"use client"

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { apiClient } from "@/lib/api-client"
import type { CostAllocationRule, PricingTier, CostSnapshot, MarginAnalysis, TierMargin } from "@/lib/types/pricing"
import type { PaginatedResponse, ListParams } from "@/lib/types/common"

// Cost Allocation Rules
export function useCostAllocationRules(params: ListParams = {}) {
  return useQuery({
    queryKey: ["cost-allocation-rules", params],
    queryFn: () => apiClient.get<PaginatedResponse<CostAllocationRule>>("/cost-allocation-rules/", params),
  })
}

export function useCreateCostAllocationRule() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: Partial<CostAllocationRule>) =>
      apiClient.post<CostAllocationRule>("/cost-allocation-rules/", data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["cost-allocation-rules"] }),
  })
}

export function useUpdateCostAllocationRule() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<CostAllocationRule> }) =>
      apiClient.patch<CostAllocationRule>(`/cost-allocation-rules/${id}/`, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["cost-allocation-rules"] }),
  })
}

// Pricing Tiers
export function usePricingTiers(params: ListParams = {}) {
  return useQuery({
    queryKey: ["pricing-tiers", params],
    queryFn: () => apiClient.get<PaginatedResponse<PricingTier>>("/pricing-tiers/", params),
  })
}

export function usePricingTierForQuantity(quantity: number) {
  return useQuery({
    queryKey: ["pricing-tiers", "for-quantity", quantity],
    queryFn: () => apiClient.get<PricingTier>("/pricing-tiers/for_quantity/", { quantity }),
    enabled: quantity > 0,
  })
}

export function useCreatePricingTier() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: Partial<PricingTier>) => apiClient.post<PricingTier>("/pricing-tiers/", data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["pricing-tiers"] }),
  })
}

export function useUpdatePricingTier() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<PricingTier> }) =>
      apiClient.patch<PricingTier>(`/pricing-tiers/${id}/`, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["pricing-tiers"] }),
  })
}

// Cost Snapshots
export function useCostSnapshots(params: ListParams = {}) {
  return useQuery({
    queryKey: ["cost-snapshots", params],
    queryFn: () => apiClient.get<PaginatedResponse<CostSnapshot>>("/cost-snapshots/", params),
  })
}

export function useCalculateCostSnapshot() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: { location_id: number; period_start: string; period_end: string }) =>
      apiClient.post<CostSnapshot>("/cost-snapshots/calculate/", data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["cost-snapshots"] }),
  })
}

export function useMarginAnalysis(params: {
  location_id: number
  period_start: string
  period_end: string
  price: string
}) {
  return useQuery({
    queryKey: ["margin-analysis", params],
    queryFn: () => apiClient.get<MarginAnalysis>("/cost-snapshots/margin_analysis/", params),
    enabled: !!(params.location_id && params.period_start && params.period_end && params.price),
  })
}

export function useTierMargins(params: { location_id: number; period_start: string; period_end: string }) {
  return useQuery({
    queryKey: ["tier-margins", params],
    queryFn: () => apiClient.get<TierMargin[]>("/cost-snapshots/tier_margins/", params),
    enabled: !!(params.location_id && params.period_start && params.period_end),
  })
}
