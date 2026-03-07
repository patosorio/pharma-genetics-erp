import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

interface StrainData {
  id: number
  name: string
  category: string
  activeClones: number
}

interface TopStrainsProps {
  strains?: StrainData[]
}

export function TopStrains({ strains = [] }: TopStrainsProps) {
  return (
    <Card className="thin-border">
      <CardHeader>
        <CardTitle className="text-lg">Inventory by Strain</CardTitle>
      </CardHeader>
      <CardContent>
        {strains.length === 0 ? (
          <p className="text-sm text-muted-foreground text-center py-8">No inventory data available</p>
        ) : (
          <div className="space-y-3">
            {strains.map((strain) => (
              <div
                key={strain.id}
                className="flex items-center justify-between py-3 border-b border-border last:border-0"
              >
                <div className="flex-1">
                  <p className="font-medium mb-1">{strain.name}</p>
                  <Badge variant="outline" className="text-xs thin-border">
                    {strain.category}
                  </Badge>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium data-value">{strain.activeClones}</p>
                  <p className="text-xs text-muted-foreground">rooted clones</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
