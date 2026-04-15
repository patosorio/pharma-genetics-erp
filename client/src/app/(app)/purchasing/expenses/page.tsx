"use client"

import { useState } from "react"
import { Plus, Search } from "lucide-react"
import { format } from "date-fns"
import { toast } from "sonner"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import {
  useExpenses,
  useCreateExpense,
  useUpdateExpense,
  useDeleteExpense,
  useApproveExpenseInvoice,
  useRecordExpensePayment,
  useExpenseCategories,
  useExpenseSubcategoriesByCategory,
  useBatchUpdateExpensesCategory,
  useSuppliers,
} from "@/hooks/use-purchasing"
import { useLocations } from "@/hooks/use-locations"
import { useCurrencies } from "@/hooks/use-currencies"
import { useTaxTypes } from "@/hooks/use-tax-types"
import { PageHeader } from "@/components/layout/page-header"
import { DataTable } from "@/components/common/data-table"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog"
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import type { Expense } from "@/lib/types/purchasing"

const TYPE_COLORS = {
  opex: "border-[#5A7A8C] text-[#5A7A8C] bg-[#5A7A8C]/10",
  capex: "border-[#B8A361] text-[#B8A361] bg-[#B8A361]/10",
  cogs: "border-[#3D4F2F] text-[#3D4F2F] bg-[#3D4F2F]/10",
} as const

const STATUS_COLORS: Record<string, string> = {
  pending: "border-yellow-500 text-yellow-600 bg-yellow-50",
  approved: "border-blue-500 text-blue-600 bg-blue-50",
  paid: "border-green-600 text-green-700 bg-green-50",
  partially_paid: "border-orange-500 text-orange-600 bg-orange-50",
  overdue: "border-red-500 text-red-600 bg-red-50",
  cancelled: "border-gray-400 text-gray-500 bg-gray-50",
}

// ── Shared: cascading category/subcategory fields ──────────────────────────

