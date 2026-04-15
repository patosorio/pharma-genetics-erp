"use client"

import { useState } from "react"
import { Plus } from "lucide-react"
import { toast } from "sonner"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { usePriceLists, useCreatePriceList } from "@/hooks/use-price-lists"
import { useStrains } from "@/hooks/use-strains"
import { useCurrencies } from "@/hooks/use-currencies"
import { PageHeader } from "@/components/layout/page-header"
import { DataTable } from "@/components/common/data-table"
import { StatusBadge } from "@/components/common/status-badge"
import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog"
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import type { PriceList } from "@/lib/types/sales"

const tierLabels: Record<string, string> = { retail: "Retail", wholesale: "Wholesale", bulk: "Bulk" }

const schema = z.object({
  strain: z.coerce.number({ required_error: "Strain is required" }),
  tier: z.enum(["retail", "wholesale", "bulk"]),
  price_per_clone: z.string().min(1, "Price is required"),
  currency: z.coerce.number({ required_error: "Currency is required" }),
  min_quantity: z.coerce.number().min(1).default(1),
})
type FormValues = z.infer<typeof schema>

function AddPriceDialog({ open, onOpenChange }: { open: boolean; onOpenChange: (v: boolean) => void }) {
  const create = useCreatePriceList()
  const { data: strains } = useStrains({ page_size: 200, is_active: true })
  const { data: currencies } = useCurrencies({ page_size: 50 })
  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { tier: "wholesale", price_per_clone: "", min_quantity: 1 },
  })

  const onSubmit = async (values: FormValues) => {
    try {
      await create.mutateAsync(values)
      toast.success("Price entry added")
      form.reset()
      onOpenChange(false)
    } catch {
      toast.error("Failed to add price entry.")
    }
  }

  return (
    <Dialog open={open} onOpenChange={(v) => { if (!v) form.reset(); onOpenChange(v) }}>
      <DialogContent>
        <DialogHeader><DialogTitle>Add Price Entry</DialogTitle></DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
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
            <div className="grid grid-cols-2 gap-4">
              <FormField control={form.control} name="tier" render={({ field }) => (
                <FormItem><FormLabel>Tier</FormLabel>
                  <Select onValueChange={field.onChange} value={field.value}>
                    <FormControl><SelectTrigger className="thin-border"><SelectValue /></SelectTrigger></FormControl>
                    <SelectContent>
                      <SelectItem value="retail">Retail</SelectItem>
                      <SelectItem value="wholesale">Wholesale</SelectItem>
                      <SelectItem value="bulk">Bulk</SelectItem>
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )} />
              <FormField control={form.control} name="min_quantity" render={({ field }) => (
                <FormItem><FormLabel>Min Quantity</FormLabel>
                  <FormControl><Input type="number" min={1} className="thin-border" {...field} /></FormControl>
                  <FormMessage />
                </FormItem>
              )} />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <FormField control={form.control} name="price_per_clone" render={({ field }) => (
                <FormItem><FormLabel>Price per Clone</FormLabel>
                  <FormControl><Input className="thin-border" placeholder="0.00" {...field} /></FormControl>
                  <FormMessage />
                </FormItem>
              )} />
              <FormField control={form.control} name="currency" render={({ field }) => (
                <FormItem><FormLabel>Currency</FormLabel>
                  <Select onValueChange={(v) => field.onChange(Number(v))} value={field.value?.toString() ?? ""}>
                    <FormControl><SelectTrigger className="thin-border"><SelectValue placeholder="Select" /></SelectTrigger></FormControl>
                    <SelectContent>
                      {currencies?.results.map((c) => <SelectItem key={c.id} value={c.id.toString()}>{c.code}</SelectItem>)}
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )} />
            </div>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>Cancel</Button>
              <Button type="submit" disabled={create.isPending}>{create.isPending ? "Saving..." : "Add Price"}</Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}

export default function PriceListsPage() {
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [search, setSearch] = useState("")
  const [open, setOpen] = useState(false)

  const { data, isLoading } = usePriceLists({ page, page_size: pageSize, search })

  const columns = [
    { key: "strain_name", label: "Strain", render: (pl: PriceList) => <span className="font-medium">{pl.strain_name}</span> },
    { key: "tier", label: "Tier", render: (pl: PriceList) => tierLabels[pl.tier] ?? pl.tier },
    {
      key: "price_per_clone",
      label: "Price / Clone",
      render: (pl: PriceList) => (
        <span className="data-value font-medium">{pl.currency_code} {Number.parseFloat(pl.price_per_clone).toLocaleString()}</span>
      ),
    },
    { key: "min_quantity", label: "Min Qty", render: (pl: PriceList) => <span className="data-value">{pl.min_quantity}</span> },
    { key: "is_active", label: "Status", render: (pl: PriceList) => <StatusBadge status={pl.is_active ? "Active" : "Inactive"} /> },
  ]

  return (
    <div>
      <PageHeader
        title="Price Lists"
        description="Manage strain pricing by customer tier"
        action={<Button onClick={() => setOpen(true)}><Plus className="w-4 h-4 mr-2" />Add Price</Button>}
      />
      <DataTable columns={columns} data={data?.results || []} loading={isLoading} searchPlaceholder="Search price lists..." onSearch={setSearch}
        pagination={data ? { currentPage: page, totalPages: Math.ceil(data.count / pageSize), pageSize, totalItems: data.count, onPageChange: setPage, onPageSizeChange: setPageSize } : undefined}
      />
      <AddPriceDialog open={open} onOpenChange={setOpen} />
    </div>
  )
}
