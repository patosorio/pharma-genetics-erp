"use client"

import { useState } from "react"
import { Plus, ChevronRight } from "lucide-react"
import { format } from "date-fns"
import { toast } from "sonner"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { useInvoices, useCreateInvoice } from "@/hooks/use-invoices"
import { useMarkSalesInvoiceSent, useRecordSalesInvoicePayment } from "@/hooks/use-payments"
import { useOrders } from "@/hooks/use-orders"
import { useTaxTypes } from "@/hooks/use-tax-types"
import { PageHeader } from "@/components/layout/page-header"
import { DataTable } from "@/components/common/data-table"
import { InvoiceStatusBadge } from "@/components/sales/invoice-status-badge"
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
import type { SalesInvoice } from "@/lib/types/sales"

const paymentSchema = z.object({
  amount: z.string().min(1, "Amount is required"),
  payment_method: z.string().min(1, "Payment method is required"),
  payment_date: z.string().min(1, "Payment date is required"),
  reference_number: z.string().optional(),
  notes: z.string().optional(),
})
type PaymentFormValues = z.infer<typeof paymentSchema>

const invoiceSchema = z.object({
  order: z.coerce.number({ required_error: "Order is required" }),
  invoice_date: z.string().min(1, "Invoice date is required"),
  due_date: z.string().min(1, "Due date is required"),
  base_amount: z.string().min(1, "Amount is required"),
  tax_type: z.coerce.number().optional(),
  notes: z.string().optional(),
})
type InvoiceFormValues = z.infer<typeof invoiceSchema>

