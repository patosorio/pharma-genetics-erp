"use client"

import { useState } from "react"
import { Plus, ChevronRight } from "lucide-react"
import { format } from "date-fns"
import { toast } from "sonner"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import {
  usePurchaseOrders,
  useCreatePurchaseOrder,
  useSendPurchaseOrder,
  useConfirmPurchaseOrder,
  useMarkDeliveredPurchaseOrder,
  useCancelPurchaseOrder,
  useSuppliers,
} from "@/hooks/use-purchasing"
import { useLocations } from "@/hooks/use-locations"
import { useCurrencies } from "@/hooks/use-currencies"
import { PageHeader } from "@/components/layout/page-header"
import { DataTable } from "@/components/common/data-table"
import { PurchaseOrderStatusBadge } from "@/components/purchasing/purchase-order-status-badge"
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
import type { PurchaseOrder } from "@/lib/types/purchasing"

const poSchema = z.object({
  supplier: z.coerce.number({ required_error: "Supplier is required" }),
  location: z.coerce.number({ required_error: "Location is required" }),
  order_date: z.string().min(1, "Order date is required"),
  expected_delivery_date: z.string().optional(),
  currency: z.coerce.number({ required_error: "Currency is required" }),
  notes: z.string().optional(),
})
type POFormValues = z.infer<typeof poSchema>

