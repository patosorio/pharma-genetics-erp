"use client"

import { useState } from "react"
import { Plus, Leaf } from "lucide-react"
import { format } from "date-fns"
import { useClones } from "@/hooks/use-cultivation"
import { PageHeader } from "@/components/layout/page-header"
import { DataTable } from "@/components/common/data-table"
import { CloneStatusBadge } from "@/components/cultivation/clone-status-badge"
import { Button } from "@/components/ui/button"
import type { Clone } from "@/lib/types/cultivation"

export default function ClonesPage() {
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [search, setSearch] = useState("")

  const { data, isLoading } = useClones({
    page,
    page_size: pageSize,
    search,
  })

  const columns = [
    {
      key: "code",
      label: "Clone Code",
      render: (clone: Clone) => (
        <div className="flex items-center gap-2">
          <Leaf className="w-4 h-4 text-primary" />
          <span className="font-medium">{clone.code}</span>
        </div>
      ),
    },
    {
      key: "batch_number",
      label: "Batch",
    },
    {
      key: "strain_name",
      label: "Strain",
    },
    {
      key: "location_code",
      label: "Location",
    },
    {
      key: "status",
      label: "Status",
      render: (clone: Clone) => <CloneStatusBadge status={clone.status} />,
    },
    {
      key: "rooting_date",
      label: "Rooting Date",
      render: (clone: Clone) => (clone.rooting_date ? format(new Date(clone.rooting_date), "MMM d, yyyy") : "-"),
    },
    {
      key: "unit_cost",
      label: "Unit Cost",
      render: (clone: Clone) => (clone.unit_cost ? `฿${Number.parseFloat(clone.unit_cost).toFixed(2)}` : "-"),
    },
    {
      key: "sold_date",
      label: "Sold Date",
      render: (clone: Clone) => (clone.sold_date ? format(new Date(clone.sold_date), "MMM d, yyyy") : "-"),
    },
    {
      key: "age_in_days",
      label: "Age (days)",
      render: (clone: Clone) => <span className="data-value">{clone.age_in_days}</span>,
    },
  ]

  return (
    <div>
      <PageHeader
        title="Clones Inventory"
        description="Manage rooted clones available for sale"
        action={
          <Button>
            <Plus className="w-4 h-4 mr-2" />
            Add Clone
          </Button>
        }
      />

      <DataTable
        columns={columns}
        data={data?.results || []}
        loading={isLoading}
        searchPlaceholder="Search by clone code..."
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
