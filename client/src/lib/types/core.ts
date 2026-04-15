export interface User {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  full_name: string
  role: "admin" | "cultivation_manager" | "sales_rep" | "accountant" | "viewer"
  location: number | null
  location_name: string | null
  firebase_uid: string | null
  is_active: boolean
  date_joined: string
  last_login: string | null
  created_at: string
  updated_at: string
}

export interface Location {
  id: number
  name: string
  code: string
  address: string
  is_active: boolean
  created_at: string
  updated_at: string
  created_by: number | null
  updated_by: number | null
}

export interface Contact {
  id: number
  contact_type: "customer" | "supplier" | "vendor" | "other"
  contact_type_display: string
  name: string
  email: string | null
  phone: string | null
  address: string | null
  tax_id: string | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Currency {
  id: number
  code: string
  name: string
  symbol: string
  is_default: boolean
}

export interface TaxType {
  id: number
  name: string
  rate: string
  is_active: boolean
}

export interface CompanySettings {
  id: number
  company_name: string
  tax_id: string | null
  default_currency: number
  default_currency_code: string
  fiscal_year_start_month: number
  break_even_price: string
}
