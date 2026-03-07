"use client"

import { useState } from "react"
import { Plus } from "lucide-react"
import { toast } from "sonner"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { useCustomers, useCreateCustomer } from "@/hooks/use-customers"
import { useContacts } from "@/hooks/use-contacts"
import { PageHeader } from "@/components/layout/page-header"
import { DataTable } from "@/components/common/data-table"
import { StatusBadge } from "@/components/common/status-badge"
import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog"
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import type { Customer } from "@/lib/types/sales"

const schema = z.object({
  contact: z.coerce.number({ required_error: "Contact is required" }),
  tier: z.enum(["Standard", "Premium", "Enterprise", "VIP"]).default("Standard"),
  credit_limit: z.string().optional(),
  payment_terms_days: z.coerce.number().min(0).default(30),
})
type FormValues = z.infer<typeof schema>

function AddCustomerDialog({ open, onOpenChange }: { open: boolean; onOpenChange: (v: boolean) => void }) {
  const create = useCreateCustomer()
  const { data: contacts } = useContacts({ page_size: 200, contact_type: "customer" })
  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { tier: "Standard", credit_limit: "", payment_terms_days: 30 },
  })

  const onSubmit = async (values: FormValues) => {
    try {
      await create.mutateAsync(values)
      toast.success("Customer added")
      form.reset()
      onOpenChange(false)
    } catch {
      toast.error("Failed to add customer.")
    }
  }

  return (
    <Dialog open={open} onOpenChange={(v) => { if (!v) form.reset(); onOpenChange(v) }}>
      <DialogContent>
        <DialogHeader><DialogTitle>Add Customer</DialogTitle></DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField control={form.control} name="contact" render={({ field }) => (
              <FormItem><FormLabel>Contact</FormLabel>
                <Select onValueChange={(v) => field.onChange(Number(v))} value={field.value?.toString() ?? ""}>
                  <FormControl><SelectTrigger className="thin-border"><SelectValue placeholder="Select contact" /></SelectTrigger></FormControl>
                  <SelectContent>
                    {contacts?.results.map((c) => <SelectItem key={c.id} value={c.id.toString()}>{c.name}</SelectItem>)}
                  </SelectContent>
                </Select>
                <FormMessage />
              </FormItem>
            )} />
            <div className="grid grid-cols-2 gap-4">
              <FormField control={form.control} name="tier" render={({ field }) => (
                <FormItem><FormLabel>Tier</FormLabel>
                  <Select onValueChange={field.onChange} value={field.value}>
                    <FormControl><SelectTrigger className="thin-border"><SelectValue /></SelectTrigger></FormControl>
                    <SelectContent>
                      <SelectItem value="Standard">Standard</SelectItem>
                      <SelectItem value="Premium">Premium</SelectItem>
                      <SelectItem value="Enterprise">Enterprise</SelectItem>
                      <SelectItem value="VIP">VIP</SelectItem>
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )} />
              <FormField control={form.control} name="payment_terms_days" render={({ field }) => (
                <FormItem><FormLabel>Payment Terms (days)</FormLabel>
                  <FormControl><Input type="number" min={0} className="thin-border" {...field} /></FormControl>
                  <FormMessage />
                </FormItem>
              )} />
            </div>
            <FormField control={form.control} name="credit_limit" render={({ field }) => (
              <FormItem><FormLabel>Credit Limit (฿, optional)</FormLabel>
                <FormControl><Input className="thin-border" placeholder="0.00" {...field} /></FormControl>
                <FormMessage />
              </FormItem>
            )} />
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>Cancel</Button>
              <Button type="submit" disabled={create.isPending}>{create.isPending ? "Saving..." : "Add Customer"}</Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}

export default function CustomersPage() {
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [search, setSearch] = useState("")
  const [open, setOpen] = useState(false)

  const { data, isLoading } = useCustomers({ page, page_size: pageSize, search })

  const columns = [
    { key: "customer_code", label: "Code", render: (customer: Customer) => <span className="font-medium">{customer.customer_code}</span> },
    { key: "contact_name", label: "Customer Name" },
    {
      key: "credit_limit",
      label: "Credit Limit",
      render: (customer: Customer) => (
        <span className="data-value">{customer.credit_limit ? `฿${Number.parseFloat(customer.credit_limit).toLocaleString()}` : "-"}</span>
      ),
    },
    { key: "payment_terms_days", label: "Payment Terms", render: (customer: Customer) => <span className="data-value">{customer.payment_terms_days} days</span> },
    { key: "is_active", label: "Status", render: (customer: Customer) => <StatusBadge status={customer.is_active ? "Active" : "Inactive"} /> },
  ]

  return (
    <div>
      <PageHeader
        title="Customers"
        description="Manage customer accounts and credit terms"
        action={<Button onClick={() => setOpen(true)}><Plus className="w-4 h-4 mr-2" />Add Customer</Button>}
      />
      <DataTable columns={columns} data={data?.results || []} loading={isLoading} searchPlaceholder="Search customers..." onSearch={setSearch}
        pagination={data ? { currentPage: page, totalPages: Math.ceil(data.count / pageSize), pageSize, totalItems: data.count, onPageChange: setPage, onPageSizeChange: setPageSize } : undefined}
      />
      <AddCustomerDialog open={open} onOpenChange={setOpen} />
    </div>
  )
}
