"use client"

import { useInventorySummaryByStrain, useInventorySummaryByLocation, useInventoryValue } from "@/hooks/use-inventory-reports"
import { PageHeader } from "@/components/layout/page-header"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

export default function InventoryReportsPage() {
  const { data: byStrain, isLoading: loadingStrain } = useInventorySummaryByStrain()
  const { data: byLocation, isLoading: loadingLocation } = useInventorySummaryByLocation()
  const { data: valueData } = useInventoryValue()

  return (
    <div>
      <PageHeader
        title="Inventory Reports"
        description="Summary views and analytics across all inventory"
      />

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <Card className="thin-border">
          <CardContent className="p-6">
            <p className="text-sm text-muted-foreground mb-1">Total Inventory Value</p>
            <p className="text-2xl font-semibold data-value">
              {valueData ? `฿${Number.parseFloat(valueData.total_value).toLocaleString()}` : "—"}
            </p>
          </CardContent>
        </Card>
        <Card className="thin-border">
          <CardContent className="p-6">
            <p className="text-sm text-muted-foreground mb-1">Total Rooted Clones</p>
            <p className="text-2xl font-semibold data-value">
              {byStrain ? byStrain.reduce((s, r) => s + r.rooted_clones, 0).toLocaleString() : "—"}
            </p>
          </CardContent>
        </Card>
        <Card className="thin-border">
          <CardContent className="p-6">
            <p className="text-sm text-muted-foreground mb-1">Available Clones</p>
            <p className="text-2xl font-semibold data-value text-[#4A7C59]">
              {byStrain ? byStrain.reduce((s, r) => s + r.available_clones, 0).toLocaleString() : "—"}
            </p>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="by_strain">
        <TabsList className="mb-4">
          <TabsTrigger value="by_strain">By Strain</TabsTrigger>
          <TabsTrigger value="by_location">By Location</TabsTrigger>
        </TabsList>

        <TabsContent value="by_strain">
          <Card className="thin-border">
            <CardHeader>
              <CardTitle className="text-base">Inventory Summary by Strain</CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-muted">
                    <tr>
                      <th className="px-4 py-3 text-left text-sm font-medium border-b border-border">Strain</th>
                      <th className="px-4 py-3 text-left text-sm font-medium border-b border-border">Total</th>
                      <th className="px-4 py-3 text-left text-sm font-medium border-b border-border">Rooted</th>
                      <th className="px-4 py-3 text-left text-sm font-medium border-b border-border">Reserved</th>
                      <th className="px-4 py-3 text-left text-sm font-medium border-b border-border">Available</th>
                    </tr>
                  </thead>
                  <tbody>
                    {loadingStrain ? (
                      <tr>
                        <td colSpan={5} className="px-4 py-8 text-center text-muted-foreground">Loading...</td>
                      </tr>
                    ) : !byStrain?.length ? (
                      <tr>
                        <td colSpan={5} className="px-4 py-8 text-center text-muted-foreground">No inventory data</td>
                      </tr>
                    ) : (
                      byStrain.map((row) => (
                        <tr key={row.strain_id} className="hover:bg-muted/50 transition-colors">
                          <td className="px-4 py-3 text-sm border-b border-border font-medium">{row.strain_name}</td>
                          <td className="px-4 py-3 text-sm border-b border-border data-value">{row.total_clones}</td>
                          <td className="px-4 py-3 text-sm border-b border-border data-value">{row.rooted_clones}</td>
                          <td className="px-4 py-3 text-sm border-b border-border data-value text-[#B8A361]">{row.reserved_clones}</td>
                          <td className="px-4 py-3 text-sm border-b border-border data-value text-[#4A7C59] font-medium">{row.available_clones}</td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="by_location">
          <Card className="thin-border">
            <CardHeader>
              <CardTitle className="text-base">Inventory Summary by Location</CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-muted">
                    <tr>
                      <th className="px-4 py-3 text-left text-sm font-medium border-b border-border">Location</th>
                      <th className="px-4 py-3 text-left text-sm font-medium border-b border-border">Total</th>
                      <th className="px-4 py-3 text-left text-sm font-medium border-b border-border">Rooted</th>
                      <th className="px-4 py-3 text-left text-sm font-medium border-b border-border">Reserved</th>
                      <th className="px-4 py-3 text-left text-sm font-medium border-b border-border">Available</th>
                    </tr>
                  </thead>
                  <tbody>
                    {loadingLocation ? (
                      <tr>
                        <td colSpan={5} className="px-4 py-8 text-center text-muted-foreground">Loading...</td>
                      </tr>
                    ) : !byLocation?.length ? (
                      <tr>
                        <td colSpan={5} className="px-4 py-8 text-center text-muted-foreground">No inventory data</td>
                      </tr>
                    ) : (
                      byLocation.map((row) => (
                        <tr key={row.location_id} className="hover:bg-muted/50 transition-colors">
                          <td className="px-4 py-3 text-sm border-b border-border font-medium">{row.location_code}</td>
                          <td className="px-4 py-3 text-sm border-b border-border data-value">{row.total_clones}</td>
                          <td className="px-4 py-3 text-sm border-b border-border data-value">{row.rooted_clones}</td>
                          <td className="px-4 py-3 text-sm border-b border-border data-value text-[#B8A361]">{row.reserved_clones}</td>
                          <td className="px-4 py-3 text-sm border-b border-border data-value text-[#4A7C59] font-medium">{row.available_clones}</td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
