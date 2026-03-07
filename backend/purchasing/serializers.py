"""
Purchasing Serializers
Supplier, ExpenseCategory, ExpenseSubcategory, PurchaseOrder, PurchaseOrderItem,
Expense (unified), PurchaseInvoice
"""

from rest_framework import serializers
from .models import (
    Supplier, ExpenseCategory, ExpenseSubcategory,
    PurchaseOrder, PurchaseOrderItem,
    Expense, PurchaseInvoice
)


class SupplierSerializer(serializers.ModelSerializer):
    contact_name = serializers.CharField(source='contact.name', read_only=True)
    contact_email = serializers.CharField(source='contact.email', read_only=True)
    contact_phone = serializers.CharField(source='contact.phone', read_only=True)

    class Meta:
        model = Supplier
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']


class ExpenseSubcategorySerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    expense_type_display = serializers.CharField(source='get_expense_type_display', read_only=True)

    class Meta:
        model = ExpenseSubcategory
        fields = ['id', 'category', 'category_name', 'name', 'expense_type', 'expense_type_display', 'is_active']


class ExpenseCategorySerializer(serializers.ModelSerializer):
    category_type_display = serializers.CharField(source='get_category_type_display', read_only=True)
    subcategories = ExpenseSubcategorySerializer(many=True, read_only=True)

    class Meta:
        model = ExpenseCategory
        fields = ['id', 'name', 'code', 'category_type', 'category_type_display', 'description', 'is_active', 'subcategories']


class ExpenseCategoryListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for dropdowns (no nested subcategories)."""
    category_type_display = serializers.CharField(source='get_category_type_display', read_only=True)

    class Meta:
        model = ExpenseCategory
        fields = ['id', 'name', 'code', 'category_type', 'category_type_display', 'is_active']


class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    expense_category_name = serializers.CharField(source='expense_category.name', read_only=True)

    class Meta:
        model = PurchaseOrderItem
        fields = '__all__'
        read_only_fields = ['id', 'line_total']

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero.")
        return value

    def validate_unit_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Unit price must be greater than zero.")
        return value


class PurchaseOrderSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source='supplier.contact.name', read_only=True)
    location_name = serializers.CharField(source='location.name', read_only=True)
    currency_code = serializers.CharField(source='currency.code', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    items = PurchaseOrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = PurchaseOrder
        fields = '__all__'
        read_only_fields = [
            'id', 'po_number', 'tax_amount', 'total_amount',
            'created_at', 'updated_at', 'created_by', 'updated_by',
        ]


class PurchaseOrderListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views"""
    supplier_name = serializers.CharField(source='supplier.contact.name', read_only=True)

    class Meta:
        model = PurchaseOrder
        fields = ['id', 'po_number', 'supplier', 'supplier_name', 'order_date', 'status', 'total_amount']


class ExpenseSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_type = serializers.CharField(source='category.category_type', read_only=True)
    subcategory_name = serializers.CharField(source='subcategory.name', read_only=True, allow_null=True)
    subcategory_expense_type = serializers.CharField(source='subcategory.expense_type', read_only=True, allow_null=True)
    supplier_name = serializers.CharField(source='supplier.contact.name', read_only=True, allow_null=True)
    location_name = serializers.CharField(source='location.name', read_only=True)
    location_code = serializers.CharField(source='location.code', read_only=True)
    currency_code = serializers.CharField(source='currency.code', read_only=True)
    currency_symbol = serializers.CharField(source='currency.symbol', read_only=True)
    purchase_order_number = serializers.CharField(source='purchase_order.po_number', read_only=True, allow_null=True)
    tax_type_name = serializers.CharField(source='tax_type.name', read_only=True, allow_null=True)
    balance_due = serializers.ReadOnlyField()
    document_type_display = serializers.CharField(source='get_document_type_display', read_only=True)
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = Expense
        fields = '__all__'
        read_only_fields = [
            'id', 'expense_number', 'vat_amount', 'total_amount', 'balance_due',
            'created_at', 'updated_at', 'created_by', 'updated_by',
        ]

    def get_status_display(self, obj):
        if not obj.status:
            return None
        return obj.get_status_display()

    def validate(self, data):
        document_type = data.get('document_type') or (self.instance.document_type if self.instance else 'expense')

        if document_type == 'invoice':
            due_date = data.get('due_date') or (self.instance.due_date if self.instance else None)
            expense_date = data.get('expense_date') or (self.instance.expense_date if self.instance else None)
            if due_date and expense_date and due_date < expense_date:
                raise serializers.ValidationError("due_date must be on or after invoice date.")

            paid_amount = data.get('paid_amount') if 'paid_amount' in data else (
                self.instance.paid_amount if self.instance else None
            )
            total_amount = self.instance.total_amount if self.instance else None
            if paid_amount is not None and total_amount and paid_amount > total_amount:
                raise serializers.ValidationError(
                    f"paid_amount ({paid_amount}) cannot exceed total_amount ({total_amount})."
                )

        # Ensure subcategory belongs to the selected category
        subcategory = data.get('subcategory') or (self.instance.subcategory if self.instance else None)
        category = data.get('category') or (self.instance.category if self.instance else None)
        if subcategory and category and subcategory.category_id != category.id:
            raise serializers.ValidationError("Subcategory does not belong to the selected category.")

        return data


class PurchaseInvoiceSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source='supplier.contact.name', read_only=True)
    currency_code = serializers.CharField(source='currency.code', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    balance_due = serializers.ReadOnlyField()

    class Meta:
        model = PurchaseInvoice
        fields = '__all__'
        read_only_fields = [
            'id', 'invoice_number', 'tax_amount', 'total_amount', 'balance_due',
            'created_at', 'updated_at', 'created_by', 'updated_by',
        ]

    def validate(self, data):
        due_date = data.get('due_date') or (self.instance.due_date if self.instance else None)
        invoice_date = data.get('invoice_date') or (self.instance.invoice_date if self.instance else None)
        if due_date and invoice_date and due_date < invoice_date:
            raise serializers.ValidationError("due_date must be on or after invoice_date.")

        paid_amount = data.get('paid_amount') if 'paid_amount' in data else (
            self.instance.paid_amount if self.instance else None
        )
        total_amount = data.get('total_amount') or (self.instance.total_amount if self.instance else None)
        if paid_amount is not None and total_amount and paid_amount > total_amount:
            raise serializers.ValidationError(
                f"paid_amount ({paid_amount}) cannot exceed total_amount ({total_amount})."
            )
        return data
