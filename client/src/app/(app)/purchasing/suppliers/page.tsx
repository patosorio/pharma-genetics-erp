"use client"

import { useState } from "react"
import { Plus } from "lucide-react"
import { toast } from "sonner"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { useSuppliers, useCreateSupplier } from "@/hooks/use-purchasing"
import { useContacts } from "@/hooks/use-contacts"
import { PageHeader } from "@/components/layout/page-header"
import { DataTable } from "@/components/common/data-table"
import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog"
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import type { Supplier } from "@/lib/types/purchasing"

const schema = z.object({
  contact: z.coerce.number({ required_error: "Contact is required" }),
  payment_terms_days: z.coerce.number().min(0).default(30),
})
type FormValues = z.infer<typeof schema>

function AddSupplierDialog({ open, onOpenChange }: { open: boolean; onOpenChange: (v: boolean) => void }) {
  const create = useCreateSupplier()
  const { data: contacts } = useContacts({ page_size: 200, contact_type: "supplier" })
  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { payment_terms_days: 30 },
  })

  const onSubmit = async (values: FormValues) => {
    try {
      await create.mutateAsync(values)
      toast.success("Supplier added")
      form.reset()
      onOpenChange(false)
    } catch {
      toast.error("Failed to add supplier.")
    }
  }

  return (
    <Dialog open={open} onOpenChange={(v) => { if (!v) form.reset(); onOpenChange(v) }}>
      <DialogContent>
        <DialogHeader><DialogTitle>Add Supplier</DialogTitle></DialogHeader>
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
            <FormField control={form.control} name="payment_terms_days" render={({ field }) => (
              <FormItem><FormLabel>Payment Terms (days)</FormLabel>
                <FormControl><Input type="number" min={0} className="thin-border" {...field} /></FormControl>
                <FormMessage />
              </FormItem>
            )} />
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>Cancel</Button>
              <Button type="submit" disabled={create.isPending}>{create.isPending ? "Saving..." : "Add Supplier"}</Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}

export default function SuppliersPage() {
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [search, setSearch] = useState("")
  const [open, setOpen] = useState(false)

  const { data, isLoading } = useSuppliers({ page, page_size: pageSize, search })

  const columns = [
    { key: "supplier_code", label: "Code", render: (s: Supplier) => <span className="font-medium">{s.supplier_code}</span> },
    { key: "contact_name", label: "Supplier Name" },
    { key: "payment_terms_days", label: "Payment Terms", render: (s: Supplier) => <span className="data-value">{s.payment_terms_days} days</span> },
    { key: "created_at", label: "Added", render: (s: Supplier) => new Date(s.created_at).toLocaleDateString() },
  ]

  return (
    <div>
      <PageHeader
        title="Suppliers"
        description="Manage supplier contacts and payment terms"
        action={<Button onClick={() => setOpen(true)}><Plus className="w-4 h-4 mr-2" />Add Supplier</Button>}
      />
      <DataTable columns={columns} data={data?.results || []} loading={isLoading} searchPlaceholder="Search suppliers..." onSearch={setSearch} emptyMessage="No suppliers found"
        pagination={data ? { currentPage: page, totalPages: Math.ceil(data.count / pageSize), pageSize, totalItems: data.count, onPageChange: setPage, onPageSizeChange: setPageSize } : undefined}
      />
      <AddSupplierDialog open={open} onOpenChange={setOpen} />
    </div>
  )
}
