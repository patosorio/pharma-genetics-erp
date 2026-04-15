"use client"

import { useState, useEffect } from "react"
import { toast } from "sonner"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { Plus } from "lucide-react"
import { useCompanySettings, useUpdateCompanySettings } from "@/hooks/use-company-settings"
import { useCurrencies, useCreateCurrency } from "@/hooks/use-currencies"
import { useTaxTypes, useCreateTaxType } from "@/hooks/use-tax-types"
import { PageHeader } from "@/components/layout/page-header"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog"
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Skeleton } from "@/components/ui/skeleton"
import { StatusBadge } from "@/components/common/status-badge"
import type { Currency, TaxType } from "@/lib/types/core"

// ─── Company ───────────────────────────────────────────────────────────────

const companySchema = z.object({
  company_name: z.string().min(1, "Company name is required"),
  tax_id: z.string().optional(),
  break_even_price: z.string().min(1, "Break-even price is required"),
  fiscal_year_start_month: z.coerce.number().min(1).max(12),
})
type CompanyFormValues = z.infer<typeof companySchema>

function CompanySettingsTab() {
  const { data: settings, isLoading } = useCompanySettings()
  const update = useUpdateCompanySettings()

  const form = useForm<CompanyFormValues>({
    resolver: zodResolver(companySchema),
    defaultValues: {
      company_name: "",
      tax_id: "",
      break_even_price: "",
      fiscal_year_start_month: 1,
    },
  })

  // Populate form once data arrives — avoids the uncontrolled→controlled warning
  useEffect(() => {
    if (settings) {
      form.reset({
        company_name: settings.company_name,
        tax_id: settings.tax_id ?? "",
        break_even_price: settings.break_even_price,
        fiscal_year_start_month: settings.fiscal_year_start_month,
      })
    }
  }, [settings, form])

  const onSubmit = async (values: CompanyFormValues) => {
    try {
      await update.mutateAsync(values)
      toast.success("Company settings saved")
    } catch {
      toast.error("Failed to save settings.")
    }
  }

  return (
    <Card className="thin-border max-w-lg">
      <CardHeader>
        <CardTitle className="text-base">Company Information</CardTitle>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="space-y-4">
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
          </div>
        ) : (
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
              <FormField
                control={form.control}
                name="company_name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Company Name</FormLabel>
                    <FormControl>
                      <Input className="thin-border" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="tax_id"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Tax ID</FormLabel>
                    <FormControl>
                      <Input className="thin-border" placeholder="e.g. 0105XXXXXXXXX" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="break_even_price"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Break-Even Price (฿ per clone)</FormLabel>
                    <FormControl>
                      <Input className="thin-border" placeholder="0.00" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="fiscal_year_start_month"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Fiscal Year Start Month (1–12)</FormLabel>
                    <FormControl>
                      <Input type="number" min={1} max={12} className="thin-border" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <div className="pt-2">
                <Button type="submit" disabled={update.isPending}>
                  {update.isPending ? "Saving..." : "Save Changes"}
                </Button>
              </div>
            </form>
          </Form>
        )}
      </CardContent>
    </Card>
  )
}

// ─── Currencies ────────────────────────────────────────────────────────────

const currencySchema = z.object({
  code: z.string().min(1, "Code is required").max(10),
  name: z.string().min(1, "Name is required"),
  symbol: z.string().min(1, "Symbol is required").max(5),
  is_default: z.boolean().default(false),
})
type CurrencyFormValues = z.infer<typeof currencySchema>

