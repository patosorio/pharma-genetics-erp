from django.contrib import admin
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget
from .models import (
    Supplier, ExpenseCategory, ExpenseSubcategory,
    PurchaseOrder, PurchaseOrderItem,
    Expense, PurchaseInvoice,
    CapexBudget, CapexBudgetLine,
    FixedAsset, DepreciationEntry,
)
from core.models import Location, Currency


class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 1
    fields = ['expense_category', 'description', 'quantity', 'unit_price', 'line_total']
    readonly_fields = ['line_total']


class ExpenseSubcategoryInline(admin.TabularInline):
    model = ExpenseSubcategory
    extra = 1
    fields = ['name', 'expense_type', 'is_active']


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['supplier_code', 'contact_name', 'payment_terms_days', 'is_active']
    list_filter = ['contact__is_active']
    search_fields = ['supplier_code', 'contact__name', 'contact__email']
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']

    fieldsets = (
        ('Basic Information', {'fields': ('supplier_code', 'contact')}),
        ('Payment Terms', {'fields': ('payment_terms_days',)}),
        ('Audit Trail', {'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'), 'classes': ('collapse',)}),
    )

    def contact_name(self, obj):
        return obj.contact.name
    contact_name.short_description = 'Name'
    contact_name.admin_order_field = 'contact__name'

    def is_active(self, obj):
        return obj.contact.is_active
    is_active.short_description = 'Active'
    is_active.boolean = True
    is_active.admin_order_field = 'contact__is_active'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('contact')


@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category_type', 'subcategory_count', 'is_active']
    list_filter = ['category_type', 'is_active']
    search_fields = ['name', 'code']
    inlines = [ExpenseSubcategoryInline]

    fieldsets = (
        ('Basic Information', {'fields': ('name', 'code', 'category_type', 'is_active')}),
        ('Description', {'fields': ('description',)}),
    )

    def subcategory_count(self, obj):
        return obj.subcategories.count()
    subcategory_count.short_description = '# Subcategories'


@admin.register(ExpenseSubcategory)
class ExpenseSubcategoryAdmin(admin.ModelAdmin):
    list_display = ['category', 'name', 'expense_type', 'is_active']
    list_filter = ['expense_type', 'is_active', 'category']
    search_fields = ['name', 'category__name']
    ordering = ['category__name', 'name']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category')


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = [
        'po_number', 'supplier_name', 'location', 'order_date',
        'expected_delivery_date', 'status', 'total_amount', 'currency'
    ]
    list_filter = ['status', 'location', 'order_date']
    search_fields = ['po_number', 'supplier__supplier_code', 'supplier__contact__name']
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']
    inlines = [PurchaseOrderItemInline]

    fieldsets = (
        ('Basic Information', {'fields': ('po_number', 'supplier', 'location', 'status')}),
        ('Dates', {'fields': ('order_date', 'expected_delivery_date')}),
        ('Tax & Amounts', {'fields': ('tax_type', 'base_amount', 'tax_amount', 'total_amount', 'currency')}),
        ('Notes', {'fields': ('notes',)}),
        ('Audit Trail', {'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'), 'classes': ('collapse',)}),
    )
    actions = ['mark_as_sent', 'mark_as_confirmed', 'mark_as_delivered']

    def supplier_name(self, obj):
        return obj.supplier.contact.name
    supplier_name.short_description = 'Supplier'
    supplier_name.admin_order_field = 'supplier__contact__name'

    def mark_as_sent(self, request, queryset):
        updated = queryset.filter(status='draft').update(status='sent')
        self.message_user(request, f"Successfully marked {updated} purchase order(s) as sent.")
    mark_as_sent.short_description = "Mark selected POs as sent"

    def mark_as_confirmed(self, request, queryset):
        updated = queryset.filter(status='sent').update(status='confirmed')
        self.message_user(request, f"Successfully confirmed {updated} purchase order(s).")
    mark_as_confirmed.short_description = "Mark selected POs as confirmed"

    def mark_as_delivered(self, request, queryset):
        updated = queryset.filter(status='confirmed').update(status='delivered')
        self.message_user(request, f"Successfully marked {updated} purchase order(s) as delivered.")
    mark_as_delivered.short_description = "Mark selected POs as delivered"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('supplier__contact', 'location', 'currency')


