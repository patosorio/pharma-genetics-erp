"""
API v1 URL Configuration
Aggregates all app URLs into a single API endpoint
"""

from django.urls import path, include

urlpatterns = [
    # Core - Users, Locations, Contacts, Currencies, TaxTypes, CompanySettings
    path('', include('core.urls')),
    
    # Genetics - StrainCategories, Strains
    path('', include('genetics.urls')),
    
    # Cultivation - MotherPlants, ProductionBatches, Clones, ProductionAssumptions
    path('', include('cultivation.urls')),
    
    # HR - Departments, Employees, PayrollPeriods, Payrolls
    path('', include('hr.urls')),
    
    # Pricing - CostAllocationRules, PricingTiers, CostSnapshots
    path('', include('pricing.urls')),
    
    # Purchasing - Suppliers, ExpenseCategories, PurchaseOrders, Expenses, PurchaseInvoices
    path('', include('purchasing.urls')),
    
    # Sales - Customers, PriceLists, Orders, DeliveryNotes, SalesInvoices, Payments
    path('', include('sales.urls')),
    
    # Taxes - TaxReports, TaxJournalEntries
    path('', include('taxes.urls')),
    
    # Inventory - InventoryAlerts, StockMovements, InventoryAdjustments
    path('', include('inventory.urls')),
]
