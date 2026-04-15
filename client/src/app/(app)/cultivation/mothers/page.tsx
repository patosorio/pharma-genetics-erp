"use client"

import { useState } from "react"
import { Plus, Heart, Search } from "lucide-react"
import { format } from "date-fns"
import { toast } from "sonner"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import {
  useMotherPlants,
  useCreateMotherPlant,
  useUpdateMotherPlant,
  useDeleteMotherPlant,
  useBatchUpdateMotherPlantStatus,
} from "@/hooks/use-cultivation"
import { useStrains } from "@/hooks/use-strains"
import { useLocations } from "@/hooks/use-locations"
import { PageHeader } from "@/components/layout/page-header"
import { DataTable } from "@/components/common/data-table"
import { MotherPlantStatusBadge } from "@/components/cultivation/mother-plant-status-badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog"
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import type { MotherPlant } from "@/lib/types/cultivation"

const STATUSES = [
  { value: "Growing", label: "Growing" },
  { value: "Active_Production", label: "Active Production" },
  { value: "Recovery", label: "Recovery" },
  { value: "Low_Production", label: "Low Production" },
  { value: "Quarantine", label: "Quarantine" },
  { value: "Retired", label: "Retired" },
  { value: "Under_Treatment", label: "Under Treatment" },
]

const schema = z.object({
  strain: z.coerce.number({ required_error: "Strain is required" }),
  location: z.coerce.number({ required_error: "Location is required" }),
  status: z.enum(["Growing", "Active_Production", "Recovery", "Low_Production", "Quarantine", "Retired", "Under_Treatment"]),
  health_grade: z.enum(["A", "B", "C", "D"]),
  cultivation_date: z.string().min(1, "Cultivation date is required"),
  expected_ready_date: z.string().min(1, "Expected ready date is required"),
  expected_retirement_date: z.string().min(1, "Expected retirement date is required"),
  notes: z.string().optional(),
})
type FormValues = z.infer<typeof schema>

function MotherPlantForm({
  defaultValues,
  onSubmit,
  isPending,
  onCancel,
  submitLabel,
}: {
  defaultValues: Partial<FormValues>
  onSubmit: (values: FormValues) => void
  isPending: boolean
  onCancel: () => void
  submitLabel: string
}) {
  const { data: strains } = useStrains({ page_size: 200, is_active: true })
  const { data: locations } = useLocations({ page_size: 100 })
  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      status: "Growing",
      health_grade: "A",
      cultivation_date: "",
      expected_ready_date: "",
      expected_retirement_date: "",
      notes: "",
      ...defaultValues,
    },
  })

  return (
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
                  {STATUSES.map((s) => <SelectItem key={s.value} value={s.value}>{s.label}</SelectItem>)}
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
        <FormField control={form.control} name="notes" render={({ field }) => (
          <FormItem><FormLabel>Notes</FormLabel>
            <FormControl><Input className="thin-border" placeholder="Optional notes..." {...field} /></FormControl>
            <FormMessage />
          </FormItem>
        )} />
        <DialogFooter>
          <Button type="button" variant="outline" onClick={onCancel}>Cancel</Button>
          <Button type="submit" disabled={isPending}>{isPending ? "Saving..." : submitLabel}</Button>
        </DialogFooter>
      </form>
    </Form>
  )
}

function AddMotherPlantDialog({ open, onOpenChange }: { open: boolean; onOpenChange: (v: boolean) => void }) {
  const create = useCreateMotherPlant()
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader><DialogTitle>Add Mother Plant</DialogTitle></DialogHeader>
        <MotherPlantForm
          defaultValues={{}}
          onSubmit={async (values) => {
            try {
              await create.mutateAsync(values)
              toast.success("Mother plant added")
              onOpenChange(false)
            } catch { toast.error("Failed to add mother plant.") }
          }}
          isPending={create.isPending}
          onCancel={() => onOpenChange(false)}
          submitLabel="Add Mother Plant"
        />
      </DialogContent>
    </Dialog>
  )
}

function EditMotherPlantDialog({
  plant,
  open,
  onOpenChange,
}: {
  plant: MotherPlant
  open: boolean
  onOpenChange: (v: boolean) => void
}) {
  const update = useUpdateMotherPlant()
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader><DialogTitle>Edit {plant.code}</DialogTitle></DialogHeader>
        <MotherPlantForm
          defaultValues={{
            strain: plant.strain,
            location: plant.location,
            status: plant.status,
            health_grade: plant.health_grade,
            cultivation_date: plant.cultivation_date,
            expected_ready_date: plant.expected_ready_date,
            expected_retirement_date: plant.expected_retirement_date,
            notes: plant.notes ?? "",
          }}
          onSubmit={async (values) => {
            try {
              await update.mutateAsync({ id: plant.id, data: values })
              toast.success(`${plant.code} updated`)
              onOpenChange(false)
            } catch { toast.error("Failed to update mother plant.") }
          }}
          isPending={update.isPending}
          onCancel={() => onOpenChange(false)}
          submitLabel="Save Changes"
        />
      </DialogContent>
    </Dialog>
  )
}

