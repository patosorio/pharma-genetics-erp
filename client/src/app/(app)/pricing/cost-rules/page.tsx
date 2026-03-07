"use client"

import { useState } from "react"
import { Plus } from "lucide-react"
import { format } from "date-fns"
import { toast } from "sonner"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { useCostAllocationRules, useCreateCostAllocationRule } from "@/hooks/use-pricing"
import { useLocations } from "@/hooks/use-locations"
import { PageHeader } from "@/components/layout/page-header"
import { DataTable } from "@/components/common/data-table"
import { StatusBadge } from "@/components/common/status-badge"
import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog"
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import type { CostAllocationRule } from "@/lib/types/pricing"

const schema = z.object({
  location: z.coerce.number({ required_error: "Location is required" }),
  effective_date: z.string().min(1, "Effective date is required"),
  monthly_capacity_clones: z.coerce.number().min(1),
  mother_plant_lifecycle_days: z.coerce.number().min(1).default(365),
  expected_clones_per_mother_lifecycle: z.coerce.number().min(1).default(100),
  cost_per_mother_plant: z.string().default("0.00"),
  labour_cost_per_clone: z.string().default("0.00"),
  overhead_allocation_pct: z.string().default("0.00"),
})
type FormValues = z.infer<typeof schema>

function AddRuleDialog({ open, onOpenChange }: { open: boolean; onOpenChange: (v: boolean) => void }) {
  const create = useCreateCostAllocationRule()
  const { data: locations } = useLocations({ page_size: 100 })
  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      effective_date: new Date().toISOString().split("T")[0],
      monthly_capacity_clones: 1000,
      mother_plant_lifecycle_days: 365,
      expected_clones_per_mother_lifecycle: 100,
      cost_per_mother_plant: "0.00",
      labour_cost_per_clone: "0.00",
      overhead_allocation_pct: "0.00",
    },
  })

  const onSubmit = async (values: FormValues) => {
    try {
      await create.mutateAsync(values)
      toast.success("Cost allocation rule added")
      form.reset()
      onOpenChange(false)
    } catch {
      toast.error("Failed to add rule.")
    }
  }

  return (
    <Dialog open={open} onOpenChange={(v) => { if (!v) form.reset(); onOpenChange(v) }}>
      <DialogContent className="max-w-lg">
        <DialogHeader><DialogTitle>Add Cost Allocation Rule</DialogTitle></DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
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
              <FormField control={form.control} name="effective_date" render={({ field }) => (
                <FormItem><FormLabel>Effective Date</FormLabel>
                  <FormControl><Input type="date" className="thin-border" {...field} /></FormControl>
                  <FormMessage />
                </FormItem>
              )} />
            </div>
            <div className="grid grid-cols-3 gap-4">
              <FormField control={form.control} name="monthly_capacity_clones" render={({ field }) => (
                <FormItem><FormLabel>Monthly Capacity</FormLabel>
                  <FormControl><Input type="number" min={1} className="thin-border" {...field} /></FormControl>
                  <FormMessage />
                </FormItem>
              )} />
              <FormField control={form.control} name="mother_plant_lifecycle_days" render={({ field }) => (
                <FormItem><FormLabel>Mother Lifecycle Days</FormLabel>
                  <FormControl><Input type="number" min={1} className="thin-border" {...field} /></FormControl>
                  <FormMessage />
                </FormItem>
              )} />
              <FormField control={form.control} name="expected_clones_per_mother_lifecycle" render={({ field }) => (
                <FormItem><FormLabel>Clones / Mother Life</FormLabel>
                  <FormControl><Input type="number" min={1} className="thin-border" {...field} /></FormControl>
                  <FormMessage />
                </FormItem>
              )} />
            </div>
            <div className="grid grid-cols-3 gap-4">
              <FormField control={form.control} name="cost_per_mother_plant" render={({ field }) => (
                <FormItem><FormLabel>Cost / Mother (฿)</FormLabel>
                  <FormControl><Input className="thin-border" placeholder="0.00" {...field} /></FormControl>
                  <FormMessage />
                </FormItem>
              )} />
              <FormField control={form.control} name="labour_cost_per_clone" render={({ field }) => (
                <FormItem><FormLabel>Labour / Clone (฿)</FormLabel>
                  <FormControl><Input className="thin-border" placeholder="0.00" {...field} /></FormControl>
                  <FormMessage />
                </FormItem>
              )} />
              <FormField control={form.control} name="overhead_allocation_pct" render={({ field }) => (
                <FormItem><FormLabel>Overhead %</FormLabel>
                  <FormControl><Input className="thin-border" placeholder="0.00" {...field} /></FormControl>
                  <FormMessage />
                </FormItem>
              )} />
            </div>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>Cancel</Button>
              <Button type="submit" disabled={create.isPending}>{create.isPending ? "Saving..." : "Add Rule"}</Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}

export default function CostRulesPage() {
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [search, setSearch] = useState("")
  const [open, setOpen] = useState(false)

  const { data, isLoading } = useCostAllocationRules({ page, page_size: pageSize })

  const columns = [
    { key: "location_code", label: "Location", render: (r: CostAllocationRule) => <span className="font-medium">{r.location_code}</span> },
    { key: "effective_date", label: "Effective", render: (r: CostAllocationRule) => format(new Date(r.effective_date), "MMM d, yyyy") },
    { key: "end_date", label: "Expires", render: (r: CostAllocationRule) => (r.end_date ? format(new Date(r.end_date), "MMM d, yyyy") : "—") },
    { key: "monthly_capacity_clones", label: "Monthly Capacity", render: (r: CostAllocationRule) => <span className="data-value">{r.monthly_capacity_clones.toLocaleString()} clones</span> },
    { key: "mother_plant_lifecycle_days", label: "Mother Lifecycle", render: (r: CostAllocationRule) => <span className="data-value">{r.mother_plant_lifecycle_days} days</span> },
    { key: "expected_clones_per_mother_lifecycle", label: "Clones / Mother Life", render: (r: CostAllocationRule) => <span className="data-value">{r.expected_clones_per_mother_lifecycle}</span> },
    { key: "is_active", label: "Status", render: (r: CostAllocationRule) => <StatusBadge status={r.is_active ? "Active" : "Inactive"} /> },
  ]

  return (
    <div>
      <PageHeader
        title="Cost Allocation Rules"
        description="Configure how costs are allocated across locations and departments"
        action={<Button onClick={() => setOpen(true)}><Plus className="w-4 h-4 mr-2" />Add Rule</Button>}
      />
      <DataTable columns={columns} data={data?.results || []} loading={isLoading} searchPlaceholder="Search rules..." onSearch={setSearch} emptyMessage="No cost allocation rules configured"
        pagination={data ? { currentPage: page, totalPages: Math.ceil(data.count / pageSize), pageSize, totalItems: data.count, onPageChange: setPage, onPageSizeChange: setPageSize } : undefined}
      />
      <AddRuleDialog open={open} onOpenChange={setOpen} />
    </div>
  )
}
