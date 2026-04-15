import type React from "react"

interface PageHeaderProps {
  title: string
  description?: string
  action?: React.ReactNode
  filters?: React.ReactNode
}

export function PageHeader({ title, description, action, filters }: PageHeaderProps) {
  return (
    <div className="mb-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-semibold mb-1">{title}</h1>
          {description && <p className="text-sm text-muted-foreground">{description}</p>}
        </div>
        {action && <div className="flex items-center gap-2">{action}</div>}
      </div>
      {filters && <div className="flex items-center gap-3 mt-4">{filters}</div>}
    </div>
  )
}
