"""
API Serializers for Pharma Genetics ERP
Organized by module: Core, Genetics, Cultivation, HR, Pricing, Purchasing, Sales, Taxes, Inventory
"""

from rest_framework import serializers
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


# ========================================
# CORE SERIALIZERS
# ========================================

class UserSerializer(serializers.ModelSerializer):
    location_name = serializers.CharField(source='location.name', read_only=True)
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'role', 'location', 'location_name', 'firebase_uid', 'is_active',
            'date_joined', 'last_login', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login', 'created_at', 'updated_at']
        extra_kwargs = {
            'password': {'write_only': True},
            'firebase_uid': {'required': False}
        }
    
    def get_full_name(self, obj):
        return obj.get_full_name()


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']


class ContactSerializer(serializers.ModelSerializer):
    contact_type_display = serializers.CharField(source='get_contact_type_display', read_only=True)
    
    class Meta:
        model = Contact
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = '__all__'


class TaxTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaxType
        fields = '__all__'


class CompanySettingsSerializer(serializers.ModelSerializer):
    default_currency_code = serializers.CharField(source='default_currency.code', read_only=True)
    
    class Meta:
        model = CompanySettings
        fields = '__all__'


# ========================================
# GENETICS SERIALIZERS
# ========================================

class StrainCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = StrainCategory
        fields = '__all__'


class StrainSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    terpene_profile_display = serializers.CharField(source='get_terpene_profile_display', read_only=True)
    
    class Meta:
        model = Strain
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']


class StrainListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Strain
        fields = ['id', 'name', 'slug', 'category', 'category_name', 'is_active', 'catalogue_year']


# ========================================
# CULTIVATION SERIALIZERS
# ========================================

