import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"

const statusColors: Record<string, string> = {
  active: "border-[#4A7C59] text-[#4A7C59] bg-[#4A7C59]/10",
  inactive: "border-[#A65D57] text-[#A65D57] bg-[#A65D57]/10",
  pending: "border-[#C4A035] text-[#C4A035] bg-[#C4A035]/10",
  completed: "border-[#4A7C59] text-[#4A7C59] bg-[#4A7C59]/10",
  cancelled: "border-[#A65D57] text-[#A65D57] bg-[#A65D57]/10",
  draft: "border-[#4A4A45] text-[#4A4A45] bg-[#4A4A45]/10",
}

interface StatusBadgeProps {
  status: string
  className?: string
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
  const normalizedStatus = status.toLowerCase().replace(/\s+/g, "")
  const colorClass = statusColors[normalizedStatus] || "border-[#4A4A45] text-[#4A4A45] bg-[#4A4A45]/10"

  return (
    <Badge variant="outline" className={cn("thin-border", colorClass, className)}>
      {status}
    </Badge>
  )
}
