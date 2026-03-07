"""
Sales ViewSets
Customer, PriceList, Order, OrderLine, DeliveryNote, DeliveryNoteLine, SalesInvoice, Payment
"""

from django.utils import timezone
import django_filters
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from core.views import AuditViewSetMixin

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


class CustomerViewSet(AuditViewSetMixin, viewsets.ModelViewSet):
    queryset = Customer.objects.select_related('contact').all()
    serializer_class = CustomerSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['tier']
    search_fields = ['customer_code', 'contact__name', 'contact__email']
    ordering_fields = ['customer_code', 'contact__name']
    ordering = ['customer_code']

    @action(detail=True, methods=['get'], url_path='orders')
    def orders(self, request, pk=None):
        """GET /api/v1/customers/{id}/orders/ — order history for a customer"""
        customer = self.get_object()
        qs = Order.objects.filter(customer=customer).order_by('-order_date')
        serializer = OrderListSerializer(qs, many=True)
        return Response(serializer.data)


class PriceListViewSet(AuditViewSetMixin, viewsets.ModelViewSet):
    queryset = PriceList.objects.select_related('strain', 'currency').all()
    serializer_class = PriceListSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['strain', 'tier', 'is_active']
    ordering_fields = ['strain', 'tier', 'price_per_clone']
    ordering = ['strain', 'tier']


class OrderFilterSet(django_filters.FilterSet):
    status = django_filters.CharFilter(method='filter_status')

    def filter_status(self, queryset, name, value):
        statuses = [s.strip() for s in value.split(',') if s.strip()]
        return queryset.filter(status__in=statuses)

    class Meta:
        model = Order
        fields = ['customer', 'location', 'order_date']


# Valid forward-only transitions for Order status
ORDER_TRANSITIONS = {
    'draft': ['confirmed', 'cancelled'],
    'confirmed': ['in_production', 'cancelled'],
    'in_production': ['ready', 'cancelled'],
    'ready': ['partially_delivered', 'delivered', 'cancelled'],
    'partially_delivered': ['delivered', 'cancelled'],
    'delivered': [],
    'cancelled': [],
}


