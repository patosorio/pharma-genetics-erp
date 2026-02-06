"use client"

import { useState } from "react"
import { Plus } from "lucide-react"
import { useCustomers } from "@/hooks/use-customers"
import { PageHeader } from "@/components/layout/page-header"
import { DataTable } from "@/components/common/data-table"
import { StatusBadge } from "@/components/common/status-badge"
import { Button } from "@/components/ui/button"
import type { Customer } from "@/lib/types/sales"

export default function CustomersPage() {
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [search, setSearch] = useState("")

  const { data, isLoading } = useCustomers({
    page,
    page_size: pageSize,
    search,
  })

  const columns = [
    {
      key: "customer_code",
      label: "Code",
      render: (customer: Customer) => <span className="font-medium">{customer.customer_code}</span>,
    },
    {
      key: "contact_name",
      label: "Customer Name",
    },
    {
      key: "credit_limit",
      label: "Credit Limit",
      render: (customer: Customer) => (
        <span className="data-value">
          {customer.credit_limit ? `฿${Number.parseFloat(customer.credit_limit).toLocaleString()}` : "-"}
        </span>
      ),
    },
    {
      key: "payment_terms_days",
      label: "Payment Terms",
      render: (customer: Customer) => <span className="data-value">{customer.payment_terms_days} days</span>,
    },
    {
      key: "is_active",
      label: "Status",
      render: (customer: Customer) => <StatusBadge status={customer.is_active ? "Active" : "Inactive"} />,
    },
  ]

  return (
    <div>
      <PageHeader
        title="Customers"
        description="Manage customer accounts and credit terms"
        action={
          <Button>
            <Plus className="w-4 h-4 mr-2" />
            Add Customer
          </Button>
        }
      />

      <DataTable
        columns={columns}
        data={data?.results || []}
        loading={isLoading}
        searchPlaceholder="Search customers..."
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
