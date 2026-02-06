"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import {
  Home,
  Building2,
  Dna,
  Sprout,
  Package,
  ShoppingCart,
  ShoppingBag,
  Users,
  Receipt,
  Settings,
} from "lucide-react"
import { cn } from "@/lib/utils"

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: Home },
  {
    href: "/core",
    label: "Core",
    icon: Building2,
    children: [
      { href: "/core/users", label: "Users" },
      { href: "/core/locations", label: "Locations" },
      { href: "/core/contacts", label: "Contacts" },
    ],
  },
  {
    href: "/genetics",
    label: "Genetics",
    icon: Dna,
    children: [
      { href: "/genetics/strains", label: "Strains" },
      { href: "/genetics/categories", label: "Categories" },
    ],
  },
  {
    href: "/cultivation",
    label: "Cultivation",
    icon: Sprout,
    children: [
      { href: "/cultivation/mothers", label: "Mother Plants" },
      { href: "/cultivation/batches", label: "Production Batches" },
      { href: "/cultivation/clones", label: "Clones" },
    ],
  },
  {
    href: "/inventory",
    label: "Inventory",
    icon: Package,
    children: [
      { href: "/inventory/items", label: "Items" },
      { href: "/inventory/movements", label: "Movements" },
    ],
  },
  {
    href: "/sales",
    label: "Sales",
    icon: ShoppingCart,
    children: [
      { href: "/sales/customers", label: "Customers" },
      { href: "/sales/orders", label: "Orders" },
      { href: "/sales/invoices", label: "Invoices" },
    ],
  },
  { href: "/purchasing", label: "Purchasing", icon: ShoppingBag },
  { href: "/hr", label: "HR", icon: Users },
  { href: "/taxes", label: "Taxes", icon: Receipt },
  { href: "/settings", label: "Settings", icon: Settings },
]

export function AppSidebar() {
  const pathname = usePathname()

  return (
    <aside className="w-64 border-r border-border bg-sidebar flex flex-col">
      <div className="p-6 border-b border-border">
        <Link href="/dashboard" className="flex items-center gap-2">
          <div className="w-8 h-8 bg-primary rounded flex items-center justify-center">
            <Sprout className="w-5 h-5 text-primary-foreground" />
          </div>
          <span className="font-semibold text-lg">HitThai ERP</span>
        </Link>
      </div>

      <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
        {navItems.map((item) => {
          const Icon = item.icon
          const isActive = pathname === item.href || pathname.startsWith(item.href + "/")

          return (
            <div key={item.href}>
              <Link
                href={item.href}
                className={cn(
                  "flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors",
                  isActive
                    ? "bg-sidebar-accent text-sidebar-accent-foreground font-medium"
                    : "text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground",
                )}
              >
                <Icon className="w-4 h-4" strokeWidth={1.5} />
                {item.label}
              </Link>

              {item.children && isActive && (
                <div className="ml-7 mt-1 space-y-1">
                  {item.children.map((child) => (
                    <Link
                      key={child.href}
                      href={child.href}
                      className={cn(
                        "block px-3 py-1.5 rounded-md text-sm transition-colors",
                        pathname === child.href
                          ? "text-sidebar-primary font-medium"
                          : "text-muted-foreground hover:text-sidebar-foreground",
                      )}
                    >
                      {child.label}
                    </Link>
                  ))}
                </div>
              )}
            </div>
          )
        })}
      </nav>
    </aside>
  )
}
