"use client"

import { useState } from "react"
import { Plus, Scissors } from "lucide-react"
import { format } from "date-fns"
import { useProductionBatches } from "@/hooks/use-batches"
import { PageHeader } from "@/components/layout/page-header"
import { DataTable } from "@/components/common/data-table"
import { ProductionBatchStatusBadge } from "@/components/cultivation/production-batch-status-badge"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import type { ProductionBatch } from "@/lib/types/cultivation"

export default function ProductionBatchesPage() {
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [search, setSearch] = useState("")

  const { data, isLoading } = useProductionBatches({
    page,
    page_size: pageSize,
    search,
  })

  const columns = [
    {
      key: "batch_number",
      label: "Batch Number",
      render: (batch: ProductionBatch) => (
        <div className="flex items-center gap-2">
          <Scissors className="w-4 h-4 text-muted-foreground" />
          <span className="font-medium">{batch.batch_number}</span>
        </div>
      ),
    },
    {
      key: "mother_plant_code",
      label: "Mother Plant",
    },
    {
      key: "location_code",
      label: "Location",
    },
    {
      key: "initial_clone_count",
      label: "Initial Cuts",
      render: (batch: ProductionBatch) => <span className="data-value">{batch.initial_clone_count}</span>,
    },
    {
      key: "rooted_clone_count",
      label: "Rooted",
      render: (batch: ProductionBatch) => <span className="data-value">{batch.rooted_clone_count}</span>,
    },
    {
      key: "survival_rate",
      label: "Survival Rate",
      render: (batch: ProductionBatch) => (
        <div className="flex items-center gap-2 min-w-[120px]">
          <Progress value={batch.survival_rate} className="h-2 flex-1" />
          <span className="text-sm text-muted-foreground w-10">{batch.survival_rate.toFixed(0)}%</span>
        </div>
      ),
    },
    {
      key: "status",
      label: "Status",
      render: (batch: ProductionBatch) => <ProductionBatchStatusBadge status={batch.status} />,
    },
    {
      key: "cutting_date",
      label: "Cutting Date",
      render: (batch: ProductionBatch) => format(new Date(batch.cutting_date), "MMM d, yyyy"),
    },
    {
      key: "expected_rooting_date",
      label: "Expected Rooting",
      render: (batch: ProductionBatch) =>
        batch.expected_rooting_date ? format(new Date(batch.expected_rooting_date), "MMM d, yyyy") : "-",
    },
  ]

  return (
    <div>
      <PageHeader
        title="Production Batches"
        description="Track cutting and rooting batches from mother plants"
        action={
          <Button>
            <Plus className="w-4 h-4 mr-2" />
            New Batch
          </Button>
        }
      />

      <DataTable
        columns={columns}
        data={data?.results || []}
        loading={isLoading}
        searchPlaceholder="Search batches..."
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
