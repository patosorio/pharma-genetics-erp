"use client"

import { useState } from "react"
import { Plus } from "lucide-react"
import { format } from "date-fns"
import { toast } from "sonner"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { useProductionAssumptions, useCreateProductionAssumption } from "@/hooks/use-cultivation"
import { useLocations } from "@/hooks/use-locations"
import { PageHeader } from "@/components/layout/page-header"
import { DataTable } from "@/components/common/data-table"
import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog"
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import type { ProductionAssumption } from "@/lib/types/cultivation"

const schema = z.object({
  location: z.coerce.number({ required_error: "Location is required" }),
  effective_date: z.string().min(1, "Effective date is required"),
  mother_plants_count: z.coerce.number().min(1),
  clones_per_mother_per_cycle: z.coerce.number().min(1),
  cycle_duration_days: z.coerce.number().min(1),
  survival_rate_pct: z.string().min(1, "Survival rate is required"),
  ramp_up_months: z.coerce.number().min(0).default(0),
  target_capacity_utilization_pct: z.string().default("100.00"),
  annual_cycles: z.coerce.number().min(1),
})
type FormValues = z.infer<typeof schema>

function AddAssumptionsDialog({ open, onOpenChange }: { open: boolean; onOpenChange: (v: boolean) => void }) {
  const create = useCreateProductionAssumption()
  const { data: locations } = useLocations({ page_size: 100 })
  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      effective_date: "",
      mother_plants_count: 10,
      clones_per_mother_per_cycle: 20,
      cycle_duration_days: 21,
      survival_rate_pct: "85.00",
      ramp_up_months: 0,
      target_capacity_utilization_pct: "100.00",
      annual_cycles: 12,
    },
  })

  const onSubmit = async (values: FormValues) => {
    try {
      await create.mutateAsync(values)
      toast.success("Production assumptions saved")
      form.reset()
      onOpenChange(false)
    } catch {
      toast.error("Failed to save assumptions.")
    }
  }

  return (
    <Dialog open={open} onOpenChange={(v) => { if (!v) form.reset(); onOpenChange(v) }}>
      <DialogContent className="max-w-lg">
        <DialogHeader><DialogTitle>Add Production Assumptions</DialogTitle></DialogHeader>
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
              <FormField control={form.control} name="mother_plants_count" render={({ field }) => (
                <FormItem><FormLabel>Mother Plants</FormLabel>
                  <FormControl><Input type="number" min={1} className="thin-border" {...field} /></FormControl>
                  <FormMessage />
                </FormItem>
              )} />
              <FormField control={form.control} name="clones_per_mother_per_cycle" render={({ field }) => (
                <FormItem><FormLabel>Clones / Mother</FormLabel>
                  <FormControl><Input type="number" min={1} className="thin-border" {...field} /></FormControl>
                  <FormMessage />
                </FormItem>
              )} />
              <FormField control={form.control} name="cycle_duration_days" render={({ field }) => (
                <FormItem><FormLabel>Cycle Days</FormLabel>
                  <FormControl><Input type="number" min={1} className="thin-border" {...field} /></FormControl>
                  <FormMessage />
                </FormItem>
              )} />
            </div>
            <div className="grid grid-cols-3 gap-4">
              <FormField control={form.control} name="survival_rate_pct" render={({ field }) => (
                <FormItem><FormLabel>Survival Rate %</FormLabel>
                  <FormControl><Input className="thin-border" placeholder="85.00" {...field} /></FormControl>
                  <FormMessage />
                </FormItem>
              )} />
              <FormField control={form.control} name="annual_cycles" render={({ field }) => (
                <FormItem><FormLabel>Annual Cycles</FormLabel>
                  <FormControl><Input type="number" min={1} className="thin-border" {...field} /></FormControl>
                  <FormMessage />
                </FormItem>
              )} />
              <FormField control={form.control} name="ramp_up_months" render={({ field }) => (
                <FormItem><FormLabel>Ramp-up Months</FormLabel>
                  <FormControl><Input type="number" min={0} className="thin-border" {...field} /></FormControl>
                  <FormMessage />
                </FormItem>
              )} />
            </div>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>Cancel</Button>
              <Button type="submit" disabled={create.isPending}>{create.isPending ? "Saving..." : "Add Assumptions"}</Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}

export default function ProductionAssumptionsPage() {
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [search, setSearch] = useState("")
  const [open, setOpen] = useState(false)

  const { data, isLoading } = useProductionAssumptions({ page, page_size: pageSize })

  const columns = [
    { key: "location_code", label: "Location", render: (a: ProductionAssumption) => <span className="font-medium">{a.location_code}</span> },
    { key: "version", label: "Version", render: (a: ProductionAssumption) => <span className="data-value">v{a.version}</span> },
    { key: "effective_date", label: "Effective Date", render: (a: ProductionAssumption) => format(new Date(a.effective_date), "MMM d, yyyy") },
    { key: "mother_plants_count", label: "Mother Plants", render: (a: ProductionAssumption) => <span className="data-value">{a.mother_plants_count}</span> },
    { key: "clones_per_mother_per_cycle", label: "Clones / Mother / Cycle", render: (a: ProductionAssumption) => <span className="data-value">{a.clones_per_mother_per_cycle}</span> },
    { key: "cycle_duration_days", label: "Cycle (days)", render: (a: ProductionAssumption) => <span className="data-value">{a.cycle_duration_days}</span> },
    { key: "survival_rate_pct", label: "Survival Rate", render: (a: ProductionAssumption) => <span className="data-value">{Number.parseFloat(a.survival_rate_pct).toFixed(1)}%</span> },
    { key: "max_monthly_capacity", label: "Max Monthly Capacity", render: (a: ProductionAssumption) => <span className="data-value font-medium">{a.max_monthly_capacity.toLocaleString()}</span> },
    { key: "annual_cycles", label: "Annual Cycles", render: (a: ProductionAssumption) => <span className="data-value">{a.annual_cycles}</span> },
  ]

  return (
    <div>
      <PageHeader
        title="Production Assumptions"
        description="Configure capacity and yield assumptions for each location"
        action={<Button onClick={() => setOpen(true)}><Plus className="w-4 h-4 mr-2" />Add Assumptions</Button>}
      />
      <DataTable columns={columns} data={data?.results || []} loading={isLoading} searchPlaceholder="Search assumptions..." onSearch={setSearch} emptyMessage="No production assumptions configured"
        pagination={data ? { currentPage: page, totalPages: Math.ceil(data.count / pageSize), pageSize, totalItems: data.count, onPageChange: setPage, onPageSizeChange: setPageSize } : undefined}
      />
      <AddAssumptionsDialog open={open} onOpenChange={setOpen} />
    </div>
  )
}
