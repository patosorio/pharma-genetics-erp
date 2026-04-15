"use client"

import { useState } from "react"
import { Plus } from "lucide-react"
import { format } from "date-fns"
import { toast } from "sonner"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { useInventoryAdjustments, useCreateInventoryAdjustment } from "@/hooks/use-inventory-reports"
import { useClones } from "@/hooks/use-cultivation"
import { PageHeader } from "@/components/layout/page-header"
import { DataTable } from "@/components/common/data-table"
import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog"
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import type { InventoryAdjustment } from "@/lib/types/inventory"

const REASONS = [
  "Dead / Diseased",
  "Lost / Missing",
  "Quality Downgrade",
  "Transferred Out",
  "Pest Damage",
  "Environmental Stress",
  "Other",
]

const schema = z.object({
  clone: z.coerce.number({ required_error: "Clone is required" }),
  adjustment_date: z.string().min(1, "Date is required"),
  reason: z.string().min(1, "Reason is required"),
  notes: z.string().optional(),
})
type FormValues = z.infer<typeof schema>

function NewAdjustmentDialog({ open, onOpenChange }: { open: boolean; onOpenChange: (v: boolean) => void }) {
  const create = useCreateInventoryAdjustment()
  const { data: clones } = useClones({ page_size: 200 })
  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { adjustment_date: new Date().toISOString().split("T")[0], reason: "", notes: "" },
  })

  const onSubmit = async (values: FormValues) => {
    try {
      await create.mutateAsync(values)
      toast.success("Adjustment recorded")
      form.reset()
      onOpenChange(false)
    } catch {
      toast.error("Failed to record adjustment.")
    }
  }

  return (
    <Dialog open={open} onOpenChange={(v) => { if (!v) form.reset(); onOpenChange(v) }}>
      <DialogContent>
        <DialogHeader><DialogTitle>New Inventory Adjustment</DialogTitle></DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField control={form.control} name="clone" render={({ field }) => (
              <FormItem><FormLabel>Clone</FormLabel>
                <Select onValueChange={(v) => field.onChange(Number(v))} value={field.value?.toString() ?? ""}>
                  <FormControl><SelectTrigger className="thin-border"><SelectValue placeholder="Select clone" /></SelectTrigger></FormControl>
                  <SelectContent>
                    {clones?.results.map((c) => <SelectItem key={c.id} value={c.id.toString()}>{c.code} — {c.strain_name}</SelectItem>)}
                  </SelectContent>
                </Select>
                <FormMessage />
              </FormItem>
            )} />
            <FormField control={form.control} name="adjustment_date" render={({ field }) => (
              <FormItem><FormLabel>Date</FormLabel>
                <FormControl><Input type="date" className="thin-border" {...field} /></FormControl>
                <FormMessage />
              </FormItem>
            )} />
            <FormField control={form.control} name="reason" render={({ field }) => (
              <FormItem><FormLabel>Reason</FormLabel>
                <Select onValueChange={field.onChange} value={field.value}>
                  <FormControl><SelectTrigger className="thin-border"><SelectValue placeholder="Select reason" /></SelectTrigger></FormControl>
                  <SelectContent>
                    {REASONS.map((r) => <SelectItem key={r} value={r}>{r}</SelectItem>)}
                  </SelectContent>
                </Select>
                <FormMessage />
              </FormItem>
            )} />
            <FormField control={form.control} name="notes" render={({ field }) => (
              <FormItem><FormLabel>Notes (optional)</FormLabel>
                <FormControl><Input className="thin-border" placeholder="Additional details..." {...field} /></FormControl>
                <FormMessage />
              </FormItem>
            )} />
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>Cancel</Button>
              <Button type="submit" disabled={create.isPending}>{create.isPending ? "Saving..." : "Record Adjustment"}</Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}

export default function InventoryAdjustmentsPage() {
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [search, setSearch] = useState("")
  const [open, setOpen] = useState(false)

  const { data, isLoading } = useInventoryAdjustments({ page, page_size: pageSize })

  const columns = [
    { key: "clone_code", label: "Clone", render: (adj: InventoryAdjustment) => <span className="font-medium">{adj.clone_code}</span> },
    { key: "adjustment_date", label: "Date", render: (adj: InventoryAdjustment) => format(new Date(adj.adjustment_date), "MMM d, yyyy") },
    { key: "reason", label: "Reason" },
    { key: "notes", label: "Notes", render: (adj: InventoryAdjustment) => <span className="text-muted-foreground text-sm line-clamp-1">{adj.notes}</span> },
    { key: "approved_by_name", label: "Approved By", render: (adj: InventoryAdjustment) => adj.approved_by_name ?? "—" },
    { key: "created_at", label: "Recorded", render: (adj: InventoryAdjustment) => format(new Date(adj.created_at), "MMM d, yyyy") },
  ]

  return (
    <div>
      <PageHeader
        title="Inventory Adjustments"
        description="Record and audit inventory write-offs and corrections"
        action={<Button onClick={() => setOpen(true)}><Plus className="w-4 h-4 mr-2" />New Adjustment</Button>}
      />
      <DataTable columns={columns} data={data?.results || []} loading={isLoading} searchPlaceholder="Search adjustments..." onSearch={setSearch} emptyMessage="No adjustments recorded"
        pagination={data ? { currentPage: page, totalPages: Math.ceil(data.count / pageSize), pageSize, totalItems: data.count, onPageChange: setPage, onPageSizeChange: setPageSize } : undefined}
      />
      <NewAdjustmentDialog open={open} onOpenChange={setOpen} />
    </div>
  )
}
