import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"
import type { TaxReportStatus } from "@/lib/types/common"

const statusConfig: Record<TaxReportStatus, { color: string; label: string }> = {
  draft: { color: "border-[#4A4A45] text-[#4A4A45] bg-[#4A4A45]/10", label: "Draft" },
  finalized: { color: "border-[#5A7A8C] text-[#5A7A8C] bg-[#5A7A8C]/10", label: "Finalized" },
  filed: { color: "border-[#B8A361] text-[#B8A361] bg-[#B8A361]/10", label: "Filed" },
  paid: { color: "border-[#4A7C59] text-[#4A7C59] bg-[#4A7C59]/10", label: "Paid" },
}

interface TaxReportStatusBadgeProps {
  status: TaxReportStatus
  className?: string
}

export function TaxReportStatusBadge({ status, className }: TaxReportStatusBadgeProps) {
  const config = statusConfig[status] ?? { color: "border-[#4A4A45] text-[#4A4A45] bg-[#4A4A45]/10", label: status }
  return (
    <Badge variant="outline" className={cn("thin-border", config.color, className)}>
      {config.label}
    </Badge>
  )
}
