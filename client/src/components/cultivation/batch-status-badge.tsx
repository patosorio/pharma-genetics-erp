import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"
import type { BatchStatus } from "@/lib/types/common"

const statusConfig: Record<BatchStatus, { color: string; label: string }> = {
  planned: { color: "border-[#4A4A45] text-[#4A4A45] bg-[#4A4A45]/10", label: "Planned" },
  germination: { color: "border-[#C4A035] text-[#C4A035] bg-[#C4A035]/10", label: "Germination" },
  vegetative: { color: "border-[#6B7F4A] text-[#6B7F4A] bg-[#6B7F4A]/10", label: "Vegetative" },
  flowering: { color: "border-[#4A5D3A] text-[#4A5D3A] bg-[#4A5D3A]/10", label: "Flowering" },
  harvested: { color: "border-[#4A7C59] text-[#4A7C59] bg-[#4A7C59]/10", label: "Harvested" },
  cured: { color: "border-[#3D4F2F] text-[#3D4F2F] bg-[#3D4F2F]/10", label: "Cured" },
  archived: { color: "border-[#A65D57] text-[#A65D57] bg-[#A65D57]/10", label: "Archived" },
}

interface BatchStatusBadgeProps {
  status: BatchStatus
  className?: string
}

export function BatchStatusBadge({ status, className }: BatchStatusBadgeProps) {
  const config = statusConfig[status]

  return (
    <Badge variant="outline" className={cn("thin-border", config.color, className)}>
      {config.label}
    </Badge>
  )
}
