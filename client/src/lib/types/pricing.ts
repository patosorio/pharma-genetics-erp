export interface CostAllocationRule {
  id: number
  location: number
  location_code: string
  effective_date: string
  end_date: string | null
  monthly_capacity_clones: number
  mother_plant_lifecycle_days: number
  expected_clones_per_mother_lifecycle: number
  direct_labor_departments: number[]
  overhead_labor_departments: number[]
  cogs_expense_categories: number[]
  variable_expense_categories: number[]
  fixed_expense_categories: number[]
  notes: string | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface PricingTier {
  id: number
  tier_name: "retail" | "wholesale" | "bulk"
  tier_name_display: string
  min_quantity: number
  max_quantity: number | null
  price_per_clone: string
  effective_date: string
  end_date: string | null
  annual_price_increase_pct: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface CostSnapshot {
  id: number
  location: number
  location_code: string
  snapshot_date: string
  period_start: string
  period_end: string
  total_clones_produced: number
  capacity_utilization_pct: string
  total_cogs_expenses: string
  total_variable_opex: string
  total_fixed_opex: string
  total_direct_labor: string
  total_overhead_labor: string
  cogs_per_clone: string
  direct_labor_per_clone: string
  variable_base_per_clone: string
  overhead_per_clone: string
  total_cost_per_clone: string
  notes: string | null
  created_at: string
  updated_at: string
}

export interface MarginAnalysis {
  price: string
  cost_per_clone: string
  gross_margin: string
  gross_margin_pct: string
  contribution_margin: string
}

export interface TierMargin {
  tier_name: string
  price_per_clone: string
  cost_per_clone: string
  gross_margin: string
  gross_margin_pct: string
}
