"use client"

import { useState } from "react"
import { Plus, ChevronRight } from "lucide-react"
import { format } from "date-fns"
import { toast } from "sonner"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import {
  useOrders,
  useCreateOrder,
  useConfirmOrder,
  useMarkOrderInProduction,
  useMarkOrderReady,
  useCancelOrder,
} from "@/hooks/use-orders"
import { useCustomers } from "@/hooks/use-customers"
import { useLocations } from "@/hooks/use-locations"
import { PageHeader } from "@/components/layout/page-header"
import { DataTable } from "@/components/common/data-table"
import { OrderStatusBadge } from "@/components/sales/order-status-badge"
import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog"
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import type { Order } from "@/lib/types/sales"

const orderSchema = z.object({
  customer: z.coerce.number({ required_error: "Customer is required" }),
  location: z.coerce.number({ required_error: "Location is required" }),
  order_date: z.string().min(1, "Order date is required"),
  expected_delivery_date: z.string().optional(),
  notes: z.string().optional(),
})
type OrderFormValues = z.infer<typeof orderSchema>

function NewOrderDialog({ open, onOpenChange }: { open: boolean; onOpenChange: (v: boolean) => void }) {
  const create = useCreateOrder()
  const { data: customers } = useCustomers({ page_size: 200 })
  const { data: locations } = useLocations({ page_size: 100 })
  const form = useForm<OrderFormValues>({
    resolver: zodResolver(orderSchema),
    defaultValues: { order_date: new Date().toISOString().split("T")[0], expected_delivery_date: "", notes: "" },
  })

  const onSubmit = async (values: OrderFormValues) => {
    try {
      await create.mutateAsync(values)
      toast.success("Order created")
      form.reset()
      onOpenChange(false)
    } catch {
      toast.error("Failed to create order.")
    }
  }

  return (
    <Dialog open={open} onOpenChange={(v) => { if (!v) form.reset(); onOpenChange(v) }}>
      <DialogContent>
        <DialogHeader><DialogTitle>New Sales Order</DialogTitle></DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField control={form.control} name="customer" render={({ field }) => (
              <FormItem><FormLabel>Customer</FormLabel>
                <Select onValueChange={(v) => field.onChange(Number(v))} value={field.value?.toString() ?? ""}>
                  <FormControl><SelectTrigger className="thin-border"><SelectValue placeholder="Select customer" /></SelectTrigger></FormControl>
                  <SelectContent>
                    {customers?.results.map((c) => <SelectItem key={c.id} value={c.id.toString()}>{c.contact_name}</SelectItem>)}
                  </SelectContent>
                </Select>
                <FormMessage />
              </FormItem>
            )} />
            <FormField control={form.control} name="location" render={({ field }) => (
              <FormItem><FormLabel>Fulfillment Location</FormLabel>
                <Select onValueChange={(v) => field.onChange(Number(v))} value={field.value?.toString() ?? ""}>
                  <FormControl><SelectTrigger className="thin-border"><SelectValue placeholder="Select location" /></SelectTrigger></FormControl>
                  <SelectContent>
                    {locations?.results.map((l) => <SelectItem key={l.id} value={l.id.toString()}>{l.code} — {l.name}</SelectItem>)}
                  </SelectContent>
                </Select>
                <FormMessage />
              </FormItem>
            )} />
            <div className="grid grid-cols-2 gap-4">
              <FormField control={form.control} name="order_date" render={({ field }) => (
                <FormItem><FormLabel>Order Date</FormLabel>
                  <FormControl><Input type="date" className="thin-border" {...field} /></FormControl>
                  <FormMessage />
                </FormItem>
              )} />
              <FormField control={form.control} name="expected_delivery_date" render={({ field }) => (
                <FormItem><FormLabel>Expected Delivery (optional)</FormLabel>
                  <FormControl><Input type="date" className="thin-border" {...field} /></FormControl>
                  <FormMessage />
                </FormItem>
              )} />
            </div>
            <FormField control={form.control} name="notes" render={({ field }) => (
              <FormItem><FormLabel>Notes (optional)</FormLabel>
                <FormControl><Input className="thin-border" {...field} /></FormControl>
                <FormMessage />
              </FormItem>
            )} />
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>Cancel</Button>
              <Button type="submit" disabled={create.isPending}>{create.isPending ? "Creating..." : "Create Order"}</Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}

export default function OrdersPage() {
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [search, setSearch] = useState("")
  const [open, setOpen] = useState(false)

  const { data, isLoading } = useOrders({ page, page_size: pageSize, search, ordering: "-order_date" })
  const confirmOrder = useConfirmOrder()
  const markInProduction = useMarkOrderInProduction()
  const markReady = useMarkOrderReady()
  const cancelOrder = useCancelOrder()

  const handleAction = async (action: "confirm" | "in_production" | "ready" | "cancel", order: Order) => {
    const labels = {
      confirm: "confirmed",
      in_production: "moved to production",
      ready: "marked ready",
      cancel: "cancelled",
    }
    try {
      if (action === "confirm") await confirmOrder.mutateAsync(order.id)
      else if (action === "in_production") await markInProduction.mutateAsync(order.id)
      else if (action === "ready") await markReady.mutateAsync(order.id)
      else if (action === "cancel") await cancelOrder.mutateAsync(order.id)
      toast.success(`Order ${order.order_number} ${labels[action]}`)
    } catch {
      toast.error("Action failed. Please try again.")
    }
  }

  const columns = [
    {
      key: "order_number",
      label: "Order #",
      render: (order: Order) => <span className="font-medium">{order.order_number}</span>,
    },
    { key: "customer_name", label: "Customer" },
    {
      key: "order_date",
      label: "Order Date",
      render: (order: Order) => format(new Date(order.order_date), "MMM d, yyyy"),
    },
    {
      key: "expected_delivery_date",
      label: "Delivery Date",
      render: (order: Order) =>
        order.expected_delivery_date ? format(new Date(order.expected_delivery_date), "MMM d, yyyy") : "-",
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
    {
      key: "actions",
      label: "",
      render: (order: Order) => {
        const canConfirm = order.status === "draft"
        const canProduction = order.status === "confirmed"
        const canReady = order.status === "in_production"
        const canCancel = !["delivered", "cancelled"].includes(order.status)

        if (!canConfirm && !canProduction && !canReady && !canCancel) return null

        return (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="sm" className="h-7 w-7 p-0">
                <ChevronRight className="w-4 h-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              {canConfirm && (
                <DropdownMenuItem onClick={() => handleAction("confirm", order)}>Confirm Order</DropdownMenuItem>
              )}
              {canProduction && (
                <DropdownMenuItem onClick={() => handleAction("in_production", order)}>
                  Mark In Production
                </DropdownMenuItem>
              )}
              {canReady && (
                <DropdownMenuItem onClick={() => handleAction("ready", order)}>Mark Ready</DropdownMenuItem>
              )}
              {canCancel && (
                <>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem
                    className="text-destructive focus:text-destructive"
                    onClick={() => handleAction("cancel", order)}
                  >
                    Cancel Order
                  </DropdownMenuItem>
                </>
              )}
            </DropdownMenuContent>
          </DropdownMenu>
        )
      },
    },
  ]

  return (
    <div>
      <PageHeader
        title="Sales Orders"
        description="Manage customer orders and fulfilment"
        action={
          <Button onClick={() => setOpen(true)}>
            <Plus className="w-4 h-4 mr-2" />
            New Order
          </Button>
        }
      />

      <DataTable
        columns={columns}
        data={data?.results || []}
        loading={isLoading}
        searchPlaceholder="Search orders..."
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
      <NewOrderDialog open={open} onOpenChange={setOpen} />
    </div>
  )
}
