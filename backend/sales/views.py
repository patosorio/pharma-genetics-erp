"""
Sales ViewSets
Customer, PriceList, Order, OrderLine, DeliveryNote, DeliveryNoteLine, SalesInvoice, Payment
"""

from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    Customer, PriceList, Order, OrderLine, DeliveryNote, DeliveryNoteLine,
    SalesInvoice, Payment
)
from .serializers import (
    CustomerSerializer, PriceListSerializer,
    OrderSerializer, OrderListSerializer, OrderLineSerializer,
    DeliveryNoteSerializer, DeliveryNoteLineSerializer,
    SalesInvoiceSerializer, PaymentSerializer
)


class CustomerViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Customer model
    """
    queryset = Customer.objects.select_related('contact').all()
    serializer_class = CustomerSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['tier']
    search_fields = ['customer_code', 'contact__name', 'contact__email']
    ordering_fields = ['customer_code', 'contact__name']
    ordering = ['customer_code']


class PriceListViewSet(viewsets.ModelViewSet):
    """
    ViewSet for PriceList model
    Pricing rules by strain and tier
    """
    queryset = PriceList.objects.select_related('strain', 'currency').all()
    serializer_class = PriceListSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['strain', 'tier', 'is_active']
    ordering_fields = ['strain', 'tier', 'price_per_clone']
    ordering = ['strain', 'tier']


class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Order model
    Customer orders with line items
    """
    queryset = Order.objects.select_related(
        'customer', 'location'
    ).prefetch_related('order_lines').all()
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'customer', 'location', 'order_date']
    search_fields = ['order_number']
    ordering_fields = ['order_date', 'total_amount']
    ordering = ['-order_date']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return OrderListSerializer
        return OrderSerializer


class OrderLineViewSet(viewsets.ModelViewSet):
    """
    ViewSet for OrderLine model
    """
    queryset = OrderLine.objects.select_related('order', 'strain').all()
    serializer_class = OrderLineSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['order', 'strain']


class DeliveryNoteViewSet(viewsets.ModelViewSet):
    """
    ViewSet for DeliveryNote model
    Physical delivery documentation
    """
    queryset = DeliveryNote.objects.select_related(
        'order', 'delivery_location'
    ).prefetch_related('delivery_lines').all()
    serializer_class = DeliveryNoteSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'order', 'delivery_date']
    search_fields = ['delivery_note_number']
    ordering_fields = ['delivery_date']
    ordering = ['-delivery_date']


class DeliveryNoteLineViewSet(viewsets.ModelViewSet):
    """
    ViewSet for DeliveryNoteLine model
    """
    queryset = DeliveryNoteLine.objects.select_related('delivery_note', 'order_line').all()
    serializer_class = DeliveryNoteLineSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['delivery_note', 'order_line']


class SalesInvoiceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for SalesInvoice model
    Sales invoices for customer billing
    """
    queryset = SalesInvoice.objects.select_related(
        'order', 'delivery_note', 'tax_type'
    ).all()
    serializer_class = SalesInvoiceSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'order', 'invoice_date', 'due_date']
    search_fields = ['invoice_number']
    ordering_fields = ['invoice_date', 'due_date', 'total_amount']
    ordering = ['-invoice_date']


class PaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Payment model
    Customer payments against invoices
    """
    queryset = Payment.objects.select_related('invoice').all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['invoice', 'payment_method', 'payment_date']
    search_fields = ['payment_number', 'reference_number']
    ordering_fields = ['payment_date', 'amount']
    ordering = ['-payment_date']
