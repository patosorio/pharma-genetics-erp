"use client"

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { apiClient } from "@/lib/api-client"
import type { CompanySettings } from "@/lib/types/core"

export function useCompanySettings() {
  return useQuery({
    queryKey: ["company-settings"],
    queryFn: () => apiClient.get<CompanySettings>("/company-settings/1/"),
  })
}

export function useUpdateCompanySettings() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: Partial<CompanySettings>) => apiClient.patch<CompanySettings>("/company-settings/1/", data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["company-settings"] }),
  })
}
