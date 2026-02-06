"use client"

import { useState } from "react"
import { Plus } from "lucide-react"
import { format } from "date-fns"
import { PageHeader } from "@/components/layout/page-header"
import { DataTable } from "@/components/common/data-table"
import { OrderStatusBadge } from "@/components/sales/order-status-badge"
import { Button } from "@/components/ui/button"
import type { Order } from "@/lib/types/sales"

const mockOrders: Order[] = [
  {
    id: "1",
    order_number: "ORD-2024-001",
    customer: "1",
    customer_name: "Green Leaf Dispensary",
    order_date: "2024-03-01",
    delivery_date: "2024-03-05",
    status: "confirmed",
    total_amount: "125000.00",
    notes: "Priority delivery",
    created_at: "2024-03-01T10:00:00Z",
    updated_at: "2024-03-01T10:00:00Z",
  },
  {
    id: "2",
    order_number: "ORD-2024-002",
    customer: "2",
    customer_name: "Bangkok Cannabis Co",
    order_date: "2024-03-02",
    delivery_date: "2024-03-08",
    status: "pending",
    total_amount: "85000.00",
    notes: "",
    created_at: "2024-03-02T10:00:00Z",
    updated_at: "2024-03-02T10:00:00Z",
  },
  {
    id: "3",
    order_number: "ORD-2024-003",
    customer: "3",
    customer_name: "Thai Herbal Solutions",
    order_date: "2024-02-28",
    delivery_date: "2024-03-03",
    status: "shipped",
    total_amount: "195000.00",
    notes: "Fragile items",
    created_at: "2024-02-28T10:00:00Z",
    updated_at: "2024-03-01T10:00:00Z",
  },
  {
    id: "4",
    order_number: "ORD-2024-004",
    customer: "1",
    customer_name: "Green Leaf Dispensary",
    order_date: "2024-02-25",
    delivery_date: "2024-02-28",
    status: "delivered",
    total_amount: "110000.00",
    notes: "Regular customer",
    created_at: "2024-02-25T10:00:00Z",
    updated_at: "2024-02-28T10:00:00Z",
  },
]

export default function OrdersPage() {
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [search, setSearch] = useState("")

  const data = {
    count: mockOrders.length,
    results: mockOrders.filter((o) => o.order_number.toLowerCase().includes(search.toLowerCase())),
  }

  const columns = [
    {
      key: "order_number",
      label: "Order #",
      render: (order: Order) => <span className="font-medium">{order.order_number}</span>,
    },
    {
      key: "customer_name",
      label: "Customer",
    },
    {
      key: "order_date",
      label: "Order Date",
      render: (order: Order) => format(new Date(order.order_date), "MMM d, yyyy"),
    },
    {
      key: "delivery_date",
      label: "Delivery Date",
      render: (order: Order) => (order.delivery_date ? format(new Date(order.delivery_date), "MMM d, yyyy") : "-"),
    },
    {
      key: "status",
      label: "Status",
      render: (order: Order) => <OrderStatusBadge status={order.status} />,
    },
    {
      key: "total_amount",
      label: "Total",
      render: (order: Order) => (
        <span className="data-value font-medium">฿{Number.parseFloat(order.total_amount).toLocaleString()}</span>
      ),
    },
  ]

  return (
    <div>
      <PageHeader
        title="Sales Orders"
        description="Manage customer orders and shipments"
        action={
          <Button>
            <Plus className="w-4 h-4 mr-2" />
            New Order
          </Button>
        }
      />

      <DataTable
        columns={columns}
        data={data.results}
        loading={false}
        searchPlaceholder="Search orders..."
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
