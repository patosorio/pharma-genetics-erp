"use client"

import { useState } from "react"
import { Plus } from "lucide-react"
import { format } from "date-fns"
import { toast } from "sonner"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { usePricingTiers, useCreatePricingTier } from "@/hooks/use-pricing"
import { PageHeader } from "@/components/layout/page-header"
import { DataTable } from "@/components/common/data-table"
import { StatusBadge } from "@/components/common/status-badge"
import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog"
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import type { PricingTier } from "@/lib/types/pricing"

const schema = z.object({
  tier_name: z.enum(["retail", "wholesale", "bulk"]),
  min_quantity: z.coerce.number().min(1),
  max_quantity: z.coerce.number().optional(),
  price_per_clone: z.string().min(1, "Price is required"),
  effective_date: z.string().min(1, "Effective date is required"),
  annual_price_increase_pct: z.string().default("0.00"),
})
type FormValues = z.infer<typeof schema>

function AddTierDialog({ open, onOpenChange }: { open: boolean; onOpenChange: (v: boolean) => void }) {
  const create = useCreatePricingTier()
  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { tier_name: "wholesale", min_quantity: 1, price_per_clone: "", effective_date: new Date().toISOString().split("T")[0], annual_price_increase_pct: "0.00" },
  })

  const onSubmit = async (values: FormValues) => {
    try {
      await create.mutateAsync(values)
      toast.success("Pricing tier added")
      form.reset()
      onOpenChange(false)
    } catch {
      toast.error("Failed to add tier.")
    }
  }

  return (
    <Dialog open={open} onOpenChange={(v) => { if (!v) form.reset(); onOpenChange(v) }}>
      <DialogContent>
        <DialogHeader><DialogTitle>Add Pricing Tier</DialogTitle></DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <FormField control={form.control} name="tier_name" render={({ field }) => (
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
              <FormField control={form.control} name="price_per_clone" render={({ field }) => (
                <FormItem><FormLabel>Price / Clone (฿)</FormLabel>
                  <FormControl><Input className="thin-border" placeholder="0.00" {...field} /></FormControl>
                  <FormMessage />
                </FormItem>
              )} />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <FormField control={form.control} name="min_quantity" render={({ field }) => (
                <FormItem><FormLabel>Min Quantity</FormLabel>
                  <FormControl><Input type="number" min={1} className="thin-border" {...field} /></FormControl>
                  <FormMessage />
                </FormItem>
              )} />
              <FormField control={form.control} name="max_quantity" render={({ field }) => (
                <FormItem><FormLabel>Max Quantity (optional)</FormLabel>
                  <FormControl><Input type="number" min={1} className="thin-border" placeholder="Unlimited" value={field.value ?? ""} onChange={(e) => field.onChange(e.target.value ? Number(e.target.value) : undefined)} /></FormControl>
                  <FormMessage />
                </FormItem>
              )} />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <FormField control={form.control} name="effective_date" render={({ field }) => (
                <FormItem><FormLabel>Effective Date</FormLabel>
                  <FormControl><Input type="date" className="thin-border" {...field} /></FormControl>
                  <FormMessage />
                </FormItem>
              )} />
              <FormField control={form.control} name="annual_price_increase_pct" render={({ field }) => (
                <FormItem><FormLabel>Annual Increase %</FormLabel>
                  <FormControl><Input className="thin-border" placeholder="0.00" {...field} /></FormControl>
                  <FormMessage />
                </FormItem>
              )} />
            </div>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>Cancel</Button>
              <Button type="submit" disabled={create.isPending}>{create.isPending ? "Saving..." : "Add Tier"}</Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}

export default function PricingTiersPage() {
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [search, setSearch] = useState("")
  const [open, setOpen] = useState(false)

  const { data, isLoading } = usePricingTiers({ page, page_size: pageSize })

  const columns = [
    { key: "tier_name", label: "Tier", render: (t: PricingTier) => <span className="font-medium capitalize">{t.tier_name_display}</span> },
    { key: "min_quantity", label: "Min Qty", render: (t: PricingTier) => <span className="data-value">{t.min_quantity}</span> },
    { key: "max_quantity", label: "Max Qty", render: (t: PricingTier) => <span className="data-value">{t.max_quantity != null ? t.max_quantity : "Unlimited"}</span> },
    {
      key: "price_per_clone",
      label: "Price / Clone",
      render: (t: PricingTier) => <span className="data-value font-medium text-[#3D4F2F]">฿{Number.parseFloat(t.price_per_clone).toLocaleString()}</span>,
    },
    { key: "effective_date", label: "Effective", render: (t: PricingTier) => format(new Date(t.effective_date), "MMM d, yyyy") },
    { key: "end_date", label: "Expires", render: (t: PricingTier) => (t.end_date ? format(new Date(t.end_date), "MMM d, yyyy") : "—") },
    { key: "annual_price_increase_pct", label: "Annual Increase", render: (t: PricingTier) => <span className="data-value">{t.annual_price_increase_pct}%</span> },
    { key: "is_active", label: "Status", render: (t: PricingTier) => <StatusBadge status={t.is_active ? "Active" : "Inactive"} /> },
  ]

  return (
    <div>
      <PageHeader
        title="Pricing Tiers"
        description="Configure retail, wholesale and bulk pricing structures"
        action={<Button onClick={() => setOpen(true)}><Plus className="w-4 h-4 mr-2" />Add Tier</Button>}
      />
      <DataTable columns={columns} data={data?.results || []} loading={isLoading} searchPlaceholder="Search tiers..." onSearch={setSearch} emptyMessage="No pricing tiers configured"
        pagination={data ? { currentPage: page, totalPages: Math.ceil(data.count / pageSize), pageSize, totalItems: data.count, onPageChange: setPage, onPageSizeChange: setPageSize } : undefined}
      />
      <AddTierDialog open={open} onOpenChange={setOpen} />
    </div>
  )
}
