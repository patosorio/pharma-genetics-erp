import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"
import type { OrderStatus } from "@/lib/types/common"

const statusConfig: Record<OrderStatus, { color: string; label: string }> = {
  draft: { color: "border-[#4A4A45] text-[#4A4A45] bg-[#4A4A45]/10", label: "Draft" },
  pending: { color: "border-[#C4A035] text-[#C4A035] bg-[#C4A035]/10", label: "Pending" },
  confirmed: { color: "border-[#5A7A8C] text-[#5A7A8C] bg-[#5A7A8C]/10", label: "Confirmed" },
  shipped: { color: "border-[#6B7F4A] text-[#6B7F4A] bg-[#6B7F4A]/10", label: "Shipped" },
  delivered: { color: "border-[#4A7C59] text-[#4A7C59] bg-[#4A7C59]/10", label: "Delivered" },
  cancelled: { color: "border-[#A65D57] text-[#A65D57] bg-[#A65D57]/10", label: "Cancelled" },
}

interface OrderStatusBadgeProps {
  status: OrderStatus
  className?: string
}

export function OrderStatusBadge({ status, className }: OrderStatusBadgeProps) {
  const config = statusConfig[status]

  return (
    <Badge variant="outline" className={cn("thin-border", config.color, className)}>
      {config.label}
    </Badge>
  )
}
