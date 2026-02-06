export interface Customer {
  id: number
  contact: number
  contact_name: string
  customer_code: string
  credit_limit: string | null
  payment_terms_days: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Order {
  id: number
  order_number: string
  customer: number
  customer_name: string
  order_date: string
  delivery_date: string | null
  status: "draft" | "pending" | "confirmed" | "shipped" | "delivered" | "cancelled"
  status_display: string
  subtotal: string
  tax_amount: string
  total_amount: string
  notes: string | null
  created_at: string
  updated_at: string
}

export interface OrderItem {
  id: number
  order: number
  item: number
  item_name: string
  quantity: string
  unit_price: string
  discount: string
  tax_rate: string
  total: string
}

export interface Invoice {
  id: number
  invoice_number: string
  order: number | null
  order_number: string | null
  customer: number
  customer_name: string
  invoice_date: string
  due_date: string
  status: "draft" | "sent" | "paid" | "overdue" | "cancelled"
  status_display: string
  subtotal: string
  tax_amount: string
  total_amount: string
  paid_amount: string
  balance_due: string
  notes: string | null
  created_at: string
  updated_at: string
}
