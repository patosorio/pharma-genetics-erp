"use client"

import { useState } from "react"
import { Plus } from "lucide-react"
import { toast } from "sonner"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { useUsers, useCreateUser } from "@/hooks/use-users"
import { useLocations } from "@/hooks/use-locations"
import { PageHeader } from "@/components/layout/page-header"
import { DataTable } from "@/components/common/data-table"
import { StatusBadge } from "@/components/common/status-badge"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog"
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import type { User } from "@/lib/types/core"

const schema = z.object({
  username: z.string().min(1, "Username is required"),
  email: z.string().email("Invalid email"),
  first_name: z.string().optional(),
  last_name: z.string().optional(),
  role: z.enum(["admin", "cultivation_manager", "sales_rep", "accountant", "viewer"]),
  password: z.string().min(8, "Password must be at least 8 characters"),
  location: z.coerce.number().optional(),
})
type FormValues = z.infer<typeof schema>

function AddUserDialog({ open, onOpenChange }: { open: boolean; onOpenChange: (v: boolean) => void }) {
  const create = useCreateUser()
  const { data: locations } = useLocations({ page_size: 100 })
  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { username: "", email: "", first_name: "", last_name: "", role: "viewer", password: "" },
  })

  const onSubmit = async (values: FormValues) => {
    try {
      await create.mutateAsync(values)
      toast.success("User created")
      form.reset()
      onOpenChange(false)
    } catch {
      toast.error("Failed to create user.")
    }
  }

  return (
    <Dialog open={open} onOpenChange={(v) => { if (!v) form.reset(); onOpenChange(v) }}>
      <DialogContent>
        <DialogHeader><DialogTitle>Add User</DialogTitle></DialogHeader>
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
            <FormField control={form.control} name="username" render={({ field }) => (
              <FormItem><FormLabel>Username</FormLabel>
                <FormControl><Input className="thin-border" {...field} /></FormControl>
                <FormMessage />
              </FormItem>
            )} />
            <FormField control={form.control} name="email" render={({ field }) => (
              <FormItem><FormLabel>Email</FormLabel>
                <FormControl><Input className="thin-border" type="email" {...field} /></FormControl>
                <FormMessage />
              </FormItem>
            )} />
            <FormField control={form.control} name="password" render={({ field }) => (
              <FormItem><FormLabel>Password</FormLabel>
                <FormControl><Input className="thin-border" type="password" {...field} /></FormControl>
                <FormMessage />
              </FormItem>
            )} />
            <div className="grid grid-cols-2 gap-4">
              <FormField control={form.control} name="role" render={({ field }) => (
                <FormItem><FormLabel>Role</FormLabel>
                  <Select onValueChange={field.onChange} value={field.value}>
                    <FormControl><SelectTrigger className="thin-border"><SelectValue /></SelectTrigger></FormControl>
                    <SelectContent>
                      <SelectItem value="admin">Admin</SelectItem>
                      <SelectItem value="cultivation_manager">Cultivation Manager</SelectItem>
                      <SelectItem value="sales_rep">Sales Rep</SelectItem>
                      <SelectItem value="accountant">Accountant</SelectItem>
                      <SelectItem value="viewer">Viewer</SelectItem>
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )} />
              <FormField control={form.control} name="location" render={({ field }) => (
                <FormItem><FormLabel>Location (optional)</FormLabel>
                  <Select onValueChange={(v) => field.onChange(v ? Number(v) : undefined)} value={field.value?.toString() ?? ""}>
                    <FormControl><SelectTrigger className="thin-border"><SelectValue placeholder="None" /></SelectTrigger></FormControl>
                    <SelectContent>
                      <SelectItem value="">None</SelectItem>
                      {locations?.results.map((l) => <SelectItem key={l.id} value={l.id.toString()}>{l.code} — {l.name}</SelectItem>)}
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )} />
            </div>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>Cancel</Button>
              <Button type="submit" disabled={create.isPending}>{create.isPending ? "Saving..." : "Add User"}</Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}

export default function UsersPage() {
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [search, setSearch] = useState("")
  const [open, setOpen] = useState(false)

  const { data, isLoading } = useUsers({ page, page_size: pageSize, search })

  const columns = [
    {
      key: "username",
      label: "Username",
      render: (user: User) => (
        <div>
          <p className="font-medium">{user.username}</p>
          <p className="text-xs text-muted-foreground">{user.email}</p>
        </div>
      ),
    },
    { key: "full_name", label: "Full Name" },
    {
      key: "role",
      label: "Role",
      render: (user: User) => <Badge variant="outline" className="thin-border">{user.role.replace(/_/g, " ")}</Badge>,
    },
    { key: "location_name", label: "Location", render: (user: User) => user.location_name || "-" },
    {
      key: "is_active",
      label: "Status",
      render: (user: User) => <StatusBadge status={user.is_active ? "Active" : "Inactive"} />,
    },
  ]

  return (
    <div>
      <PageHeader
        title="Users"
        description="Manage system users and their roles"
        action={<Button onClick={() => setOpen(true)}><Plus className="w-4 h-4 mr-2" />Add User</Button>}
      />
      <DataTable columns={columns} data={data?.results || []} loading={isLoading} searchPlaceholder="Search users..." onSearch={setSearch}
        pagination={data ? { currentPage: page, totalPages: Math.ceil(data.count / pageSize), pageSize, totalItems: data.count, onPageChange: setPage, onPageSizeChange: setPageSize } : undefined}
      />
      <AddUserDialog open={open} onOpenChange={setOpen} />
    </div>
  )
}
