import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"
import type { PurchaseOrderStatus } from "@/lib/types/common"

const statusConfig: Record<PurchaseOrderStatus, { color: string; label: string }> = {
  draft: { color: "border-[#4A4A45] text-[#4A4A45] bg-[#4A4A45]/10", label: "Draft" },
  sent: { color: "border-[#5A7A8C] text-[#5A7A8C] bg-[#5A7A8C]/10", label: "Sent" },
  confirmed: { color: "border-[#B8A361] text-[#B8A361] bg-[#B8A361]/10", label: "Confirmed" },
  delivered: { color: "border-[#4A7C59] text-[#4A7C59] bg-[#4A7C59]/10", label: "Delivered" },
  cancelled: { color: "border-[#A65D57] text-[#A65D57] bg-[#A65D57]/10", label: "Cancelled" },
}

interface PurchaseOrderStatusBadgeProps {
  status: PurchaseOrderStatus
  className?: string
}

export function PurchaseOrderStatusBadge({ status, className }: PurchaseOrderStatusBadgeProps) {
  const config = statusConfig[status] ?? { color: "border-[#4A4A45] text-[#4A4A45] bg-[#4A4A45]/10", label: status }
  return (
    <Badge variant="outline" className={cn("thin-border", config.color, className)}>
      {config.label}
    </Badge>
  )
}
