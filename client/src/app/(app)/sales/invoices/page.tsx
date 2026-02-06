"use client"

import { useState } from "react"
import { Plus } from "lucide-react"
import { format } from "date-fns"
import { useInvoices } from "@/hooks/use-invoices"
import { PageHeader } from "@/components/layout/page-header"
import { DataTable } from "@/components/common/data-table"
import { InvoiceStatusBadge } from "@/components/sales/invoice-status-badge"
import { Button } from "@/components/ui/button"
import type { Invoice } from "@/lib/types/sales"

export default function InvoicesPage() {
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [search, setSearch] = useState("")

  const { data, isLoading } = useInvoices({
    page,
    page_size: pageSize,
    search,
    ordering: "-invoice_date",
  })

  const columns = [
    {
      key: "invoice_number",
      label: "Invoice #",
      render: (invoice: Invoice) => <span className="font-medium">{invoice.invoice_number}</span>,
    },
    {
      key: "customer_name",
      label: "Customer",
    },
    {
      key: "invoice_date",
      label: "Invoice Date",
      render: (invoice: Invoice) => format(new Date(invoice.invoice_date), "MMM d, yyyy"),
    },
    {
      key: "due_date",
      label: "Due Date",
      render: (invoice: Invoice) => format(new Date(invoice.due_date), "MMM d, yyyy"),
    },
    {
      key: "status",
      label: "Status",
      render: (invoice: Invoice) => <InvoiceStatusBadge status={invoice.status} />,
    },
    {
      key: "total_amount",
      label: "Total",
      render: (invoice: Invoice) => (
        <span className="data-value">฿{Number.parseFloat(invoice.total_amount).toLocaleString()}</span>
      ),
    },
    {
      key: "balance_due",
      label: "Balance Due",
      render: (invoice: Invoice) => (
        <span className="data-value font-medium text-[#A65D57]">
          ฿{Number.parseFloat(invoice.balance_due).toLocaleString()}
        </span>
      ),
    },
  ]

  return (
    <div>
      <PageHeader
        title="Invoices"
        description="Manage invoices and payment tracking"
        action={
          <Button>
            <Plus className="w-4 h-4 mr-2" />
            Create Invoice
          </Button>
        }
      />

      <DataTable
        columns={columns}
        data={data?.results || []}
        loading={isLoading}
        searchPlaceholder="Search invoices..."
        onSearch={setSearch}
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
