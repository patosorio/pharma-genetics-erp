import { PageHeader } from "@/components/layout/page-header"
import { Card, CardContent } from "@/components/ui/card"

export default function HRPage() {
  return (
    <div>
      <PageHeader title="Human Resources" description="Manage employees, attendance, and payroll" />
      <Card className="thin-border">
        <CardContent className="p-12 text-center">
          <p className="text-muted-foreground">
            HR module coming soon. This will include employee records, attendance tracking, and payroll management.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
