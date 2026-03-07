"use client"

import { useState } from "react"
import { Plus, Heart } from "lucide-react"
import { format } from "date-fns"
import { toast } from "sonner"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { useMotherPlants, useCreateMotherPlant } from "@/hooks/use-cultivation"
import { useStrains } from "@/hooks/use-strains"
import { useLocations } from "@/hooks/use-locations"
import { PageHeader } from "@/components/layout/page-header"
import { DataTable } from "@/components/common/data-table"
import { MotherPlantStatusBadge } from "@/components/cultivation/mother-plant-status-badge"
import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog"
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import type { MotherPlant } from "@/lib/types/cultivation"

const schema = z.object({
  strain: z.coerce.number({ required_error: "Strain is required" }),
  location: z.coerce.number({ required_error: "Location is required" }),
  status: z.string().min(1),
  health_grade: z.enum(["A", "B", "C", "D"]),
  cultivation_date: z.string().min(1, "Cultivation date is required"),
  expected_ready_date: z.string().min(1, "Expected ready date is required"),
  expected_retirement_date: z.string().min(1, "Expected retirement date is required"),
})
type FormValues = z.infer<typeof schema>

function AddMotherPlantDialog({ open, onOpenChange }: { open: boolean; onOpenChange: (v: boolean) => void }) {
  const create = useCreateMotherPlant()
  const { data: strains } = useStrains({ page_size: 200, is_active: true })
  const { data: locations } = useLocations({ page_size: 100 })
  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { status: "Growing", health_grade: "A", cultivation_date: "", expected_ready_date: "", expected_retirement_date: "" },
  })

  const onSubmit = async (values: FormValues) => {
    try {
      await create.mutateAsync(values)
      toast.success("Mother plant added")
      form.reset()
      onOpenChange(false)
    } catch {
      toast.error("Failed to add mother plant.")
    }
  }

  return (
    <Dialog open={open} onOpenChange={(v) => { if (!v) form.reset(); onOpenChange(v) }}>
      <DialogContent>
        <DialogHeader><DialogTitle>Add Mother Plant</DialogTitle></DialogHeader>
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
            <div className="grid grid-cols-2 gap-4">
              <FormField control={form.control} name="status" render={({ field }) => (
                <FormItem><FormLabel>Status</FormLabel>
                  <Select onValueChange={field.onChange} value={field.value}>
                    <FormControl><SelectTrigger className="thin-border"><SelectValue /></SelectTrigger></FormControl>
                    <SelectContent>
                      <SelectItem value="Growing">Growing</SelectItem>
                      <SelectItem value="Active_Production">Active Production</SelectItem>
                      <SelectItem value="Recovery">Recovery</SelectItem>
                      <SelectItem value="Low_Production">Low Production</SelectItem>
                      <SelectItem value="Quarantine">Quarantine</SelectItem>
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )} />
              <FormField control={form.control} name="health_grade" render={({ field }) => (
                <FormItem><FormLabel>Health Grade</FormLabel>
                  <Select onValueChange={field.onChange} value={field.value}>
                    <FormControl><SelectTrigger className="thin-border"><SelectValue /></SelectTrigger></FormControl>
                    <SelectContent>
                      <SelectItem value="A">A — Excellent</SelectItem>
                      <SelectItem value="B">B — Good</SelectItem>
                      <SelectItem value="C">C — Fair</SelectItem>
                      <SelectItem value="D">D — Poor</SelectItem>
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )} />
            </div>
            <FormField control={form.control} name="cultivation_date" render={({ field }) => (
              <FormItem><FormLabel>Cultivation Date</FormLabel>
                <FormControl><Input type="date" className="thin-border" {...field} /></FormControl>
                <FormMessage />
              </FormItem>
            )} />
            <div className="grid grid-cols-2 gap-4">
              <FormField control={form.control} name="expected_ready_date" render={({ field }) => (
                <FormItem><FormLabel>Expected Ready</FormLabel>
                  <FormControl><Input type="date" className="thin-border" {...field} /></FormControl>
                  <FormMessage />
                </FormItem>
              )} />
              <FormField control={form.control} name="expected_retirement_date" render={({ field }) => (
                <FormItem><FormLabel>Expected Retirement</FormLabel>
                  <FormControl><Input type="date" className="thin-border" {...field} /></FormControl>
                  <FormMessage />
                </FormItem>
              )} />
            </div>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>Cancel</Button>
              <Button type="submit" disabled={create.isPending}>{create.isPending ? "Saving..." : "Add Mother Plant"}</Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}

export default function MotherPlantsPage() {
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [search, setSearch] = useState("")
  const [open, setOpen] = useState(false)

  const { data, isLoading } = useMotherPlants({ page, page_size: pageSize, search })

  const columns = [
    {
      key: "code",
      label: "Plant Code",
      render: (plant: MotherPlant) => (
        <div className="flex items-center gap-2">
          <Heart className="w-4 h-4 text-primary" />
          <span className="font-medium">{plant.code}</span>
        </div>
      ),
    },
    { key: "strain_name", label: "Strain" },
    { key: "location_code", label: "Location" },
    { key: "status", label: "Status", render: (plant: MotherPlant) => <MotherPlantStatusBadge status={plant.status} /> },
    {
      key: "health_grade",
      label: "Health",
      render: (plant: MotherPlant) => (
        <div className="flex items-center gap-2">
          <span className="font-medium">{plant.health_grade}</span>
          <span className="text-xs text-muted-foreground">({plant.health_grade_display})</span>
        </div>
      ),
    },
    { key: "total_cuttings_taken", label: "Total Cuts", render: (plant: MotherPlant) => <span className="data-value">{plant.total_cuttings_taken}</span> },
    { key: "last_cut_date", label: "Last Cut", render: (plant: MotherPlant) => plant.last_cut_date ? format(new Date(plant.last_cut_date), "MMM d, yyyy") : "-" },
  ]

  return (
    <div>
      <PageHeader
        title="Mother Plants"
        description="Manage mother plants for clone production"
        action={<Button onClick={() => setOpen(true)}><Plus className="w-4 h-4 mr-2" />Add Mother Plant</Button>}
      />
      <DataTable columns={columns} data={data?.results || []} loading={isLoading} searchPlaceholder="Search by code or strain..." onSearch={setSearch}
        pagination={data ? { currentPage: page, totalPages: Math.ceil(data.count / pageSize), pageSize, totalItems: data.count, onPageChange: setPage, onPageSizeChange: setPageSize } : undefined}
      />
      <AddMotherPlantDialog open={open} onOpenChange={setOpen} />
    </div>
  )
}
