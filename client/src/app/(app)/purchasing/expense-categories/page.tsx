"use client"

import { useState } from "react"
import { Plus, ChevronRight } from "lucide-react"
import { toast } from "sonner"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import {
  useExpenseCategories,
  useCreateExpenseCategory,
  useCreateExpenseSubcategory,
} from "@/hooks/use-purchasing"
import { PageHeader } from "@/components/layout/page-header"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog"
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Skeleton } from "@/components/ui/skeleton"
import type { ExpenseCategory, ExpenseSubcategory } from "@/lib/types/purchasing"

const TYPE_COLORS = {
  opex: "border-[#5A7A8C] text-[#5A7A8C] bg-[#5A7A8C]/10",
  capex: "border-[#B8A361] text-[#B8A361] bg-[#B8A361]/10",
  cogs: "border-[#3D4F2F] text-[#3D4F2F] bg-[#3D4F2F]/10",
} as const

const TYPE_LABELS = { opex: "OPEX", capex: "CAPEX", cogs: "COGS" }

// ── Add Category Dialog ────────────────────────────────────────────────────

const categorySchema = z.object({
  name: z.string().min(1, "Name is required"),
  category_type: z.enum(["opex", "capex", "cogs"]),
})
type CategoryFormValues = z.infer<typeof categorySchema>

