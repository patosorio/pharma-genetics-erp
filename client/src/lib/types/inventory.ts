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
  id: string
  item: string
  item_name: string
  movement_type: "in" | "out" | "adjustment" | "transfer"
  movement_type_display: string
  quantity: number
  from_location: string | null
  from_location_name: string | null
  to_location: string | null
  to_location_name: string | null
  reference: string | null
  notes: string | null
  created_by: string
  created_by_name: string
  created_at: string
}
