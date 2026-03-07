"use client"

import { useState } from "react"
import { Plus, Scissors, ChevronRight } from "lucide-react"
import { format } from "date-fns"
import { toast } from "sonner"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { useProductionBatches, useCreateProductionBatch, useCompleteProductionBatch } from "@/hooks/use-batches"
import { useMotherPlants } from "@/hooks/use-cultivation"
import { PageHeader } from "@/components/layout/page-header"
import { DataTable } from "@/components/common/data-table"
import { ProductionBatchStatusBadge } from "@/components/cultivation/production-batch-status-badge"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
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
import type { ProductionBatch } from "@/lib/types/cultivation"

const batchSchema = z.object({
  mother_plant: z.coerce.number({ required_error: "Mother plant is required" }),
  cutting_date: z.string().min(1, "Cutting date is required"),
  initial_clone_count: z.coerce.number().min(1, "Must be at least 1"),
})
type BatchFormValues = z.infer<typeof batchSchema>

function NewBatchDialog({ open, onOpenChange }: { open: boolean; onOpenChange: (v: boolean) => void }) {
  const create = useCreateProductionBatch()
  const { data: motherPlants } = useMotherPlants({ page_size: 200 })
  const form = useForm<BatchFormValues>({
    resolver: zodResolver(batchSchema),
    defaultValues: { cutting_date: "", initial_clone_count: 1 },
  })

  const onSubmit = async (values: BatchFormValues) => {
    try {
      await create.mutateAsync(values)
      toast.success("Production batch created")
      form.reset()
      onOpenChange(false)
    } catch {
      toast.error("Failed to create batch.")
    }
  }

  return (
    <Dialog open={open} onOpenChange={(v) => { if (!v) form.reset(); onOpenChange(v) }}>
      <DialogContent>
        <DialogHeader><DialogTitle>New Production Batch</DialogTitle></DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField control={form.control} name="mother_plant" render={({ field }) => (
              <FormItem><FormLabel>Mother Plant</FormLabel>
                <Select onValueChange={(v) => field.onChange(Number(v))} value={field.value?.toString() ?? ""}>
                  <FormControl><SelectTrigger className="thin-border"><SelectValue placeholder="Select mother plant" /></SelectTrigger></FormControl>
                  <SelectContent>
                    {motherPlants?.results.map((m) => <SelectItem key={m.id} value={m.id.toString()}>{m.code} — {m.strain_name}</SelectItem>)}
                  </SelectContent>
                </Select>
                <FormMessage />
              </FormItem>
            )} />
            <FormField control={form.control} name="cutting_date" render={({ field }) => (
              <FormItem><FormLabel>Cutting Date</FormLabel>
                <FormControl><Input type="date" className="thin-border" {...field} /></FormControl>
                <FormMessage />
              </FormItem>
            )} />
            <FormField control={form.control} name="initial_clone_count" render={({ field }) => (
              <FormItem><FormLabel>Initial Clone Count</FormLabel>
                <FormControl><Input type="number" min={1} className="thin-border" {...field} /></FormControl>
                <FormMessage />
              </FormItem>
            )} />
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>Cancel</Button>
              <Button type="submit" disabled={create.isPending}>{create.isPending ? "Creating..." : "Create Batch"}</Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}

export default function ProductionBatchesPage() {
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [search, setSearch] = useState("")
  const [open, setOpen] = useState(false)

  const { data, isLoading } = useProductionBatches({ page, page_size: pageSize, search })
  const completeBatch = useCompleteProductionBatch()

  const handleComplete = async (batch: ProductionBatch) => {
    try {
      await completeBatch.mutateAsync(batch.id)
      toast.success(`Batch ${batch.batch_number} completed — cost per clone calculated`)
    } catch {
      toast.error("Failed to complete batch. Please try again.")
    }
  }

  const columns = [
    {
      key: "batch_number",
      label: "Batch Number",
      render: (batch: ProductionBatch) => (
        <div className="flex items-center gap-2">
          <Scissors className="w-4 h-4 text-muted-foreground" />
          <span className="font-medium">{batch.batch_number}</span>
        </div>
      ),
    },
    { key: "mother_plant_code", label: "Mother Plant" },
    { key: "location_code", label: "Location" },
    {
      key: "initial_clone_count",
      label: "Initial Cuts",
      render: (batch: ProductionBatch) => <span className="data-value">{batch.initial_clone_count}</span>,
    },
    {
      key: "rooted_clone_count",
      label: "Rooted",
      render: (batch: ProductionBatch) => <span className="data-value">{batch.rooted_clone_count}</span>,
    },
    {
      key: "survival_rate",
      label: "Survival Rate",
      render: (batch: ProductionBatch) => (
        <div className="flex items-center gap-2 min-w-[120px]">
          <Progress value={batch.survival_rate} className="h-2 flex-1" />
          <span className="text-sm text-muted-foreground w-10">{batch.survival_rate.toFixed(0)}%</span>
        </div>
      ),
    },
    {
      key: "status",
      label: "Status",
      render: (batch: ProductionBatch) => <ProductionBatchStatusBadge status={batch.status} />,
    },
    {
      key: "cutting_date",
      label: "Cutting Date",
      render: (batch: ProductionBatch) => format(new Date(batch.cutting_date), "MMM d, yyyy"),
    },
    {
      key: "expected_rooting_date",
      label: "Expected Rooting",
      render: (batch: ProductionBatch) =>
        batch.expected_rooting_date ? format(new Date(batch.expected_rooting_date), "MMM d, yyyy") : "-",
    },
    {
      key: "cost_per_clone",
      label: "Cost/Clone",
      render: (batch: ProductionBatch) =>
        batch.cost_per_clone && Number.parseFloat(batch.cost_per_clone) > 0
          ? <span className="data-value">฿{Number.parseFloat(batch.cost_per_clone).toLocaleString()}</span>
          : <span className="text-muted-foreground">—</span>,
    },
    {
      key: "actions",
      label: "",
      render: (batch: ProductionBatch) => {
        if (batch.status !== "rooting") return null
        return (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="sm" className="h-7 w-7 p-0">
                <ChevronRight className="w-4 h-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={() => handleComplete(batch)}>Complete Batch</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        )
      },
    },
  ]

  return (
    <div>
      <PageHeader
        title="Production Batches"
        description="Track cutting and rooting batches from mother plants"
        action={
          <Button onClick={() => setOpen(true)}>
            <Plus className="w-4 h-4 mr-2" />
            New Batch
          </Button>
        }
      />

      <DataTable
        columns={columns}
        data={data?.results || []}
        loading={isLoading}
        searchPlaceholder="Search batches..."
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
      <NewBatchDialog open={open} onOpenChange={setOpen} />
    </div>
  )
}
