"use client"

import { useState } from "react"
import { Plus, ChevronRight } from "lucide-react"
import { toast } from "sonner"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { usePayrolls, useCreatePayroll, useMarkPayrollPaid, useEmployees, usePayrollPeriods } from "@/hooks/use-hr"
import { PageHeader } from "@/components/layout/page-header"
import { DataTable } from "@/components/common/data-table"
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
import type { Payroll } from "@/lib/types/hr"

const schema = z.object({
  employee: z.coerce.number({ required_error: "Employee is required" }),
  period: z.coerce.number({ required_error: "Period is required" }),
  base_salary: z.string().min(1, "Base salary is required"),
  deductions: z.string().default("0.00"),
  notes: z.string().optional(),
})
type FormValues = z.infer<typeof schema>

function AddPayrollDialog({ open, onOpenChange }: { open: boolean; onOpenChange: (v: boolean) => void }) {
  const create = useCreatePayroll()
  const { data: employees } = useEmployees({ page_size: 200 })
  const { data: periods } = usePayrollPeriods({ page_size: 100, is_closed: false })
  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { base_salary: "", deductions: "0.00", notes: "" },
  })

  const onSubmit = async (values: FormValues) => {
    try {
      await create.mutateAsync(values)
      toast.success("Payroll record added")
      form.reset()
      onOpenChange(false)
    } catch {
      toast.error("Failed to add payroll record.")
    }
  }

  return (
    <Dialog open={open} onOpenChange={(v) => { if (!v) form.reset(); onOpenChange(v) }}>
      <DialogContent>
        <DialogHeader><DialogTitle>Add Payroll Record</DialogTitle></DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField control={form.control} name="employee" render={({ field }) => (
              <FormItem><FormLabel>Employee</FormLabel>
                <Select onValueChange={(v) => field.onChange(Number(v))} value={field.value?.toString() ?? ""}>
                  <FormControl><SelectTrigger className="thin-border"><SelectValue placeholder="Select employee" /></SelectTrigger></FormControl>
                  <SelectContent>
                    {employees?.results.map((e) => <SelectItem key={e.id} value={e.id.toString()}>{e.full_name}</SelectItem>)}
                  </SelectContent>
                </Select>
                <FormMessage />
              </FormItem>
            )} />
            <FormField control={form.control} name="period" render={({ field }) => (
              <FormItem><FormLabel>Payroll Period</FormLabel>
                <Select onValueChange={(v) => field.onChange(Number(v))} value={field.value?.toString() ?? ""}>
                  <FormControl><SelectTrigger className="thin-border"><SelectValue placeholder="Select period" /></SelectTrigger></FormControl>
                  <SelectContent>
                    {periods?.results.map((p) => <SelectItem key={p.id} value={p.id.toString()}>{p.period_name}</SelectItem>)}
                  </SelectContent>
                </Select>
                <FormMessage />
              </FormItem>
            )} />
            <div className="grid grid-cols-2 gap-4">
              <FormField control={form.control} name="base_salary" render={({ field }) => (
                <FormItem><FormLabel>Base Salary (฿)</FormLabel>
                  <FormControl><Input className="thin-border" placeholder="0.00" {...field} /></FormControl>
                  <FormMessage />
                </FormItem>
              )} />
              <FormField control={form.control} name="deductions" render={({ field }) => (
                <FormItem><FormLabel>Deductions (฿)</FormLabel>
                  <FormControl><Input className="thin-border" placeholder="0.00" {...field} /></FormControl>
                  <FormMessage />
                </FormItem>
              )} />
            </div>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>Cancel</Button>
              <Button type="submit" disabled={create.isPending}>{create.isPending ? "Saving..." : "Add Payroll"}</Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}

export default function PayrollsPage() {
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [search, setSearch] = useState("")
  const [open, setOpen] = useState(false)

  const { data, isLoading } = usePayrolls({ page, page_size: pageSize })
  const markPaid = useMarkPayrollPaid()

  const handleMarkPaid = async (payroll: Payroll) => {
    try {
      await markPaid.mutateAsync({ id: payroll.id })
      toast.success(`Payroll for ${payroll.employee_name} marked as paid`)
    } catch {
      toast.error("Action failed. Please try again.")
    }
  }

  const columns = [
    {
      key: "employee_name",
      label: "Employee",
      render: (p: Payroll) => <span className="font-medium">{p.employee_name}</span>,
    },
    { key: "period_name", label: "Period" },
    {
      key: "base_salary",
      label: "Base Salary",
      render: (p: Payroll) => <span className="data-value">฿{Number.parseFloat(p.base_salary).toLocaleString()}</span>,
    },
    {
      key: "deductions",
      label: "Deductions",
      render: (p: Payroll) => (
        <span className="data-value text-[#A65D57]">-฿{Number.parseFloat(p.deductions).toLocaleString()}</span>
      ),
    },
    {
      key: "net_salary",
      label: "Net Salary",
      render: (p: Payroll) => (
        <span className="data-value font-medium text-[#4A7C59]">
          ฿{Number.parseFloat(p.net_salary).toLocaleString()}
        </span>
      ),
    },
    {
      key: "is_paid",
      label: "Status",
      render: (p: Payroll) => (
        <span
          className={`text-xs font-medium px-2 py-0.5 rounded-full border ${
            p.is_paid
              ? "border-[#4A7C59] text-[#4A7C59] bg-[#4A7C59]/10"
              : "border-[#B8A361] text-[#B8A361] bg-[#B8A361]/10"
          }`}
        >
          {p.is_paid ? "Paid" : "Pending"}
        </span>
      ),
    },
    {
      key: "payment_date",
      label: "Paid On",
      render: (p: Payroll) =>
        p.payment_date ? new Date(p.payment_date).toLocaleDateString() : "—",
    },
    {
      key: "actions",
      label: "",
      render: (p: Payroll) => {
        if (p.is_paid) return null
        return (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="sm" className="h-7 w-7 p-0">
                <ChevronRight className="w-4 h-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={() => handleMarkPaid(p)}>Mark Paid</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        )
      },
    },
  ]

  return (
    <div>
      <PageHeader
        title="Payrolls"
        description="Manage payroll records and payment status"
        action={
          <Button onClick={() => setOpen(true)}>
            <Plus className="w-4 h-4 mr-2" />
            Add Payroll
          </Button>
        }
      />

      <DataTable
        columns={columns}
        data={data?.results || []}
        loading={isLoading}
        searchPlaceholder="Search payrolls..."
        onSearch={setSearch}
        emptyMessage="No payroll records found"
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
      <AddPayrollDialog open={open} onOpenChange={setOpen} />
    </div>
  )
}
