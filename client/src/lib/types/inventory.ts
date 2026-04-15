export interface InventoryItem {
  id: string
  name: string
  sku: string
  strain: string | null
  strain_name: string | null
  category: "clones" | "mother_plants" | "supplies" | "packaging" | "other"
  category_display: string
  location: string
  location_name: string
  quantity: number
  unit: "units" | "pcs"
  unit_cost: string | null
  reorder_point: number | null
  batch?: string | null
  batch_number?: string | null
  clone_status?: "available" | "reserved" | "sold"
  clone_status_display?: string
  notes: string | null
  created_at: string
  updated_at: string
}

export interface StockMovement {
  id: number
  clone: number
  clone_code: string
  movement_type: "sale" | "transfer" | "adjustment" | "batch_complete" | "reservation" | "reservation_release"
  movement_type_display: string
  from_location: number | null
  from_location_code: string | null
  to_location: number | null
  to_location_code: string | null
  movement_date: string
  reference_type: string | null
  reference_id: number | null
  notes: string | null
  performed_by: number | null
  performed_by_name: string | null
  created_at: string
}

export interface InventoryAlert {
  id: number
  strain: number
  strain_name: string
  location: number
  location_code: string
  reorder_point: number
  alert_email: string | null
  is_active: boolean
  current_stock: number
  is_low_stock: boolean
  stock_deficit: number
  created_at: string
  updated_at: string
}

export interface InventoryAdjustment {
  id: number
  clone: number
  clone_code: string
  adjustment_date: string
  reason: string
  notes: string
  approved_by: number | null
  approved_by_name: string | null
  photo_url: string | null
  created_at: string
  updated_at: string
}

export interface InventorySummaryByStrain {
  strain_id: number
  strain_name: string
  total_clones: number
  rooted_clones: number
  reserved_clones: number
  available_clones: number
}

export interface InventorySummaryByLocation {
  location_id: number
  location_code: string
  total_clones: number
  rooted_clones: number
  reserved_clones: number
  available_clones: number
}

export interface InventoryAgingReport {
  clone_id: number
  clone_code: string
  strain_name: string
  location_code: string
  status: string
  age_in_days: number
  unit_cost: string
}