function AddCategoryDialog({ open, onOpenChange }: { open: boolean; onOpenChange: (v: boolean) => void }) {
  const create = useCreateExpenseCategory()
  const form = useForm<CategoryFormValues>({
    resolver: zodResolver(categorySchema),
    defaultValues: { name: "", category_type: "opex" },
  })

  const onSubmit = async (values: CategoryFormValues) => {
    try {
      await create.mutateAsync(values)
      toast.success("Category added")
      form.reset()
      onOpenChange(false)
    } catch {
      toast.error("Failed to add category.")
    }
  }

  return (
    <Dialog open={open} onOpenChange={(v) => { if (!v) form.reset(); onOpenChange(v) }}>
      <DialogContent>
        <DialogHeader><DialogTitle>Add Category</DialogTitle></DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField control={form.control} name="name" render={({ field }) => (
              <FormItem><FormLabel>Category Name</FormLabel>
                <FormControl><Input className="thin-border" placeholder="Utilidades" {...field} /></FormControl>
                <FormMessage />
              </FormItem>
            )} />
            <FormField control={form.control} name="category_type" render={({ field }) => (
              <FormItem><FormLabel>Default Type</FormLabel>
                <Select onValueChange={field.onChange} value={field.value}>
                  <FormControl><SelectTrigger className="thin-border"><SelectValue /></SelectTrigger></FormControl>
                  <SelectContent>
                    <SelectItem value="opex">OPEX — Operating Expense</SelectItem>
                    <SelectItem value="capex">CAPEX — Capital Expenditure</SelectItem>
                    <SelectItem value="cogs">COGS — Cost of Goods Sold</SelectItem>
                  </SelectContent>
                </Select>
                <FormMessage />
              </FormItem>
            )} />
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>Cancel</Button>
              <Button type="submit" disabled={create.isPending}>{create.isPending ? "Saving..." : "Add Category"}</Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}

// ── Add Subcategory Dialog ─────────────────────────────────────────────────

const subcategorySchema = z.object({
  name: z.string().min(1, "Name is required"),
  expense_type: z.enum(["opex", "capex", "cogs"]),
})
type SubcategoryFormValues = z.infer<typeof subcategorySchema>

function AddSubcategoryDialog({
  category,
  open,
  onOpenChange,
}: {
  category: ExpenseCategory
  open: boolean
  onOpenChange: (v: boolean) => void
}) {
  const create = useCreateExpenseSubcategory()
  const form = useForm<SubcategoryFormValues>({
    resolver: zodResolver(subcategorySchema),
    defaultValues: { name: "", expense_type: category.category_type },
  })

  const onSubmit = async (values: SubcategoryFormValues) => {
    try {
      await create.mutateAsync({ ...values, category: category.id })
      toast.success("Subcategory added")
      form.reset()
      onOpenChange(false)
    } catch {
      toast.error("Failed to add subcategory.")
    }
  }

  return (
    <Dialog open={open} onOpenChange={(v) => { if (!v) form.reset(); onOpenChange(v) }}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Add Subcategory to <span className="text-muted-foreground">{category.name}</span></DialogTitle>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField control={form.control} name="name" render={({ field }) => (
              <FormItem><FormLabel>Subcategory Name</FormLabel>
                <FormControl><Input className="thin-border" placeholder="Electricidad Nave" {...field} /></FormControl>
                <FormMessage />
              </FormItem>
            )} />
            <FormField control={form.control} name="expense_type" render={({ field }) => (
              <FormItem><FormLabel>Type</FormLabel>
                <Select onValueChange={field.onChange} value={field.value}>
                  <FormControl><SelectTrigger className="thin-border"><SelectValue /></SelectTrigger></FormControl>
                  <SelectContent>
                    <SelectItem value="opex">OPEX — Operating Expense</SelectItem>
                    <SelectItem value="capex">CAPEX — Capital Expenditure</SelectItem>
                    <SelectItem value="cogs">COGS — Cost of Goods Sold</SelectItem>
                  </SelectContent>
                </Select>
                <FormMessage />
              </FormItem>
            )} />
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>Cancel</Button>
              <Button type="submit" disabled={create.isPending}>{create.isPending ? "Saving..." : "Add Subcategory"}</Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}

// ── Category Row ───────────────────────────────────────────────────────────

function CategoryRow({ category }: { category: ExpenseCategory }) {
  const [expanded, setExpanded] = useState(false)
  const [subDialogOpen, setSubDialogOpen] = useState(false)
  const subs = category.subcategories ?? []

  const typeCounts = subs.reduce<Record<string, number>>((acc, s) => {
    acc[s.expense_type] = (acc[s.expense_type] ?? 0) + 1
    return acc
  }, {})

  return (
    <>
      <div className="border rounded-lg overflow-hidden">
        <div
          className="flex items-center gap-3 px-4 py-3 cursor-pointer hover:bg-muted/30 transition-colors"
          onClick={() => setExpanded((v) => !v)}
        >
          <ChevronRight
            className={`w-4 h-4 text-muted-foreground flex-shrink-0 transition-transform ${expanded ? "rotate-90" : ""}`}
          />
          <span className="font-medium flex-1">{category.name}</span>
          <div className="flex items-center gap-2">
            {Object.entries(typeCounts).map(([type, count]) => (
              <Badge
                key={type}
                variant="outline"
                className={`thin-border text-xs ${TYPE_COLORS[type as keyof typeof TYPE_COLORS] ?? ""}`}
              >
                {count} {TYPE_LABELS[type as keyof typeof TYPE_LABELS] ?? type.toUpperCase()}
              </Badge>
            ))}
            {subs.length === 0 && (
              <span className="text-xs text-muted-foreground">{subs.length} subcategories</span>
            )}
          </div>
          <Button
            size="sm"
            variant="ghost"
            className="h-7 px-2 text-xs"
            onClick={(e) => { e.stopPropagation(); setSubDialogOpen(true) }}
          >
            <Plus className="w-3 h-3 mr-1" />
            Add
          </Button>
        </div>

        {expanded && subs.length > 0 && (
          <div className="border-t divide-y bg-muted/10">
            {subs.map((sub: ExpenseSubcategory) => (
              <div key={sub.id} className="flex items-center gap-3 px-4 py-2 pl-11">
                <span className="text-sm flex-1">{sub.name}</span>
                <Badge
                  variant="outline"
                  className={`thin-border text-xs ${TYPE_COLORS[sub.expense_type] ?? ""}`}
                >
                  {TYPE_LABELS[sub.expense_type] ?? sub.expense_type.toUpperCase()}
                </Badge>
              </div>
            ))}
          </div>
        )}

        {expanded && subs.length === 0 && (
          <div className="px-4 py-3 pl-11 text-sm text-muted-foreground border-t bg-muted/10">
            No subcategories yet.
          </div>
        )}
      </div>

      <AddSubcategoryDialog
        category={category}
        open={subDialogOpen}
        onOpenChange={setSubDialogOpen}
      />
    </>
  )
}

// ── Page ───────────────────────────────────────────────────────────────────

export default function ExpenseCategoriesPage() {
  const [categoryDialogOpen, setCategoryDialogOpen] = useState(false)
  const [typeFilter, setTypeFilter] = useState<"all" | "opex" | "capex" | "cogs">("all")

  const { data, isLoading } = useExpenseCategories({ page_size: 200 })

  const categories = data?.results ?? []
  const filtered =
    typeFilter === "all" ? categories : categories.filter((c) => c.category_type === typeFilter)

  const grouped = {
    capex: filtered.filter((c) => c.category_type === "capex"),
    opex: filtered.filter((c) => c.category_type === "opex"),
    cogs: filtered.filter((c) => c.category_type === "cogs"),
  }

  return (
    <div>
      <PageHeader
        title="Expense Categories"
        description="Manage your chart of accounts — Type → Category → Subcategory"
        action={
          <Button onClick={() => setCategoryDialogOpen(true)}>
            <Plus className="w-4 h-4 mr-2" />
            Add Category
          </Button>
        }
      />

      {/* Type filter tabs */}
      <div className="flex gap-2 mb-6">
        {(["all", "capex", "opex", "cogs"] as const).map((t) => (
          <Button
            key={t}
            variant={typeFilter === t ? "default" : "outline"}
            size="sm"
            className={typeFilter === t ? "" : "thin-border"}
            onClick={() => setTypeFilter(t)}
          >
            {t === "all" ? "All" : TYPE_LABELS[t]}
          </Button>
        ))}
      </div>

      {isLoading ? (
        <div className="space-y-2">
          {Array.from({ length: 8 }).map((_, i) => (
            <Skeleton key={i} className="h-12 w-full rounded-lg" />
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <p className="text-muted-foreground text-sm py-8 text-center">No categories found.</p>
      ) : (
        <div className="space-y-6">
          {(["capex", "opex", "cogs"] as const).map((type) => {
            const group = grouped[type]
            if (typeFilter !== "all" && typeFilter !== type) return null
            if (group.length === 0) return null
            return (
              <div key={type}>
                <div className="flex items-center gap-2 mb-3">
                  <Badge variant="outline" className={`thin-border ${TYPE_COLORS[type]}`}>
                    {TYPE_LABELS[type]}
                  </Badge>
                  <span className="text-sm text-muted-foreground">{group.length} categories</span>
                </div>
                <div className="space-y-2">
                  {group.map((cat) => (
                    <CategoryRow key={cat.id} category={cat} />
                  ))}
                </div>
              </div>
            )
          })}
        </div>
      )}

      <AddCategoryDialog open={categoryDialogOpen} onOpenChange={setCategoryDialogOpen} />
    </div>
  )
}
