export interface Customer {
  id: number
  contact: number
  contact_name: string
  customer_code: string
  tier: "retail" | "wholesale" | "bulk"
  credit_limit: string | null
  payment_terms_days: number
  created_at: string
  updated_at: string
}

export interface PriceList {
  id: number
  strain: number
  strain_name: string
  tier: "retail" | "wholesale" | "bulk"
  price_per_clone: string
  currency: number
  currency_code: string
  min_quantity: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface OrderLine {
  id: number
  order: number
  strain: number
  strain_name: string
  quantity: number
  unit_price: string
  line_total: string
}

export interface Order {
  id: number
  order_number: string
  customer: number
  customer_name: string
  location: number
  location_code: string
  order_date: string
  expected_delivery_date: string | null
  status: "draft" | "confirmed" | "in_production" | "ready" | "partially_delivered" | "delivered" | "cancelled"
  status_display: string
  total_amount: string
  notes: string | null
  order_lines?: OrderLine[]
  created_at: string
  updated_at: string
}

export interface DeliveryNoteLine {
  id: number
  delivery_note: number
  order_line: number
  quantity_delivered: number
  notes: string | null
}

export interface DeliveryNote {
  id: number
  delivery_note_number: string
  order: number
  order_number: string
  delivery_date: string
  delivered_by: string | null
  received_by: string | null
  delivery_location: number
  delivery_location_code: string
  status: "draft" | "in_transit" | "delivered"
  status_display: string
  notes: string | null
  delivery_lines?: DeliveryNoteLine[]
  created_at: string
  updated_at: string
}

export interface SalesInvoice {
  id: number
  invoice_number: string
  order: number | null
  order_number: string | null
  delivery_note: number | null
  invoice_date: string
  due_date: string
  tax_type: number | null
  tax_type_name: string | null
  base_amount: string
  tax_amount: string
  total_amount: string
  paid_amount: string
  balance_due: string
  status: "draft" | "sent" | "paid" | "overdue" | "cancelled"
  status_display: string
  notes: string | null
  created_at: string
  updated_at: string
}

export interface Payment {
  id: number
  payment_number: string
  invoice: number
  invoice_number: string
  payment_date: string
  amount: string
  payment_method: "cash" | "bank_transfer" | "cheque" | "credit_card" | "other"
  payment_method_display: string
  reference_number: string | null
  notes: string | null
  created_at: string
  updated_at: string
}

// Legacy alias kept for backwards compatibility with existing pages
export type Invoice = SalesInvoice