function NewPODialog({ open, onOpenChange }: { open: boolean; onOpenChange: (v: boolean) => void }) {
  const create = useCreatePurchaseOrder()
  const { data: suppliers } = useSuppliers({ page_size: 200 })
  const { data: locations } = useLocations({ page_size: 100 })
  const { data: currencies } = useCurrencies({ page_size: 50 })
  const form = useForm<POFormValues>({
    resolver: zodResolver(poSchema),
    defaultValues: { order_date: new Date().toISOString().split("T")[0], expected_delivery_date: "", notes: "" },
  })

  const onSubmit = async (values: POFormValues) => {
    try {
      await create.mutateAsync(values)
      toast.success("Purchase order created")
      form.reset()
      onOpenChange(false)
    } catch {
      toast.error("Failed to create purchase order.")
    }
  }

  return (
    <Dialog open={open} onOpenChange={(v) => { if (!v) form.reset(); onOpenChange(v) }}>
      <DialogContent>
        <DialogHeader><DialogTitle>New Purchase Order</DialogTitle></DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField control={form.control} name="supplier" render={({ field }) => (
              <FormItem><FormLabel>Supplier</FormLabel>
                <Select onValueChange={(v) => field.onChange(Number(v))} value={field.value?.toString() ?? ""}>
                  <FormControl><SelectTrigger className="thin-border"><SelectValue placeholder="Select supplier" /></SelectTrigger></FormControl>
                  <SelectContent>
                    {suppliers?.results.map((s) => <SelectItem key={s.id} value={s.id.toString()}>{s.contact_name}</SelectItem>)}
                  </SelectContent>
                </Select>
                <FormMessage />
              </FormItem>
            )} />
            <div className="grid grid-cols-2 gap-4">
              <FormField control={form.control} name="location" render={({ field }) => (
                <FormItem><FormLabel>Location</FormLabel>
                  <Select onValueChange={(v) => field.onChange(Number(v))} value={field.value?.toString() ?? ""}>
                    <FormControl><SelectTrigger className="thin-border"><SelectValue placeholder="Select" /></SelectTrigger></FormControl>
                    <SelectContent>
                      {locations?.results.map((l) => <SelectItem key={l.id} value={l.id.toString()}>{l.code} — {l.name}</SelectItem>)}
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )} />
              <FormField control={form.control} name="currency" render={({ field }) => (
                <FormItem><FormLabel>Currency</FormLabel>
                  <Select onValueChange={(v) => field.onChange(Number(v))} value={field.value?.toString() ?? ""}>
                    <FormControl><SelectTrigger className="thin-border"><SelectValue placeholder="Select" /></SelectTrigger></FormControl>
                    <SelectContent>
                      {currencies?.results.map((c) => <SelectItem key={c.id} value={c.id.toString()}>{c.code}</SelectItem>)}
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )} />
            </div>
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
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>Cancel</Button>
              <Button type="submit" disabled={create.isPending}>{create.isPending ? "Creating..." : "Create PO"}</Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}

export default function PurchaseOrdersPage() {
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [search, setSearch] = useState("")
  const [open, setOpen] = useState(false)

  const { data, isLoading } = usePurchaseOrders({ page, page_size: pageSize, search, ordering: "-order_date" })
  const sendPO = useSendPurchaseOrder()
  const confirmPO = useConfirmPurchaseOrder()
  const deliverPO = useMarkDeliveredPurchaseOrder()
  const cancelPO = useCancelPurchaseOrder()

  const handleAction = async (
    action: "send" | "confirm" | "deliver" | "cancel",
    po: PurchaseOrder,
  ) => {
    const labels = { send: "sent", confirm: "confirmed", deliver: "marked delivered", cancel: "cancelled" }
    try {
      if (action === "send") await sendPO.mutateAsync(po.id)
      else if (action === "confirm") await confirmPO.mutateAsync(po.id)
      else if (action === "deliver") await deliverPO.mutateAsync(po.id)
      else if (action === "cancel") await cancelPO.mutateAsync(po.id)
      toast.success(`PO ${po.po_number} ${labels[action]}`)
    } catch {
      toast.error("Action failed. Please try again.")
    }
  }

  const columns = [
    {
      key: "po_number",
      label: "PO #",
      render: (po: PurchaseOrder) => <span className="font-medium">{po.po_number}</span>,
    },
    { key: "supplier_name", label: "Supplier" },
    { key: "location_code", label: "Location" },
    {
      key: "order_date",
      label: "Order Date",
      render: (po: PurchaseOrder) => format(new Date(po.order_date), "MMM d, yyyy"),
    },
    {
      key: "expected_delivery_date",
      label: "Expected Delivery",
      render: (po: PurchaseOrder) =>
        po.expected_delivery_date ? format(new Date(po.expected_delivery_date), "MMM d, yyyy") : "—",
    },
    {
      key: "status",
      label: "Status",
      render: (po: PurchaseOrder) => <PurchaseOrderStatusBadge status={po.status} />,
    },
    {
      key: "total_amount",
      label: "Total",
      render: (po: PurchaseOrder) => (
        <span className="data-value font-medium">
          {po.currency_code} {Number.parseFloat(po.total_amount).toLocaleString()}
        </span>
      ),
    },
    {
      key: "actions",
      label: "",
      render: (po: PurchaseOrder) => {
        const canSend = po.status === "draft"
        const canConfirm = po.status === "sent"
        const canDeliver = po.status === "confirmed"
        const canCancel = !["delivered", "cancelled"].includes(po.status)
        if (!canSend && !canConfirm && !canDeliver && !canCancel) return null

        return (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="sm" className="h-7 w-7 p-0">
                <ChevronRight className="w-4 h-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              {canSend && <DropdownMenuItem onClick={() => handleAction("send", po)}>Send to Supplier</DropdownMenuItem>}
              {canConfirm && <DropdownMenuItem onClick={() => handleAction("confirm", po)}>Confirm Order</DropdownMenuItem>}
              {canDeliver && <DropdownMenuItem onClick={() => handleAction("deliver", po)}>Mark Delivered</DropdownMenuItem>}
              {canCancel && (
                <>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem
                    className="text-destructive focus:text-destructive"
                    onClick={() => handleAction("cancel", po)}
                  >
                    Cancel PO
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
        title="Purchase Orders"
        description="Manage supplier orders and procurement"
        action={
          <Button onClick={() => setOpen(true)}>
            <Plus className="w-4 h-4 mr-2" />
            New PO
          </Button>
        }
      />

      <DataTable
        columns={columns}
        data={data?.results || []}
        loading={isLoading}
        searchPlaceholder="Search purchase orders..."
        onSearch={setSearch}
        emptyMessage="No purchase orders found"
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
      <NewPODialog open={open} onOpenChange={setOpen} />
    </div>
  )
}
