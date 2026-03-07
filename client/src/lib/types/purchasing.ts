export interface Supplier {
  id: number
  contact: number
  contact_name: string
  contact_email: string | null
  contact_phone: string | null
  supplier_code: string
  payment_terms_days: number
  created_at: string
  updated_at: string
}

export type ExpenseType = "opex" | "capex" | "cogs"

export interface ExpenseSubcategory {
  id: number
  category: number
  category_name: string
  name: string
  expense_type: ExpenseType
  expense_type_display: string
  is_active: boolean
}

export interface ExpenseCategory {
  id: number
  name: string
  code: string
  category_type: ExpenseType
  category_type_display: string
  description: string | null
  is_active: boolean
  subcategories?: ExpenseSubcategory[]
}

export interface PurchaseOrderItem {
  id: number
  purchase_order: number
  expense_category: number
  expense_category_name: string
  description: string
  quantity: string
  unit_price: string
  line_total: string
}

export interface PurchaseOrder {
  id: number
  po_number: string
  supplier: number
  supplier_name: string
  location: number
  location_code: string
  order_date: string
  expected_delivery_date: string | null
  status: "draft" | "sent" | "confirmed" | "delivered" | "cancelled"
  status_display: string
  tax_type: number | null
  tax_type_name: string | null
  base_amount: string
  tax_amount: string
  total_amount: string
  currency: number
  currency_code: string
  notes: string | null
  items?: PurchaseOrderItem[]
  created_at: string
  updated_at: string
}

export type ExpenseDocumentType = "expense" | "invoice"
export type ExpenseStatus = "pending" | "approved" | "paid" | "partially_paid" | "overdue" | "cancelled"

export interface Expense {
  id: number
  expense_number: string
  document_type: ExpenseDocumentType
  document_type_display: string

  // Categorisation
  category: number
  category_name: string
  category_type: ExpenseType
  subcategory: number | null
  subcategory_name: string | null
  subcategory_expense_type: ExpenseType | null

  // Core fields
  supplier: number | null
  supplier_name: string | null
  location: number
  location_name: string
  location_code: string
  expense_date: string
  amount: string
  currency: number
  currency_code: string
  currency_symbol: string
  description: string
  purchase_order: number | null
  purchase_order_number: string | null

  // Invoice-specific
  invoice_reference: string
  due_date: string | null
  tax_type: number | null
  tax_type_name: string | null
  vat_amount: string
  retention_amount: string
  total_amount: string
  paid_amount: string
  balance_due: string
  status: ExpenseStatus | ""
  status_display: string | null
  payment_date: string | null

  created_at: string
  updated_at: string
}

export interface PurchaseInvoice {
  id: number
  invoice_number: string
  supplier: number
  supplier_name: string
  purchase_order: number | null
  purchase_order_number: string | null
  invoice_date: string
  due_date: string
  tax_type: number | null
  tax_type_name: string | null
  base_amount: string
  tax_amount: string
  total_amount: string
  paid_amount: string
  balance_due: string
  currency: number
  currency_code: string
  status: "pending" | "approved" | "paid" | "partially_paid" | "overdue" | "cancelled"
  status_display: string
  notes: string | null
  created_at: string
  updated_at: string
}
