"use client"

import { useState } from "react"
import { Plus, ChevronRight } from "lucide-react"
import { format } from "date-fns"
import { toast } from "sonner"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { usePayrollPeriods, useCreatePayrollPeriod, useClosePeriod } from "@/hooks/use-hr"
import { PageHeader } from "@/components/layout/page-header"
import { DataTable } from "@/components/common/data-table"
import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog"
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import type { PayrollPeriod } from "@/lib/types/hr"

const schema = z.object({
  period_name: z.string().min(1, "Name is required"),
  start_date: z.string().min(1, "Start date is required"),
  end_date: z.string().min(1, "End date is required"),
})
type FormValues = z.infer<typeof schema>

function NewPeriodDialog({ open, onOpenChange }: { open: boolean; onOpenChange: (v: boolean) => void }) {
  const create = useCreatePayrollPeriod()
  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { period_name: "", start_date: "", end_date: "" },
  })

  const onSubmit = async (values: FormValues) => {
    try {
      await create.mutateAsync(values)
      toast.success("Payroll period created")
      form.reset()
      onOpenChange(false)
    } catch {
      toast.error("Failed to create period.")
    }
  }

  return (
    <Dialog open={open} onOpenChange={(v) => { if (!v) form.reset(); onOpenChange(v) }}>
      <DialogContent>
        <DialogHeader><DialogTitle>New Payroll Period</DialogTitle></DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField control={form.control} name="period_name" render={({ field }) => (
              <FormItem><FormLabel>Period Name</FormLabel>
                <FormControl><Input className="thin-border" placeholder="March 2026" {...field} /></FormControl>
                <FormMessage />
              </FormItem>
            )} />
            <div className="grid grid-cols-2 gap-4">
              <FormField control={form.control} name="start_date" render={({ field }) => (
                <FormItem><FormLabel>Start Date</FormLabel>
                  <FormControl><Input type="date" className="thin-border" {...field} /></FormControl>
                  <FormMessage />
                </FormItem>
              )} />
              <FormField control={form.control} name="end_date" render={({ field }) => (
                <FormItem><FormLabel>End Date</FormLabel>
                  <FormControl><Input type="date" className="thin-border" {...field} /></FormControl>
                  <FormMessage />
                </FormItem>
              )} />
            </div>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>Cancel</Button>
              <Button type="submit" disabled={create.isPending}>{create.isPending ? "Creating..." : "Create Period"}</Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}

export default function PayrollPeriodsPage() {
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [search, setSearch] = useState("")
  const [open, setOpen] = useState(false)

  const { data, isLoading } = usePayrollPeriods({ page, page_size: pageSize })
  const closePeriod = useClosePeriod()

  const handleClose = async (period: PayrollPeriod) => {
    try {
      await closePeriod.mutateAsync(period.id)
      toast.success(`Period "${period.period_name}" closed`)
    } catch {
      toast.error("Failed to close period. Ensure all payrolls are paid first.")
    }
  }

  const columns = [
    {
      key: "period_name",
      label: "Period",
      render: (p: PayrollPeriod) => <span className="font-medium">{p.period_name}</span>,
    },
    {
      key: "start_date",
      label: "Start",
      render: (p: PayrollPeriod) => format(new Date(p.start_date), "MMM d, yyyy"),
    },
    {
      key: "end_date",
      label: "End",
      render: (p: PayrollPeriod) => format(new Date(p.end_date), "MMM d, yyyy"),
    },
    {
      key: "is_closed",
      label: "Status",
      render: (p: PayrollPeriod) => (
        <span
          className={`text-xs font-medium px-2 py-0.5 rounded-full border ${
            p.is_closed
              ? "border-[#4A4A45] text-[#4A4A45] bg-[#4A4A45]/10"
              : "border-[#4A7C59] text-[#4A7C59] bg-[#4A7C59]/10"
          }`}
        >
          {p.is_closed ? "Closed" : "Open"}
        </span>
      ),
    },
    {
      key: "actions",
      label: "",
      render: (p: PayrollPeriod) => {
        if (p.is_closed) return null
        return (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="sm" className="h-7 w-7 p-0">
                <ChevronRight className="w-4 h-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={() => handleClose(p)}>Close Period</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        )
      },
    },
  ]

  return (
    <div>
      <PageHeader
        title="Payroll Periods"
        description="Manage payroll periods and period close-outs"
        action={
          <Button onClick={() => setOpen(true)}>
            <Plus className="w-4 h-4 mr-2" />
            New Period
          </Button>
        }
      />

      <DataTable
        columns={columns}
        data={data?.results || []}
        loading={isLoading}
        searchPlaceholder="Search periods..."
        onSearch={setSearch}
        emptyMessage="No payroll periods found"
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
      <NewPeriodDialog open={open} onOpenChange={setOpen} />
    </div>
  )
}
