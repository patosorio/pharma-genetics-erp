"use client"

import { Heart, Leaf, ShoppingCart, TrendingUp } from "lucide-react"
import { StatCard } from "@/components/dashboard/stat-card"
import { RecentActivity } from "@/components/dashboard/recent-activity"
import { BatchStatusChart } from "@/components/dashboard/batch-status-chart"
import { TopStrains } from "@/components/dashboard/top-strains"
import { PageHeader } from "@/components/layout/page-header"
import { useMotherPlants } from "@/hooks/use-cultivation"
import { useProductionBatches } from "@/hooks/use-batches"
import { useOrders } from "@/hooks/use-orders"
import { useInvoices } from "@/hooks/use-invoices"
import { useInventorySummaryByStrain } from "@/hooks/use-inventory-reports"

export default function DashboardPage() {
  const { data: mothersData } = useMotherPlants({ status: "Active_Production", page_size: 1 })
  const { data: rootedClonesData } = useInventorySummaryByStrain()
  const { data: pendingOrdersData } = useOrders({ status: "draft,confirmed", page_size: 1 })
  const { data: allBatchesData } = useProductionBatches({ page_size: 100 })
  const { data: recentBatchesData } = useProductionBatches({ page_size: 5, ordering: "-created_at" })
  const { data: recentOrdersData } = useOrders({ page_size: 5, ordering: "-created_at" })
  const { data: invoicesData } = useInvoices({ page_size: 100 })

  const activeMothers = mothersData?.count ?? 0
  const totalRootedClones = rootedClonesData?.reduce((sum, s) => sum + s.rooted_clones, 0) ?? 0
  const pendingOrders = pendingOrdersData?.count ?? 0

  const revenueMTD = invoicesData?.results
    .filter((inv) => {
      const now = new Date()
      const invDate = new Date(inv.invoice_date)
      return invDate.getMonth() === now.getMonth() && invDate.getFullYear() === now.getFullYear()
    })
    .reduce((sum, inv) => sum + Number.parseFloat(inv.total_amount), 0) ?? 0

  const batchStatusCounts = allBatchesData?.results.reduce(
    (acc, batch) => {
      const label =
        batch.status === "cutting"
          ? "Cutting"
          : batch.status === "rooting"
            ? "Rooting"
            : batch.status === "completed"
              ? "Completed"
              : "Failed"
      acc[label] = (acc[label] || 0) + 1
      return acc
    },
    {} as Record<string, number>,
  )

  const batchChartData = [
    { status: "Cutting", count: batchStatusCounts?.["Cutting"] ?? 0 },
    { status: "Rooting", count: batchStatusCounts?.["Rooting"] ?? 0 },
    { status: "Completed", count: batchStatusCounts?.["Completed"] ?? 0 },
    { status: "Failed", count: batchStatusCounts?.["Failed"] ?? 0 },
  ]

  const topStrains = (rootedClonesData ?? [])
    .filter((s) => s.rooted_clones > 0)
    .sort((a, b) => b.rooted_clones - a.rooted_clones)
    .slice(0, 5)
    .map((s) => ({
      id: s.strain_id,
      name: s.strain_name,
      category: "",
      activeClones: s.rooted_clones,
    }))

  const revenueDisplay =
    revenueMTD >= 1_000_000
      ? `฿${(revenueMTD / 1_000_000).toFixed(1)}M`
      : revenueMTD >= 1_000
        ? `฿${(revenueMTD / 1_000).toFixed(0)}K`
        : `฿${revenueMTD.toLocaleString()}`

  return (
    <div>
      <PageHeader title="Dashboard" description="Overview of your clone nursery operations" />

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
        <StatCard
          title="Active Mothers"
          value={activeMothers}
          icon={Heart}
          iconColor="text-[#3D4F2F]"
        />
        <StatCard
          title="Rooted Clones"
          value={totalRootedClones}
          icon={Leaf}
          iconColor="text-[#4A7C59]"
        />
        <StatCard
          title="Pending Orders"
          value={pendingOrders}
          icon={ShoppingCart}
          iconColor="text-[#B8A361]"
        />
        <StatCard
          title="Revenue (MTD)"
          value={revenueDisplay}
          icon={TrendingUp}
          iconColor="text-[#4A7C59]"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <BatchStatusChart data={batchChartData} />
        <TopStrains strains={topStrains} />
      </div>

      <RecentActivity
        batches={recentBatchesData?.results ?? []}
        orders={recentOrdersData?.results ?? []}
      />
    </div>
  )
}