class MotherPlantSerializer(serializers.ModelSerializer):
    strain_name = serializers.CharField(source='strain.name', read_only=True)
    location_code = serializers.CharField(source='location.code', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    health_grade_display = serializers.CharField(source='get_health_grade_display', read_only=True)
    
    class Meta:
        model = MotherPlant
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']


class MotherPlantListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views"""
    strain_name = serializers.CharField(source='strain.name', read_only=True)
    location_code = serializers.CharField(source='location.code', read_only=True)
    
    class Meta:
        model = MotherPlant
        fields = ['id', 'code', 'strain', 'strain_name', 'location', 'location_code', 'status', 'health_grade']


class ProductionBatchSerializer(serializers.ModelSerializer):
    mother_plant_code = serializers.CharField(source='mother_plant.code', read_only=True)
    location_code = serializers.CharField(source='location.code', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    rooted_clone_count = serializers.ReadOnlyField()
    survival_rate = serializers.ReadOnlyField()
    
    class Meta:
        model = ProductionBatch
        fields = '__all__'
        read_only_fields = ['id', 'rooted_clone_count', 'survival_rate', 'created_at', 'updated_at', 'created_by', 'updated_by']


class CloneSerializer(serializers.ModelSerializer):
    strain_name = serializers.CharField(source='strain.name', read_only=True)
    location_code = serializers.CharField(source='location.code', read_only=True)
    batch_number = serializers.CharField(source='production_batch.batch_number', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    age_in_days = serializers.ReadOnlyField()
    
    class Meta:
        model = Clone
        fields = '__all__'
        read_only_fields = [
            'id', 'strain', 'location', 'age_in_days',
            'created_at', 'updated_at', 'created_by', 'updated_by'
        ]


class CloneListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views"""
    strain_name = serializers.CharField(source='strain.name', read_only=True)
    location_code = serializers.CharField(source='location.code', read_only=True)
    
    class Meta:
        model = Clone
        fields = ['id', 'code', 'strain', 'strain_name', 'location', 'location_code', 'status', 'rooting_date', 'unit_cost']


class ProductionAssumptionSerializer(serializers.ModelSerializer):
    location_code = serializers.CharField(source='location.code', read_only=True)
    
    class Meta:
        model = ProductionAssumption
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']


# ========================================
# HR SERIALIZERS
# ========================================

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']


class EmployeeSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    location_name = serializers.CharField(source='location.name', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True, allow_null=True)
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = Employee
        fields = '__all__'
        read_only_fields = ['id', 'full_name', 'created_at', 'updated_at', 'created_by', 'updated_by']


class EmployeeListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views"""
    department_name = serializers.CharField(source='department.name', read_only=True)
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = Employee
        fields = ['id', 'employee_code', 'full_name', 'department', 'department_name', 'is_active', 'hire_date']


class PayrollPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayrollPeriod
        fields = '__all__'


class PayrollSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    period_name = serializers.CharField(source='period.period_name', read_only=True)
    
    class Meta:
        model = Payroll
        fields = '__all__'
        read_only_fields = ['id', 'net_salary', 'created_at', 'updated_at', 'created_by', 'updated_by']


# ========================================
# PRICING SERIALIZERS
# ========================================

class CostAllocationRuleSerializer(serializers.ModelSerializer):
    location_code = serializers.CharField(source='location.code', read_only=True)
    
    class Meta:
        model = CostAllocationRule
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']


class PricingTierSerializer(serializers.ModelSerializer):
    tier_name_display = serializers.CharField(source='get_tier_name_display', read_only=True)
    
    class Meta:
        model = PricingTier
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']


class CostSnapshotSerializer(serializers.ModelSerializer):
    location_code = serializers.CharField(source='location.code', read_only=True)
    
    class Meta:
        model = CostSnapshot
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']


# ========================================
# PURCHASING SERIALIZERS
# ========================================

class SupplierSerializer(serializers.ModelSerializer):
    contact_name = serializers.CharField(source='contact.name', read_only=True)
    contact_email = serializers.CharField(source='contact.email', read_only=True)
    contact_phone = serializers.CharField(source='contact.phone', read_only=True)
    
    class Meta:
        model = Supplier
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']


class ExpenseCategorySerializer(serializers.ModelSerializer):
    category_type_display = serializers.CharField(source='get_category_type_display', read_only=True)
    
    class Meta:
        model = ExpenseCategory
        fields = '__all__'


class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    expense_category_name = serializers.CharField(source='expense_category.name', read_only=True)
    
    class Meta:
        model = PurchaseOrderItem
        fields = '__all__'
        read_only_fields = ['id', 'line_total']


class PurchaseOrderSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source='supplier.contact.name', read_only=True)
    location_name = serializers.CharField(source='location.name', read_only=True)
    currency_code = serializers.CharField(source='currency.code', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    items = PurchaseOrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = PurchaseOrder
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']


class PurchaseOrderListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views"""
    supplier_name = serializers.CharField(source='supplier.contact.name', read_only=True)
    
    class Meta:
        model = PurchaseOrder
        fields = ['id', 'po_number', 'supplier', 'supplier_name', 'order_date', 'status', 'total_amount']


class ExpenseSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    supplier_name = serializers.CharField(source='supplier.contact.name', read_only=True, allow_null=True)
    location_name = serializers.CharField(source='location.name', read_only=True)
    currency_code = serializers.CharField(source='currency.code', read_only=True)
    
    class Meta:
        model = Expense
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']


class PurchaseInvoiceSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source='supplier.contact.name', read_only=True)
    currency_code = serializers.CharField(source='currency.code', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    balance_due = serializers.ReadOnlyField()
    
    class Meta:
        model = PurchaseInvoice
        fields = '__all__'
        read_only_fields = ['id', 'balance_due', 'created_at', 'updated_at', 'created_by', 'updated_by']


# ========================================
# SALES SERIALIZERS
# ========================================

class CustomerSerializer(serializers.ModelSerializer):
    contact_name = serializers.CharField(source='contact.name', read_only=True)
    contact_email = serializers.CharField(source='contact.email', read_only=True)
    contact_phone = serializers.CharField(source='contact.phone', read_only=True)
    tier_display = serializers.CharField(source='get_tier_display', read_only=True)
    
    class Meta:
        model = Customer
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']


class PriceListSerializer(serializers.ModelSerializer):
    strain_name = serializers.CharField(source='strain.name', read_only=True)
    currency_code = serializers.CharField(source='currency.code', read_only=True)
    tier_display = serializers.CharField(source='get_tier_display', read_only=True)
    
    class Meta:
        model = PriceList
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']


class OrderLineSerializer(serializers.ModelSerializer):
    strain_name = serializers.CharField(source='strain.name', read_only=True)
    
    class Meta:
        model = OrderLine
        fields = '__all__'
        read_only_fields = ['id', 'line_total']


class OrderSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.contact.name', read_only=True)
    location_name = serializers.CharField(source='location.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    order_lines = OrderLineSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']


class OrderListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views"""
    customer_name = serializers.CharField(source='customer.contact.name', read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'order_number', 'customer', 'customer_name', 'order_date', 'status', 'total_amount']


class DeliveryNoteLineSerializer(serializers.ModelSerializer):
    order_line_strain = serializers.CharField(source='order_line.strain.name', read_only=True)
    
    class Meta:
        model = DeliveryNoteLine
        fields = '__all__'


class DeliveryNoteSerializer(serializers.ModelSerializer):
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    location_name = serializers.CharField(source='delivery_location.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    delivery_lines = DeliveryNoteLineSerializer(many=True, read_only=True)
    
    class Meta:
        model = DeliveryNote
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']


class SalesInvoiceSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='order.customer.contact.name', read_only=True)
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    balance_due = serializers.ReadOnlyField()
    
    class Meta:
        model = SalesInvoice
        fields = '__all__'
        read_only_fields = ['id', 'balance_due', 'created_at', 'updated_at', 'created_by', 'updated_by']


class PaymentSerializer(serializers.ModelSerializer):
    invoice_number = serializers.CharField(source='invoice.invoice_number', read_only=True)
    customer_name = serializers.CharField(source='invoice.order.customer.contact.name', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']


# ========================================
# TAXES SERIALIZERS
# ========================================

class TaxJournalEntrySerializer(serializers.ModelSerializer):
    entry_type_display = serializers.CharField(source='get_entry_type_display', read_only=True)
    tax_type_name = serializers.CharField(source='tax_type.name', read_only=True)
    
    class Meta:
        model = TaxJournalEntry
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']


class TaxReportSerializer(serializers.ModelSerializer):
    currency_code = serializers.CharField(source='currency.code', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_payable = serializers.ReadOnlyField()
    is_recoverable = serializers.ReadOnlyField()
    journal_entries = TaxJournalEntrySerializer(many=True, read_only=True)
    
    class Meta:
        model = TaxReport
        fields = '__all__'
        read_only_fields = ['id', 'is_payable', 'is_recoverable', 'created_at', 'updated_at', 'created_by', 'updated_by']


# ========================================
# INVENTORY SERIALIZERS
# ========================================

class InventoryAlertSerializer(serializers.ModelSerializer):
    strain_name = serializers.CharField(source='strain.name', read_only=True)
    location_code = serializers.CharField(source='location.code', read_only=True)
    current_stock = serializers.ReadOnlyField()
    is_low_stock = serializers.ReadOnlyField()
    stock_deficit = serializers.ReadOnlyField()
    
    class Meta:
        model = InventoryAlert
        fields = '__all__'


class StockMovementSerializer(serializers.ModelSerializer):
    clone_code = serializers.ReadOnlyField()
    strain_name = serializers.ReadOnlyField()
    from_location_code = serializers.CharField(source='from_location.code', read_only=True, allow_null=True)
    to_location_code = serializers.CharField(source='to_location.code', read_only=True, allow_null=True)
    movement_type_display = serializers.CharField(source='get_movement_type_display', read_only=True)
    
    class Meta:
        model = StockMovement
        fields = '__all__'
        read_only_fields = ['id', 'clone_code', 'strain_name', 'created_at', 'updated_at', 'created_by', 'updated_by']


class InventoryAdjustmentSerializer(serializers.ModelSerializer):
    clone_code = serializers.ReadOnlyField()
    strain_name = serializers.ReadOnlyField()
    location_code = serializers.ReadOnlyField()
    reason_display = serializers.CharField(source='get_reason_display', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    
    class Meta:
        model = InventoryAdjustment
        fields = '__all__'
        read_only_fields = ['id', 'clone_code', 'strain_name', 'location_code', 'created_at', 'updated_at', 'created_by', 'updated_by']

