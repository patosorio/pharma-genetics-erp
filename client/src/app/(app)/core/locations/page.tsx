"use client"

import { useState } from "react"
import { Plus, MapPin } from "lucide-react"
import { useLocations } from "@/hooks/use-locations"
import { PageHeader } from "@/components/layout/page-header"
import { DataTable } from "@/components/common/data-table"
import { StatusBadge } from "@/components/common/status-badge"
import { Button } from "@/components/ui/button"
import type { Location } from "@/lib/types/core"

export default function LocationsPage() {
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [search, setSearch] = useState("")

  const { data, isLoading } = useLocations({
    page,
    page_size: pageSize,
    search,
  })

  const columns = [
    {
      key: "code",
      label: "Code",
      render: (location: Location) => (
        <div className="flex items-center gap-2">
          <MapPin className="w-4 h-4 text-muted-foreground" strokeWidth={1.5} />
          <span className="font-medium">{location.code}</span>
        </div>
      ),
    },
    {
      key: "name",
      label: "Name",
    },
    {
      key: "address",
      label: "Address",
    },
    {
      key: "is_active",
      label: "Status",
      render: (location: Location) => <StatusBadge status={location.is_active ? "Active" : "Inactive"} />,
    },
  ]

  return (
    <div>
      <PageHeader
        title="Locations"
        description="Manage cultivation and warehouse locations"
        action={
          <Button>
            <Plus className="w-4 h-4 mr-2" />
            Add Location
          </Button>
        }
      />

      <DataTable
        columns={columns}
        data={data?.results || []}
        loading={isLoading}
        searchPlaceholder="Search locations..."
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
