"""
API v1 URL Configuration
Registers all ViewSets with Django REST Framework Router
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    # Core
    UserViewSet, LocationViewSet, ContactViewSet,
    CurrencyViewSet, TaxTypeViewSet, CompanySettingsViewSet,
    # Genetics
    StrainCategoryViewSet, StrainViewSet,
    # Cultivation
    MotherPlantViewSet, ProductionBatchViewSet, CloneViewSet,
    ProductionAssumptionViewSet,
    # HR
    DepartmentViewSet, EmployeeViewSet, PayrollPeriodViewSet, PayrollViewSet,
    # Pricing
    CostAllocationRuleViewSet, PricingTierViewSet, CostSnapshotViewSet,
    # Purchasing
    SupplierViewSet, ExpenseCategoryViewSet,
    PurchaseOrderViewSet, PurchaseOrderItemViewSet,
    ExpenseViewSet, PurchaseInvoiceViewSet,
    # Sales
    CustomerViewSet, PriceListViewSet,
    OrderViewSet, OrderLineViewSet,
    DeliveryNoteViewSet, DeliveryNoteLineViewSet,
    SalesInvoiceViewSet, PaymentViewSet,
    # Taxes
    TaxReportViewSet, TaxJournalEntryViewSet,
    # Inventory
    InventoryAlertViewSet, StockMovementViewSet, InventoryAdjustmentViewSet
)

# Create router and register all viewsets
router = DefaultRouter()

# Core
router.register(r'users', UserViewSet, basename='user')
router.register(r'locations', LocationViewSet, basename='location')
router.register(r'contacts', ContactViewSet, basename='contact')
router.register(r'currencies', CurrencyViewSet, basename='currency')
router.register(r'tax-types', TaxTypeViewSet, basename='taxtype')
router.register(r'company-settings', CompanySettingsViewSet, basename='companysettings')

# Genetics
router.register(r'strain-categories', StrainCategoryViewSet, basename='straincategory')
router.register(r'strains', StrainViewSet, basename='strain')

# Cultivation
router.register(r'mother-plants', MotherPlantViewSet, basename='motherplant')
router.register(r'production-batches', ProductionBatchViewSet, basename='productionbatch')
router.register(r'clones', CloneViewSet, basename='clone')
router.register(r'production-assumptions', ProductionAssumptionViewSet, basename='productionassumption')

# HR
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'employees', EmployeeViewSet, basename='employee')
router.register(r'payroll-periods', PayrollPeriodViewSet, basename='payrollperiod')
router.register(r'payrolls', PayrollViewSet, basename='payroll')

# Pricing
router.register(r'cost-allocation-rules', CostAllocationRuleViewSet, basename='costallocationrule')
router.register(r'pricing-tiers', PricingTierViewSet, basename='pricingtier')
router.register(r'cost-snapshots', CostSnapshotViewSet, basename='costsnapshot')

# Purchasing
router.register(r'suppliers', SupplierViewSet, basename='supplier')
router.register(r'expense-categories', ExpenseCategoryViewSet, basename='expensecategory')
router.register(r'purchase-orders', PurchaseOrderViewSet, basename='purchaseorder')
router.register(r'purchase-order-items', PurchaseOrderItemViewSet, basename='purchaseorderitem')
router.register(r'expenses', ExpenseViewSet, basename='expense')
router.register(r'purchase-invoices', PurchaseInvoiceViewSet, basename='purchaseinvoice')

# Sales
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'price-lists', PriceListViewSet, basename='pricelist')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'order-lines', OrderLineViewSet, basename='orderline')
router.register(r'delivery-notes', DeliveryNoteViewSet, basename='deliverynote')
router.register(r'delivery-note-lines', DeliveryNoteLineViewSet, basename='deliverynoteline')
router.register(r'sales-invoices', SalesInvoiceViewSet, basename='salesinvoice')
router.register(r'payments', PaymentViewSet, basename='payment')

# Taxes
router.register(r'tax-reports', TaxReportViewSet, basename='taxreport')
router.register(r'tax-journal-entries', TaxJournalEntryViewSet, basename='taxjournalentry')

# Inventory
router.register(r'inventory-alerts', InventoryAlertViewSet, basename='inventoryalert')
router.register(r'stock-movements', StockMovementViewSet, basename='stockmovement')
router.register(r'inventory-adjustments', InventoryAdjustmentViewSet, basename='inventoryadjustment')

# URL patterns
urlpatterns = [
    path('', include(router.urls)),
]

