import { Heart, Leaf, ShoppingCart, TrendingUp } from "lucide-react"
import { StatCard } from "@/components/dashboard/stat-card"
import { RecentActivity } from "@/components/dashboard/recent-activity"
import { BatchStatusChart } from "@/components/dashboard/batch-status-chart"
import { TopStrains } from "@/components/dashboard/top-strains"
import { PageHeader } from "@/components/layout/page-header"

export default function DashboardPage() {
  return (
    <div>
      <PageHeader title="Dashboard" description="Overview of your clone nursery operations" />

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
        <StatCard
          title="Active Mothers"
          value={12}
          change={{ value: 2, trend: "up" }}
          icon={Heart}
          iconColor="text-[#3D4F2F]"
        />
        <StatCard
          title="Rooted Clones"
          value={342}
          change={{ value: 15, trend: "up" }}
          icon={Leaf}
          iconColor="text-[#4A7C59]"
        />
        <StatCard
          title="Pending Orders"
          value={15}
          change={{ value: 5, trend: "down" }}
          icon={ShoppingCart}
          iconColor="text-[#B8A361]"
        />
        <StatCard
          title="Revenue (MTD)"
          value="฿1.2M"
          change={{ value: 18, trend: "up" }}
          icon={TrendingUp}
          iconColor="text-[#4A7C59]"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <BatchStatusChart />
        <TopStrains />
      </div>

      <RecentActivity />
    </div>
  )
}
