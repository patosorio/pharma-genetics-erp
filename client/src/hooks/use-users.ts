"use client"

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { apiClient } from "@/lib/api-client"
import type { User } from "@/lib/types/core"
import type { PaginatedResponse, ListParams } from "@/lib/types/common"

export function useUsers(params: ListParams = {}) {
  return useQuery({
    queryKey: ["users", params],
    queryFn: () => apiClient.get<PaginatedResponse<User>>("/users/", params),
  })
}

export function useUser(id: number) {
  return useQuery({
    queryKey: ["users", id],
    queryFn: () => apiClient.get<User>(`/users/${id}/`),
    enabled: !!id,
  })
}

export function useCreateUser() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: Partial<User>) => apiClient.post<User>("/users/", data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["users"] }),
  })
}

export function useUpdateUser() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<User> }) => apiClient.patch<User>(`/users/${id}/`, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["users"] }),
  })
}
