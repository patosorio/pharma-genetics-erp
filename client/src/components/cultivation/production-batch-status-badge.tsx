import { Badge } from "@/components/ui/badge"
import type { ProductionBatch } from "@/lib/types/cultivation"

interface ProductionBatchStatusBadgeProps {
  status: ProductionBatch["status"]
}

const statusConfig = {
  cutting: { label: "Cutting", className: "bg-blue-50 text-blue-700 border-blue-200" },
  rooting: { label: "Rooting", className: "bg-amber-50 text-amber-700 border-amber-200" },
  completed: { label: "Completed", className: "bg-emerald-50 text-emerald-700 border-emerald-200" },
  failed: { label: "Failed", className: "bg-red-50 text-red-700 border-red-200" },
}

export function ProductionBatchStatusBadge({ status }: ProductionBatchStatusBadgeProps) {
  const config = statusConfig[status]
  return (
    <Badge variant="outline" className={config.className}>
      {config.label}
    </Badge>
  )
}
