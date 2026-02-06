"use client"

import { useState } from "react"
import { Plus } from "lucide-react"
import { useContacts } from "@/hooks/use-contacts"
import { PageHeader } from "@/components/layout/page-header"
import { DataTable } from "@/components/common/data-table"
import { StatusBadge } from "@/components/common/status-badge"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import type { Contact } from "@/lib/types/core"

export default function ContactsPage() {
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [search, setSearch] = useState("")

  const { data, isLoading } = useContacts({
    page,
    page_size: pageSize,
    search,
  })

  const columns = [
    {
      key: "name",
      label: "Name",
      render: (contact: Contact) => (
        <div>
          <p className="font-medium">{contact.name}</p>
          {contact.email && <p className="text-xs text-muted-foreground">{contact.email}</p>}
        </div>
      ),
    },
    {
      key: "contact_type_display",
      label: "Type",
      render: (contact: Contact) => (
        <Badge variant="outline" className="thin-border">
          {contact.contact_type_display}
        </Badge>
      ),
    },
    {
      key: "phone",
      label: "Phone",
      render: (contact: Contact) => contact.phone || "-",
    },
    {
      key: "tax_id",
      label: "Tax ID",
      render: (contact: Contact) => contact.tax_id || "-",
    },
    {
      key: "is_active",
      label: "Status",
      render: (contact: Contact) => <StatusBadge status={contact.is_active ? "Active" : "Inactive"} />,
    },
  ]

  return (
    <div>
      <PageHeader
        title="Contacts"
        description="Manage customers, suppliers, and vendors"
        action={
          <Button>
            <Plus className="w-4 h-4 mr-2" />
            Add Contact
          </Button>
        }
      />

      <DataTable
        columns={columns}
        data={data?.results || []}
        loading={isLoading}
        searchPlaceholder="Search contacts..."
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
