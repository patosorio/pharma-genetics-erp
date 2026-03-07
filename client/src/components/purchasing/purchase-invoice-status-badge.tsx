import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"
import type { PurchaseInvoiceStatus } from "@/lib/types/common"

const statusConfig: Record<PurchaseInvoiceStatus, { color: string; label: string }> = {
  pending: { color: "border-[#4A4A45] text-[#4A4A45] bg-[#4A4A45]/10", label: "Pending" },
  approved: { color: "border-[#5A7A8C] text-[#5A7A8C] bg-[#5A7A8C]/10", label: "Approved" },
  paid: { color: "border-[#4A7C59] text-[#4A7C59] bg-[#4A7C59]/10", label: "Paid" },
  overdue: { color: "border-[#A65D57] text-[#A65D57] bg-[#A65D57]/10", label: "Overdue" },
  cancelled: { color: "border-[#4A4A45] text-[#4A4A45] bg-[#4A4A45]/10", label: "Cancelled" },
}

interface PurchaseInvoiceStatusBadgeProps {
  status: PurchaseInvoiceStatus
  className?: string
}

export function PurchaseInvoiceStatusBadge({ status, className }: PurchaseInvoiceStatusBadgeProps) {
  const config = statusConfig[status] ?? { color: "border-[#4A4A45] text-[#4A4A45] bg-[#4A4A45]/10", label: status }
  return (
    <Badge variant="outline" className={cn("thin-border", config.color, className)}>
      {config.label}
    </Badge>
  )
}
