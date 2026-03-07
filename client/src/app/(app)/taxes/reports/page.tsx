"use client"

import { useState } from "react"
import { Plus, ChevronRight } from "lucide-react"
import { format } from "date-fns"
import { toast } from "sonner"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { useTaxReports, useCreateTaxReport, useCalculateTaxTotals, useGenerateTaxEntries } from "@/hooks/use-taxes"
import { useCurrencies } from "@/hooks/use-currencies"
import { PageHeader } from "@/components/layout/page-header"
import { DataTable } from "@/components/common/data-table"
import { TaxReportStatusBadge } from "@/components/taxes/tax-report-status-badge"
import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog"
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import type { TaxReport } from "@/lib/types/taxes"

const schema = z.object({
  period_start: z.string().min(1, "Start date is required"),
  period_end: z.string().min(1, "End date is required"),
  currency: z.coerce.number({ required_error: "Currency is required" }),
  notes: z.string().optional(),
})
type FormValues = z.infer<typeof schema>

function NewTaxReportDialog({ open, onOpenChange }: { open: boolean; onOpenChange: (v: boolean) => void }) {
  const create = useCreateTaxReport()
  const { data: currencies } = useCurrencies({ page_size: 50 })
  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { period_start: "", period_end: "", notes: "" },
  })

  const onSubmit = async (values: FormValues) => {
    try {
      await create.mutateAsync(values)
      toast.success("Tax report created")
      form.reset()
      onOpenChange(false)
    } catch {
      toast.error("Failed to create tax report.")
    }
  }

  return (
    <Dialog open={open} onOpenChange={(v) => { if (!v) form.reset(); onOpenChange(v) }}>
      <DialogContent>
        <DialogHeader><DialogTitle>New Tax Report</DialogTitle></DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <FormField control={form.control} name="period_start" render={({ field }) => (
                <FormItem><FormLabel>Period Start</FormLabel>
                  <FormControl><Input type="date" className="thin-border" {...field} /></FormControl>
                  <FormMessage />
                </FormItem>
              )} />
              <FormField control={form.control} name="period_end" render={({ field }) => (
                <FormItem><FormLabel>Period End</FormLabel>
                  <FormControl><Input type="date" className="thin-border" {...field} /></FormControl>
                  <FormMessage />
                </FormItem>
              )} />
            </div>
            <FormField control={form.control} name="currency" render={({ field }) => (
              <FormItem><FormLabel>Currency</FormLabel>
                <Select onValueChange={(v) => field.onChange(Number(v))} value={field.value?.toString() ?? ""}>
                  <FormControl><SelectTrigger className="thin-border"><SelectValue placeholder="Select currency" /></SelectTrigger></FormControl>
                  <SelectContent>
                    {currencies?.results.map((c) => <SelectItem key={c.id} value={c.id.toString()}>{c.code} — {c.name}</SelectItem>)}
                  </SelectContent>
                </Select>
                <FormMessage />
              </FormItem>
            )} />
            <FormField control={form.control} name="notes" render={({ field }) => (
              <FormItem><FormLabel>Notes (optional)</FormLabel>
                <FormControl><Input className="thin-border" {...field} /></FormControl>
                <FormMessage />
              </FormItem>
            )} />
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>Cancel</Button>
              <Button type="submit" disabled={create.isPending}>{create.isPending ? "Creating..." : "Create Report"}</Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}

export default function TaxReportsPage() {
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [search, setSearch] = useState("")
  const [open, setOpen] = useState(false)

  const { data, isLoading } = useTaxReports({ page, page_size: pageSize })
  const calculateTotals = useCalculateTaxTotals()
  const generateEntries = useGenerateTaxEntries()

  const handleCalculate = async (report: TaxReport) => {
    try {
      await calculateTotals.mutateAsync(report.id)
      toast.success(`Totals recalculated for ${report.report_number}`)
    } catch {
      toast.error("Calculation failed. Please try again.")
    }
  }

  const handleGenerate = async (report: TaxReport) => {
    try {
      await generateEntries.mutateAsync(report.id)
      toast.success(`Journal entries generated for ${report.report_number}`)
    } catch {
      toast.error("Failed to generate entries. Please try again.")
    }
  }

  const columns = [
    {
      key: "report_number",
      label: "Report #",
      render: (r: TaxReport) => <span className="font-medium">{r.report_number}</span>,
    },
    {
      key: "period_start",
      label: "Period",
      render: (r: TaxReport) =>
        `${format(new Date(r.period_start), "MMM d")} – ${format(new Date(r.period_end), "MMM d, yyyy")}`,
    },
    {
      key: "status",
      label: "Status",
      render: (r: TaxReport) => <TaxReportStatusBadge status={r.status} />,
    },
    {
      key: "total_vat_payable",
      label: "VAT Payable",
      render: (r: TaxReport) => (
        <span className="data-value text-[#A65D57]">
          ฿{Number.parseFloat(r.total_vat_payable).toLocaleString()}
        </span>
      ),
    },
    {
      key: "total_vat_recoverable",
      label: "VAT Recoverable",
      render: (r: TaxReport) => (
        <span className="data-value text-[#4A7C59]">
          ฿{Number.parseFloat(r.total_vat_recoverable).toLocaleString()}
        </span>
      ),
    },
    {
      key: "net_vat_position",
      label: "Net VAT",
      render: (r: TaxReport) => {
        const net = Number.parseFloat(r.net_vat_position)
        return (
          <span className={`data-value font-medium ${net > 0 ? "text-[#A65D57]" : "text-[#4A7C59]"}`}>
            ฿{net.toLocaleString()}
          </span>
        )
      },
    },
    {
      key: "actions",
      label: "",
      render: (r: TaxReport) => {
        if (!["draft", "finalized"].includes(r.status)) return null
        return (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="sm" className="h-7 w-7 p-0">
                <ChevronRight className="w-4 h-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={() => handleCalculate(r)}>Recalculate Totals</DropdownMenuItem>
              <DropdownMenuItem onClick={() => handleGenerate(r)}>Generate Journal Entries</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        )
      },
    },
  ]

  return (
    <div>
      <PageHeader
        title="Tax Reports"
        description="Manage VAT reporting periods and tax obligations"
        action={
          <Button onClick={() => setOpen(true)}>
            <Plus className="w-4 h-4 mr-2" />
            New Report
          </Button>
        }
      />

      <DataTable
        columns={columns}
        data={data?.results || []}
        loading={isLoading}
        searchPlaceholder="Search reports..."
        onSearch={setSearch}
        emptyMessage="No tax reports found"
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
      <NewTaxReportDialog open={open} onOpenChange={setOpen} />
    </div>
  )
}
