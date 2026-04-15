"""
Sales URL Configuration
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CustomerViewSet, PriceListViewSet,
    OrderViewSet, OrderLineViewSet,
    DeliveryNoteViewSet, DeliveryNoteLineViewSet,
    SalesInvoiceViewSet, PaymentViewSet
)

router = DefaultRouter()
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'price-lists', PriceListViewSet, basename='pricelist')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'order-lines', OrderLineViewSet, basename='orderline')
router.register(r'delivery-notes', DeliveryNoteViewSet, basename='deliverynote')
router.register(r'delivery-note-lines', DeliveryNoteLineViewSet, basename='deliverynoteline')
router.register(r'sales-invoices', SalesInvoiceViewSet, basename='salesinvoice')
router.register(r'payments', PaymentViewSet, basename='payment')

urlpatterns = [
    path('', include(router.urls)),
]

