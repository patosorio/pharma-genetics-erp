"use client"

import { useState } from "react"
import { Plus, AlertTriangle } from "lucide-react"
import { toast } from "sonner"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { useInventoryAlerts, useLowStockAlerts, useCreateInventoryAlert } from "@/hooks/use-inventory-reports"
import { useStrains } from "@/hooks/use-strains"
import { useLocations } from "@/hooks/use-locations"
import { PageHeader } from "@/components/layout/page-header"
import { DataTable } from "@/components/common/data-table"
import { StatusBadge } from "@/components/common/status-badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog"
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import type { InventoryAlert } from "@/lib/types/inventory"

const schema = z.object({
  strain: z.coerce.number({ required_error: "Strain is required" }),
  location: z.coerce.number({ required_error: "Location is required" }),
  reorder_point: z.coerce.number().min(0, "Must be 0 or more"),
  alert_email: z.string().email("Invalid email").optional().or(z.literal("")),
})
type FormValues = z.infer<typeof schema>

function AddAlertDialog({ open, onOpenChange }: { open: boolean; onOpenChange: (v: boolean) => void }) {
  const create = useCreateInventoryAlert()
  const { data: strains } = useStrains({ page_size: 200, is_active: true })
  const { data: locations } = useLocations({ page_size: 100 })
  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { reorder_point: 50, alert_email: "" },
  })

  const onSubmit = async (values: FormValues) => {
    try {
      await create.mutateAsync(values)
      toast.success("Inventory alert configured")
      form.reset()
      onOpenChange(false)
    } catch {
      toast.error("Failed to add alert.")
    }
  }

  return (
    <Dialog open={open} onOpenChange={(v) => { if (!v) form.reset(); onOpenChange(v) }}>
      <DialogContent>
        <DialogHeader><DialogTitle>Add Inventory Alert</DialogTitle></DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <FormField control={form.control} name="strain" render={({ field }) => (
                <FormItem><FormLabel>Strain</FormLabel>
                  <Select onValueChange={(v) => field.onChange(Number(v))} value={field.value?.toString() ?? ""}>
                    <FormControl><SelectTrigger className="thin-border"><SelectValue placeholder="Select strain" /></SelectTrigger></FormControl>
                    <SelectContent>
                      {strains?.results.map((s) => <SelectItem key={s.id} value={s.id.toString()}>{s.name}</SelectItem>)}
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )} />
              <FormField control={form.control} name="location" render={({ field }) => (
                <FormItem><FormLabel>Location</FormLabel>
                  <Select onValueChange={(v) => field.onChange(Number(v))} value={field.value?.toString() ?? ""}>
                    <FormControl><SelectTrigger className="thin-border"><SelectValue placeholder="Select location" /></SelectTrigger></FormControl>
                    <SelectContent>
                      {locations?.results.map((l) => <SelectItem key={l.id} value={l.id.toString()}>{l.code} — {l.name}</SelectItem>)}
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )} />
            </div>
            <FormField control={form.control} name="reorder_point" render={({ field }) => (
              <FormItem><FormLabel>Reorder Point (units)</FormLabel>
                <FormControl><Input type="number" min={0} className="thin-border" {...field} /></FormControl>
                <FormMessage />
              </FormItem>
            )} />
            <FormField control={form.control} name="alert_email" render={({ field }) => (
              <FormItem><FormLabel>Alert Email (optional)</FormLabel>
                <FormControl><Input type="email" className="thin-border" placeholder="notify@company.com" {...field} /></FormControl>
                <FormMessage />
              </FormItem>
            )} />
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>Cancel</Button>
              <Button type="submit" disabled={create.isPending}>{create.isPending ? "Saving..." : "Add Alert"}</Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}

export default function InventoryAlertsPage() {
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [search, setSearch] = useState("")
  const [open, setOpen] = useState(false)

  const { data, isLoading } = useInventoryAlerts({ page, page_size: pageSize, search })
  const { data: lowStock } = useLowStockAlerts()

  const columns = [
    { key: "strain_name", label: "Strain", render: (alert: InventoryAlert) => <span className="font-medium">{alert.strain_name}</span> },
    { key: "location_code", label: "Location" },
    {
      key: "current_stock",
      label: "Current Stock",
      render: (alert: InventoryAlert) => (
        <span className={`data-value font-medium ${alert.is_low_stock ? "text-[#A65D57]" : ""}`}>{alert.current_stock}</span>
      ),
    },
    { key: "reorder_point", label: "Reorder Point", render: (alert: InventoryAlert) => <span className="data-value">{alert.reorder_point}</span> },
    {
      key: "stock_deficit",
      label: "Deficit",
      render: (alert: InventoryAlert) =>
        alert.stock_deficit > 0 ? (
          <span className="data-value text-[#A65D57] font-medium">{alert.stock_deficit}</span>
        ) : <span className="text-muted-foreground">—</span>,
    },
    {
      key: "is_low_stock",
      label: "Low Stock",
      render: (alert: InventoryAlert) =>
        alert.is_low_stock ? (
          <div className="flex items-center gap-1 text-[#A65D57]">
            <AlertTriangle className="w-3 h-3" />
            <span className="text-xs font-medium">Low Stock</span>
          </div>
        ) : <span className="text-[#4A7C59] text-xs font-medium">OK</span>,
    },
    { key: "is_active", label: "Alert Active", render: (alert: InventoryAlert) => <StatusBadge status={alert.is_active ? "Active" : "Inactive"} /> },
    { key: "alert_email", label: "Alert Email", render: (alert: InventoryAlert) => <span className="text-muted-foreground text-sm">{alert.alert_email ?? "—"}</span> },
  ]

  return (
    <div>
      <PageHeader
        title="Inventory Alerts"
        description="Configure reorder points and monitor low stock levels"
        action={<Button onClick={() => setOpen(true)}><Plus className="w-4 h-4 mr-2" />Add Alert</Button>}
      />

      {(lowStock?.length ?? 0) > 0 && (
        <Card className="thin-border mb-6 border-[#A65D57]/30 bg-[#A65D57]/5">
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-[#A65D57]" />
              <span className="text-sm font-medium text-[#A65D57]">
                {lowStock?.length} strain{(lowStock?.length ?? 0) !== 1 ? "s" : ""} below reorder point
              </span>
            </div>
          </CardContent>
        </Card>
      )}

      <DataTable columns={columns} data={data?.results || []} loading={isLoading} searchPlaceholder="Search alerts..." onSearch={setSearch} emptyMessage="No inventory alerts configured"
        pagination={data ? { currentPage: page, totalPages: Math.ceil(data.count / pageSize), pageSize, totalItems: data.count, onPageChange: setPage, onPageSizeChange: setPageSize } : undefined}
      />
      <AddAlertDialog open={open} onOpenChange={setOpen} />
    </div>
  )
}
