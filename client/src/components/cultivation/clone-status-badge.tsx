import { Badge } from "@/components/ui/badge"
import type { Clone } from "@/lib/types/cultivation"

interface CloneStatusBadgeProps {
  status: Clone["status"]
}

const statusConfig = {
  cutting: { label: "Cutting", className: "bg-sky-50 text-sky-700 border-sky-200" },
  rooting: { label: "Rooting", className: "bg-amber-50 text-amber-700 border-amber-200" },
  rooted: { label: "Available", className: "bg-emerald-50 text-emerald-700 border-emerald-200" },
  reserved: { label: "Reserved", className: "bg-blue-50 text-blue-700 border-blue-200" },
  sold: { label: "Sold", className: "bg-gray-50 text-gray-700 border-gray-200" },
  died: { label: "Died", className: "bg-red-50 text-red-700 border-red-200" },
}

export function CloneStatusBadge({ status }: CloneStatusBadgeProps) {
  const config = statusConfig[status]
  return (
    <Badge variant="outline" className={config.className}>
      {config.label}
    </Badge>
  )
}
