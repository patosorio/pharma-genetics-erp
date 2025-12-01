from django.contrib import admin
from .models import (
    Supplier, ExpenseCategory, PurchaseOrder, PurchaseOrderItem,
    Expense, PurchaseInvoice
)


class PurchaseOrderItemInline(admin.TabularInline):
    """Inline for purchase order items"""
    model = PurchaseOrderItem
    extra = 1
    fields = ['expense_category', 'description', 'quantity', 'unit_price', 'line_total']
    readonly_fields = ['line_total']


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = [
        'supplier_code',
        'contact_name',
        'payment_terms_days',
        'is_active'
    ]
    list_filter = ['contact__is_active']
    search_fields = ['supplier_code', 'contact__name', 'contact__email']
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('supplier_code', 'contact')
        }),
        ('Payment Terms', {
            'fields': ('payment_terms_days',)
        }),
        ('Audit Trail', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
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
        qs = super().get_queryset(request)
        return qs.select_related('contact')


@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = [
        'code',
        'name',
        'category_type',
        'is_active'
    ]
    list_filter = ['category_type', 'is_active']
    search_fields = ['code', 'name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('code', 'name', 'category_type', 'is_active')
        }),
        ('Description', {
            'fields': ('description',)
        }),
    )


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = [
        'po_number',
        'supplier_name',
        'location',
        'order_date',
        'expected_delivery_date',
        'status',
        'total_amount',
        'currency'
    ]
    list_filter = ['status', 'location', 'order_date']
    search_fields = [
        'po_number',
        'supplier__supplier_code',
        'supplier__contact__name'
    ]
    readonly_fields = [
        'created_at',
        'updated_at',
        'created_by',
        'updated_by'
    ]
    inlines = [PurchaseOrderItemInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('po_number', 'supplier', 'location', 'status')
        }),
        ('Dates', {
            'fields': ('order_date', 'expected_delivery_date')
        }),
        ('Tax & Amounts', {
            'fields': ('tax_type', 'base_amount', 'tax_amount', 'total_amount', 'currency')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Audit Trail', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_sent', 'mark_as_confirmed', 'mark_as_delivered']
    
    def supplier_name(self, obj):
        return obj.supplier.contact.name
    supplier_name.short_description = 'Supplier'
    supplier_name.admin_order_field = 'supplier__contact__name'
    
    def mark_as_sent(self, request, queryset):
        updated = queryset.filter(status='draft').update(status='sent')
        self.message_user(
            request,
            f"Successfully marked {updated} purchase order(s) as sent."
        )
    mark_as_sent.short_description = "Mark selected POs as sent"
    
    def mark_as_confirmed(self, request, queryset):
        updated = queryset.filter(status='sent').update(status='confirmed')
        self.message_user(
            request,
            f"Successfully confirmed {updated} purchase order(s)."
        )
    mark_as_confirmed.short_description = "Mark selected POs as confirmed"
    
    def mark_as_delivered(self, request, queryset):
        updated = queryset.filter(status='confirmed').update(status='delivered')
        self.message_user(
            request,
            f"Successfully marked {updated} purchase order(s) as delivered."
        )
    mark_as_delivered.short_description = "Mark selected POs as delivered"
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('supplier__contact', 'location', 'currency')


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = [
        'expense_number',
        'category',
        'supplier_name',
        'location',
        'expense_date',
        'amount',
        'currency'
    ]
    list_filter = ['category', 'location', 'expense_date']
    search_fields = [
        'expense_number',
        'description',
        'supplier__supplier_code',
        'supplier__contact__name'
    ]
    readonly_fields = [
        'created_at',
        'updated_at',
        'created_by',
        'updated_by'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('expense_number', 'category', 'supplier', 'location')
        }),
        ('Date and Amount', {
            'fields': ('expense_date', 'amount', 'currency')
        }),
        ('Details', {
            'fields': ('description', 'purchase_order')
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
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related(
            'category',
            'supplier__contact',
            'location',
            'currency',
            'purchase_order'
        )


@admin.register(PurchaseInvoice)
class PurchaseInvoiceAdmin(admin.ModelAdmin):
    list_display = [
        'invoice_number',
        'supplier_name',
        'invoice_date',
        'due_date',
        'total_amount',
        'paid_amount',
        'balance_due',
        'currency',
        'status'
    ]
    list_filter = ['status', 'invoice_date', 'due_date']
    search_fields = [
        'invoice_number',
        'supplier__supplier_code',
        'supplier__contact__name',
        'purchase_order__po_number'
    ]
    readonly_fields = [
        'balance_due',
        'created_at',
        'updated_at',
        'created_by',
        'updated_by'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('invoice_number', 'supplier', 'purchase_order', 'status')
        }),
        ('Dates', {
            'fields': ('invoice_date', 'due_date')
        }),
        ('Tax & Amounts', {
            'fields': (
                'tax_type',
                'base_amount',
                'tax_amount',
                'total_amount',
                'paid_amount',
                'balance_due',
                'currency'
            )
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Audit Trail', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_approved', 'mark_as_paid']
    
    def supplier_name(self, obj):
        return obj.supplier.contact.name
    supplier_name.short_description = 'Supplier'
    supplier_name.admin_order_field = 'supplier__contact__name'
    
    def mark_as_approved(self, request, queryset):
        updated = queryset.filter(status='pending').update(status='approved')
        self.message_user(
            request,
            f"Successfully approved {updated} invoice(s)."
        )
    mark_as_approved.short_description = "Mark selected invoices as approved"
    
    def mark_as_paid(self, request, queryset):
        for invoice in queryset.filter(status__in=['approved', 'partially_paid']):
            if invoice.balance_due == 0:
                invoice.status = 'paid'
                invoice.save()
        self.message_user(
            request,
            "Updated invoice statuses based on payments."
        )
    mark_as_paid.short_description = "Update status to paid (if balance is zero)"
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related(
            'supplier__contact',
            'purchase_order',
            'currency'
        )
