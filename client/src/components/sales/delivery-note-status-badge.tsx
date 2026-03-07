import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"
import type { DeliveryNoteStatus } from "@/lib/types/common"

const statusConfig: Record<DeliveryNoteStatus, { color: string; label: string }> = {
  draft: { color: "border-[#4A4A45] text-[#4A4A45] bg-[#4A4A45]/10", label: "Draft" },
  in_transit: { color: "border-[#B8A361] text-[#B8A361] bg-[#B8A361]/10", label: "In Transit" },
  delivered: { color: "border-[#4A7C59] text-[#4A7C59] bg-[#4A7C59]/10", label: "Delivered" },
}

interface DeliveryNoteStatusBadgeProps {
  status: DeliveryNoteStatus
  className?: string
}

export function DeliveryNoteStatusBadge({ status, className }: DeliveryNoteStatusBadgeProps) {
  const config = statusConfig[status] ?? { color: "border-[#4A4A45] text-[#4A4A45] bg-[#4A4A45]/10", label: status }

  return (
    <Badge variant="outline" className={cn("thin-border", config.color, className)}>
      {config.label}
    </Badge>
  )
}