@admin.register(PurchaseInvoice)
class PurchaseInvoiceAdmin(admin.ModelAdmin):
    list_display = [
        'invoice_number', 'supplier_name', 'invoice_date', 'due_date',
        'total_amount', 'paid_amount', 'balance_due', 'currency', 'status'
    ]
    list_filter = ['status', 'invoice_date', 'due_date']
    search_fields = ['invoice_number', 'supplier__supplier_code', 'supplier__contact__name', 'purchase_order__po_number']
    readonly_fields = ['balance_due', 'created_at', 'updated_at', 'created_by', 'updated_by']

    fieldsets = (
        ('Basic Information', {'fields': ('invoice_number', 'supplier', 'purchase_order', 'status')}),
        ('Dates', {'fields': ('invoice_date', 'due_date')}),
        ('Tax & Amounts', {'fields': ('tax_type', 'base_amount', 'tax_amount', 'total_amount', 'paid_amount', 'balance_due', 'currency')}),
        ('Notes', {'fields': ('notes',)}),
        ('Audit Trail', {'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'), 'classes': ('collapse',)}),
    )
    actions = ['mark_as_approved', 'mark_as_paid']

    def supplier_name(self, obj):
        return obj.supplier.contact.name
    supplier_name.short_description = 'Supplier'
    supplier_name.admin_order_field = 'supplier__contact__name'

    def mark_as_approved(self, request, queryset):
        updated = queryset.filter(status='pending').update(status='approved')
        self.message_user(request, f"Successfully approved {updated} invoice(s).")
    mark_as_approved.short_description = "Mark selected invoices as approved"

    def mark_as_paid(self, request, queryset):
        for invoice in queryset.filter(status__in=['approved', 'partially_paid']):
            if invoice.balance_due == 0:
                invoice.status = 'paid'
                invoice.save()
        self.message_user(request, "Updated invoice statuses based on payments.")
    mark_as_paid.short_description = "Update status to paid (if balance is zero)"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('supplier__contact', 'purchase_order', 'currency')


# ---------------------------------------------------------------------------
# Import/Export resource for Expense
# ---------------------------------------------------------------------------

class ExpenseResource(resources.ModelResource):
    category = fields.Field(
        column_name='category',
        attribute='category',
        widget=ForeignKeyWidget(ExpenseCategory, field='name'),
    )
    location = fields.Field(
        column_name='location',
        attribute='location',
        widget=ForeignKeyWidget(Location, field='code'),
    )
    currency = fields.Field(
        column_name='currency',
        attribute='currency',
        widget=ForeignKeyWidget(Currency, field='code'),
    )

    class Meta:
        model = Expense
        fields = (
            'id', 'expense_number', 'document_type', 'category', 'location',
            'expense_date', 'amount', 'currency', 'description',
            'invoice_reference', 'due_date', 'status',
        )
        export_order = fields


@admin.register(Expense)
class ExpenseAdmin(ImportExportModelAdmin):
    resource_classes = [ExpenseResource]
    list_display = [
        'expense_number', 'document_type', 'category', 'subcategory_display',
        'supplier_name', 'location', 'expense_date', 'amount', 'currency', 'status'
    ]
    list_filter = ['document_type', 'category', 'location', 'expense_date', 'status']
    search_fields = ['expense_number', 'description', 'invoice_reference', 'supplier__contact__name']
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']

    fieldsets = (
        ('Basic Information', {
            'fields': ('expense_number', 'document_type', 'category', 'subcategory', 'supplier', 'location')
        }),
        ('Date and Amount', {
            'fields': ('expense_date', 'amount', 'currency')
        }),
        ('Details', {
            'fields': ('description', 'purchase_order')
        }),
        ('Invoice Fields', {
            'fields': (
                'invoice_reference', 'due_date', 'tax_type', 'vat_amount',
                'retention_amount', 'total_amount', 'paid_amount', 'status', 'payment_date'
            ),
            'classes': ('collapse',),
            'description': 'These fields are only relevant when document_type = Invoice',
        }),
        ('Audit Trail', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )

    def supplier_name(self, obj):
        return obj.supplier.contact.name if obj.supplier else '-'
    supplier_name.short_description = 'Supplier'
    supplier_name.admin_order_field = 'supplier__contact__name'

    def subcategory_display(self, obj):
        return obj.subcategory.name if obj.subcategory else '—'
    subcategory_display.short_description = 'Subcategory'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'category', 'subcategory', 'supplier__contact', 'location', 'currency', 'purchase_order'
        )


# ---------------------------------------------------------------------------
# CAPEX Budget admin
# ---------------------------------------------------------------------------

