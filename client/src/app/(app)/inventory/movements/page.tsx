"use client"

import { useState } from "react"
import { Plus, ArrowDown, ArrowUp, RefreshCw, ArrowRightLeft } from "lucide-react"
import { format } from "date-fns"
import { PageHeader } from "@/components/layout/page-header"
import { DataTable } from "@/components/common/data-table"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import type { StockMovement } from "@/lib/types/inventory"

const movementIcons = {
  in: ArrowDown,
  out: ArrowUp,
  adjustment: RefreshCw,
  transfer: ArrowRightLeft,
}

const movementColors = {
  in: "border-[#4A7C59] text-[#4A7C59] bg-[#4A7C59]/10",
  out: "border-[#A65D57] text-[#A65D57] bg-[#A65D57]/10",
  adjustment: "border-[#C4A035] text-[#C4A035] bg-[#C4A035]/10",
  transfer: "border-[#5A7A8C] text-[#5A7A8C] bg-[#5A7A8C]/10",
}

const mockMovements: StockMovement[] = [
  {
    id: "1",
    item: "1",
    item_name: "OG Kush Clones",
    movement_type: "in",
    movement_type_display: "Incoming",
    quantity: 50,
    from_location: null,
    from_location_name: null,
    to_location: "1",
    to_location_name: "Clone Room A",
    reference: "BKK-2024-001",
    notes: "Production batch completed rooting",
    created_by: "1",
    created_by_name: "Admin User",
    created_at: "2024-03-01T14:30:00Z",
  },
  {
    id: "2",
    item: "2",
    item_name: "Blue Dream Clones",
    movement_type: "out",
    movement_type_display: "Outgoing",
    quantity: 25,
    from_location: "1",
    from_location_name: "Clone Room A",
    to_location: null,
    to_location_name: null,
    reference: "ORDER-1234",
    notes: "Sold to customer",
    created_by: "1",
    created_by_name: "Admin User",
    created_at: "2024-03-01T11:15:00Z",
  },
  {
    id: "3",
    item: "3",
    item_name: "Sour Diesel Clones",
    movement_type: "transfer",
    movement_type_display: "Transfer",
    quantity: 15,
    from_location: "1",
    from_location_name: "Clone Room A",
    to_location: "2",
    to_location_name: "Clone Room B",
    reference: null,
    notes: "Balancing inventory across rooms",
    created_by: "1",
    created_by_name: "Admin User",
    created_at: "2024-02-29T16:45:00Z",
  },
  {
    id: "4",
    item: "1",
    item_name: "OG Kush Clones",
    movement_type: "adjustment",
    movement_type_display: "Adjustment",
    quantity: -5,
    from_location: "1",
    from_location_name: "Clone Room A",
    to_location: "1",
    to_location_name: "Clone Room A",
    reference: null,
    notes: "Inventory correction - damaged clones",
    created_by: "1",
    created_by_name: "Admin User",
    created_at: "2024-02-28T09:20:00Z",
  },
  {
    id: "5",
    item: "6",
    item_name: "Girl Scout Cookies Clones",
    movement_type: "in",
    movement_type_display: "Incoming",
    quantity: 30,
    from_location: null,
    from_location_name: null,
    to_location: "2",
    to_location_name: "Clone Room B",
    reference: "BKK-2024-004",
    notes: "New batch from production",
    created_by: "1",
    created_by_name: "Admin User",
    created_at: "2024-02-27T13:00:00Z",
  },
]

export default function StockMovementsPage() {
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [search, setSearch] = useState("")

  const data = {
    count: mockMovements.length,
    results: mockMovements.filter((m) => m.item_name.toLowerCase().includes(search.toLowerCase())),
  }

  const columns = [
    {
      key: "movement_type",
      label: "Type",
      render: (movement: StockMovement) => {
        const Icon = movementIcons[movement.movement_type]
        const color = movementColors[movement.movement_type]
        return (
          <Badge variant="outline" className={`thin-border ${color}`}>
            <Icon className="w-3 h-3 mr-1" strokeWidth={1.5} />
            {movement.movement_type_display}
          </Badge>
        )
      },
    },
    {
      key: "item_name",
      label: "Item",
      render: (movement: StockMovement) => <span className="font-medium">{movement.item_name}</span>,
    },
    {
      key: "quantity",
      label: "Quantity",
      render: (movement: StockMovement) => {
        const isNegative = movement.quantity < 0 || movement.movement_type === "out"
        const displayQty = Math.abs(movement.quantity)
        return (
          <span className={`data-value font-medium ${isNegative ? "text-[#A65D57]" : "text-[#4A7C59]"}`}>
            {isNegative ? "-" : "+"}
            {displayQty} units
          </span>
        )
      },
    },
    {
      key: "from_location_name",
      label: "From",
      render: (movement: StockMovement) => movement.from_location_name || "-",
    },
    {
      key: "to_location_name",
      label: "To",
      render: (movement: StockMovement) => movement.to_location_name || "-",
    },
    {
      key: "reference",
      label: "Reference",
      render: (movement: StockMovement) =>
        movement.reference ? <span className="font-mono text-sm">{movement.reference}</span> : "-",
    },
    {
      key: "created_by_name",
      label: "Created By",
    },
    {
      key: "created_at",
      label: "Date",
      render: (movement: StockMovement) => format(new Date(movement.created_at), "MMM d, yyyy HH:mm"),
    },
  ]

  return (
    <div>
      <PageHeader
        title="Stock Movements"
        description="Track clone inventory transactions and transfers"
        action={
          <Button>
            <Plus className="w-4 h-4 mr-2" />
            Record Movement
          </Button>
        }
      />

      <DataTable
        columns={columns}
        data={data.results}
        loading={false}
        searchPlaceholder="Search movements..."
        onSearch={setSearch}
        pagination={{
          currentPage: page,
          totalPages: Math.ceil(data.count / pageSize),
          pageSize,
          totalItems: data.count,
          onPageChange: setPage,
          onPageSizeChange: setPageSize,
        }}
      />
    </div>
  )
}
