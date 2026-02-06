import { PageHeader } from "@/components/layout/page-header"
import { Card, CardContent } from "@/components/ui/card"

export default function TaxesPage() {
  return (
    <div>
      <PageHeader title="Tax Management" description="Track tax obligations and generate tax reports" />
      <Card className="thin-border">
        <CardContent className="p-12 text-center">
          <p className="text-muted-foreground">
            Tax module coming soon. This will include tax reporting, VAT tracking, and compliance management.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
