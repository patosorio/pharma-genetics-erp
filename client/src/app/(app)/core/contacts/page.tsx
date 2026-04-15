"use client"

import { useState } from "react"
import { Plus } from "lucide-react"
import { toast } from "sonner"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { useContacts, useCreateContact } from "@/hooks/use-contacts"
import { PageHeader } from "@/components/layout/page-header"
import { DataTable } from "@/components/common/data-table"
import { StatusBadge } from "@/components/common/status-badge"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog"
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import type { Contact } from "@/lib/types/core"

const schema = z.object({
  name: z.string().min(1, "Name is required"),
  contact_type: z.enum(["customer", "supplier", "vendor", "other"]),
  email: z.string().email("Invalid email").optional().or(z.literal("")),
  phone: z.string().optional(),
  address: z.string().optional(),
  tax_id: z.string().optional(),
})
type FormValues = z.infer<typeof schema>

function AddContactDialog({ open, onOpenChange }: { open: boolean; onOpenChange: (v: boolean) => void }) {
  const create = useCreateContact()
  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { name: "", contact_type: "customer", email: "", phone: "", address: "", tax_id: "" },
  })

  const onSubmit = async (values: FormValues) => {
    try {
      await create.mutateAsync(values)
      toast.success("Contact added")
      form.reset()
      onOpenChange(false)
    } catch {
      toast.error("Failed to add contact.")
    }
  }

  return (
    <Dialog open={open} onOpenChange={(v) => { if (!v) form.reset(); onOpenChange(v) }}>
      <DialogContent>
        <DialogHeader><DialogTitle>Add Contact</DialogTitle></DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField control={form.control} name="name" render={({ field }) => (
              <FormItem><FormLabel>Name</FormLabel>
                <FormControl><Input className="thin-border" placeholder="Contact name" {...field} /></FormControl>
                <FormMessage />
              </FormItem>
            )} />
            <FormField control={form.control} name="contact_type" render={({ field }) => (
              <FormItem><FormLabel>Type</FormLabel>
                <Select onValueChange={field.onChange} value={field.value}>
                  <FormControl>
                    <SelectTrigger className="thin-border"><SelectValue /></SelectTrigger>
                  </FormControl>
                  <SelectContent>
                    <SelectItem value="customer">Customer</SelectItem>
                    <SelectItem value="supplier">Supplier</SelectItem>
                    <SelectItem value="vendor">Vendor</SelectItem>
                    <SelectItem value="other">Other</SelectItem>
                  </SelectContent>
                </Select>
                <FormMessage />
              </FormItem>
            )} />
            <div className="grid grid-cols-2 gap-4">
              <FormField control={form.control} name="email" render={({ field }) => (
                <FormItem><FormLabel>Email (optional)</FormLabel>
                  <FormControl><Input className="thin-border" placeholder="email@example.com" {...field} /></FormControl>
                  <FormMessage />
                </FormItem>
              )} />
              <FormField control={form.control} name="phone" render={({ field }) => (
                <FormItem><FormLabel>Phone (optional)</FormLabel>
                  <FormControl><Input className="thin-border" placeholder="+66..." {...field} /></FormControl>
                  <FormMessage />
                </FormItem>
              )} />
            </div>
            <FormField control={form.control} name="tax_id" render={({ field }) => (
              <FormItem><FormLabel>Tax ID (optional)</FormLabel>
                <FormControl><Input className="thin-border" placeholder="0105XXXXXXXXX" {...field} /></FormControl>
                <FormMessage />
              </FormItem>
            )} />
            <FormField control={form.control} name="address" render={({ field }) => (
              <FormItem><FormLabel>Address (optional)</FormLabel>
                <FormControl><Input className="thin-border" placeholder="Street, City" {...field} /></FormControl>
                <FormMessage />
              </FormItem>
            )} />
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>Cancel</Button>
              <Button type="submit" disabled={create.isPending}>{create.isPending ? "Saving..." : "Add Contact"}</Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}

export default function ContactsPage() {
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [search, setSearch] = useState("")
  const [open, setOpen] = useState(false)

  const { data, isLoading } = useContacts({ page, page_size: pageSize, search })

  const columns = [
    {
      key: "name",
      label: "Name",
      render: (contact: Contact) => (
        <div>
          <p className="font-medium">{contact.name}</p>
          {contact.email && <p className="text-xs text-muted-foreground">{contact.email}</p>}
        </div>
      ),
    },
    {
      key: "contact_type_display",
      label: "Type",
      render: (contact: Contact) => <Badge variant="outline" className="thin-border">{contact.contact_type_display}</Badge>,
    },
    { key: "phone", label: "Phone", render: (contact: Contact) => contact.phone || "-" },
    { key: "tax_id", label: "Tax ID", render: (contact: Contact) => contact.tax_id || "-" },
    {
      key: "is_active",
      label: "Status",
      render: (contact: Contact) => <StatusBadge status={contact.is_active ? "Active" : "Inactive"} />,
    },
  ]

  return (
    <div>
      <PageHeader
        title="Contacts"
        description="Manage customers, suppliers, and vendors"
        action={<Button onClick={() => setOpen(true)}><Plus className="w-4 h-4 mr-2" />Add Contact</Button>}
      />
      <DataTable columns={columns} data={data?.results || []} loading={isLoading} searchPlaceholder="Search contacts..." onSearch={setSearch}
        pagination={data ? { currentPage: page, totalPages: Math.ceil(data.count / pageSize), pageSize, totalItems: data.count, onPageChange: setPage, onPageSizeChange: setPageSize } : undefined}
      />
      <AddContactDialog open={open} onOpenChange={setOpen} />
    </div>
  )
}