function CreateInvoiceDialog({ open, onOpenChange }: { open: boolean; onOpenChange: (v: boolean) => void }) {
  const create = useCreateInvoice()
  const { data: orders } = useOrders({ page_size: 200, status: "ready" })
  const { data: taxTypes } = useTaxTypes({ page_size: 50 })
  const form = useForm<InvoiceFormValues>({
    resolver: zodResolver(invoiceSchema),
    defaultValues: { invoice_date: new Date().toISOString().split("T")[0], due_date: "", base_amount: "", notes: "" },
  })

  const onSubmit = async (values: InvoiceFormValues) => {
    try {
      await create.mutateAsync(values)
      toast.success("Invoice created")
      form.reset()
      onOpenChange(false)
    } catch {
      toast.error("Failed to create invoice.")
    }
  }

  return (
    <Dialog open={open} onOpenChange={(v) => { if (!v) form.reset(); onOpenChange(v) }}>
      <DialogContent>
        <DialogHeader><DialogTitle>Create Sales Invoice</DialogTitle></DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField control={form.control} name="order" render={({ field }) => (
              <FormItem><FormLabel>Order</FormLabel>
                <Select onValueChange={(v) => field.onChange(Number(v))} value={field.value?.toString() ?? ""}>
                  <FormControl><SelectTrigger className="thin-border"><SelectValue placeholder="Select order" /></SelectTrigger></FormControl>
                  <SelectContent>
                    {orders?.results.map((o) => <SelectItem key={o.id} value={o.id.toString()}>{o.order_number} — {o.customer_name}</SelectItem>)}
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
                <FormItem><FormLabel>Base Amount (฿)</FormLabel>
                  <FormControl><Input className="thin-border" placeholder="0.00" {...field} /></FormControl>
                  <FormMessage />
                </FormItem>
              )} />
              <FormField control={form.control} name="tax_type" render={({ field }) => (
                <FormItem><FormLabel>Tax Type (optional)</FormLabel>
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

export default function InvoicesPage() {
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [search, setSearch] = useState("")
  const [createOpen, setCreateOpen] = useState(false)
  const [paymentInvoice, setPaymentInvoice] = useState<SalesInvoice | null>(null)

  const { data, isLoading } = useInvoices({ page, page_size: pageSize, search, ordering: "-invoice_date" })
  const markSent = useMarkSalesInvoiceSent()
  const recordPayment = useRecordSalesInvoicePayment()

  const form = useForm<PaymentFormValues>({
    resolver: zodResolver(paymentSchema),
    defaultValues: { amount: "", payment_method: "", payment_date: format(new Date(), "yyyy-MM-dd") },
  })

  const handleMarkSent = async (invoice: SalesInvoice) => {
    try {
      await markSent.mutateAsync(invoice.id)
      toast.success(`Invoice ${invoice.invoice_number} marked as sent`)
    } catch {
      toast.error("Action failed. Please try again.")
    }
  }

  const handleRecordPayment = async (values: PaymentFormValues) => {
    if (!paymentInvoice) return
    try {
      await recordPayment.mutateAsync({ invoiceId: paymentInvoice.id, data: values })
      toast.success(`Payment recorded for invoice ${paymentInvoice.invoice_number}`)
      setPaymentInvoice(null)
      form.reset()
    } catch {
      toast.error("Failed to record payment. Please try again.")
    }
  }

  const columns = [
    {
      key: "invoice_number",
      label: "Invoice #",
      render: (invoice: SalesInvoice) => <span className="font-medium">{invoice.invoice_number}</span>,
    },
    {
      key: "order_number",
      label: "Order",
      render: (invoice: SalesInvoice) => invoice.order_number ?? "-",
    },
    {
      key: "invoice_date",
      label: "Date",
      render: (invoice: SalesInvoice) => format(new Date(invoice.invoice_date), "MMM d, yyyy"),
    },
    {
      key: "due_date",
      label: "Due",
      render: (invoice: SalesInvoice) => format(new Date(invoice.due_date), "MMM d, yyyy"),
    },
    {
      key: "status",
      label: "Status",
      render: (invoice: SalesInvoice) => <InvoiceStatusBadge status={invoice.status} />,
    },
    {
      key: "total_amount",
      label: "Total",
      render: (invoice: SalesInvoice) => (
        <span className="data-value">฿{Number.parseFloat(invoice.total_amount).toLocaleString()}</span>
      ),
    },
    {
      key: "balance_due",
      label: "Balance Due",
      render: (invoice: SalesInvoice) => (
        <span className="data-value font-medium text-[#A65D57]">
          ฿{Number.parseFloat(invoice.balance_due).toLocaleString()}
        </span>
      ),
    },
    {
      key: "actions",
      label: "",
      render: (invoice: SalesInvoice) => {
        const canMarkSent = invoice.status === "draft"
        const canPay = ["sent", "overdue"].includes(invoice.status)
        if (!canMarkSent && !canPay) return null

        return (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="sm" className="h-7 w-7 p-0">
                <ChevronRight className="w-4 h-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              {canMarkSent && (
                <DropdownMenuItem onClick={() => handleMarkSent(invoice)}>Mark as Sent</DropdownMenuItem>
              )}
              {canPay && (
                <DropdownMenuItem
                  onClick={() => {
                    setPaymentInvoice(invoice)
                    form.setValue("amount", invoice.balance_due)
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
        title="Sales Invoices"
        description="Manage invoices and payment tracking"
        action={
          <Button onClick={() => setCreateOpen(true)}>
            <Plus className="w-4 h-4 mr-2" />
            Create Invoice
          </Button>
        }
      />

      <DataTable
        columns={columns}
        data={data?.results || []}
        loading={isLoading}
        searchPlaceholder="Search invoices..."
        onSearch={setSearch}
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

      <CreateInvoiceDialog open={createOpen} onOpenChange={setCreateOpen} />
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
                    <FormLabel>Amount (฿)</FormLabel>
                    <FormControl>
                      <Input placeholder="0.00" className="thin-border" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="payment_method"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Payment Method</FormLabel>
                    <Select onValueChange={field.onChange} value={field.value}>
                      <FormControl>
                        <SelectTrigger className="thin-border">
                          <SelectValue placeholder="Select method" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="cash">Cash</SelectItem>
                        <SelectItem value="bank_transfer">Bank Transfer</SelectItem>
                        <SelectItem value="cheque">Cheque</SelectItem>
                        <SelectItem value="credit_card">Credit Card</SelectItem>
                        <SelectItem value="other">Other</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="payment_date"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Payment Date</FormLabel>
                    <FormControl>
                      <Input type="date" className="thin-border" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="reference_number"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Reference Number (optional)</FormLabel>
                    <FormControl>
                      <Input placeholder="e.g. transfer ref, cheque #" className="thin-border" {...field} />
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
