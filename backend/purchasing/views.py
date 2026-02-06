"""
Purchasing ViewSets
Supplier, ExpenseCategory, PurchaseOrder, PurchaseOrderItem, Expense, PurchaseInvoice
"""

from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    Supplier, ExpenseCategory, PurchaseOrder, PurchaseOrderItem,
    Expense, PurchaseInvoice
)
from .serializers import (
    SupplierSerializer, ExpenseCategorySerializer,
    PurchaseOrderSerializer, PurchaseOrderListSerializer, PurchaseOrderItemSerializer,
    ExpenseSerializer, PurchaseInvoiceSerializer
)


class SupplierViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Supplier model
    """
    queryset = Supplier.objects.select_related('contact').all()
    serializer_class = SupplierSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['supplier_code', 'contact__name', 'contact__email']
    ordering_fields = ['supplier_code', 'contact__name']
    ordering = ['supplier_code']


class ExpenseCategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for ExpenseCategory model
    """
    queryset = ExpenseCategory.objects.all()
    serializer_class = ExpenseCategorySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category_type', 'is_active']
    search_fields = ['name', 'code']
    ordering_fields = ['code', 'name']
    ordering = ['code']


class PurchaseOrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for PurchaseOrder model
    Purchase orders with line items
    """
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


class PurchaseOrderItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet for PurchaseOrderItem model
    """
    queryset = PurchaseOrderItem.objects.select_related('purchase_order', 'expense_category').all()
    serializer_class = PurchaseOrderItemSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['purchase_order', 'expense_category']


class ExpenseViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Expense model
    Individual expense records
    """
    queryset = Expense.objects.select_related(
        'category', 'supplier', 'location', 'currency', 'purchase_order'
    ).all()
    serializer_class = ExpenseSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'supplier', 'location', 'expense_date']
    search_fields = ['expense_number', 'description']
    ordering_fields = ['expense_date', 'amount']
    ordering = ['-expense_date']


class PurchaseInvoiceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for PurchaseInvoice model
    Supplier invoices for payables tracking
    """
    queryset = PurchaseInvoice.objects.select_related(
        'supplier', 'purchase_order', 'currency', 'tax_type'
    ).all()
    serializer_class = PurchaseInvoiceSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'supplier', 'invoice_date', 'due_date']
    search_fields = ['invoice_number']
    ordering_fields = ['invoice_date', 'due_date', 'total_amount']
    ordering = ['-invoice_date']
