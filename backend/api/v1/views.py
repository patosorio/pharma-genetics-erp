"""
API ViewSets for Pharma Genetics ERP
Organized by module: Core, Genetics, Cultivation, HR, Pricing, Purchasing, Sales, Taxes, Inventory
"""

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from core.models import User, Location, Contact, Currency, TaxType, CompanySettings
from genetics.models import StrainCategory, Strain
from cultivation.models import MotherPlant, ProductionBatch, Clone, ProductionAssumption
from hr.models import Department, Employee, PayrollPeriod, Payroll
from pricing.models import CostAllocationRule, PricingTier, CostSnapshot
from purchasing.models import (
    Supplier, ExpenseCategory, PurchaseOrder, PurchaseOrderItem,
    Expense, PurchaseInvoice
)
from sales.models import (
    Customer, PriceList, Order, OrderLine, DeliveryNote, DeliveryNoteLine,
    SalesInvoice, Payment
)
from taxes.models import TaxReport, TaxJournalEntry
from inventory.models import InventoryAlert, StockMovement, InventoryAdjustment

from .serializers import (
    # Core
    UserSerializer, LocationSerializer, ContactSerializer,
    CurrencySerializer, TaxTypeSerializer, CompanySettingsSerializer,
    # Genetics
    StrainCategorySerializer, StrainSerializer, StrainListSerializer,
    # Cultivation
    MotherPlantSerializer, MotherPlantListSerializer,
    ProductionBatchSerializer, CloneSerializer, CloneListSerializer,
    ProductionAssumptionSerializer,
    # HR
    DepartmentSerializer, EmployeeSerializer, EmployeeListSerializer,
    PayrollPeriodSerializer, PayrollSerializer,
    # Pricing
    CostAllocationRuleSerializer, PricingTierSerializer, CostSnapshotSerializer,
    # Purchasing
    SupplierSerializer, ExpenseCategorySerializer,
    PurchaseOrderSerializer, PurchaseOrderListSerializer, PurchaseOrderItemSerializer,
    ExpenseSerializer, PurchaseInvoiceSerializer,
    # Sales
    CustomerSerializer, PriceListSerializer,
    OrderSerializer, OrderListSerializer, OrderLineSerializer,
    DeliveryNoteSerializer, DeliveryNoteLineSerializer,
    SalesInvoiceSerializer, PaymentSerializer,
    # Taxes
    TaxReportSerializer, TaxJournalEntrySerializer,
    # Inventory
    InventoryAlertSerializer, StockMovementSerializer, InventoryAdjustmentSerializer
)


# ========================================
# CORE VIEWSETS
# ========================================

class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for User model
    Provides CRUD operations for user management
    """
    queryset = User.objects.select_related('location').all()
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['role', 'is_active', 'location']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['username', 'date_joined', 'last_login']
    ordering = ['-date_joined']


class LocationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Location model
    Manages physical locations/facilities
    """
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'code']
    search_fields = ['name', 'code', 'address']
    ordering_fields = ['code', 'name']
    ordering = ['code']


class ContactViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Contact model
    Unified contacts for customers, suppliers, vendors
    """
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['contact_type', 'is_active']
    search_fields = ['name', 'email', 'phone', 'tax_id']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class CurrencyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Currency model
    """
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['code', 'name']
    ordering_fields = ['code', 'name']
    ordering = ['code']


class TaxTypeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for TaxType model
    """
    queryset = TaxType.objects.all()
    serializer_class = TaxTypeSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name']
    ordering_fields = ['name', 'rate']
    ordering = ['name']


class CompanySettingsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for CompanySettings (singleton)
    Read-only - use admin interface for updates
    """
    queryset = CompanySettings.objects.all()
    serializer_class = CompanySettingsSerializer


# ========================================
# GENETICS VIEWSETS
# ========================================

class StrainCategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for StrainCategory model
    """
    queryset = StrainCategory.objects.all()
    serializer_class = StrainCategorySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name']
    ordering = ['name']


class StrainViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Strain model
    Cannabis genetic strains with comprehensive filtering
    """
    queryset = Strain.objects.select_related('category').all()
    serializer_class = StrainSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_active', 'catalogue_year', 'terpene_profile']
    search_fields = ['name', 'slug', 'description', 'breeder', 'lineage']
    ordering_fields = ['name', 'catalogue_year', 'created_at']
    ordering = ['name']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return StrainListSerializer
        return StrainSerializer


# ========================================
# CULTIVATION VIEWSETS
# ========================================

class MotherPlantViewSet(viewsets.ModelViewSet):
    """
    ViewSet for MotherPlant model
    Mother plants used for clone production
    """
    queryset = MotherPlant.objects.select_related('strain', 'location').all()
    serializer_class = MotherPlantSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['strain', 'location', 'status', 'health_grade']
    search_fields = ['code']
    ordering_fields = ['code', 'cultivation_date', 'last_cut_date']
    ordering = ['code']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return MotherPlantListSerializer
        return MotherPlantSerializer


class ProductionBatchViewSet(viewsets.ModelViewSet):
    """
    ViewSet for ProductionBatch model
    Production batches from mother plants
    """
    queryset = ProductionBatch.objects.select_related('mother_plant', 'location').all()
    serializer_class = ProductionBatchSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'location', 'mother_plant']
    search_fields = ['batch_number']
    ordering_fields = ['cutting_date', 'batch_number']
    ordering = ['-cutting_date']
    
    @action(detail=True, methods=['post'])
    def complete_batch(self, request, pk=None):
        """
        Custom action to complete a production batch
        Calculates cost per clone and updates clone unit costs
        """
        batch = self.get_object()
        try:
            batch.complete_batch()
            serializer = self.get_serializer(batch)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class CloneViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Clone model
    Individual clone plants with comprehensive filtering
    """
    queryset = Clone.objects.select_related(
        'production_batch', 'strain', 'location',
        'reserved_for_order', 'sold_to_order'
    ).all()
    serializer_class = CloneSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'strain', 'location', 'production_batch']
    search_fields = ['code']
    ordering_fields = ['code', 'rooting_date', 'unit_cost']
    ordering = ['code']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CloneListSerializer
        return CloneSerializer
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """
        Get available clones (status='rooted')
        """
        available_clones = self.get_queryset().filter(status='rooted')
        
        # Apply filters
        strain = request.query_params.get('strain')
        location = request.query_params.get('location')
        
        if strain:
            available_clones = available_clones.filter(strain_id=strain)
        if location:
            available_clones = available_clones.filter(location_id=location)
        
        page = self.paginate_queryset(available_clones)
        if page is not None:
            serializer = CloneListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = CloneListSerializer(available_clones, many=True)
        return Response(serializer.data)


class ProductionAssumptionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for ProductionAssumption model
    Production capacity assumptions and planning
    """
    queryset = ProductionAssumption.objects.select_related('location').all()
    serializer_class = ProductionAssumptionSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['location', 'version']
    ordering_fields = ['effective_date', 'version']
    ordering = ['-effective_date', 'location']


# ========================================
# HR VIEWSETS
# ========================================

class DepartmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Department model
    """
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'code']
    ordering_fields = ['code', 'name']
    ordering = ['code']


class EmployeeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Employee model
    Employee records with department and location
    """
    queryset = Employee.objects.select_related('user', 'department', 'location').all()
    serializer_class = EmployeeSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['department', 'location', 'is_active']
    search_fields = ['employee_code', 'first_name', 'last_name', 'email']
    ordering_fields = ['employee_code', 'hire_date', 'last_name']
    ordering = ['employee_code']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return EmployeeListSerializer
        return EmployeeSerializer


class PayrollPeriodViewSet(viewsets.ModelViewSet):
    """
    ViewSet for PayrollPeriod model
    Monthly payroll periods
    """
    queryset = PayrollPeriod.objects.all()
    serializer_class = PayrollPeriodSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['is_closed']
    ordering_fields = ['start_date', 'period_name']
    ordering = ['-start_date']


class PayrollViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Payroll model
    Employee payroll records
    """
    queryset = Payroll.objects.select_related('employee', 'period').all()
    serializer_class = PayrollSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['employee', 'period', 'is_paid']
    ordering_fields = ['period__start_date', 'employee__employee_code']
    ordering = ['-period__start_date', 'employee__employee_code']


# ========================================
# PRICING VIEWSETS
# ========================================

class CostAllocationRuleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for CostAllocationRule model
    """
    queryset = CostAllocationRule.objects.select_related('location').all()
    serializer_class = CostAllocationRuleSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['location', 'is_active']
    ordering_fields = ['effective_date', 'location']
    ordering = ['-effective_date', 'location']


class PricingTierViewSet(viewsets.ModelViewSet):
    """
    ViewSet for PricingTier model
    """
    queryset = PricingTier.objects.all()
    serializer_class = PricingTierSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['tier_name', 'is_active']
    ordering_fields = ['min_quantity', 'effective_date']
    ordering = ['min_quantity', 'tier_name']


class CostSnapshotViewSet(viewsets.ModelViewSet):
    """
    ViewSet for CostSnapshot model
    Historical cost snapshots
    """
    queryset = CostSnapshot.objects.select_related('location').all()
    serializer_class = CostSnapshotSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['location']
    ordering_fields = ['snapshot_date', 'location']
    ordering = ['-snapshot_date', 'location']


# ========================================
# PURCHASING VIEWSETS
# ========================================

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


# ========================================
# SALES VIEWSETS
# ========================================

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


# ========================================
# TAXES VIEWSETS
# ========================================

class TaxReportViewSet(viewsets.ModelViewSet):
    """
    ViewSet for TaxReport model
    Tax reports for specific periods
    """
    queryset = TaxReport.objects.select_related('currency').prefetch_related('journal_entries').all()
    serializer_class = TaxReportSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'period_start', 'period_end']
    ordering_fields = ['period_end', 'report_number']
    ordering = ['-period_end']
    
    @action(detail=True, methods=['post'])
    def calculate_totals(self, request, pk=None):
        """
        Custom action to calculate tax totals from invoices
        """
        report = self.get_object()
        try:
            result = report.calculate_totals()
            return Response(result)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class TaxJournalEntryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for TaxJournalEntry model
    Individual tax journal entries
    """
    queryset = TaxJournalEntry.objects.select_related(
        'tax_report', 'sales_invoice', 'purchase_invoice', 'tax_type'
    ).all()
    serializer_class = TaxJournalEntrySerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['tax_report', 'entry_type', 'entry_date']
    ordering_fields = ['entry_date', 'tax_amount']
    ordering = ['-entry_date']


# ========================================
# INVENTORY VIEWSETS
# ========================================

class InventoryAlertViewSet(viewsets.ModelViewSet):
    """
    ViewSet for InventoryAlert model
    Reorder point alerts for low stock
    """
    queryset = InventoryAlert.objects.select_related('strain', 'location').all()
    serializer_class = InventoryAlertSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['strain', 'location', 'is_active']
    ordering_fields = ['reorder_point']
    ordering = ['strain', 'location']
    
    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """
        Get all alerts with low stock
        """
        alerts = self.get_queryset().filter(is_active=True)
        low_stock_alerts = [alert for alert in alerts if alert.is_low_stock]
        
        serializer = self.get_serializer(low_stock_alerts, many=True)
        return Response(serializer.data)


class StockMovementViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for StockMovement model (read-only)
    Audit trail for inventory movements
    """
    queryset = StockMovement.objects.select_related(
        'clone', 'from_location', 'to_location', 'performed_by'
    ).all()
    serializer_class = StockMovementSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['movement_type', 'clone', 'from_location', 'to_location', 'movement_date']
    ordering_fields = ['movement_date', 'created_at']
    ordering = ['-movement_date', '-created_at']


class InventoryAdjustmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for InventoryAdjustment model
    Manual inventory adjustments
    """
    queryset = InventoryAdjustment.objects.select_related(
        'clone', 'approved_by'
    ).all()
    serializer_class = InventoryAdjustmentSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['reason', 'adjustment_date', 'approved_by']
    ordering_fields = ['adjustment_date']
    ordering = ['-adjustment_date']

