"use client"

import { useState } from "react"
import { Plus, AlertTriangle } from "lucide-react"
import { PageHeader } from "@/components/layout/page-header"
import { DataTable } from "@/components/common/data-table"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import type { InventoryItem } from "@/lib/types/inventory"

const mockInventory: InventoryItem[] = [
  {
    id: "1",
    sku: "CLN-OGKUSH-001",
    name: "OG Kush Clones",
    strain: "1",
    strain_name: "OG Kush",
    category: "clones",
    category_display: "Clones",
    quantity: 145,
    unit: "units",
    location: "1",
    location_name: "Clone Room A",
    batch: "1",
    batch_number: "BKK-2024-001",
    unit_cost: "250.00",
    reorder_point: 50,
    clone_status: "available",
    clone_status_display: "Available",
    notes: null,
    created_at: "2024-02-15T10:00:00Z",
    updated_at: "2024-03-01T10:00:00Z",
  },
  {
    id: "2",
    sku: "CLN-BLDREAM-001",
    name: "Blue Dream Clones",
    strain: "2",
    strain_name: "Blue Dream",
    category: "clones",
    category_display: "Clones",
    quantity: 32,
    unit: "units",
    location: "1",
    location_name: "Clone Room A",
    batch: "2",
    batch_number: "BKK-2024-002",
    unit_cost: "280.00",
    reorder_point: 50,
    clone_status: "available",
    clone_status_display: "Available",
    notes: "Low stock alert",
    created_at: "2024-02-20T10:00:00Z",
    updated_at: "2024-03-01T10:00:00Z",
  },
  {
    id: "3",
    sku: "CLN-SOURDSL-001",
    name: "Sour Diesel Clones",
    strain: "3",
    strain_name: "Sour Diesel",
    category: "clones",
    category_display: "Clones",
    quantity: 87,
    unit: "units",
    location: "2",
    location_name: "Clone Room B",
    batch: "3",
    batch_number: "BKK-2024-003",
    unit_cost: "300.00",
    reorder_point: 40,
    clone_status: "available",
    clone_status_display: "Available",
    notes: null,
    created_at: "2024-02-25T10:00:00Z",
    updated_at: "2024-03-01T10:00:00Z",
  },
  {
    id: "4",
    sku: "MTH-GGSTR-001",
    name: "Gorilla Glue Mother Plant",
    strain: "4",
    strain_name: "Gorilla Glue #4",
    category: "mother_plants",
    category_display: "Mother Plants",
    quantity: 2,
    unit: "units",
    location: "3",
    location_name: "Mother Room",
    batch: null,
    batch_number: null,
    unit_cost: "5000.00",
    reorder_point: 1,
    notes: "Premium genetics - high yielder",
    created_at: "2024-01-10T10:00:00Z",
    updated_at: "2024-03-01T10:00:00Z",
  },
  {
    id: "5",
    sku: "SUP-ROCKWOOL-100",
    name: "Rockwool Cubes 4x4",
    strain: null,
    strain_name: null,
    category: "supplies",
    category_display: "Supplies",
    quantity: 500,
    unit: "pcs",
    location: "4",
    location_name: "Supply Storage",
    batch: null,
    batch_number: null,
    unit_cost: "8.00",
    reorder_point: 100,
    notes: null,
    created_at: "2024-02-01T10:00:00Z",
    updated_at: "2024-03-01T10:00:00Z",
  },
  {
    id: "6",
    sku: "CLN-GSCOOK-001",
    name: "Girl Scout Cookies Clones",
    strain: "5",
    strain_name: "Girl Scout Cookies",
    category: "clones",
    category_display: "Clones",
    quantity: 23,
    unit: "units",
    location: "2",
    location_name: "Clone Room B",
    batch: "4",
    batch_number: "BKK-2024-004",
    unit_cost: "320.00",
    reorder_point: 30,
    clone_status: "reserved",
    clone_status_display: "Reserved",
    notes: "Reserved for Order #1234",
    created_at: "2024-02-28T10:00:00Z",
    updated_at: "2024-03-01T10:00:00Z",
  },
]

export default function InventoryItemsPage() {
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [search, setSearch] = useState("")

  const data = {
    count: mockInventory.length,
    results: mockInventory.filter((i) => i.name.toLowerCase().includes(search.toLowerCase())),
  }

  const columns = [
    {
      key: "sku",
      label: "SKU",
      render: (item: InventoryItem) => (
        <div>
          <span className="font-medium">{item.sku}</span>
          {item.reorder_point && item.quantity <= item.reorder_point && (
            <AlertTriangle className="inline-block w-4 h-4 ml-2 text-[#C4A035]" strokeWidth={1.5} />
          )}
        </div>
      ),
    },
    {
      key: "name",
      label: "Item Name",
      render: (item: InventoryItem) => (
        <div>
          <p className="font-medium">{item.name}</p>
          {item.strain_name && <p className="text-xs text-muted-foreground">{item.strain_name}</p>}
        </div>
      ),
    },
    {
      key: "category_display",
      label: "Category",
      render: (item: InventoryItem) => (
        <Badge variant="outline" className="thin-border">
          {item.category_display}
        </Badge>
      ),
    },
    {
      key: "quantity",
      label: "Quantity",
      render: (item: InventoryItem) => (
        <div>
          <span className="data-value font-medium">
            {item.quantity} {item.unit}
          </span>
          {item.clone_status && (
            <Badge
              variant="outline"
              className={`ml-2 thin-border ${
                item.clone_status === "available"
                  ? "border-[#4A7C59] text-[#4A7C59] bg-[#4A7C59]/10"
                  : item.clone_status === "reserved"
                    ? "border-[#C4A035] text-[#C4A035] bg-[#C4A035]/10"
                    : "border-muted-foreground/30 text-muted-foreground bg-muted/50"
              }`}
            >
              {item.clone_status_display}
            </Badge>
          )}
        </div>
      ),
    },
    {
      key: "batch_number",
      label: "Batch",
      render: (item: InventoryItem) =>
        item.batch_number ? <span className="font-mono text-sm">{item.batch_number}</span> : "-",
    },
    {
      key: "location_name",
      label: "Location",
    },
    {
      key: "unit_cost",
      label: "Unit Cost",
      render: (item: InventoryItem) => (
        <span className="data-value">{item.unit_cost ? `฿${Number.parseFloat(item.unit_cost).toFixed(2)}` : "-"}</span>
      ),
    },
    {
      key: "reorder_point",
      label: "Reorder Point",
      render: (item: InventoryItem) => <span className="data-value">{item.reorder_point || "-"}</span>,
    },
  ]

  return (
    <div>
      <PageHeader
        title="Inventory Items"
        description="Manage clone inventory, mother plants, and supplies"
        action={
          <Button>
            <Plus className="w-4 h-4 mr-2" />
            Add Item
          </Button>
        }
      />

      <DataTable
        columns={columns}
        data={data.results}
        loading={false}
        searchPlaceholder="Search inventory..."
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
