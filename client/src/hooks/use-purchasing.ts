"use client"

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { apiClient } from "@/lib/api-client"
import type {
  Supplier, ExpenseCategory, ExpenseSubcategory,
  PurchaseOrder, Expense, PurchaseInvoice
} from "@/lib/types/purchasing"
import type { PaginatedResponse, ListParams } from "@/lib/types/common"

// ── Suppliers ──────────────────────────────────────────────────────────────

export function useSuppliers(params: ListParams = {}) {
  return useQuery({
    queryKey: ["suppliers", params],
    queryFn: () => apiClient.get<PaginatedResponse<Supplier>>("/suppliers/", params),
  })
}

export function useSupplier(id: number) {
  return useQuery({
    queryKey: ["suppliers", id],
    queryFn: () => apiClient.get<Supplier>(`/suppliers/${id}/`),
    enabled: !!id,
  })
}

export function useCreateSupplier() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: Partial<Supplier>) => apiClient.post<Supplier>("/suppliers/", data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["suppliers"] }),
  })
}

export function useUpdateSupplier() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<Supplier> }) =>
      apiClient.patch<Supplier>(`/suppliers/${id}/`, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["suppliers"] }),
  })
}

// ── Expense Categories ─────────────────────────────────────────────────────

export function useExpenseCategories(params: ListParams = {}) {
  return useQuery({
    queryKey: ["expense-categories", params],
    queryFn: () => apiClient.get<PaginatedResponse<ExpenseCategory>>("/expense-categories/", params),
  })
}

export function useExpenseCategory(id: number) {
  return useQuery({
    queryKey: ["expense-categories", id],
    queryFn: () => apiClient.get<ExpenseCategory>(`/expense-categories/${id}/`),
    enabled: !!id,
  })
}

export function useCreateExpenseCategory() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: Partial<ExpenseCategory>) =>
      apiClient.post<ExpenseCategory>("/expense-categories/", data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["expense-categories"] }),
  })
}

export function useUpdateExpenseCategory() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<ExpenseCategory> }) =>
      apiClient.patch<ExpenseCategory>(`/expense-categories/${id}/`, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["expense-categories"] }),
  })
}

// ── Expense Subcategories ──────────────────────────────────────────────────

export function useExpenseSubcategories(params: ListParams = {}) {
  return useQuery({
    queryKey: ["expense-subcategories", params],
    queryFn: () => apiClient.get<PaginatedResponse<ExpenseSubcategory>>("/expense-subcategories/", params),
  })
}

/** Fetch subcategories for a specific category (cascade dropdown helper). */
export function useExpenseSubcategoriesByCategory(categoryId: number | null) {
  return useQuery({
    queryKey: ["expense-subcategories", { category: categoryId }],
    queryFn: () =>
      apiClient.get<PaginatedResponse<ExpenseSubcategory>>("/expense-subcategories/", {
        category: categoryId,
        page_size: 200,
        is_active: true,
      }),
    enabled: !!categoryId,
  })
}

export function useCreateExpenseSubcategory() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: Partial<ExpenseSubcategory>) =>
      apiClient.post<ExpenseSubcategory>("/expense-subcategories/", data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["expense-subcategories"] }),
  })
}

export function useUpdateExpenseSubcategory() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<ExpenseSubcategory> }) =>
      apiClient.patch<ExpenseSubcategory>(`/expense-subcategories/${id}/`, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["expense-subcategories"] }),
  })
}

// ── Purchase Orders ────────────────────────────────────────────────────────

export function usePurchaseOrders(params: ListParams = {}) {
  return useQuery({
    queryKey: ["purchase-orders", params],
    queryFn: () => apiClient.get<PaginatedResponse<PurchaseOrder>>("/purchase-orders/", params),
  })
}

export function usePurchaseOrder(id: number) {
  return useQuery({
    queryKey: ["purchase-orders", id],
    queryFn: () => apiClient.get<PurchaseOrder>(`/purchase-orders/${id}/`),
    enabled: !!id,
  })
}

export function useCreatePurchaseOrder() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: Partial<PurchaseOrder>) =>
      apiClient.post<PurchaseOrder>("/purchase-orders/", data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["purchase-orders"] }),
  })
}

export function useUpdatePurchaseOrder() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<PurchaseOrder> }) =>
      apiClient.patch<PurchaseOrder>(`/purchase-orders/${id}/`, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["purchase-orders"] }),
  })
}

export function useSendPurchaseOrder() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => apiClient.post<PurchaseOrder>(`/purchase-orders/${id}/send/`, {}),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["purchase-orders"] }),
  })
}

export function useConfirmPurchaseOrder() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => apiClient.post<PurchaseOrder>(`/purchase-orders/${id}/confirm/`, {}),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["purchase-orders"] }),
  })
}

export function useMarkDeliveredPurchaseOrder() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: number) =>
      apiClient.post<PurchaseOrder>(`/purchase-orders/${id}/mark_delivered/`, {}),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["purchase-orders"] }),
  })
}

export function useCancelPurchaseOrder() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => apiClient.post<PurchaseOrder>(`/purchase-orders/${id}/cancel/`, {}),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["purchase-orders"] }),
  })
}

// ── Expenses (unified ledger) ──────────────────────────────────────────────

export function useExpenses(params: ListParams = {}) {
  return useQuery({
    queryKey: ["expenses", params],
    queryFn: () => apiClient.get<PaginatedResponse<Expense>>("/expenses/", params),
  })
}

export function useCreateExpense() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: Partial<Expense>) => apiClient.post<Expense>("/expenses/", data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["expenses"] }),
  })
}

export function useUpdateExpense() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<Expense> }) =>
      apiClient.patch<Expense>(`/expenses/${id}/`, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["expenses"] }),
  })
}

export function useApproveExpenseInvoice() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => apiClient.post<Expense>(`/expenses/${id}/approve/`, {}),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["expenses"] }),
  })
}

export function useRecordExpensePayment() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, amount }: { id: number; amount: string }) =>
      apiClient.post<Expense>(`/expenses/${id}/record_payment/`, { amount }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["expenses"] }),
  })
}

// ── Purchase Invoices (legacy) ─────────────────────────────────────────────

export function usePurchaseInvoices(params: ListParams = {}) {
  return useQuery({
    queryKey: ["purchase-invoices", params],
    queryFn: () => apiClient.get<PaginatedResponse<PurchaseInvoice>>("/purchase-invoices/", params),
  })
}

export function usePurchaseInvoice(id: number) {
  return useQuery({
    queryKey: ["purchase-invoices", id],
    queryFn: () => apiClient.get<PurchaseInvoice>(`/purchase-invoices/${id}/`),
    enabled: !!id,
  })
}

export function useCreatePurchaseInvoice() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: Partial<PurchaseInvoice>) =>
      apiClient.post<PurchaseInvoice>("/purchase-invoices/", data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["purchase-invoices"] }),
  })
}

export function useApprovePurchaseInvoice() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: number) =>
      apiClient.post<PurchaseInvoice>(`/purchase-invoices/${id}/approve/`, {}),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["purchase-invoices"] }),
  })
}

export function useRecordPurchaseInvoicePayment() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, amount }: { id: number; amount: string }) =>
      apiClient.post<PurchaseInvoice>(`/purchase-invoices/${id}/record_payment/`, { amount }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["purchase-invoices"] }),
  })
}