class CapexBudgetLineInline(admin.TabularInline):
    model = CapexBudgetLine
    extra = 1
    fields = ['expense_category', 'budgeted_amount', 'actual_spend_display', 'variance_display', 'description']
    readonly_fields = ['actual_spend_display', 'variance_display']

    def actual_spend_display(self, obj):
        if obj.pk:
            return f"{obj.actual_spend:,.2f}"
        return '-'
    actual_spend_display.short_description = 'Actual Spend'

    def variance_display(self, obj):
        if obj.pk:
            v = obj.variance
            return f"{v:,.2f}"
        return '-'
    variance_display.short_description = 'Variance'


@admin.register(CapexBudget)
class CapexBudgetAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'location', 'status', 'total_budget', 'currency',
        'actual_spend_display', 'variance_display', 'utilization_pct_display',
        'start_date', 'expected_completion_date',
    ]
    list_filter = ['status', 'location', 'currency']
    search_fields = ['name']
    readonly_fields = [
        'actual_spend_display', 'variance_display', 'utilization_pct_display',
        'created_at', 'updated_at', 'created_by', 'updated_by',
    ]
    inlines = [CapexBudgetLineInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'location', 'status', 'notes')
        }),
        ('Budget', {
            'fields': ('total_budget', 'currency', 'actual_spend_display', 'variance_display', 'utilization_pct_display')
        }),
        ('Timeline', {
            'fields': ('start_date', 'expected_completion_date')
        }),
        ('Audit Trail', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )

    def actual_spend_display(self, obj):
        return f"{obj.actual_spend:,.2f}"
    actual_spend_display.short_description = 'Actual Spend'

    def variance_display(self, obj):
        return f"{obj.variance:,.2f}"
    variance_display.short_description = 'Variance'

    def utilization_pct_display(self, obj):
        return f"{obj.utilization_pct}%"
    utilization_pct_display.short_description = 'Utilization %'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('location', 'currency')


# ---------------------------------------------------------------------------
# Fixed Asset admin
# ---------------------------------------------------------------------------

class DepreciationEntryInline(admin.TabularInline):
    model = DepreciationEntry
    extra = 0
    fields = ['period_date', 'depreciation_amount', 'book_value', 'notes']
    ordering = ['period_date']


@admin.register(FixedAsset)
class FixedAssetAdmin(admin.ModelAdmin):
    list_display = [
        'asset_code', 'name', 'category', 'location', 'status',
        'acquisition_date', 'acquisition_cost', 'currency',
        'net_book_value_display', 'accumulated_depreciation_display',
    ]
    list_filter = ['status', 'location', 'category', 'depreciation_method']
    search_fields = ['asset_code', 'name', 'serial_number']
    readonly_fields = [
        'asset_code',
        'net_book_value_display', 'accumulated_depreciation_display', 'monthly_depreciation_display',
        'created_at', 'updated_at', 'created_by', 'updated_by',
    ]
    inlines = [DepreciationEntryInline]

    fieldsets = (
        ('Asset Details', {
            'fields': ('asset_code', 'name', 'category', 'location', 'serial_number', 'status')
        }),
        ('Acquisition', {
            'fields': ('acquisition_date', 'acquisition_cost', 'currency', 'acquisition_expense', 'acquisition_invoice')
        }),
        ('Depreciation', {
            'fields': (
                'depreciation_method', 'useful_life_months', 'residual_value',
                'monthly_depreciation_display', 'accumulated_depreciation_display', 'net_book_value_display',
            )
        }),
        ('Disposal', {
            'fields': ('disposal_date', 'disposal_amount'),
            'classes': ('collapse',),
            'description': 'Complete only when status is Disposed or Written Off',
        }),
        ('Notes', {'fields': ('notes',)}),
        ('Audit Trail', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )

    def net_book_value_display(self, obj):
        if obj.pk:
            return f"{obj.net_book_value:,.2f}"
        return '-'
    net_book_value_display.short_description = 'Net Book Value'

    def accumulated_depreciation_display(self, obj):
        if obj.pk:
            return f"{obj.accumulated_depreciation:,.2f}"
        return '-'
    accumulated_depreciation_display.short_description = 'Accum. Depreciation'

    def monthly_depreciation_display(self, obj):
        return f"{obj.monthly_depreciation:,.2f}"
    monthly_depreciation_display.short_description = 'Monthly Depreciation'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category', 'location', 'currency')


@admin.register(DepreciationEntry)
class DepreciationEntryAdmin(admin.ModelAdmin):
    list_display = ['asset', 'period_date', 'depreciation_amount', 'book_value']
    list_filter = ['period_date', 'asset__location']
    search_fields = ['asset__asset_code', 'asset__name']
    ordering = ['asset', 'period_date']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('asset')
