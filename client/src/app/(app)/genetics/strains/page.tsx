"use client"

import { useState } from "react"
import { Plus } from "lucide-react"
import { useStrains } from "@/hooks/use-strains"
import { PageHeader } from "@/components/layout/page-header"
import { DataTable } from "@/components/common/data-table"
import { StatusBadge } from "@/components/common/status-badge"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import type { Strain } from "@/lib/types/genetics"

export default function StrainsPage() {
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [search, setSearch] = useState("")

  const { data, isLoading } = useStrains({
    page,
    page_size: pageSize,
    search,
  })

  const columns = [
    {
      key: "name",
      label: "Strain",
      render: (strain: Strain) => (
        <div>
          <p className="font-medium">{strain.name}</p>
          <p className="text-xs text-muted-foreground">{strain.slug}</p>
        </div>
      ),
    },
    {
      key: "category_name",
      label: "Category",
      render: (strain: Strain) => (
        <Badge variant="outline" className="thin-border">
          {strain.category_name}
        </Badge>
      ),
    },
    {
      key: "thc_percentage",
      label: "THC %",
      render: (strain: Strain) => <span className="data-value">{strain.thc_percentage || "-"}</span>,
    },
    {
      key: "cbd_percentage",
      label: "CBD %",
      render: (strain: Strain) => <span className="data-value">{strain.cbd_percentage || "-"}</span>,
    },
    {
      key: "terpene_profile",
      label: "Terpene",
      render: (strain: Strain) => strain.terpene_profile || "-",
    },
    {
      key: "catalogue_year",
      label: "Year",
      render: (strain: Strain) => <span className="data-value">{strain.catalogue_year}</span>,
    },
    {
      key: "is_active",
      label: "Status",
      render: (strain: Strain) => <StatusBadge status={strain.is_active ? "Active" : "Inactive"} />,
    },
  ]

  return (
    <div>
      <PageHeader
        title="Strains"
        description="Manage cannabis genetics and strain catalog"
        action={
          <Button>
            <Plus className="w-4 h-4 mr-2" />
            Add Strain
          </Button>
        }
      />

      <DataTable
        columns={columns}
        data={data?.results || []}
        loading={isLoading}
        searchPlaceholder="Search strains..."
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
