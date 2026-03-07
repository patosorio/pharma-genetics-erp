"use client"

import { useState } from "react"
import { Plus } from "lucide-react"
import { toast } from "sonner"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { useStrains, useCreateStrain, useStrainCategories } from "@/hooks/use-strains"
import { PageHeader } from "@/components/layout/page-header"
import { DataTable } from "@/components/common/data-table"
import { StatusBadge } from "@/components/common/status-badge"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog"
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import type { Strain } from "@/lib/types/genetics"

const schema = z.object({
  name: z.string().min(1, "Name is required"),
  category: z.coerce.number({ required_error: "Category is required" }),
  catalogue_year: z.coerce.number().min(2020).max(2100),
  thc_percentage: z.string().optional(),
  cbd_percentage: z.string().optional(),
  breeder: z.string().optional(),
  description: z.string().optional(),
})
type FormValues = z.infer<typeof schema>

function AddStrainDialog({ open, onOpenChange }: { open: boolean; onOpenChange: (v: boolean) => void }) {
  const create = useCreateStrain()
  const { data: categories } = useStrainCategories({ page_size: 100 })
  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { name: "", catalogue_year: new Date().getFullYear(), breeder: "", description: "" },
  })

  const onSubmit = async (values: FormValues) => {
    try {
      await create.mutateAsync(values)
      toast.success("Strain added")
      form.reset()
      onOpenChange(false)
    } catch {
      toast.error("Failed to add strain.")
    }
  }

  return (
    <Dialog open={open} onOpenChange={(v) => { if (!v) form.reset(); onOpenChange(v) }}>
      <DialogContent>
        <DialogHeader><DialogTitle>Add Strain</DialogTitle></DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField control={form.control} name="name" render={({ field }) => (
              <FormItem><FormLabel>Strain Name</FormLabel>
                <FormControl><Input className="thin-border" placeholder="OG Kush" {...field} /></FormControl>
                <FormMessage />
              </FormItem>
            )} />
            <div className="grid grid-cols-2 gap-4">
              <FormField control={form.control} name="category" render={({ field }) => (
                <FormItem><FormLabel>Category</FormLabel>
                  <Select onValueChange={(v) => field.onChange(Number(v))} value={field.value?.toString() ?? ""}>
                    <FormControl><SelectTrigger className="thin-border"><SelectValue placeholder="Select" /></SelectTrigger></FormControl>
                    <SelectContent>
                      {categories?.results.map((c) => <SelectItem key={c.id} value={c.id.toString()}>{c.name}</SelectItem>)}
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )} />
              <FormField control={form.control} name="catalogue_year" render={({ field }) => (
                <FormItem><FormLabel>Catalogue Year</FormLabel>
                  <FormControl><Input type="number" className="thin-border" {...field} /></FormControl>
                  <FormMessage />
                </FormItem>
              )} />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <FormField control={form.control} name="thc_percentage" render={({ field }) => (
                <FormItem><FormLabel>THC % (optional)</FormLabel>
                  <FormControl><Input className="thin-border" placeholder="20.5" {...field} /></FormControl>
                  <FormMessage />
                </FormItem>
              )} />
              <FormField control={form.control} name="cbd_percentage" render={({ field }) => (
                <FormItem><FormLabel>CBD % (optional)</FormLabel>
                  <FormControl><Input className="thin-border" placeholder="0.5" {...field} /></FormControl>
                  <FormMessage />
                </FormItem>
              )} />
            </div>
            <FormField control={form.control} name="breeder" render={({ field }) => (
              <FormItem><FormLabel>Breeder (optional)</FormLabel>
                <FormControl><Input className="thin-border" {...field} /></FormControl>
                <FormMessage />
              </FormItem>
            )} />
            <FormField control={form.control} name="description" render={({ field }) => (
              <FormItem><FormLabel>Description (optional)</FormLabel>
                <FormControl><Input className="thin-border" {...field} /></FormControl>
                <FormMessage />
              </FormItem>
            )} />
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>Cancel</Button>
              <Button type="submit" disabled={create.isPending}>{create.isPending ? "Saving..." : "Add Strain"}</Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}

export default function StrainsPage() {
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [search, setSearch] = useState("")
  const [open, setOpen] = useState(false)

  const { data, isLoading } = useStrains({ page, page_size: pageSize, search })

  const columns = [
    {
      key: "name",
      label: "Strain",
      render: (strain: Strain) => (
        <div>
          <p className="font-medium">{strain.name}</p>
          <p className="text-xs text-muted-foreground">{strain.slug}</p>
        </div>
      ),
    },
    {
      key: "category_name",
      label: "Category",
      render: (strain: Strain) => <Badge variant="outline" className="thin-border">{strain.category_name}</Badge>,
    },
    { key: "thc_percentage", label: "THC %", render: (strain: Strain) => <span className="data-value">{strain.thc_percentage || "-"}</span> },
    { key: "cbd_percentage", label: "CBD %", render: (strain: Strain) => <span className="data-value">{strain.cbd_percentage || "-"}</span> },
    { key: "terpene_profile", label: "Terpene", render: (strain: Strain) => strain.terpene_profile || "-" },
    { key: "catalogue_year", label: "Year", render: (strain: Strain) => <span className="data-value">{strain.catalogue_year}</span> },
    {
      key: "is_active",
      label: "Status",
      render: (strain: Strain) => <StatusBadge status={strain.is_active ? "Active" : "Inactive"} />,
    },
  ]

  return (
    <div>
      <PageHeader
        title="Strains"
        description="Manage cannabis genetics and strain catalog"
        action={<Button onClick={() => setOpen(true)}><Plus className="w-4 h-4 mr-2" />Add Strain</Button>}
      />
      <DataTable columns={columns} data={data?.results || []} loading={isLoading} searchPlaceholder="Search strains..." onSearch={setSearch}
        pagination={data ? { currentPage: page, totalPages: Math.ceil(data.count / pageSize), pageSize, totalItems: data.count, onPageChange: setPage, onPageSizeChange: setPageSize } : undefined}
      />
      <AddStrainDialog open={open} onOpenChange={setOpen} />
    </div>
  )
}
