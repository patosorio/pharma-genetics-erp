"use client"

import { useState } from "react"
import { format } from "date-fns"
import { useTaxJournalEntries } from "@/hooks/use-taxes"
import { PageHeader } from "@/components/layout/page-header"
import { DataTable } from "@/components/common/data-table"
import { Badge } from "@/components/ui/badge"
import type { TaxJournalEntry } from "@/lib/types/taxes"

export default function TaxJournalEntriesPage() {
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [search, setSearch] = useState("")

  const { data, isLoading } = useTaxJournalEntries({ page, page_size: pageSize })

  const columns = [
    {
      key: "entry_date",
      label: "Date",
      render: (e: TaxJournalEntry) => format(new Date(e.entry_date), "MMM d, yyyy"),
    },
    {
      key: "entry_type",
      label: "Type",
      render: (e: TaxJournalEntry) => (
        <Badge
          variant="outline"
          className={`thin-border ${
            e.entry_type === "payable"
              ? "border-[#A65D57] text-[#A65D57] bg-[#A65D57]/10"
              : "border-[#4A7C59] text-[#4A7C59] bg-[#4A7C59]/10"
          }`}
        >
          {e.entry_type_display}
        </Badge>
      ),
    },
    { key: "tax_type_name", label: "Tax Type" },
    {
      key: "sales_invoice_number",
      label: "Sales Invoice",
      render: (e: TaxJournalEntry) => e.sales_invoice_number ?? "—",
    },
    {
      key: "purchase_invoice_number",
      label: "Purchase Invoice",
      render: (e: TaxJournalEntry) => e.purchase_invoice_number ?? "—",
    },
    {
      key: "base_amount",
      label: "Base Amount",
      render: (e: TaxJournalEntry) => (
        <span className="data-value">฿{Number.parseFloat(e.base_amount).toLocaleString()}</span>
      ),
    },
    {
      key: "tax_amount",
      label: "Tax Amount",
      render: (e: TaxJournalEntry) => (
        <span className="data-value font-medium">฿{Number.parseFloat(e.tax_amount).toLocaleString()}</span>
      ),
    },
  ]

  return (
    <div>
      <PageHeader
        title="Tax Journal Entries"
        description="View all VAT journal entries from sales and purchase invoices"
      />

      <DataTable
        columns={columns}
        data={data?.results || []}
        loading={isLoading}
        searchPlaceholder="Search entries..."
        onSearch={setSearch}
        emptyMessage="No journal entries found"
        pagination={
          data
            ? {
                currentPage: page,
                totalPages: Math.ceil(data.count / pageSize),
                pageSize,
                totalItems: data.count,
                onPageChange: setPage,
                onPageSizeChange: setPageSize,
              }
            : undefined
        }
      />
    </div>
  )
}
