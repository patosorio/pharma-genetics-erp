"use client"

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { apiClient } from "@/lib/api-client"
import type { Department, Employee, PayrollPeriod, Payroll } from "@/lib/types/hr"
import type { PaginatedResponse, ListParams } from "@/lib/types/common"

// Departments
export function useDepartments(params: ListParams = {}) {
  return useQuery({
    queryKey: ["departments", params],
    queryFn: () => apiClient.get<PaginatedResponse<Department>>("/departments/", params),
  })
}

export function useCreateDepartment() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: Partial<Department>) => apiClient.post<Department>("/departments/", data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["departments"] }),
  })
}

export function useUpdateDepartment() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<Department> }) =>
      apiClient.patch<Department>(`/departments/${id}/`, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["departments"] }),
  })
}

// Employees
export function useEmployees(params: ListParams = {}) {
  return useQuery({
    queryKey: ["employees", params],
    queryFn: () => apiClient.get<PaginatedResponse<Employee>>("/employees/", params),
  })
}

export function useEmployee(id: number) {
  return useQuery({
    queryKey: ["employees", id],
    queryFn: () => apiClient.get<Employee>(`/employees/${id}/`),
    enabled: !!id,
  })
}

export function useCreateEmployee() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: Partial<Employee>) => apiClient.post<Employee>("/employees/", data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["employees"] }),
  })
}

export function useUpdateEmployee() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<Employee> }) =>
      apiClient.patch<Employee>(`/employees/${id}/`, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["employees"] }),
  })
}

// Payroll Periods
export function usePayrollPeriods(params: ListParams = {}) {
  return useQuery({
    queryKey: ["payroll-periods", params],
    queryFn: () => apiClient.get<PaginatedResponse<PayrollPeriod>>("/payroll-periods/", params),
  })
}

export function useCreatePayrollPeriod() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: Partial<PayrollPeriod>) => apiClient.post<PayrollPeriod>("/payroll-periods/", data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["payroll-periods"] }),
  })
}

export function useClosePeriod() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => apiClient.post<PayrollPeriod>(`/payroll-periods/${id}/close_period/`, {}),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["payroll-periods"] }),
  })
}

// Payrolls
export function usePayrolls(params: ListParams = {}) {
  return useQuery({
    queryKey: ["payrolls", params],
    queryFn: () => apiClient.get<PaginatedResponse<Payroll>>("/payrolls/", params),
  })
}

export function useCreatePayroll() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: Partial<Payroll>) => apiClient.post<Payroll>("/payrolls/", data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["payrolls"] }),
  })
}

export function useUpdatePayroll() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<Payroll> }) =>
      apiClient.patch<Payroll>(`/payrolls/${id}/`, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["payrolls"] }),
  })
}

export function useMarkPayrollPaid() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, payment_date }: { id: number; payment_date?: string }) =>
      apiClient.post<Payroll>(`/payrolls/${id}/mark_paid/`, { payment_date }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["payrolls"] }),
  })
}
