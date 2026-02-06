"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts"

const data = [
  { status: "Cutting", count: 5 },
  { status: "Rooting", count: 12 },
  { status: "Completed", count: 18 },
  { status: "Failed", count: 3 },
]

export function BatchStatusChart() {
  return (
    <Card className="thin-border">
      <CardHeader>
        <CardTitle className="text-lg">Production Batches by Status</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#E8E8E3" />
            <XAxis dataKey="status" tick={{ fontSize: 12 }} stroke="#4A4A45" />
            <YAxis tick={{ fontSize: 12 }} stroke="#4A4A45" />
            <Tooltip
              contentStyle={{
                backgroundColor: "#FFFFFF",
                border: "1px solid #E8E8E3",
                borderRadius: "6px",
              }}
            />
            <Bar dataKey="count" fill="#3D4F2F" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}
