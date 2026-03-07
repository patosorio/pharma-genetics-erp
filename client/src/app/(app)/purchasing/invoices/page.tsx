"use client"

import { useState } from "react"
import { Plus, ChevronRight } from "lucide-react"
import { format } from "date-fns"
import { toast } from "sonner"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import {
  usePurchaseInvoices,
  useCreatePurchaseInvoice,
  useApprovePurchaseInvoice,
  useRecordPurchaseInvoicePayment,
  useSuppliers,
} from "@/hooks/use-purchasing"
import { useCurrencies } from "@/hooks/use-currencies"
import { PageHeader } from "@/components/layout/page-header"
import { DataTable } from "@/components/common/data-table"
import { PurchaseInvoiceStatusBadge } from "@/components/purchasing/purchase-invoice-status-badge"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import type { PurchaseInvoice } from "@/lib/types/purchasing"

const paymentSchema = z.object({
  amount: z.string().min(1, "Amount is required"),
})
type PaymentFormValues = z.infer<typeof paymentSchema>

const invoiceSchema = z.object({
  supplier: z.coerce.number({ required_error: "Supplier is required" }),
  invoice_date: z.string().min(1, "Invoice date is required"),
  due_date: z.string().min(1, "Due date is required"),
  base_amount: z.string().min(1, "Amount is required"),
  currency: z.coerce.number({ required_error: "Currency is required" }),
  notes: z.string().optional(),
})
type InvoiceFormValues = z.infer<typeof invoiceSchema>

