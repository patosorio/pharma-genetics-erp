"""
Purchasing URL Configuration
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    SupplierViewSet, ExpenseCategoryViewSet,
    PurchaseOrderViewSet, PurchaseOrderItemViewSet,
    ExpenseViewSet, PurchaseInvoiceViewSet
)

router = DefaultRouter()
router.register(r'suppliers', SupplierViewSet, basename='supplier')
router.register(r'expense-categories', ExpenseCategoryViewSet, basename='expensecategory')
router.register(r'purchase-orders', PurchaseOrderViewSet, basename='purchaseorder')
router.register(r'purchase-order-items', PurchaseOrderItemViewSet, basename='purchaseorderitem')
router.register(r'expenses', ExpenseViewSet, basename='expense')
router.register(r'purchase-invoices', PurchaseInvoiceViewSet, basename='purchaseinvoice')

urlpatterns = [
    path('', include(router.urls)),
]

