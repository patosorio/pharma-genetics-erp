"use client"

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { apiClient } from "@/lib/api-client"
import type { DeliveryNote } from "@/lib/types/sales"
import type { PaginatedResponse, ListParams } from "@/lib/types/common"

export function useDeliveryNotes(params: ListParams = {}) {
  return useQuery({
    queryKey: ["delivery-notes", params],
    queryFn: () => apiClient.get<PaginatedResponse<DeliveryNote>>("/delivery-notes/", params),
  })
}

export function useDeliveryNote(id: number) {
  return useQuery({
    queryKey: ["delivery-notes", id],
    queryFn: () => apiClient.get<DeliveryNote>(`/delivery-notes/${id}/`),
    enabled: !!id,
  })
}

export function useCreateDeliveryNote() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: Partial<DeliveryNote>) => apiClient.post<DeliveryNote>("/delivery-notes/", data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["delivery-notes"] }),
  })
}

export function useUpdateDeliveryNote() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<DeliveryNote> }) =>
      apiClient.patch<DeliveryNote>(`/delivery-notes/${id}/`, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["delivery-notes"] }),
  })
}

export function useMarkDeliveryNoteInTransit() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => apiClient.post<DeliveryNote>(`/delivery-notes/${id}/mark_in_transit/`, {}),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["delivery-notes"] }),
  })
}

export function useMarkDeliveryNoteDelivered() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => apiClient.post<DeliveryNote>(`/delivery-notes/${id}/mark_delivered/`, {}),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["delivery-notes"] })
      queryClient.invalidateQueries({ queryKey: ["orders"] })
    },
  })
}
