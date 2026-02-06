import { Badge } from "@/components/ui/badge"
import type { MotherPlant } from "@/lib/types/cultivation"

interface MotherPlantStatusBadgeProps {
  status: MotherPlant["status"]
}

const statusConfig = {
  Active_Production: { label: "Active Production", className: "bg-emerald-50 text-emerald-700 border-emerald-200" },
  Recovery: { label: "Recovery", className: "bg-amber-50 text-amber-700 border-amber-200" },
  Low_Production: { label: "Low Production", className: "bg-orange-50 text-orange-700 border-orange-200" },
  Quarantine: { label: "Quarantine", className: "bg-red-50 text-red-700 border-red-200" },
  Retired: { label: "Retired", className: "bg-gray-50 text-gray-700 border-gray-200" },
  Under_Treatment: { label: "Under Treatment", className: "bg-purple-50 text-purple-700 border-purple-200" },
  Growing: { label: "Growing", className: "bg-blue-50 text-blue-700 border-blue-200" },
}

export function MotherPlantStatusBadge({ status }: MotherPlantStatusBadgeProps) {
  const config = statusConfig[status]
  return (
    <Badge variant="outline" className={config.className}>
      {config.label}
    </Badge>
  )
}
