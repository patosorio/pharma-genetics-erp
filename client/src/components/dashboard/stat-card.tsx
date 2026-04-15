import type { LucideIcon } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"
import { cn } from "@/lib/utils"

interface StatCardProps {
  title: string
  value: string | number
  change?: {
    value: number
    trend: "up" | "down"
  }
  icon: LucideIcon
  iconColor?: string
}

export function StatCard({ title, value, change, icon: Icon, iconColor = "text-primary" }: StatCardProps) {
  return (
    <Card className="thin-border">
      <CardContent className="p-6">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <p className="text-sm text-muted-foreground mb-1">{title}</p>
            <h3 className="text-2xl font-semibold mb-2 data-value">{value}</h3>
            {change && (
              <p className={cn("text-sm font-medium", change.trend === "up" ? "text-[#4A7C59]" : "text-[#A65D57]")}>
                {change.trend === "up" ? "+" : ""}
                {change.value}% from last month
              </p>
            )}
          </div>
          <div className={cn("p-3 rounded-lg bg-muted", iconColor)}>
            <Icon className="w-5 h-5" strokeWidth={1.5} />
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
