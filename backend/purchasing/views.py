"""
Purchasing ViewSets
Supplier, ExpenseCategory, ExpenseSubcategory, PurchaseOrder, PurchaseOrderItem,
Expense (unified), PurchaseInvoice
"""

from decimal import Decimal
from django.utils import timezone
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from core.views import AuditViewSetMixin

from .models import (
    Supplier, ExpenseCategory, ExpenseSubcategory,
    PurchaseOrder, PurchaseOrderItem,
    Expense, PurchaseInvoice
)
from .serializers import (
    SupplierSerializer,
    ExpenseCategorySerializer, ExpenseCategoryListSerializer,
    ExpenseSubcategorySerializer,
    PurchaseOrderSerializer, PurchaseOrderListSerializer, PurchaseOrderItemSerializer,
    ExpenseSerializer, PurchaseInvoiceSerializer
)


PO_TRANSITIONS = {
    'draft': ['sent', 'cancelled'],
    'sent': ['confirmed', 'cancelled'],
    'confirmed': ['delivered', 'cancelled'],
    'delivered': [],
    'cancelled': [],
}


class SupplierViewSet(AuditViewSetMixin, viewsets.ModelViewSet):
    queryset = Supplier.objects.select_related('contact').all()
    serializer_class = SupplierSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['payment_terms_days']
    search_fields = ['supplier_code', 'contact__name', 'contact__email']
    ordering_fields = ['supplier_code', 'contact__name']
    ordering = ['supplier_code']


class ExpenseCategoryViewSet(AuditViewSetMixin, viewsets.ModelViewSet):
    queryset = ExpenseCategory.objects.prefetch_related('subcategories').all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category_type', 'is_active']
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'category_type']
    ordering = ['name']

    def get_serializer_class(self):
        if self.action == 'list':
            return ExpenseCategoryListSerializer
        return ExpenseCategorySerializer


class ExpenseSubcategoryViewSet(AuditViewSetMixin, viewsets.ModelViewSet):
    """
    GET  /expense-subcategories/?category=<id>   — list subcategories for a category
    GET  /expense-subcategories/?expense_type=opex — filter by type
    """
    queryset = ExpenseSubcategory.objects.select_related('category').all()
    serializer_class = ExpenseSubcategorySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'expense_type', 'is_active']
    search_fields = ['name', 'category__name']
    ordering_fields = ['category__name', 'name', 'expense_type']
    ordering = ['category__name', 'name']


