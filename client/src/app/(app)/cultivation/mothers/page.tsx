"use client"

import { useState } from "react"
import { Plus, Heart } from "lucide-react"
import { format } from "date-fns"
import { useMotherPlants } from "@/hooks/use-cultivation"
import { PageHeader } from "@/components/layout/page-header"
import { DataTable } from "@/components/common/data-table"
import { MotherPlantStatusBadge } from "@/components/cultivation/mother-plant-status-badge"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import type { MotherPlant } from "@/lib/types/cultivation"

export default function MotherPlantsPage() {
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [search, setSearch] = useState("")

  const { data, isLoading } = useMotherPlants({
    page,
    page_size: pageSize,
    search,
  })

  const columns = [
    {
      key: "code",
      label: "Plant Code",
      render: (plant: MotherPlant) => (
        <div className="flex items-center gap-2">
          <Heart className="w-4 h-4 text-primary" />
          <span className="font-medium">{plant.code}</span>
        </div>
      ),
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
      render: (plant: MotherPlant) => <MotherPlantStatusBadge status={plant.status} />,
    },
    {
      key: "health_grade",
      label: "Health",
      render: (plant: MotherPlant) => (
        <div className="flex items-center gap-2">
          <span className="font-medium">{plant.health_grade}</span>
          <span className="text-xs text-muted-foreground">({plant.health_grade_display})</span>
        </div>
      ),
    },
    {
      key: "total_cuttings_taken",
      label: "Total Cuts",
      render: (plant: MotherPlant) => <span className="data-value">{plant.total_cuttings_taken}</span>,
    },
    {
      key: "last_cut_date",
      label: "Last Cut",
      render: (plant: MotherPlant) =>
        plant.last_cut_date ? format(new Date(plant.last_cut_date), "MMM d, yyyy") : "-",
    },
  ]

  return (
    <div>
      <PageHeader
        title="Mother Plants"
        description="Manage mother plants for clone production"
        action={
          <Button>
            <Plus className="w-4 h-4 mr-2" />
            Add Mother Plant
          </Button>
        }
      />

      <DataTable
        columns={columns}
        data={data?.results || []}
        loading={isLoading}
        searchPlaceholder="Search by code or strain..."
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
