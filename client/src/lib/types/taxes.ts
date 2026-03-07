export interface TaxJournalEntry {
  id: number
  tax_report: number
  entry_type: "payable" | "recoverable"
  entry_type_display: string
  sales_invoice: number | null
  sales_invoice_number: string | null
  purchase_invoice: number | null
  purchase_invoice_number: string | null
  tax_type: number
  tax_type_name: string
  base_amount: string
  tax_amount: string
  entry_date: string
  notes: string | null
}

export interface TaxReport {
  id: number
  report_number: string
  period_start: string
  period_end: string
  status: "draft" | "finalized" | "filed" | "paid"
  status_display: string
  currency: number
  currency_code: string
  total_vat_payable: string
  total_vat_recoverable: string
  net_vat_position: string
  filing_date: string | null
  payment_date: string | null
  notes: string | null
  journal_entries?: TaxJournalEntry[]
  created_at: string
  updated_at: string
}
