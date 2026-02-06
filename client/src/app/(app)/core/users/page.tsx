"use client"

import { useState } from "react"
import { Plus } from "lucide-react"
import { useUsers } from "@/hooks/use-users"
import { PageHeader } from "@/components/layout/page-header"
import { DataTable } from "@/components/common/data-table"
import { StatusBadge } from "@/components/common/status-badge"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import type { User } from "@/lib/types/core"

export default function UsersPage() {
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [search, setSearch] = useState("")

  const { data, isLoading } = useUsers({
    page,
    page_size: pageSize,
    search,
  })

  const columns = [
    {
      key: "username",
      label: "Username",
      render: (user: User) => (
        <div>
          <p className="font-medium">{user.username}</p>
          <p className="text-xs text-muted-foreground">{user.email}</p>
        </div>
      ),
    },
    {
      key: "full_name",
      label: "Full Name",
    },
    {
      key: "role",
      label: "Role",
      render: (user: User) => (
        <Badge variant="outline" className="thin-border">
          {user.role.replace(/_/g, " ")}
        </Badge>
      ),
    },
    {
      key: "location_name",
      label: "Location",
      render: (user: User) => user.location_name || "-",
    },
    {
      key: "is_active",
      label: "Status",
      render: (user: User) => <StatusBadge status={user.is_active ? "Active" : "Inactive"} />,
    },
  ]

  return (
    <div>
      <PageHeader
        title="Users"
        description="Manage system users and their roles"
        action={
          <Button>
            <Plus className="w-4 h-4 mr-2" />
            Add User
          </Button>
        }
      />

      <DataTable
        columns={columns}
        data={data?.results || []}
        loading={isLoading}
        searchPlaceholder="Search users..."
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
