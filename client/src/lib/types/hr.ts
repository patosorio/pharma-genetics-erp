export interface Department {
  id: number
  name: string
  code: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Employee {
  id: number
  employee_code: string
  user: number | null
  first_name: string
  last_name: string
  full_name: string
  email: string | null
  phone: string | null
  department: number
  department_name: string
  location: number
  location_code: string
  hire_date: string
  salary: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface PayrollPeriod {
  id: number
  period_name: string
  start_date: string
  end_date: string
  is_closed: boolean
  created_at: string
  updated_at: string
}

export interface Payroll {
  id: number
  employee: number
  employee_name: string
  period: number
  period_name: string
  base_salary: string
  deductions: string
  net_salary: string
  payment_date: string | null
  is_paid: boolean
  created_at: string
  updated_at: string
}
