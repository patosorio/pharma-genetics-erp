"use client"

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { apiClient } from "@/lib/api-client"
import type { Contact } from "@/lib/types/core"
import type { PaginatedResponse, ListParams } from "@/lib/types/common"

export function useContacts(params: ListParams = {}) {
  return useQuery({
    queryKey: ["contacts", params],
    queryFn: () => apiClient.get<PaginatedResponse<Contact>>("/contacts/", params),
  })
}

export function useContact(id: number) {
  return useQuery({
    queryKey: ["contacts", id],
    queryFn: () => apiClient.get<Contact>(`/contacts/${id}/`),
    enabled: !!id,
  })
}

export function useCreateContact() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: Partial<Contact>) => apiClient.post<Contact>("/contacts/", data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["contacts"] }),
  })
}

export function useUpdateContact() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<Contact> }) =>
      apiClient.patch<Contact>(`/contacts/${id}/`, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["contacts"] }),
  })
}
