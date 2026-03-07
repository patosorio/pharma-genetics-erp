"use client"

import { useState } from "react"
import { Plus, ChevronRight } from "lucide-react"
import { format } from "date-fns"
import { toast } from "sonner"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { useDeliveryNotes, useCreateDeliveryNote, useMarkDeliveryNoteInTransit, useMarkDeliveryNoteDelivered } from "@/hooks/use-delivery-notes"
import { useOrders } from "@/hooks/use-orders"
import { useLocations } from "@/hooks/use-locations"
import { PageHeader } from "@/components/layout/page-header"
import { DataTable } from "@/components/common/data-table"
import { DeliveryNoteStatusBadge } from "@/components/sales/delivery-note-status-badge"
import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog"
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import type { DeliveryNote } from "@/lib/types/sales"

const dnSchema = z.object({
  order: z.coerce.number({ required_error: "Order is required" }),
  delivery_date: z.string().min(1, "Delivery date is required"),
  delivery_location: z.coerce.number({ required_error: "Location is required" }),
  delivered_by: z.string().optional(),
  received_by: z.string().optional(),
  notes: z.string().optional(),
})
type DNFormValues = z.infer<typeof dnSchema>

function NewDeliveryNoteDialog({ open, onOpenChange }: { open: boolean; onOpenChange: (v: boolean) => void }) {
  const create = useCreateDeliveryNote()
  const { data: orders } = useOrders({ page_size: 200, status: "ready" })
  const { data: locations } = useLocations({ page_size: 100 })
  const form = useForm<DNFormValues>({
    resolver: zodResolver(dnSchema),
    defaultValues: { delivery_date: new Date().toISOString().split("T")[0], delivered_by: "", received_by: "", notes: "" },
  })

  const onSubmit = async (values: DNFormValues) => {
    try {
      await create.mutateAsync(values)
      toast.success("Delivery note created")
      form.reset()
      onOpenChange(false)
    } catch {
      toast.error("Failed to create delivery note.")
    }
  }

  return (
    <Dialog open={open} onOpenChange={(v) => { if (!v) form.reset(); onOpenChange(v) }}>
      <DialogContent>
        <DialogHeader><DialogTitle>New Delivery Note</DialogTitle></DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField control={form.control} name="order" render={({ field }) => (
              <FormItem><FormLabel>Order</FormLabel>
                <Select onValueChange={(v) => field.onChange(Number(v))} value={field.value?.toString() ?? ""}>
                  <FormControl><SelectTrigger className="thin-border"><SelectValue placeholder="Select order" /></SelectTrigger></FormControl>
                  <SelectContent>
                    {orders?.results.map((o) => <SelectItem key={o.id} value={o.id.toString()}>{o.order_number} — {o.customer_name}</SelectItem>)}
                  </SelectContent>
                </Select>
                <FormMessage />
              </FormItem>
            )} />
            <div className="grid grid-cols-2 gap-4">
              <FormField control={form.control} name="delivery_date" render={({ field }) => (
                <FormItem><FormLabel>Delivery Date</FormLabel>
                  <FormControl><Input type="date" className="thin-border" {...field} /></FormControl>
                  <FormMessage />
                </FormItem>
              )} />
              <FormField control={form.control} name="delivery_location" render={({ field }) => (
                <FormItem><FormLabel>Delivery Location</FormLabel>
                  <Select onValueChange={(v) => field.onChange(Number(v))} value={field.value?.toString() ?? ""}>
                    <FormControl><SelectTrigger className="thin-border"><SelectValue placeholder="Select" /></SelectTrigger></FormControl>
                    <SelectContent>
                      {locations?.results.map((l) => <SelectItem key={l.id} value={l.id.toString()}>{l.code} — {l.name}</SelectItem>)}
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )} />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <FormField control={form.control} name="delivered_by" render={({ field }) => (
                <FormItem><FormLabel>Delivered By (optional)</FormLabel>
                  <FormControl><Input className="thin-border" {...field} /></FormControl>
                  <FormMessage />
                </FormItem>
              )} />
              <FormField control={form.control} name="received_by" render={({ field }) => (
                <FormItem><FormLabel>Received By (optional)</FormLabel>
                  <FormControl><Input className="thin-border" {...field} /></FormControl>
                  <FormMessage />
                </FormItem>
              )} />
            </div>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>Cancel</Button>
              <Button type="submit" disabled={create.isPending}>{create.isPending ? "Creating..." : "Create Delivery Note"}</Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}

export default function DeliveriesPage() {
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [search, setSearch] = useState("")
  const [open, setOpen] = useState(false)

  const { data, isLoading } = useDeliveryNotes({
    page,
    page_size: pageSize,
    search,
    ordering: "-delivery_date",
  })
  const markInTransit = useMarkDeliveryNoteInTransit()
  const markDelivered = useMarkDeliveryNoteDelivered()

  const handleAction = async (action: "in_transit" | "delivered", note: DeliveryNote) => {
    try {
      if (action === "in_transit") await markInTransit.mutateAsync(note.id)
      else await markDelivered.mutateAsync(note.id)
      toast.success(
        `Delivery note ${note.delivery_note_number} ${action === "in_transit" ? "marked in transit" : "marked delivered"}`,
      )
    } catch {
      toast.error("Action failed. Please try again.")
    }
  }

  const columns = [
    {
      key: "delivery_note_number",
      label: "Note #",
      render: (note: DeliveryNote) => <span className="font-medium">{note.delivery_note_number}</span>,
    },
    {
      key: "order_number",
      label: "Order",
      render: (note: DeliveryNote) => note.order_number,
    },
    {
      key: "delivery_date",
      label: "Delivery Date",
      render: (note: DeliveryNote) => format(new Date(note.delivery_date), "MMM d, yyyy"),
    },
    {
      key: "delivery_location_code",
      label: "Location",
    },
    {
      key: "delivered_by",
      label: "Delivered By",
      render: (note: DeliveryNote) => note.delivered_by ?? "-",
    },
    {
      key: "received_by",
      label: "Received By",
      render: (note: DeliveryNote) => note.received_by ?? "-",
    },
    {
      key: "status",
      label: "Status",
      render: (note: DeliveryNote) => <DeliveryNoteStatusBadge status={note.status} />,
    },
    {
      key: "actions",
      label: "",
      render: (note: DeliveryNote) => {
        const canTransit = note.status === "draft"
        const canDeliver = note.status === "in_transit"
        if (!canTransit && !canDeliver) return null

        return (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="sm" className="h-7 w-7 p-0">
                <ChevronRight className="w-4 h-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              {canTransit && (
                <DropdownMenuItem onClick={() => handleAction("in_transit", note)}>Mark In Transit</DropdownMenuItem>
              )}
              {canDeliver && (
                <DropdownMenuItem onClick={() => handleAction("delivered", note)}>Mark Delivered</DropdownMenuItem>
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
        title="Delivery Notes"
        description="Track deliveries and shipments for customer orders"
        action={
          <Button onClick={() => setOpen(true)}>
            <Plus className="w-4 h-4 mr-2" />
            New Delivery Note
          </Button>
        }
      />

      <DataTable
        columns={columns}
        data={data?.results || []}
        loading={isLoading}
        searchPlaceholder="Search delivery notes..."
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
      <NewDeliveryNoteDialog open={open} onOpenChange={setOpen} />
    </div>
  )
}
