import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Clock } from "lucide-react"

interface Activity {
  id: string
  type: string
  description: string
  timestamp: string
  user: string
}

const mockActivities: Activity[] = [
  {
    id: "1",
    type: "batch",
    description: 'Production batch "PB-2024-003" created - 60 cuts from MOM-003',
    timestamp: "2 hours ago",
    user: "John Doe",
  },
  {
    id: "2",
    type: "clone",
    description: 'Batch "PB-2024-002" completed rooting - 47/50 clones successful',
    timestamp: "5 hours ago",
    user: "Jane Smith",
  },
  {
    id: "3",
    type: "order",
    description: "Order #ORD-2024-045 shipped - 25 OG Kush clones",
    timestamp: "1 day ago",
    user: "Mike Johnson",
  },
  {
    id: "4",
    type: "mother",
    description: "Mother plant MOM-004 moved to quarantine for inspection",
    timestamp: "1 day ago",
    user: "System",
  },
]

export function RecentActivity() {
  return (
    <Card className="thin-border">
      <CardHeader>
        <CardTitle className="text-lg">Recent Activity</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {mockActivities.map((activity) => (
            <div key={activity.id} className="flex gap-3 pb-4 border-b border-border last:border-0 last:pb-0">
              <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center flex-shrink-0">
                <Clock className="w-4 h-4 text-muted-foreground" strokeWidth={1.5} />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm mb-1">{activity.description}</p>
                <p className="text-xs text-muted-foreground">
                  {activity.user} • {activity.timestamp}
                </p>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
