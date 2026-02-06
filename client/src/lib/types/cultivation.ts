export interface MotherPlant {
  id: number
  code: string
  strain: number
  strain_name: string
  location: number
  location_code: string
  status: "Active_Production" | "Recovery" | "Low_Production" | "Quarantine" | "Retired" | "Under_Treatment" | "Growing"
  status_display: string
  health_grade: "A" | "B" | "C" | "D"
  health_grade_display: string
  cultivation_date: string
  expected_ready_date: string
  actual_ready_date: string | null
  expected_retirement_date: string
  actual_retirement_date: string | null
  notes: string
  clones_per_cycle_min: number
  clones_per_cycle_max: number
  clones_per_cycle_avg: number
  total_cycles_year: number
  min_possible_clones_year: number
  max_possible_clones_year: number
  avg_clones_year: number
  last_cut_date: string | null
  total_cuttings_taken: number
  created_at: string
  updated_at: string
  created_by?: number
  updated_by?: number
}

export interface ProductionBatch {
  id: number
  batch_number: string
  mother_plant: number
  mother_plant_code: string
  location: number
  location_code: string
  cutting_date: string
  expected_rooting_date: string
  initial_clone_count: number
  status: "cutting" | "rooting" | "completed" | "failed"
  status_display: string
  total_batch_cost: string
  cost_per_clone: string
  notes: string
  rooted_clone_count: number
  survival_rate: number
  created_at: string
  updated_at: string
  created_by?: number
  updated_by?: number
}

export interface Clone {
  id: number
  code: string
  production_batch: number
  batch_number: string
  strain: number
  strain_name: string
  location: number
  location_code: string
  status: "cutting" | "rooting" | "rooted" | "reserved" | "sold" | "died"
  status_display: string
  rooting_date: string | null
  unit_cost: string
  reserved_for_order: number | null
  sold_to_order: number | null
  sold_date: string | null
  age_in_days: number
  created_at: string
  updated_at: string
  created_by?: number
  updated_by?: number
}

export interface ProductionAssumption {
  id: number
  location: number
  location_code: string
  effective_date: string
  mother_plants_count: number
  clones_per_mother_per_cycle: number
  cycle_duration_days: number
  survival_rate_pct: string
  ramp_up_months: number
  target_capacity_utilization_pct: string
  annual_cycles: number
  max_monthly_capacity: number
  version: number
  created_at: string
  updated_at: string
  created_by?: number
  updated_by?: number
}