function CategorySubcategoryFields({
  form,
  categoryFieldName = "category",
  subcategoryFieldName = "subcategory",
}: {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  form: any
  categoryFieldName?: string
  subcategoryFieldName?: string
}) {
  const selectedCategory = form.watch(categoryFieldName)
  const { data: categories } = useExpenseCategories({ page_size: 200, is_active: true })
  const { data: subcategories } = useExpenseSubcategoriesByCategory(selectedCategory ?? null)

  return (
    <div className="grid grid-cols-2 gap-4">
      <FormField control={form.control} name={categoryFieldName} render={({ field }) => (
        <FormItem><FormLabel>Category</FormLabel>
          <Select
            onValueChange={(v) => { field.onChange(Number(v)); form.setValue(subcategoryFieldName, undefined) }}
            value={field.value?.toString() ?? ""}
          >
            <FormControl><SelectTrigger className="thin-border"><SelectValue placeholder="Select category" /></SelectTrigger></FormControl>
            <SelectContent>
              {categories?.results.map((c) => (
                <SelectItem key={c.id} value={c.id.toString()}>{c.name}</SelectItem>
              ))}
            </SelectContent>
          </Select>
          <FormMessage />
        </FormItem>
      )} />
      <FormField control={form.control} name={subcategoryFieldName} render={({ field }) => (
        <FormItem><FormLabel>Subcategory</FormLabel>
          <Select
            onValueChange={(v) => field.onChange(v ? Number(v) : undefined)}
            value={field.value?.toString() ?? ""}
            disabled={!selectedCategory}
          >
            <FormControl><SelectTrigger className="thin-border"><SelectValue placeholder={selectedCategory ? "Select subcategory" : "Pick a category first"} /></SelectTrigger></FormControl>
            <SelectContent>
              <SelectItem value="">— None —</SelectItem>
              {subcategories?.results.map((s) => (
                <SelectItem key={s.id} value={s.id.toString()}>
                  {s.name}
                  <span className="ml-2 text-muted-foreground text-xs">{s.expense_type.toUpperCase()}</span>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <FormMessage />
        </FormItem>
      )} />
    </div>
  )
}

// ── Add Expense Dialog ─────────────────────────────────────────────────────

const expenseSchema = z.object({
  category: z.coerce.number({ required_error: "Category is required" }),
  subcategory: z.coerce.number().optional(),
  location: z.coerce.number({ required_error: "Location is required" }),
  expense_date: z.string().min(1, "Date is required"),
  amount: z.string().min(1, "Amount is required"),
  currency: z.coerce.number({ required_error: "Currency is required" }),
  description: z.string().min(1, "Description is required"),
  supplier: z.coerce.number().optional(),
})
type ExpenseFormValues = z.infer<typeof expenseSchema>

function ExpenseFormFields({
  form,
  submitLabel,
  isPending,
  onCancel,
}: {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  form: any
  submitLabel: string
  isPending: boolean
  onCancel: () => void
}) {
  const { data: suppliers } = useSuppliers({ page_size: 200 })
  const { data: locations } = useLocations({ page_size: 100 })
  const { data: currencies } = useCurrencies({ page_size: 50 })
  return (
    <>
      <CategorySubcategoryFields form={form} />
      <FormField control={form.control} name="description" render={({ field }) => (
        <FormItem><FormLabel>Description</FormLabel>
          <FormControl><Input className="thin-border" placeholder="Monthly electricity bill" {...field} /></FormControl>
          <FormMessage />
        </FormItem>
      )} />
      <div className="grid grid-cols-2 gap-4">
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
        <FormField control={form.control} name="expense_date" render={({ field }) => (
          <FormItem><FormLabel>Date</FormLabel>
            <FormControl><Input type="date" className="thin-border" {...field} /></FormControl>
            <FormMessage />
          </FormItem>
        )} />
      </div>
      <div className="grid grid-cols-2 gap-4">
        <FormField control={form.control} name="amount" render={({ field }) => (
          <FormItem><FormLabel>Amount</FormLabel>
            <FormControl><Input className="thin-border" placeholder="0.00" {...field} /></FormControl>
            <FormMessage />
          </FormItem>
        )} />
        <FormField control={form.control} name="currency" render={({ field }) => (
          <FormItem><FormLabel>Currency</FormLabel>
            <Select onValueChange={(v) => field.onChange(Number(v))} value={field.value?.toString() ?? ""}>
              <FormControl><SelectTrigger className="thin-border"><SelectValue placeholder="THB" /></SelectTrigger></FormControl>
              <SelectContent>
                {currencies?.results.map((c) => <SelectItem key={c.id} value={c.id.toString()}>{c.code}</SelectItem>)}
              </SelectContent>
            </Select>
            <FormMessage />
          </FormItem>
        )} />
      </div>
      <FormField control={form.control} name="supplier" render={({ field }) => (
        <FormItem><FormLabel>Supplier (optional)</FormLabel>
          <Select onValueChange={(v) => field.onChange(v ? Number(v) : undefined)} value={field.value?.toString() ?? ""}>
            <FormControl><SelectTrigger className="thin-border"><SelectValue placeholder="None" /></SelectTrigger></FormControl>
            <SelectContent>
              <SelectItem value="">None</SelectItem>
              {suppliers?.results.map((s) => <SelectItem key={s.id} value={s.id.toString()}>{s.contact_name}</SelectItem>)}
            </SelectContent>
          </Select>
          <FormMessage />
        </FormItem>
      )} />
      <DialogFooter>
        <Button type="button" variant="outline" onClick={onCancel}>Cancel</Button>
        <Button type="submit" disabled={isPending}>{isPending ? "Saving..." : submitLabel}</Button>
      </DialogFooter>
    </>
  )
}

function RecordExpenseDialog({ open, onOpenChange }: { open: boolean; onOpenChange: (v: boolean) => void }) {
  const create = useCreateExpense()
  const form = useForm<ExpenseFormValues>({
    resolver: zodResolver(expenseSchema),
    defaultValues: { expense_date: new Date().toISOString().split("T")[0], amount: "", description: "" },
  })
  const onSubmit = async (values: ExpenseFormValues) => {
    try {
      await create.mutateAsync({ ...values, document_type: "expense" })
      toast.success("Expense recorded"); form.reset(); onOpenChange(false)
    } catch { toast.error("Failed to record expense.") }
  }
  return (
    <Dialog open={open} onOpenChange={(v) => { if (!v) form.reset(); onOpenChange(v) }}>
      <DialogContent className="max-w-lg">
        <DialogHeader><DialogTitle>Record Expense</DialogTitle></DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <ExpenseFormFields form={form} submitLabel="Record Expense" isPending={create.isPending} onCancel={() => { form.reset(); onOpenChange(false) }} />
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}

function EditExpenseDialog({
  expense,
  open,
  onOpenChange,
}: {
  expense: Expense
  open: boolean
  onOpenChange: (v: boolean) => void
}) {
  const update = useUpdateExpense()
  const form = useForm<ExpenseFormValues>({
    resolver: zodResolver(expenseSchema),
    defaultValues: {
      category: expense.category,
      subcategory: expense.subcategory ?? undefined,
      location: expense.location,
      expense_date: expense.expense_date,
      amount: expense.amount,
      currency: expense.currency,
      description: expense.description,
      supplier: expense.supplier ?? undefined,
    },
  })
  const onSubmit = async (values: ExpenseFormValues) => {
    try {
      await update.mutateAsync({ id: expense.id, data: values })
      toast.success(`${expense.expense_number} updated`); onOpenChange(false)
    } catch { toast.error("Failed to update expense.") }
  }
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-lg">
        <DialogHeader><DialogTitle>Edit {expense.expense_number}</DialogTitle></DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <ExpenseFormFields form={form} submitLabel="Save Changes" isPending={update.isPending} onCancel={() => onOpenChange(false)} />
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}

// ── Invoice dialogs ────────────────────────────────────────────────────────

const invoiceSchema = z.object({
  category: z.coerce.number({ required_error: "Category is required" }),
  subcategory: z.coerce.number().optional(),
  supplier: z.coerce.number({ required_error: "Supplier is required" }),
  location: z.coerce.number({ required_error: "Location is required" }),
  expense_date: z.string().min(1, "Invoice date is required"),
  due_date: z.string().min(1, "Due date is required"),
  invoice_reference: z.string().optional(),
  amount: z.string().min(1, "Base amount is required"),
  retention_amount: z.string().optional(),
  currency: z.coerce.number({ required_error: "Currency is required" }),
  tax_type: z.coerce.number().optional(),
  description: z.string().min(1, "Description is required"),
})
type InvoiceFormValues = z.infer<typeof invoiceSchema>

function InvoiceFormFields({
  form,
  submitLabel,
  isPending,
  onCancel,
}: {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  form: any
  submitLabel: string
  isPending: boolean
  onCancel: () => void
}) {
  const { data: suppliers } = useSuppliers({ page_size: 200 })
  const { data: locations } = useLocations({ page_size: 100 })
  const { data: currencies } = useCurrencies({ page_size: 50 })
  const { data: taxTypes } = useTaxTypes({ page_size: 50 })
  return (
    <>
      <CategorySubcategoryFields form={form} />
      <div className="grid grid-cols-2 gap-4">
        <FormField control={form.control} name="supplier" render={({ field }) => (
          <FormItem><FormLabel>Supplier</FormLabel>
            <Select onValueChange={(v) => field.onChange(Number(v))} value={field.value?.toString() ?? ""}>
              <FormControl><SelectTrigger className="thin-border"><SelectValue placeholder="Select supplier" /></SelectTrigger></FormControl>
              <SelectContent>
                {suppliers?.results.map((s) => <SelectItem key={s.id} value={s.id.toString()}>{s.contact_name}</SelectItem>)}
              </SelectContent>
            </Select>
            <FormMessage />
          </FormItem>
        )} />
        <FormField control={form.control} name="invoice_reference" render={({ field }) => (
          <FormItem><FormLabel>Supplier Invoice #</FormLabel>
            <FormControl><Input className="thin-border" placeholder="INV-001" {...field} /></FormControl>
            <FormMessage />
          </FormItem>
        )} />
      </div>
      <FormField control={form.control} name="description" render={({ field }) => (
        <FormItem><FormLabel>Description</FormLabel>
          <FormControl><Input className="thin-border" placeholder="What this invoice is for" {...field} /></FormControl>
          <FormMessage />
        </FormItem>
      )} />
      <div className="grid grid-cols-2 gap-4">
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
        <FormField control={form.control} name="currency" render={({ field }) => (
          <FormItem><FormLabel>Currency</FormLabel>
            <Select onValueChange={(v) => field.onChange(Number(v))} value={field.value?.toString() ?? ""}>
              <FormControl><SelectTrigger className="thin-border"><SelectValue placeholder="THB" /></SelectTrigger></FormControl>
              <SelectContent>
                {currencies?.results.map((c) => <SelectItem key={c.id} value={c.id.toString()}>{c.code}</SelectItem>)}
              </SelectContent>
            </Select>
            <FormMessage />
          </FormItem>
        )} />
      </div>
      <div className="grid grid-cols-2 gap-4">
        <FormField control={form.control} name="expense_date" render={({ field }) => (
          <FormItem><FormLabel>Invoice Date</FormLabel>
            <FormControl><Input type="date" className="thin-border" {...field} /></FormControl>
            <FormMessage />
          </FormItem>
        )} />
        <FormField control={form.control} name="due_date" render={({ field }) => (
          <FormItem><FormLabel>Due Date</FormLabel>
            <FormControl><Input type="date" className="thin-border" {...field} /></FormControl>
            <FormMessage />
          </FormItem>
        )} />
      </div>
      <div className="grid grid-cols-3 gap-4">
        <FormField control={form.control} name="amount" render={({ field }) => (
          <FormItem><FormLabel>Base Amount</FormLabel>
            <FormControl><Input className="thin-border" placeholder="0.00" {...field} /></FormControl>
            <FormMessage />
          </FormItem>
        )} />
        <FormField control={form.control} name="tax_type" render={({ field }) => (
          <FormItem><FormLabel>VAT / Tax</FormLabel>
            <Select onValueChange={(v) => field.onChange(v ? Number(v) : undefined)} value={field.value?.toString() ?? ""}>
              <FormControl><SelectTrigger className="thin-border"><SelectValue placeholder="None" /></SelectTrigger></FormControl>
              <SelectContent>
                <SelectItem value="">None</SelectItem>
                {taxTypes?.results.map((t) => <SelectItem key={t.id} value={t.id.toString()}>{t.name} ({t.rate}%)</SelectItem>)}
              </SelectContent>
            </Select>
            <FormMessage />
          </FormItem>
        )} />
        <FormField control={form.control} name="retention_amount" render={({ field }) => (
          <FormItem><FormLabel>Retention</FormLabel>
            <FormControl><Input className="thin-border" placeholder="0.00" {...field} /></FormControl>
            <FormMessage />
          </FormItem>
        )} />
      </div>
      <DialogFooter>
        <Button type="button" variant="outline" onClick={onCancel}>Cancel</Button>
        <Button type="submit" disabled={isPending}>{isPending ? "Saving..." : submitLabel}</Button>
      </DialogFooter>
    </>
  )
}

function RecordInvoiceDialog({ open, onOpenChange }: { open: boolean; onOpenChange: (v: boolean) => void }) {
  const create = useCreateExpense()
  const form = useForm<InvoiceFormValues>({
    resolver: zodResolver(invoiceSchema),
    defaultValues: { expense_date: new Date().toISOString().split("T")[0], amount: "", retention_amount: "0", invoice_reference: "", description: "" },
  })
  const onSubmit = async (values: InvoiceFormValues) => {
    try {
      await create.mutateAsync({ ...values, document_type: "invoice" })
      toast.success("Invoice recorded"); form.reset(); onOpenChange(false)
    } catch { toast.error("Failed to record invoice.") }
  }
  return (
    <Dialog open={open} onOpenChange={(v) => { if (!v) form.reset(); onOpenChange(v) }}>
      <DialogContent className="max-w-lg">
        <DialogHeader><DialogTitle>Record Supplier Invoice</DialogTitle></DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <InvoiceFormFields form={form} submitLabel="Record Invoice" isPending={create.isPending} onCancel={() => { form.reset(); onOpenChange(false) }} />
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}

function EditInvoiceDialog({
  expense,
  open,
  onOpenChange,
}: {
  expense: Expense
  open: boolean
  onOpenChange: (v: boolean) => void
}) {
  const update = useUpdateExpense()
  const form = useForm<InvoiceFormValues>({
    resolver: zodResolver(invoiceSchema),
    defaultValues: {
      category: expense.category,
      subcategory: expense.subcategory ?? undefined,
      supplier: expense.supplier ?? undefined,
      location: expense.location,
      expense_date: expense.expense_date,
      due_date: expense.due_date ?? "",
      invoice_reference: expense.invoice_reference ?? "",
      amount: expense.amount,
      retention_amount: expense.retention_amount ?? "0",
      currency: expense.currency,
      tax_type: expense.tax_type ?? undefined,
      description: expense.description,
    },
  })
  const onSubmit = async (values: InvoiceFormValues) => {
    try {
      await update.mutateAsync({ id: expense.id, data: values })
      toast.success(`${expense.expense_number} updated`); onOpenChange(false)
    } catch { toast.error("Failed to update invoice.") }
  }
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-lg">
        <DialogHeader><DialogTitle>Edit {expense.expense_number}</DialogTitle></DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <InvoiceFormFields form={form} submitLabel="Save Changes" isPending={update.isPending} onCancel={() => onOpenChange(false)} />
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}

// ── Record Payment Dialog ──────────────────────────────────────────────────

function RecordPaymentDialog({
  expense,
  open,
  onOpenChange,
}: {
  expense: Expense
  open: boolean
  onOpenChange: (v: boolean) => void
}) {
  const recordPayment = useRecordExpensePayment()
  const [amount, setAmount] = useState("")
  const handleSubmit = async () => {
    if (!amount || Number(amount) <= 0) { toast.error("Enter a valid amount."); return }
    try {
      await recordPayment.mutateAsync({ id: expense.id, amount })
      toast.success("Payment recorded"); setAmount(""); onOpenChange(false)
    } catch { toast.error("Failed to record payment.") }
  }
  const balance = Number.parseFloat(expense.balance_due ?? "0")
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-sm">
        <DialogHeader><DialogTitle>Record Payment</DialogTitle></DialogHeader>
        <div className="space-y-4">
          <p className="text-sm text-muted-foreground">
            {expense.expense_number} — Balance due:{" "}
            <span className="font-medium text-foreground">{expense.currency_code} {balance.toLocaleString()}</span>
          </p>
          <div>
            <label className="text-sm font-medium">Payment Amount</label>
            <Input className="thin-border mt-1" placeholder="0.00" type="number" value={amount} onChange={(e) => setAmount(e.target.value)} />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => onOpenChange(false)}>Cancel</Button>
            <Button onClick={handleSubmit} disabled={recordPayment.isPending}>
              {recordPayment.isPending ? "Saving..." : "Record Payment"}
            </Button>
          </DialogFooter>
        </div>
      </DialogContent>
    </Dialog>
  )
}

// ── Delete Confirm Dialog ──────────────────────────────────────────────────

function DeleteExpenseDialog({
  expense,
  open,
  onOpenChange,
}: {
  expense: Expense
  open: boolean
  onOpenChange: (v: boolean) => void
}) {
  const deleteMutation = useDeleteExpense()
  const handleDelete = async () => {
    try {
      await deleteMutation.mutateAsync(expense.id)
      toast.success(`${expense.expense_number} deleted`); onOpenChange(false)
    } catch { toast.error("Failed to delete.") }
  }
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-sm">
        <DialogHeader><DialogTitle>Delete {expense.document_type === "invoice" ? "Invoice" : "Expense"}</DialogTitle></DialogHeader>
        <p className="text-sm text-muted-foreground">
          Delete <strong>{expense.expense_number}</strong>? This action cannot be undone.
        </p>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>Cancel</Button>
          <Button variant="destructive" onClick={handleDelete} disabled={deleteMutation.isPending}>
            {deleteMutation.isPending ? "Deleting..." : "Delete"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

// ── Batch Category Dialog ──────────────────────────────────────────────────

function BatchCategoryDialog({
  ids,
  open,
  onOpenChange,
}: {
  ids: number[]
  open: boolean
  onOpenChange: (v: boolean) => void
}) {
  const [categoryId, setCategoryId] = useState<number | undefined>()
  const [subcategoryId, setSubcategoryId] = useState<number | undefined>()
  const { data: categories } = useExpenseCategories({ page_size: 200, is_active: true })
  const { data: subcategories } = useExpenseSubcategoriesByCategory(categoryId ?? null)
  const batchUpdate = useBatchUpdateExpensesCategory()

  const handleApply = async () => {
    if (!categoryId) { toast.error("Select a category first."); return }
    try {
      await batchUpdate.mutateAsync({ ids, category: categoryId, subcategory: subcategoryId ?? null })
      toast.success(`Updated category on ${ids.length} expense(s)`)
      onOpenChange(false)
    } catch { toast.error("Batch update failed.") }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-sm">
        <DialogHeader><DialogTitle>Change Category</DialogTitle></DialogHeader>
        <p className="text-sm text-muted-foreground">
          Reassign category on <strong>{ids.length}</strong> selected record(s).
        </p>
        <div className="space-y-3">
          <div>
            <label className="text-sm font-medium">Category <span className="text-destructive">*</span></label>
            <Select
              value={categoryId?.toString() ?? ""}
              onValueChange={(v) => { setCategoryId(Number(v)); setSubcategoryId(undefined) }}
            >
              <SelectTrigger className="thin-border mt-1"><SelectValue placeholder="Select category" /></SelectTrigger>
              <SelectContent>
                {categories?.results.map((c) => <SelectItem key={c.id} value={c.id.toString()}>{c.name}</SelectItem>)}
              </SelectContent>
            </Select>
          </div>
          <div>
            <label className="text-sm font-medium">Subcategory</label>
            <Select
              value={subcategoryId?.toString() ?? ""}
              onValueChange={(v) => setSubcategoryId(v ? Number(v) : undefined)}
              disabled={!categoryId}
            >
              <SelectTrigger className="thin-border mt-1"><SelectValue placeholder={categoryId ? "Optional" : "Pick a category first"} /></SelectTrigger>
              <SelectContent>
                <SelectItem value="">— None —</SelectItem>
                {subcategories?.results.map((s) => (
                  <SelectItem key={s.id} value={s.id.toString()}>
                    {s.name} <span className="text-muted-foreground text-xs">{s.expense_type.toUpperCase()}</span>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>Cancel</Button>
          <Button onClick={handleApply} disabled={batchUpdate.isPending || !categoryId}>
            {batchUpdate.isPending ? "Applying..." : "Apply"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

// ── Page ───────────────────────────────────────────────────────────────────

type DocFilter = "all" | "expense" | "invoice"

export default function ExpensesPage() {
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [search, setSearch] = useState("")
  const [docFilter, setDocFilter] = useState<DocFilter>("all")
  const [addExpenseOpen, setAddExpenseOpen] = useState(false)
  const [addInvoiceOpen, setAddInvoiceOpen] = useState(false)
  const [editTarget, setEditTarget] = useState<Expense | null>(null)
  const [deleteTarget, setDeleteTarget] = useState<Expense | null>(null)
  const [paymentTarget, setPaymentTarget] = useState<Expense | null>(null)
  const [selectedIds, setSelectedIds] = useState<Set<number | string>>(new Set())
  const [batchCategoryOpen, setBatchCategoryOpen] = useState(false)

  const approve = useApproveExpenseInvoice()

  const { data, isLoading } = useExpenses({
    page,
    page_size: pageSize,
    search,
    ordering: "-expense_date",
    ...(docFilter !== "all" ? { document_type: docFilter } : {}),
  })

  const handleApprove = async (e: Expense) => {
    try {
      await approve.mutateAsync(e.id)
      toast.success(`${e.expense_number} approved`)
    } catch { toast.error("Failed to approve invoice.") }
  }

  const columns = [
    {
      key: "expense_number",
      label: "Document #",
      render: (e: Expense) => (
        <div className="flex items-center gap-2">
          <span className="font-medium">{e.expense_number}</span>
          <Badge variant="outline" className={`thin-border text-xs ${e.document_type === "invoice" ? "border-violet-500 text-violet-600 bg-violet-50" : "border-slate-400 text-slate-500 bg-slate-50"}`}>
            {e.document_type === "invoice" ? "INV" : "EXP"}
          </Badge>
        </div>
      ),
    },
    {
      key: "expense_date",
      label: "Date",
      render: (e: Expense) => format(new Date(e.expense_date), "dd MMM yyyy"),
    },
    {
      key: "category_name",
      label: "Category",
      render: (e: Expense) => (
        <div>
          <span className="text-sm">{e.category_name}</span>
          {e.subcategory_name && (
            <div className="text-xs text-muted-foreground">{e.subcategory_name}</div>
          )}
        </div>
      ),
    },
    {
      key: "expense_type",
      label: "Type",
      render: (e: Expense) => {
        const type = e.subcategory_expense_type ?? e.category_type
        return (
          <Badge variant="outline" className={`thin-border text-xs ${TYPE_COLORS[type] ?? ""}`}>
            {type.toUpperCase()}
          </Badge>
        )
      },
    },
    {
      key: "supplier_name",
      label: "Supplier",
      render: (e: Expense) => e.supplier_name ?? "—",
    },
    {
      key: "description",
      label: "Description",
      render: (e: Expense) => (
        <span className="text-muted-foreground text-sm line-clamp-1">{e.description}</span>
      ),
    },
    {
      key: "amount",
      label: "Amount",
      render: (e: Expense) => (
        <span className="data-value font-medium">
          {e.currency_code} {Number.parseFloat(e.document_type === "invoice" ? e.total_amount : e.amount).toLocaleString()}
        </span>
      ),
    },
    {
      key: "status",
      label: "Status",
      render: (e: Expense) => {
        if (e.document_type !== "invoice" || !e.status) return <span className="text-muted-foreground text-sm">—</span>
        return (
          <Badge variant="outline" className={`thin-border text-xs ${STATUS_COLORS[e.status] ?? ""}`}>
            {e.status_display ?? e.status}
          </Badge>
        )
      },
    },
    {
      key: "actions",
      label: "",
      render: (e: Expense) => (
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="sm" className="h-7 w-7 p-0">⋮</Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem onClick={() => setEditTarget(e)}>Edit</DropdownMenuItem>
            {e.document_type === "invoice" && e.status === "pending" && (
              <DropdownMenuItem onClick={() => handleApprove(e)}>Approve</DropdownMenuItem>
            )}
            {e.document_type === "invoice" && (e.status === "approved" || e.status === "partially_paid") && (
              <DropdownMenuItem onClick={() => setPaymentTarget(e)}>Record Payment</DropdownMenuItem>
            )}
            <DropdownMenuSeparator />
            <DropdownMenuItem
              className="text-destructive focus:text-destructive"
              onClick={() => setDeleteTarget(e)}
            >
              Delete
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      ),
    },
  ]

  return (
    <div>
      <PageHeader
        title="Expenses & Invoices"
        description="Unified ledger — EXP for expenses, INV for supplier invoices"
        action={
          <>
            <Button variant="outline" className="thin-border" onClick={() => setAddInvoiceOpen(true)}>
              <Plus className="w-4 h-4 mr-2" />Record Invoice
            </Button>
            <Button onClick={() => setAddExpenseOpen(true)}>
              <Plus className="w-4 h-4 mr-2" />Record Expense
            </Button>
          </>
        }
        filters={
          <>
            <div className="relative w-72">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <Input
                placeholder="Search by number or description..."
                value={search}
                onChange={(e) => { setSearch(e.target.value); setPage(1) }}
                className="pl-9 thin-border"
              />
            </div>
            <div className="flex gap-1">
              {(["all", "expense", "invoice"] as const).map((f) => (
                <Button
                  key={f}
                  variant={docFilter === f ? "default" : "outline"}
                  size="sm"
                  className={docFilter === f ? "" : "thin-border"}
                  onClick={() => { setDocFilter(f); setPage(1) }}
                >
                  {f === "all" ? "All" : f === "expense" ? "Expenses" : "Invoices"}
                </Button>
              ))}
            </div>
          </>
        }
      />

      <DataTable
        columns={columns}
        data={data?.results ?? []}
        loading={isLoading}
        emptyMessage="No records found"
        selectable
        selectedIds={selectedIds}
        onSelectionChange={setSelectedIds}
        batchActions={
          <Button
            variant="outline"
            size="sm"
            className="thin-border"
            onClick={() => setBatchCategoryOpen(true)}
          >
            Change Category
          </Button>
        }
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

      <RecordExpenseDialog open={addExpenseOpen} onOpenChange={setAddExpenseOpen} />
      <RecordInvoiceDialog open={addInvoiceOpen} onOpenChange={setAddInvoiceOpen} />

      {editTarget && editTarget.document_type === "expense" && (
        <EditExpenseDialog
          key={editTarget.id}
          expense={editTarget}
          open={!!editTarget}
          onOpenChange={(v) => { if (!v) setEditTarget(null) }}
        />
      )}
      {editTarget && editTarget.document_type === "invoice" && (
        <EditInvoiceDialog
          key={editTarget.id}
          expense={editTarget}
          open={!!editTarget}
          onOpenChange={(v) => { if (!v) setEditTarget(null) }}
        />
      )}
      {deleteTarget && (
        <DeleteExpenseDialog
          expense={deleteTarget}
          open={!!deleteTarget}
          onOpenChange={(v) => { if (!v) setDeleteTarget(null) }}
        />
      )}
      {paymentTarget && (
        <RecordPaymentDialog
          expense={paymentTarget}
          open={!!paymentTarget}
          onOpenChange={(v) => { if (!v) setPaymentTarget(null) }}
        />
      )}
      <BatchCategoryDialog
        ids={[...selectedIds] as number[]}
        open={batchCategoryOpen}
        onOpenChange={(v) => {
          setBatchCategoryOpen(v)
          if (!v) setSelectedIds(new Set())
        }}
      />
    </div>
  )
}
