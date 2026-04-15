"use client"

import { useState } from "react"
import { format } from "date-fns"
import { Calculator } from "lucide-react"
import { toast } from "sonner"
import { useCostSnapshots, useCalculateCostSnapshot } from "@/hooks/use-pricing"
import { PageHeader } from "@/components/layout/page-header"
import { DataTable } from "@/components/common/data-table"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import type { CostSnapshot } from "@/lib/types/pricing"

export default function CostSnapshotsPage() {
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [search, setSearch] = useState("")
  const [calcOpen, setCalcOpen] = useState(false)
  const [calcForm, setCalcForm] = useState({ location_id: "", period_start: "", period_end: "" })

  const { data, isLoading } = useCostSnapshots({ page, page_size: pageSize })
  const calculate = useCalculateCostSnapshot()

  const handleCalculate = async () => {
    if (!calcForm.location_id || !calcForm.period_start || !calcForm.period_end) {
      toast.error("All fields are required")
      return
    }
    try {
      await calculate.mutateAsync({
        location_id: Number(calcForm.location_id),
        period_start: calcForm.period_start,
        period_end: calcForm.period_end,
      })
      toast.success("Cost snapshot calculated successfully")
      setCalcOpen(false)
      setCalcForm({ location_id: "", period_start: "", period_end: "" })
    } catch {
      toast.error("Calculation failed. Please try again.")
    }
  }

  const columns = [
    {
      key: "location_code",
      label: "Location",
      render: (s: CostSnapshot) => <span className="font-medium">{s.location_code}</span>,
    },
    {
      key: "period_start",
      label: "Period",
      render: (s: CostSnapshot) =>
        `${format(new Date(s.period_start), "MMM d")} – ${format(new Date(s.period_end), "MMM d, yyyy")}`,
    },
    {
      key: "total_clones_produced",
      label: "Clones Produced",
      render: (s: CostSnapshot) => <span className="data-value">{s.total_clones_produced.toLocaleString()}</span>,
    },
    {
      key: "capacity_utilization_pct",
      label: "Utilization",
      render: (s: CostSnapshot) => (
        <span className="data-value">{Number.parseFloat(s.capacity_utilization_pct).toFixed(1)}%</span>
      ),
    },
    {
      key: "total_cost_per_clone",
      label: "Cost / Clone",
      render: (s: CostSnapshot) => (
        <span className="data-value font-medium">
          ฿{Number.parseFloat(s.total_cost_per_clone).toLocaleString()}
        </span>
      ),
    },
    {
      key: "cogs_per_clone",
      label: "COGS / Clone",
      render: (s: CostSnapshot) => (
        <span className="data-value">฿{Number.parseFloat(s.cogs_per_clone).toLocaleString()}</span>
      ),
    },
    {
      key: "direct_labor_per_clone",
      label: "Labor / Clone",
      render: (s: CostSnapshot) => (
        <span className="data-value">฿{Number.parseFloat(s.direct_labor_per_clone).toLocaleString()}</span>
      ),
    },
    {
      key: "snapshot_date",
      label: "Calculated",
      render: (s: CostSnapshot) => format(new Date(s.snapshot_date), "MMM d, yyyy"),
    },
  ]

  return (
    <div>
      <PageHeader
        title="Cost Snapshots"
        description="Calculated cost-per-clone snapshots by location and period"
        action={
          <Button onClick={() => setCalcOpen(true)}>
            <Calculator className="w-4 h-4 mr-2" />
            Calculate Snapshot
          </Button>
        }
      />

      <DataTable
        columns={columns}
        data={data?.results || []}
        loading={isLoading}
        searchPlaceholder="Search snapshots..."
        onSearch={setSearch}
        emptyMessage="No cost snapshots calculated yet"
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

      <Dialog open={calcOpen} onOpenChange={setCalcOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Calculate Cost Snapshot</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label>Location ID</Label>
              <Input
                className="thin-border mt-1"
                placeholder="e.g. 1"
                value={calcForm.location_id}
                onChange={(e) => setCalcForm((f) => ({ ...f, location_id: e.target.value }))}
              />
            </div>
            <div>
              <Label>Period Start</Label>
              <Input
                type="date"
                className="thin-border mt-1"
                value={calcForm.period_start}
                onChange={(e) => setCalcForm((f) => ({ ...f, period_start: e.target.value }))}
              />
            </div>
            <div>
              <Label>Period End</Label>
              <Input
                type="date"
                className="thin-border mt-1"
                value={calcForm.period_end}
                onChange={(e) => setCalcForm((f) => ({ ...f, period_end: e.target.value }))}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setCalcOpen(false)}>Cancel</Button>
            <Button onClick={handleCalculate} disabled={calculate.isPending}>
              {calculate.isPending ? "Calculating..." : "Calculate"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
