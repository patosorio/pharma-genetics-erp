"use client"

import { useState } from "react"
import { Plus } from "lucide-react"
import { format } from "date-fns"
import { toast } from "sonner"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { useEmployees, useCreateEmployee, useDepartments } from "@/hooks/use-hr"
import { useLocations } from "@/hooks/use-locations"
import { PageHeader } from "@/components/layout/page-header"
import { DataTable } from "@/components/common/data-table"
import { StatusBadge } from "@/components/common/status-badge"
import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog"
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import type { Employee } from "@/lib/types/hr"

const schema = z.object({
  first_name: z.string().min(1, "First name is required"),
  last_name: z.string().min(1, "Last name is required"),
  email: z.string().email("Invalid email"),
  phone: z.string().optional(),
  department: z.coerce.number({ required_error: "Department is required" }),
  location: z.coerce.number({ required_error: "Location is required" }),
  hire_date: z.string().min(1, "Hire date is required"),
  salary: z.string().min(1, "Salary is required"),
})
type FormValues = z.infer<typeof schema>

function AddEmployeeDialog({ open, onOpenChange }: { open: boolean; onOpenChange: (v: boolean) => void }) {
  const create = useCreateEmployee()
  const { data: departments } = useDepartments({ page_size: 100 })
  const { data: locations } = useLocations({ page_size: 100 })
  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { first_name: "", last_name: "", email: "", phone: "", hire_date: new Date().toISOString().split("T")[0], salary: "" },
  })

  const onSubmit = async (values: FormValues) => {
    try {
      await create.mutateAsync(values)
      toast.success("Employee added")
      form.reset()
      onOpenChange(false)
    } catch {
      toast.error("Failed to add employee.")
    }
  }

  return (
    <Dialog open={open} onOpenChange={(v) => { if (!v) form.reset(); onOpenChange(v) }}>
      <DialogContent className="max-w-lg">
        <DialogHeader><DialogTitle>Add Employee</DialogTitle></DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <FormField control={form.control} name="first_name" render={({ field }) => (
                <FormItem><FormLabel>First Name</FormLabel>
                  <FormControl><Input className="thin-border" {...field} /></FormControl>
                  <FormMessage />
                </FormItem>
              )} />
              <FormField control={form.control} name="last_name" render={({ field }) => (
                <FormItem><FormLabel>Last Name</FormLabel>
                  <FormControl><Input className="thin-border" {...field} /></FormControl>
                  <FormMessage />
                </FormItem>
              )} />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <FormField control={form.control} name="email" render={({ field }) => (
                <FormItem><FormLabel>Email</FormLabel>
                  <FormControl><Input type="email" className="thin-border" {...field} /></FormControl>
                  <FormMessage />
                </FormItem>
              )} />
              <FormField control={form.control} name="phone" render={({ field }) => (
                <FormItem><FormLabel>Phone (optional)</FormLabel>
                  <FormControl><Input className="thin-border" {...field} /></FormControl>
                  <FormMessage />
                </FormItem>
              )} />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <FormField control={form.control} name="department" render={({ field }) => (
                <FormItem><FormLabel>Department</FormLabel>
                  <Select onValueChange={(v) => field.onChange(Number(v))} value={field.value?.toString() ?? ""}>
                    <FormControl><SelectTrigger className="thin-border"><SelectValue placeholder="Select" /></SelectTrigger></FormControl>
                    <SelectContent>
                      {departments?.results.map((d) => <SelectItem key={d.id} value={d.id.toString()}>{d.name}</SelectItem>)}
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )} />
              <FormField control={form.control} name="location" render={({ field }) => (
                <FormItem><FormLabel>Location</FormLabel>
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
              <FormField control={form.control} name="hire_date" render={({ field }) => (
                <FormItem><FormLabel>Hire Date</FormLabel>
                  <FormControl><Input type="date" className="thin-border" {...field} /></FormControl>
                  <FormMessage />
                </FormItem>
              )} />
              <FormField control={form.control} name="salary" render={({ field }) => (
                <FormItem><FormLabel>Salary (฿)</FormLabel>
                  <FormControl><Input className="thin-border" placeholder="0.00" {...field} /></FormControl>
                  <FormMessage />
                </FormItem>
              )} />
            </div>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>Cancel</Button>
              <Button type="submit" disabled={create.isPending}>{create.isPending ? "Saving..." : "Add Employee"}</Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}

export default function EmployeesPage() {
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [search, setSearch] = useState("")
  const [open, setOpen] = useState(false)

  const { data, isLoading } = useEmployees({ page, page_size: pageSize, search })

  const columns = [
    { key: "employee_code", label: "Code", render: (e: Employee) => <span className="font-medium">{e.employee_code}</span> },
    { key: "full_name", label: "Name", render: (e: Employee) => e.full_name },
    { key: "department_name", label: "Department" },
    { key: "location_code", label: "Location" },
    { key: "hire_date", label: "Hire Date", render: (e: Employee) => format(new Date(e.hire_date), "MMM d, yyyy") },
    { key: "salary", label: "Salary", render: (e: Employee) => <span className="data-value">฿{Number.parseFloat(e.salary).toLocaleString()}</span> },
    { key: "is_active", label: "Status", render: (e: Employee) => <StatusBadge status={e.is_active ? "Active" : "Inactive"} /> },
  ]

  return (
    <div>
      <PageHeader
        title="Employees"
        description="Manage employee records and assignments"
        action={<Button onClick={() => setOpen(true)}><Plus className="w-4 h-4 mr-2" />Add Employee</Button>}
      />
      <DataTable columns={columns} data={data?.results || []} loading={isLoading} searchPlaceholder="Search employees..." onSearch={setSearch} emptyMessage="No employees found"
        pagination={data ? { currentPage: page, totalPages: Math.ceil(data.count / pageSize), pageSize, totalItems: data.count, onPageChange: setPage, onPageSizeChange: setPageSize } : undefined}
      />
      <AddEmployeeDialog open={open} onOpenChange={setOpen} />
    </div>
  )
}
