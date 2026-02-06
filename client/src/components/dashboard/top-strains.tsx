import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

interface StrainData {
  id: string
  name: string
  category: string
  activeBatches: number
  totalYield: string
}

const mockStrains: StrainData[] = [
  { id: "1", name: "OG Kush", category: "Indica Dominant", activeBatches: 5, totalYield: "45.2 kg" },
  { id: "2", name: "Blue Dream", category: "Hybrid", activeBatches: 4, totalYield: "38.7 kg" },
  { id: "3", name: "Sour Diesel", category: "Sativa", activeBatches: 3, totalYield: "32.1 kg" },
  { id: "4", name: "Girl Scout Cookies", category: "Hybrid", activeBatches: 3, totalYield: "28.9 kg" },
  { id: "5", name: "White Widow", category: "Hybrid", activeBatches: 2, totalYield: "24.5 kg" },
]

export function TopStrains() {
  return (
    <Card className="thin-border">
      <CardHeader>
        <CardTitle className="text-lg">Top Performing Strains</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {mockStrains.map((strain) => (
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
                <p className="text-sm font-medium data-value">{strain.totalYield}</p>
                <p className="text-xs text-muted-foreground">
                  {strain.activeBatches} active {strain.activeBatches === 1 ? "batch" : "batches"}
                </p>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