class OrderViewSet(AuditViewSetMixin, viewsets.ModelViewSet):
    queryset = Order.objects.select_related(
        'customer', 'location'
    ).prefetch_related('order_lines').all()
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = OrderFilterSet
    search_fields = ['order_number']
    ordering_fields = ['order_date', 'total_amount']
    ordering = ['-order_date']

    def get_serializer_class(self):
        if self.action == 'list':
            return OrderListSerializer
        return OrderSerializer

    def _transition(self, request, pk, target_status):
        order = self.get_object()
        allowed = ORDER_TRANSITIONS.get(order.status, [])
        if target_status not in allowed:
            return Response(
                {'detail': f"Cannot transition from '{order.status}' to '{target_status}'."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        order.status = target_status
        order.save(update_fields=['status'])
        return Response(OrderSerializer(order).data)

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """POST /api/v1/orders/{id}/confirm/"""
        return self._transition(request, pk, 'confirmed')

    @action(detail=True, methods=['post'])
    def mark_in_production(self, request, pk=None):
        """POST /api/v1/orders/{id}/mark_in_production/"""
        return self._transition(request, pk, 'in_production')

    @action(detail=True, methods=['post'])
    def mark_ready(self, request, pk=None):
        """POST /api/v1/orders/{id}/mark_ready/"""
        return self._transition(request, pk, 'ready')

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """POST /api/v1/orders/{id}/cancel/"""
        return self._transition(request, pk, 'cancelled')


class OrderLineViewSet(AuditViewSetMixin, viewsets.ModelViewSet):
    queryset = OrderLine.objects.select_related('order', 'strain').all()
    serializer_class = OrderLineSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['order', 'strain']


# Valid forward-only transitions for DeliveryNote status
DELIVERY_TRANSITIONS = {
    'draft': ['in_transit', 'cancelled'],
    'in_transit': ['delivered', 'partially_delivered', 'cancelled'],
    'partially_delivered': ['delivered', 'cancelled'],
    'delivered': [],
    'cancelled': [],
}


class DeliveryNoteViewSet(AuditViewSetMixin, viewsets.ModelViewSet):
    queryset = DeliveryNote.objects.select_related(
        'order', 'delivery_location'
    ).prefetch_related('delivery_lines').all()
    serializer_class = DeliveryNoteSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'order', 'delivery_date']
    search_fields = ['delivery_note_number']
    ordering_fields = ['delivery_date']
    ordering = ['-delivery_date']

    @action(detail=True, methods=['post'])
    def mark_in_transit(self, request, pk=None):
        """POST /api/v1/delivery-notes/{id}/mark_in_transit/"""
        note = self.get_object()
        allowed = DELIVERY_TRANSITIONS.get(note.status, [])
        if 'in_transit' not in allowed:
            return Response(
                {'detail': f"Cannot transition from '{note.status}' to 'in_transit'."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        note.status = 'in_transit'
        note.save(update_fields=['status'])
        return Response(DeliveryNoteSerializer(note).data)

    @action(detail=True, methods=['post'])
    def mark_delivered(self, request, pk=None):
        """POST /api/v1/delivery-notes/{id}/mark_delivered/"""
        note = self.get_object()
        allowed = DELIVERY_TRANSITIONS.get(note.status, [])
        if 'delivered' not in allowed:
            return Response(
                {'detail': f"Cannot transition from '{note.status}' to 'delivered'."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        note.status = 'delivered'
        note.save(update_fields=['status'])
        return Response(DeliveryNoteSerializer(note).data)


class DeliveryNoteLineViewSet(AuditViewSetMixin, viewsets.ModelViewSet):
    queryset = DeliveryNoteLine.objects.select_related('delivery_note', 'order_line').all()
    serializer_class = DeliveryNoteLineSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['delivery_note', 'order_line']


class SalesInvoiceViewSet(AuditViewSetMixin, viewsets.ModelViewSet):
    queryset = SalesInvoice.objects.select_related(
        'order', 'delivery_note', 'tax_type'
    ).all()
    serializer_class = SalesInvoiceSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'order', 'invoice_date', 'due_date']
    search_fields = ['invoice_number']
    ordering_fields = ['invoice_date', 'due_date', 'total_amount']
    ordering = ['-invoice_date']

    @action(detail=False, methods=['get'], url_path='overdue')
    def overdue(self, request):
        """GET /api/v1/sales-invoices/overdue/ — invoices past their due date and unpaid"""
        today = timezone.now().date()
        qs = self.get_queryset().filter(
            due_date__lt=today,
            status__in=['sent', 'partially_paid'],
        )
        # Mark them as overdue in bulk
        qs.update(status='overdue')
        qs = self.get_queryset().filter(status='overdue')
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='mark_sent')
    def mark_sent(self, request, pk=None):
        """POST /api/v1/sales-invoices/{id}/mark_sent/"""
        invoice = self.get_object()
        if invoice.status != 'draft':
            return Response(
                {'detail': "Only draft invoices can be marked as sent."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        invoice.status = 'sent'
        invoice.save(update_fields=['status'])
        return Response(SalesInvoiceSerializer(invoice).data)

    @action(detail=True, methods=['post'], url_path='record_payment')
    def record_payment(self, request, pk=None):
        """
        POST /api/v1/sales-invoices/{id}/record_payment/
        Body: { amount, payment_method, payment_date, reference_number (opt), notes (opt) }
        Atomically creates a Payment and triggers the paid_amount signal update.
        """
        invoice = self.get_object()
        if invoice.status == 'paid':
            return Response(
                {'detail': "Invoice is already fully paid."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if invoice.status == 'cancelled':
            return Response(
                {'detail': "Cannot record payment against a cancelled invoice."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = request.data.copy()
        data['invoice'] = invoice.pk
        serializer = PaymentSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        invoice.refresh_from_db()
        return Response(
            {
                'payment': serializer.data,
                'invoice': SalesInvoiceSerializer(invoice).data,
            },
            status=status.HTTP_201_CREATED,
        )


class PaymentViewSet(AuditViewSetMixin, viewsets.ModelViewSet):
    queryset = Payment.objects.select_related('invoice').all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['invoice', 'payment_method', 'payment_date']
    search_fields = ['payment_number', 'reference_number']
    ordering_fields = ['payment_date', 'amount']
    ordering = ['-payment_date']