function DeleteMotherPlantDialog({
  plant,
  open,
  onOpenChange,
}: {
  plant: MotherPlant
  open: boolean
  onOpenChange: (v: boolean) => void
}) {
  const deleteMutation = useDeleteMotherPlant()
  const handleDelete = async () => {
    try {
      await deleteMutation.mutateAsync(plant.id)
      toast.success(`${plant.code} deleted`)
      onOpenChange(false)
    } catch { toast.error("Failed to delete mother plant.") }
  }
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-sm">
        <DialogHeader><DialogTitle>Delete Mother Plant</DialogTitle></DialogHeader>
        <p className="text-sm text-muted-foreground">
          Delete <strong>{plant.code}</strong>? This action cannot be undone.
        </p>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>Cancel</Button>
          <Button variant="destructive" onClick={handleDelete} disabled={deleteMutation.isPending}>
            {deleteMutation.isPending ? "Deleting..." : "Delete"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

function BatchStatusDialog({
  ids,
  open,
  onOpenChange,
}: {
  ids: number[]
  open: boolean
  onOpenChange: (v: boolean) => void
}) {
  const [newStatus, setNewStatus] = useState("")
  const batchUpdate = useBatchUpdateMotherPlantStatus()

  const handleApply = async () => {
    if (!newStatus) { toast.error("Select a status first."); return }
    try {
      await batchUpdate.mutateAsync({ ids, status: newStatus })
      toast.success(`Updated ${ids.length} plant(s) to ${STATUSES.find(s => s.value === newStatus)?.label}`)
      onOpenChange(false)
    } catch { toast.error("Batch update failed.") }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-sm">
        <DialogHeader><DialogTitle>Change Status</DialogTitle></DialogHeader>
        <p className="text-sm text-muted-foreground">
          Apply a new status to <strong>{ids.length}</strong> selected plant(s).
        </p>
        <Select value={newStatus} onValueChange={setNewStatus}>
          <SelectTrigger className="thin-border"><SelectValue placeholder="Select new status" /></SelectTrigger>
          <SelectContent>
            {STATUSES.map((s) => <SelectItem key={s.value} value={s.value}>{s.label}</SelectItem>)}
          </SelectContent>
        </Select>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>Cancel</Button>
          <Button onClick={handleApply} disabled={batchUpdate.isPending || !newStatus}>
            {batchUpdate.isPending ? "Applying..." : "Apply"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

export default function MotherPlantsPage() {
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [search, setSearch] = useState("")
  const [addOpen, setAddOpen] = useState(false)
  const [editTarget, setEditTarget] = useState<MotherPlant | null>(null)
  const [deleteTarget, setDeleteTarget] = useState<MotherPlant | null>(null)
  const [selectedIds, setSelectedIds] = useState<Set<number | string>>(new Set())
  const [batchStatusOpen, setBatchStatusOpen] = useState(false)

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
    {
      key: "status",
      label: "Status",
      render: (plant: MotherPlant) => <MotherPlantStatusBadge status={plant.status} />,
    },
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
    {
      key: "total_cuttings_taken",
      label: "Total Cuts",
      render: (plant: MotherPlant) => <span className="data-value">{plant.total_cuttings_taken}</span>,
    },
    {
      key: "last_cut_date",
      label: "Last Cut",
      render: (plant: MotherPlant) =>
        plant.last_cut_date ? format(new Date(plant.last_cut_date), "MMM d, yyyy") : "—",
    },
    {
      key: "actions",
      label: "",
      render: (plant: MotherPlant) => (
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="sm" className="h-7 w-7 p-0">⋮</Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem onClick={() => setEditTarget(plant)}>Edit</DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem
              className="text-destructive focus:text-destructive"
              onClick={() => setDeleteTarget(plant)}
            >
              Delete
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      ),
    },
  ]

  return (
    <div>
      <PageHeader
        title="Mother Plants"
        description="Manage mother plants for clone production"
        action={
          <Button onClick={() => setAddOpen(true)}>
            <Plus className="w-4 h-4 mr-2" />Add Mother Plant
          </Button>
        }
        filters={
          <div className="relative w-72">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input
              placeholder="Search by code or strain..."
              value={search}
              onChange={(e) => { setSearch(e.target.value); setPage(1) }}
              className="pl-9 thin-border"
            />
          </div>
        }
      />

      <DataTable
        columns={columns}
        data={data?.results || []}
        loading={isLoading}
        selectable
        selectedIds={selectedIds}
        onSelectionChange={setSelectedIds}
        batchActions={
          <Button
            variant="outline"
            size="sm"
            className="thin-border"
            onClick={() => setBatchStatusOpen(true)}
          >
            Change Status
          </Button>
        }
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

      <AddMotherPlantDialog open={addOpen} onOpenChange={setAddOpen} />

      {editTarget && (
        <EditMotherPlantDialog
          key={editTarget.id}
          plant={editTarget}
          open={!!editTarget}
          onOpenChange={(v) => { if (!v) setEditTarget(null) }}
        />
      )}

      {deleteTarget && (
        <DeleteMotherPlantDialog
          plant={deleteTarget}
          open={!!deleteTarget}
          onOpenChange={(v) => { if (!v) setDeleteTarget(null) }}
        />
      )}

      <BatchStatusDialog
        ids={[...selectedIds] as number[]}
        open={batchStatusOpen}
        onOpenChange={(v) => {
          setBatchStatusOpen(v)
          if (!v) setSelectedIds(new Set())
        }}
      />
    </div>
  )
}