function AddCurrencyDialog({ open, onOpenChange }: { open: boolean; onOpenChange: (v: boolean) => void }) {
  const create = useCreateCurrency()
  const form = useForm<CurrencyFormValues>({
    resolver: zodResolver(currencySchema),
    defaultValues: { code: "", name: "", symbol: "", is_default: false },
  })

  const onSubmit = async (values: CurrencyFormValues) => {
    try {
      await create.mutateAsync(values)
      toast.success("Currency added")
      form.reset()
      onOpenChange(false)
    } catch {
      toast.error("Failed to add currency.")
    }
  }

  return (
    <Dialog open={open} onOpenChange={(v) => { if (!v) form.reset(); onOpenChange(v) }}>
      <DialogContent>
        <DialogHeader><DialogTitle>Add Currency</DialogTitle></DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField control={form.control} name="code" render={({ field }) => (
              <FormItem>
                <FormLabel>Code</FormLabel>
                <FormControl><Input className="thin-border" placeholder="THB" {...field} /></FormControl>
                <FormMessage />
              </FormItem>
            )} />
            <FormField control={form.control} name="name" render={({ field }) => (
              <FormItem>
                <FormLabel>Name</FormLabel>
                <FormControl><Input className="thin-border" placeholder="Thai Baht" {...field} /></FormControl>
                <FormMessage />
              </FormItem>
            )} />
            <FormField control={form.control} name="symbol" render={({ field }) => (
              <FormItem>
                <FormLabel>Symbol</FormLabel>
                <FormControl><Input className="thin-border" placeholder="฿" {...field} /></FormControl>
                <FormMessage />
              </FormItem>
            )} />
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>Cancel</Button>
              <Button type="submit" disabled={create.isPending}>{create.isPending ? "Saving..." : "Add Currency"}</Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}

function CurrenciesTab() {
  const { data, isLoading } = useCurrencies()
  const [open, setOpen] = useState(false)

  return (
    <>
      <Card className="thin-border">
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="text-base">Currencies</CardTitle>
          <Button size="sm" onClick={() => setOpen(true)}>
            <Plus className="w-4 h-4 mr-1" />Add Currency
          </Button>
        </CardHeader>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-muted">
                <tr>
                  <th className="px-4 py-3 text-left text-sm font-medium border-b border-border">Code</th>
                  <th className="px-4 py-3 text-left text-sm font-medium border-b border-border">Name</th>
                  <th className="px-4 py-3 text-left text-sm font-medium border-b border-border">Symbol</th>
                  <th className="px-4 py-3 text-left text-sm font-medium border-b border-border">Default</th>
                </tr>
              </thead>
              <tbody>
                {isLoading ? (
                  <tr><td colSpan={4} className="px-4 py-8 text-center text-muted-foreground">Loading...</td></tr>
                ) : !data?.results?.length ? (
                  <tr><td colSpan={4} className="px-4 py-8 text-center text-muted-foreground">No currencies found</td></tr>
                ) : (
                  data.results.map((c: Currency) => (
                    <tr key={c.id} className="hover:bg-muted/50 transition-colors">
                      <td className="px-4 py-3 text-sm border-b border-border font-medium">{c.code}</td>
                      <td className="px-4 py-3 text-sm border-b border-border">{c.name}</td>
                      <td className="px-4 py-3 text-sm border-b border-border">{c.symbol}</td>
                      <td className="px-4 py-3 text-sm border-b border-border">
                        {c.is_default && (
                          <span className="text-xs font-medium text-[#4A7C59] border border-[#4A7C59] bg-[#4A7C59]/10 px-2 py-0.5 rounded-full">
                            Default
                          </span>
                        )}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
      <AddCurrencyDialog open={open} onOpenChange={setOpen} />
    </>
  )
}

// ─── Tax Types ─────────────────────────────────────────────────────────────

const taxTypeSchema = z.object({
  name: z.string().min(1, "Name is required"),
  rate: z.string().min(1, "Rate is required"),
  is_active: z.boolean().default(true),
})
type TaxTypeFormValues = z.infer<typeof taxTypeSchema>

function AddTaxTypeDialog({ open, onOpenChange }: { open: boolean; onOpenChange: (v: boolean) => void }) {
  const create = useCreateTaxType()
  const form = useForm<TaxTypeFormValues>({
    resolver: zodResolver(taxTypeSchema),
    defaultValues: { name: "", rate: "", is_active: true },
  })

  const onSubmit = async (values: TaxTypeFormValues) => {
    try {
      await create.mutateAsync(values)
      toast.success("Tax type added")
      form.reset()
      onOpenChange(false)
    } catch {
      toast.error("Failed to add tax type.")
    }
  }

  return (
    <Dialog open={open} onOpenChange={(v) => { if (!v) form.reset(); onOpenChange(v) }}>
      <DialogContent>
        <DialogHeader><DialogTitle>Add Tax Type</DialogTitle></DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField control={form.control} name="name" render={({ field }) => (
              <FormItem>
                <FormLabel>Name</FormLabel>
                <FormControl><Input className="thin-border" placeholder="VAT 7%" {...field} /></FormControl>
                <FormMessage />
              </FormItem>
            )} />
            <FormField control={form.control} name="rate" render={({ field }) => (
              <FormItem>
                <FormLabel>Rate (%)</FormLabel>
                <FormControl><Input className="thin-border" placeholder="7.00" {...field} /></FormControl>
                <FormMessage />
              </FormItem>
            )} />
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>Cancel</Button>
              <Button type="submit" disabled={create.isPending}>{create.isPending ? "Saving..." : "Add Tax Type"}</Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}

function TaxTypesTab() {
  const { data, isLoading } = useTaxTypes()
  const [open, setOpen] = useState(false)

  return (
    <>
      <Card className="thin-border">
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="text-base">Tax Types</CardTitle>
          <Button size="sm" onClick={() => setOpen(true)}>
            <Plus className="w-4 h-4 mr-1" />Add Tax Type
          </Button>
        </CardHeader>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-muted">
                <tr>
                  <th className="px-4 py-3 text-left text-sm font-medium border-b border-border">Name</th>
                  <th className="px-4 py-3 text-left text-sm font-medium border-b border-border">Rate (%)</th>
                  <th className="px-4 py-3 text-left text-sm font-medium border-b border-border">Status</th>
                </tr>
              </thead>
              <tbody>
                {isLoading ? (
                  <tr><td colSpan={3} className="px-4 py-8 text-center text-muted-foreground">Loading...</td></tr>
                ) : !data?.results?.length ? (
                  <tr><td colSpan={3} className="px-4 py-8 text-center text-muted-foreground">No tax types found</td></tr>
                ) : (
                  data.results.map((t: TaxType) => (
                    <tr key={t.id} className="hover:bg-muted/50 transition-colors">
                      <td className="px-4 py-3 text-sm border-b border-border font-medium">{t.name}</td>
                      <td className="px-4 py-3 text-sm border-b border-border data-value">{t.rate}%</td>
                      <td className="px-4 py-3 text-sm border-b border-border">
                        <StatusBadge status={t.is_active ? "Active" : "Inactive"} />
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
      <AddTaxTypeDialog open={open} onOpenChange={setOpen} />
    </>
  )
}

// ─── Page ───────────────────────────────────────────────────────────────────

export default function SettingsPage() {
  return (
    <div>
      <PageHeader title="Settings" description="Configure system-wide settings and preferences" />
      <Tabs defaultValue="company">
        <TabsList className="mb-6">
          <TabsTrigger value="company">Company</TabsTrigger>
          <TabsTrigger value="currencies">Currencies</TabsTrigger>
          <TabsTrigger value="tax-types">Tax Types</TabsTrigger>
        </TabsList>
        <TabsContent value="company"><CompanySettingsTab /></TabsContent>
        <TabsContent value="currencies"><CurrenciesTab /></TabsContent>
        <TabsContent value="tax-types"><TaxTypesTab /></TabsContent>
      </Tabs>
    </div>
  )
}
