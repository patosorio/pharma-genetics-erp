import { PageHeader } from "@/components/layout/page-header"
import { Card, CardContent } from "@/components/ui/card"

export default function PurchasingPage() {
  return (
    <div>
      <PageHeader title="Purchasing" description="Manage supplier orders and procurement" />
      <Card className="thin-border">
        <CardContent className="p-12 text-center">
          <p className="text-muted-foreground">
            Purchasing module coming soon. This will include purchase orders, supplier management, and receiving.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
