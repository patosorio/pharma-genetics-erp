"use client"

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { apiClient } from "@/lib/api-client"
import type { TaxReport, TaxJournalEntry } from "@/lib/types/taxes"
import type { PaginatedResponse, ListParams } from "@/lib/types/common"

// Tax Reports
export function useTaxReports(params: ListParams = {}) {
  return useQuery({
    queryKey: ["tax-reports", params],
    queryFn: () => apiClient.get<PaginatedResponse<TaxReport>>("/tax-reports/", params),
  })
}

export function useTaxReport(id: number) {
  return useQuery({
    queryKey: ["tax-reports", id],
    queryFn: () => apiClient.get<TaxReport>(`/tax-reports/${id}/`),
    enabled: !!id,
  })
}

export function useCreateTaxReport() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: Partial<TaxReport>) => apiClient.post<TaxReport>("/tax-reports/", data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["tax-reports"] }),
  })
}

export function useUpdateTaxReport() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<TaxReport> }) =>
      apiClient.patch<TaxReport>(`/tax-reports/${id}/`, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["tax-reports"] }),
  })
}

export function useCalculateTaxTotals() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => apiClient.post<TaxReport>(`/tax-reports/${id}/calculate_totals/`, {}),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["tax-reports"] }),
  })
}

export function useGenerateTaxEntries() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => apiClient.post<TaxReport>(`/tax-reports/${id}/generate_entries/`, {}),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: ["tax-reports"] })
      queryClient.invalidateQueries({ queryKey: ["tax-journal-entries"] })
      queryClient.invalidateQueries({ queryKey: ["tax-reports", id] })
    },
  })
}

// Tax Journal Entries
export function useTaxJournalEntries(params: ListParams = {}) {
  return useQuery({
    queryKey: ["tax-journal-entries", params],
    queryFn: () => apiClient.get<PaginatedResponse<TaxJournalEntry>>("/tax-journal-entries/", params),
  })
}

export function useCreateTaxJournalEntry() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: Partial<TaxJournalEntry>) => apiClient.post<TaxJournalEntry>("/tax-journal-entries/", data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["tax-journal-entries"] }),
  })
}