function NewInvoiceDialog({ open, onOpenChange }: { open: boolean; onOpenChange: (v: boolean) => void }) {
  const create = useCreatePurchaseInvoice()
  const { data: suppliers } = useSuppliers({ page_size: 200 })
  const { data: currencies } = useCurrencies({ page_size: 50 })
  const form = useForm<InvoiceFormValues>({
    resolver: zodResolver(invoiceSchema),
    defaultValues: { invoice_date: new Date().toISOString().split("T")[0], due_date: "", base_amount: "", notes: "" },
  })

  const onSubmit = async (values: InvoiceFormValues) => {
    try {
      await create.mutateAsync(values)
      toast.success("Purchase invoice created")
      form.reset()
      onOpenChange(false)
    } catch {
      toast.error("Failed to create invoice.")
    }
  }

  return (
    <Dialog open={open} onOpenChange={(v) => { if (!v) form.reset(); onOpenChange(v) }}>
      <DialogContent>
        <DialogHeader><DialogTitle>New Purchase Invoice</DialogTitle></DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
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
            <div className="grid grid-cols-2 gap-4">
              <FormField control={form.control} name="invoice_date" render={({ field }) => (
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
            <div className="grid grid-cols-2 gap-4">
              <FormField control={form.control} name="base_amount" render={({ field }) => (
                <FormItem><FormLabel>Base Amount</FormLabel>
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
              <Button type="submit" disabled={create.isPending}>{create.isPending ? "Creating..." : "Create Invoice"}</Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}

export default function PurchaseInvoicesPage() {
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [search, setSearch] = useState("")
  const [open, setOpen] = useState(false)
  const [paymentInvoice, setPaymentInvoice] = useState<PurchaseInvoice | null>(null)

  const { data, isLoading } = usePurchaseInvoices({ page, page_size: pageSize, search, ordering: "-invoice_date" })
  const approve = useApprovePurchaseInvoice()
  const recordPayment = useRecordPurchaseInvoicePayment()

  const form = useForm<PaymentFormValues>({
    resolver: zodResolver(paymentSchema),
    defaultValues: { amount: "" },
  })

  const handleApprove = async (invoice: PurchaseInvoice) => {
    try {
      await approve.mutateAsync(invoice.id)
      toast.success(`Invoice ${invoice.invoice_number} approved`)
    } catch {
      toast.error("Action failed. Please try again.")
    }
  }

  const handleRecordPayment = async (values: PaymentFormValues) => {
    if (!paymentInvoice) return
    try {
      await recordPayment.mutateAsync({ id: paymentInvoice.id, amount: values.amount })
      toast.success(`Payment recorded for ${paymentInvoice.invoice_number}`)
      setPaymentInvoice(null)
      form.reset()
    } catch {
      toast.error("Failed to record payment.")
    }
  }

  const columns = [
    {
      key: "invoice_number",
      label: "Invoice #",
      render: (inv: PurchaseInvoice) => <span className="font-medium">{inv.invoice_number}</span>,
    },
    { key: "supplier_name", label: "Supplier" },
    {
      key: "invoice_date",
      label: "Date",
      render: (inv: PurchaseInvoice) => format(new Date(inv.invoice_date), "MMM d, yyyy"),
    },
    {
      key: "due_date",
      label: "Due",
      render: (inv: PurchaseInvoice) => format(new Date(inv.due_date), "MMM d, yyyy"),
    },
    {
      key: "status",
      label: "Status",
      render: (inv: PurchaseInvoice) => <PurchaseInvoiceStatusBadge status={inv.status} />,
    },
    {
      key: "total_amount",
      label: "Total",
      render: (inv: PurchaseInvoice) => (
        <span className="data-value">
          {inv.currency_code} {Number.parseFloat(inv.total_amount).toLocaleString()}
        </span>
      ),
    },
    {
      key: "balance_due",
      label: "Balance",
      render: (inv: PurchaseInvoice) => (
        <span className="data-value font-medium text-[#A65D57]">
          {inv.currency_code} {Number.parseFloat(inv.balance_due).toLocaleString()}
        </span>
      ),
    },
    {
      key: "actions",
      label: "",
      render: (inv: PurchaseInvoice) => {
        const canApprove = inv.status === "pending"
        const canPay = inv.status === "approved" || inv.status === "overdue"
        if (!canApprove && !canPay) return null
        return (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="sm" className="h-7 w-7 p-0">
                <ChevronRight className="w-4 h-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              {canApprove && (
                <DropdownMenuItem onClick={() => handleApprove(inv)}>Approve Invoice</DropdownMenuItem>
              )}
              {canPay && (
                <DropdownMenuItem
                  onClick={() => {
                    setPaymentInvoice(inv)
                    form.setValue("amount", inv.balance_due)
                  }}
                >
                  Record Payment
                </DropdownMenuItem>
              )}
            </DropdownMenuContent>
          </DropdownMenu>
        )
      },
    },
  ]

  return (
    <div>
      <PageHeader
        title="Purchase Invoices"
        description="Manage supplier invoices and payments"
        action={
          <Button onClick={() => setOpen(true)}>
            <Plus className="w-4 h-4 mr-2" />
            New Invoice
          </Button>
        }
      />

      <DataTable
        columns={columns}
        data={data?.results || []}
        loading={isLoading}
        searchPlaceholder="Search invoices..."
        onSearch={setSearch}
        emptyMessage="No purchase invoices found"
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

      <NewInvoiceDialog open={open} onOpenChange={setOpen} />
      <Dialog open={!!paymentInvoice} onOpenChange={(open) => !open && setPaymentInvoice(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Record Payment — {paymentInvoice?.invoice_number}</DialogTitle>
          </DialogHeader>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(handleRecordPayment)} className="space-y-4">
              <FormField
                control={form.control}
                name="amount"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Amount</FormLabel>
                    <FormControl>
                      <Input placeholder="0.00" className="thin-border" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <DialogFooter>
                <Button type="button" variant="outline" onClick={() => setPaymentInvoice(null)}>
                  Cancel
                </Button>
                <Button type="submit" disabled={recordPayment.isPending}>
                  {recordPayment.isPending ? "Saving..." : "Record Payment"}
                </Button>
              </DialogFooter>
            </form>
          </Form>
        </DialogContent>
      </Dialog>
    </div>
  )
}
