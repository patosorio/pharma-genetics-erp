"use client"

import type React from "react"
import { ChevronLeft, ChevronRight } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

export interface Column<T> {
  key: string
  label: string
  render?: (item: T) => React.ReactNode
}

interface DataTableProps<T> {
  columns: Column<T>[]
  data: T[]
  loading?: boolean
  emptyMessage?: string
  pagination?: {
    currentPage: number
    totalPages: number
    pageSize: number
    totalItems: number
    onPageChange: (page: number) => void
    onPageSizeChange: (size: number) => void
  }
  // Selection
  selectable?: boolean
  selectedIds?: Set<number | string>
  onSelectionChange?: (ids: Set<number | string>) => void
  batchActions?: React.ReactNode
}

export function DataTable<T extends { id: number | string }>({
  columns,
  data,
  loading,
  emptyMessage = "No data available",
  pagination,
  selectable,
  selectedIds,
  onSelectionChange,
  batchActions,
}: DataTableProps<T>) {
  const allPageIds = data.map((item) => item.id)
  const selectedOnPage = allPageIds.filter((id) => selectedIds?.has(id))
  const allSelected = allPageIds.length > 0 && selectedOnPage.length === allPageIds.length
  const someSelected = selectedOnPage.length > 0 && !allSelected

  const toggleAll = () => {
    if (!onSelectionChange || !selectedIds) return
    const next = new Set(selectedIds)
    if (allSelected) {
      allPageIds.forEach((id) => next.delete(id))
    } else {
      allPageIds.forEach((id) => next.add(id))
    }
    onSelectionChange(next)
  }

  const toggleRow = (id: number | string) => {
    if (!onSelectionChange || !selectedIds) return
    const next = new Set(selectedIds)
    if (next.has(id)) next.delete(id)
    else next.add(id)
    onSelectionChange(next)
  }

  const selectionCount = selectedIds?.size ?? 0

  return (
    <div className="space-y-3">
      {/* Batch action bar */}
      {selectable && selectionCount > 0 && batchActions && (
        <div className="flex items-center gap-3 px-4 py-2 bg-primary/5 border border-primary/20 rounded-lg">
          <span className="text-sm font-medium text-primary">
            {selectionCount} selected
          </span>
          <div className="flex items-center gap-2">{batchActions}</div>
          <Button
            variant="ghost"
            size="sm"
            className="ml-auto text-muted-foreground"
            onClick={() => onSelectionChange?.(new Set())}
          >
            Clear
          </Button>
        </div>
      )}

      <div className="border border-border rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-muted">
              <tr>
                {selectable && (
                  <th className="px-4 py-3 w-10 border-b border-border">
                    <input
                      type="checkbox"
                      checked={allSelected}
                      ref={(el) => { if (el) el.indeterminate = someSelected }}
                      onChange={toggleAll}
                      aria-label="Select all"
                      className="h-4 w-4 cursor-pointer accent-primary"
                    />
                  </th>
                )}
                {columns.map((column) => (
                  <th key={column.key} className="px-4 py-3 text-left text-sm font-medium border-b border-border">
                    {column.label}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={columns.length + (selectable ? 1 : 0)} className="px-4 py-8 text-center text-muted-foreground">
                    Loading...
                  </td>
                </tr>
              ) : data.length === 0 ? (
                <tr>
                  <td colSpan={columns.length + (selectable ? 1 : 0)} className="px-4 py-8 text-center text-muted-foreground">
                    {emptyMessage}
                  </td>
                </tr>
              ) : (
                data.map((item) => (
                  <tr key={item.id} className="hover:bg-muted/50 transition-colors">
                    {selectable && (
                      <td className="px-4 py-3 w-10 border-b border-border">
                        <input
                          type="checkbox"
                          checked={selectedIds?.has(item.id) ?? false}
                          onChange={() => toggleRow(item.id)}
                          aria-label="Select row"
                          className="h-4 w-4 cursor-pointer accent-primary"
                        />
                      </td>
                    )}
                    {columns.map((column) => (
                      <td key={column.key} className="px-4 py-3 text-sm border-b border-border">
                        {column.render ? column.render(item) : (item as Record<string, unknown>)[column.key] as React.ReactNode}
                      </td>
                    ))}
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {pagination && (
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-sm text-muted-foreground">Rows per page:</span>
            <Select
              value={pagination.pageSize.toString()}
              onValueChange={(value) => pagination.onPageSizeChange(Number(value))}
            >
              <SelectTrigger className="w-16 h-8">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="10">10</SelectItem>
                <SelectItem value="20">20</SelectItem>
                <SelectItem value="50">50</SelectItem>
                <SelectItem value="100">100</SelectItem>
              </SelectContent>
            </Select>
            <span className="text-sm text-muted-foreground ml-4">
              {(pagination.currentPage - 1) * pagination.pageSize + 1}–
              {Math.min(pagination.currentPage * pagination.pageSize, pagination.totalItems)} of {pagination.totalItems}
            </span>
          </div>

          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => pagination.onPageChange(pagination.currentPage - 1)}
              disabled={pagination.currentPage === 1}
            >
              <ChevronLeft className="w-4 h-4" />
            </Button>
            <span className="text-sm">
              Page {pagination.currentPage} of {pagination.totalPages}
            </span>
            <Button
              variant="outline"
              size="sm"
              onClick={() => pagination.onPageChange(pagination.currentPage + 1)}
              disabled={pagination.currentPage === pagination.totalPages}
            >
              <ChevronRight className="w-4 h-4" />
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}