class PurchaseOrderViewSet(AuditViewSetMixin, viewsets.ModelViewSet):
    queryset = PurchaseOrder.objects.select_related(
        'supplier', 'location', 'currency', 'tax_type'
    ).prefetch_related('items').all()
    serializer_class = PurchaseOrderSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'supplier', 'location']
    search_fields = ['po_number']
    ordering_fields = ['order_date', 'po_number', 'total_amount']
    ordering = ['-order_date']

    def get_serializer_class(self):
        if self.action == 'list':
            return PurchaseOrderListSerializer
        return PurchaseOrderSerializer

    def _transition(self, request, pk, target_status):
        po = self.get_object()
        allowed = PO_TRANSITIONS.get(po.status, [])
        if target_status not in allowed:
            return Response(
                {'detail': f"Cannot transition from '{po.status}' to '{target_status}'."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        po.status = target_status
        po.save(update_fields=['status'])
        return Response(PurchaseOrderSerializer(po).data)

    @action(detail=True, methods=['post'])
    def send(self, request, pk=None):
        """POST /api/v1/purchase-orders/{id}/send/"""
        return self._transition(request, pk, 'sent')

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """POST /api/v1/purchase-orders/{id}/confirm/"""
        return self._transition(request, pk, 'confirmed')

    @action(detail=True, methods=['post'])
    def mark_delivered(self, request, pk=None):
        """POST /api/v1/purchase-orders/{id}/mark_delivered/"""
        return self._transition(request, pk, 'delivered')

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """POST /api/v1/purchase-orders/{id}/cancel/"""
        return self._transition(request, pk, 'cancelled')


class PurchaseOrderItemViewSet(AuditViewSetMixin, viewsets.ModelViewSet):
    queryset = PurchaseOrderItem.objects.select_related('purchase_order', 'expense_category').all()
    serializer_class = PurchaseOrderItemSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['purchase_order', 'expense_category']


class ExpenseViewSet(AuditViewSetMixin, viewsets.ModelViewSet):
    """
    Unified expense / invoice ledger.
    Filter by document_type=expense or document_type=invoice to separate them.
    """
    queryset = Expense.objects.select_related(
        'category', 'subcategory', 'supplier', 'location', 'currency',
        'purchase_order', 'tax_type'
    ).all()
    serializer_class = ExpenseSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['document_type', 'category', 'subcategory', 'supplier', 'location', 'status']
    search_fields = ['expense_number', 'description', 'invoice_reference']
    ordering_fields = ['expense_date', 'amount', 'total_amount', 'expense_number']
    ordering = ['-expense_date']

    @action(detail=True, methods=['post'], url_path='approve')
    def approve(self, request, pk=None):
        """POST /api/v1/expenses/{id}/approve/ — approve a pending invoice."""
        expense = self.get_object()
        if expense.document_type != 'invoice':
            return Response({'detail': 'Only invoices can be approved.'}, status=status.HTTP_400_BAD_REQUEST)
        if expense.status != 'pending':
            return Response({'detail': 'Only pending invoices can be approved.'}, status=status.HTTP_400_BAD_REQUEST)
        expense.status = 'approved'
        expense.save(update_fields=['status'])
        return Response(ExpenseSerializer(expense).data)

    @action(detail=True, methods=['post'], url_path='record_payment')
    def record_payment(self, request, pk=None):
        """
        POST /api/v1/expenses/{id}/record_payment/
        Body: { amount }
        Increments paid_amount on invoice-type expenses.
        """
        expense = self.get_object()
        if expense.document_type != 'invoice':
            return Response({'detail': 'Payments can only be recorded on invoices.'}, status=status.HTTP_400_BAD_REQUEST)
        if expense.status == 'paid':
            return Response({'detail': 'Invoice is already fully paid.'}, status=status.HTTP_400_BAD_REQUEST)
        if expense.status == 'cancelled':
            return Response({'detail': 'Cannot record payment on a cancelled invoice.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            amount = Decimal(str(request.data.get('amount', 0)))
        except Exception:
            return Response({'detail': 'Invalid amount.'}, status=status.HTTP_400_BAD_REQUEST)

        if amount <= 0:
            return Response({'detail': 'Amount must be greater than zero.'}, status=status.HTTP_400_BAD_REQUEST)

        remaining = expense.balance_due
        if amount > remaining:
            return Response(
                {'detail': f'Amount ({amount}) exceeds remaining balance ({remaining}).'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        expense.paid_amount += amount
        if expense.balance_due <= 0:
            expense.status = 'paid'
            expense.payment_date = timezone.now().date()
        else:
            expense.status = 'partially_paid'
        expense.save(update_fields=['paid_amount', 'status', 'payment_date'])
        return Response(ExpenseSerializer(expense).data)

    @action(detail=False, methods=['get'], url_path='overdue')
    def overdue(self, request):
        """GET /api/v1/expenses/overdue/ — mark and return overdue invoices."""
        today = timezone.now().date()
        qs = self.get_queryset().filter(
            document_type='invoice',
            due_date__lt=today,
            status__in=['pending', 'approved', 'partially_paid'],
        )
        qs.update(status='overdue')
        qs = self.get_queryset().filter(document_type='invoice', status='overdue')
        return Response(ExpenseSerializer(qs, many=True).data)


class PurchaseInvoiceViewSet(AuditViewSetMixin, viewsets.ModelViewSet):
    """Legacy purchase invoices — kept for historical data."""
    queryset = PurchaseInvoice.objects.select_related(
        'supplier', 'purchase_order', 'currency', 'tax_type'
    ).all()
    serializer_class = PurchaseInvoiceSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'supplier', 'invoice_date', 'due_date']
    search_fields = ['invoice_number']
    ordering_fields = ['invoice_date', 'due_date', 'total_amount']
    ordering = ['-invoice_date']

    @action(detail=False, methods=['get'], url_path='overdue')
    def overdue(self, request):
        """GET /api/v1/purchase-invoices/overdue/ — mark and return overdue invoices."""
        today = timezone.now().date()
        qs = self.get_queryset().filter(
            due_date__lt=today,
            status__in=['pending', 'approved', 'partially_paid'],
        )
        qs.update(status='overdue')
        qs = self.get_queryset().filter(status='overdue')
        return Response(PurchaseInvoiceSerializer(qs, many=True).data)

    @action(detail=True, methods=['post'], url_path='approve')
    def approve(self, request, pk=None):
        """POST /api/v1/purchase-invoices/{id}/approve/"""
        invoice = self.get_object()
        if invoice.status != 'pending':
            return Response(
                {'detail': 'Only pending invoices can be approved.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        invoice.status = 'approved'
        invoice.save(update_fields=['status'])
        return Response(PurchaseInvoiceSerializer(invoice).data)

    @action(detail=True, methods=['post'], url_path='record_payment')
    def record_payment(self, request, pk=None):
        """
        POST /api/v1/purchase-invoices/{id}/record_payment/
        Body: { amount }
        """
        invoice = self.get_object()
        if invoice.status == 'paid':
            return Response({'detail': 'Invoice is already fully paid.'}, status=status.HTTP_400_BAD_REQUEST)
        if invoice.status == 'cancelled':
            return Response({'detail': 'Cannot record payment on a cancelled invoice.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            amount = Decimal(str(request.data.get('amount', 0)))
        except Exception:
            return Response({'detail': 'Invalid amount.'}, status=status.HTTP_400_BAD_REQUEST)

        if amount <= 0:
            return Response({'detail': 'Amount must be greater than zero.'}, status=status.HTTP_400_BAD_REQUEST)

        remaining = invoice.balance_due
        if amount > remaining:
            return Response(
                {'detail': f'Amount ({amount}) exceeds remaining balance ({remaining}).'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        invoice.paid_amount += amount
        if invoice.balance_due <= 0:
            invoice.status = 'paid'
        else:
            invoice.status = 'partially_paid'
        invoice.save(update_fields=['paid_amount', 'status'])
        return Response(PurchaseInvoiceSerializer(invoice).data)
