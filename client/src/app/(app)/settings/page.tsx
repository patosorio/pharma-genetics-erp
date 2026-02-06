import { PageHeader } from "@/components/layout/page-header"
import { Card, CardContent } from "@/components/ui/card"

export default function SettingsPage() {
  return (
    <div>
      <PageHeader title="Settings" description="Configure system settings and preferences" />
      <Card className="thin-border">
        <CardContent className="p-12 text-center">
          <p className="text-muted-foreground">
            Settings module coming soon. This will include company settings, currencies, tax types, and system
            configuration.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
