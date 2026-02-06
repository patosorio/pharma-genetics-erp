"use client"

import { useState } from "react"
import { Plus } from "lucide-react"
import { useStrainCategories } from "@/hooks/use-strains"
import { PageHeader } from "@/components/layout/page-header"
import { DataTable } from "@/components/common/data-table"
import { Button } from "@/components/ui/button"
import type { StrainCategory } from "@/lib/types/genetics"

export default function CategoriesPage() {
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [search, setSearch] = useState("")

  const { data, isLoading } = useStrainCategories({
    page,
    page_size: pageSize,
    search,
  })

  const columns = [
    {
      key: "name",
      label: "Category Name",
      render: (category: StrainCategory) => <span className="font-medium">{category.name}</span>,
    },
    {
      key: "description",
      label: "Description",
      render: (category: StrainCategory) => category.description || "-",
    },
  ]

  return (
    <div>
      <PageHeader
        title="Strain Categories"
        description="Manage strain classification categories"
        action={
          <Button>
            <Plus className="w-4 h-4 mr-2" />
            Add Category
          </Button>
        }
      />

      <DataTable
        columns={columns}
        data={data?.results || []}
        loading={isLoading}
        searchPlaceholder="Search categories..."
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
