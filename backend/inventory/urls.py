"""
Inventory URL Configuration
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    InventoryAlertViewSet, StockMovementViewSet, InventoryAdjustmentViewSet,
    InventorySummaryView, ReserveClonesView,
)

router = DefaultRouter()
router.register(r'inventory-alerts', InventoryAlertViewSet, basename='inventoryalert')
router.register(r'stock-movements', StockMovementViewSet, basename='stockmovement')
router.register(r'inventory-adjustments', InventoryAdjustmentViewSet, basename='inventoryadjustment')

urlpatterns = [
    path('', include(router.urls)),
    path('inventory/summary/<str:report_type>/', InventorySummaryView.as_view(), name='inventory-summary'),
    path('inventory/reserve_clones/', ReserveClonesView.as_view(), name='inventory-reserve-clones'),
]

