import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Clock, Scissors, Leaf, ShoppingCart, Heart } from "lucide-react"
import type { ProductionBatch } from "@/lib/types/cultivation"
import type { Order } from "@/lib/types/sales"
import { format } from "date-fns"

interface RecentActivityProps {
  batches?: ProductionBatch[]
  orders?: Order[]
}

export function RecentActivity({ batches = [], orders = [] }: RecentActivityProps) {
  type ActivityItem = {
    id: string
    type: string
    description: string
    timestamp: string
    icon: typeof Clock
  }

  const activities: ActivityItem[] = [
    ...batches.slice(0, 3).map((b) => ({
      id: `batch-${b.id}`,
      type: "batch",
      description: `Batch ${b.batch_number} — ${b.initial_clone_count} cuts from mother ${b.mother_plant_code}`,
      timestamp: format(new Date(b.created_at), "MMM d, h:mm a"),
      icon: Scissors,
    })),
    ...orders.slice(0, 3).map((o) => ({
      id: `order-${o.id}`,
      type: "order",
      description: `Order ${o.order_number} — ${o.customer_name} · ${o.status_display}`,
      timestamp: format(new Date(o.created_at), "MMM d, h:mm a"),
      icon: ShoppingCart,
    })),
  ]
    .sort((a, b) => (a.timestamp > b.timestamp ? -1 : 1))
    .slice(0, 5)

  const iconMap: Record<string, typeof Clock> = {
    batch: Scissors,
    order: ShoppingCart,
    clone: Leaf,
    mother: Heart,
  }

  return (
    <Card className="thin-border">
      <CardHeader>
        <CardTitle className="text-lg">Recent Activity</CardTitle>
      </CardHeader>
      <CardContent>
        {activities.length === 0 ? (
          <p className="text-sm text-muted-foreground text-center py-8">No recent activity</p>
        ) : (
          <div className="space-y-4">
            {activities.map((activity) => {
              const Icon = iconMap[activity.type] || Clock
              return (
                <div key={activity.id} className="flex gap-3 pb-4 border-b border-border last:border-0 last:pb-0">
                  <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center flex-shrink-0">
                    <Icon className="w-4 h-4 text-muted-foreground" strokeWidth={1.5} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm mb-1">{activity.description}</p>
                    <p className="text-xs text-muted-foreground">{activity.timestamp}</p>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
