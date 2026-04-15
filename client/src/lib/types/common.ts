export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export interface ListParams {
  page?: number
  page_size?: number
  search?: string
  ordering?: string
  [key: string]: any
}

export interface APIError {
  detail?: string
  [field: string]: string | string[] | undefined
}

export type UserRole = "admin" | "cultivation_manager" | "sales_rep" | "accountant" | "viewer"
export type ContactType = "customer" | "supplier" | "vendor" | "other"
export type TerpeneProfile = "aromatic" | "citrus" | "earthy" | "floral" | "herbal" | "pine"
export type BatchStatus = "planned" | "germination" | "vegetative" | "flowering" | "harvested" | "cured" | "archived"
export type OrderStatus = "draft" | "confirmed" | "in_production" | "ready" | "partially_delivered" | "delivered" | "cancelled"
export type InvoiceStatus = "draft" | "sent" | "paid" | "overdue" | "cancelled"
export type PaymentStatus = "pending" | "completed" | "failed" | "refunded"
export type DeliveryNoteStatus = "draft" | "in_transit" | "delivered"
export type PurchaseOrderStatus = "draft" | "sent" | "confirmed" | "delivered" | "cancelled"
export type PurchaseInvoiceStatus = "pending" | "approved" | "paid" | "overdue" | "cancelled"
export type TaxReportStatus = "draft" | "finalized" | "filed" | "paid"
