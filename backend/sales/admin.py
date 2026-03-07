from django.contrib import admin
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget
from .models import (
    Customer, PriceList, Order, OrderLine,
    DeliveryNote, DeliveryNoteLine, SalesInvoice, Payment
)
from core.models import Location, Currency, TaxType


class OrderResource(resources.ModelResource):
    customer = fields.Field(
        column_name='customer',
        attribute='customer',
        widget=ForeignKeyWidget(Customer, field='customer_code'),
    )
    location = fields.Field(
        column_name='location',
        attribute='location',
        widget=ForeignKeyWidget(Location, field='code'),
    )

    class Meta:
        model = Order
        fields = (
            'id', 'order_number', 'customer', 'location', 'order_date',
            'expected_delivery_date', 'status', 'total_amount', 'notes',
        )
        export_order = fields
        import_id_fields = ['order_number']


class DeliveryNoteResource(resources.ModelResource):
    order = fields.Field(
        column_name='order',
        attribute='order',
        widget=ForeignKeyWidget(Order, field='order_number'),
    )
    delivery_location = fields.Field(
        column_name='delivery_location',
        attribute='delivery_location',
        widget=ForeignKeyWidget(Location, field='code'),
    )

    class Meta:
        model = DeliveryNote
        fields = (
            'id', 'delivery_note_number', 'order', 'delivery_date',
            'delivered_by', 'received_by', 'delivery_location', 'status', 'notes',
        )
        export_order = fields
        import_id_fields = ['delivery_note_number']


class SalesInvoiceResource(resources.ModelResource):
    order = fields.Field(
        column_name='order',
        attribute='order',
        widget=ForeignKeyWidget(Order, field='order_number'),
    )
    tax_type = fields.Field(
        column_name='tax_type',
        attribute='tax_type',
        widget=ForeignKeyWidget(TaxType, field='name'),
    )

    class Meta:
        model = SalesInvoice
        fields = (
            'id', 'invoice_number', 'order', 'invoice_date', 'due_date',
            'tax_type', 'base_amount', 'tax_amount', 'total_amount',
            'paid_amount', 'status',
        )
        export_order = fields
        import_id_fields = ['invoice_number']


class OrderLineInline(admin.TabularInline):
    """Inline for order lines"""
    model = OrderLine
    extra = 1
    fields = ['strain', 'quantity', 'unit_price', 'line_total']
    readonly_fields = ['line_total']


class DeliveryNoteLineInline(admin.TabularInline):
    """Inline for delivery note lines"""
    model = DeliveryNoteLine
    extra = 0
    fields = ['order_line', 'quantity_delivered', 'notes']


class PaymentInline(admin.TabularInline):
    """Inline for payments"""
    model = Payment
    extra = 0
    fields = ['payment_number', 'payment_date', 'amount', 'payment_method', 'reference_number']
    readonly_fields = ['payment_number']


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = [
        'customer_code',
        'contact_name',
        'tier',
        'credit_limit',
        'payment_terms_days',
        'is_active'
    ]
    list_filter = ['tier', 'contact__is_active']
    search_fields = ['customer_code', 'contact__name', 'contact__email']
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('customer_code', 'contact', 'tier')
        }),
        ('Payment Terms', {
            'fields': ('credit_limit', 'payment_terms_days')
        }),
        ('Audit Trail', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )
    
    def contact_name(self, obj):
        return obj.contact.name
    contact_name.short_description = 'Contact Name'
    contact_name.admin_order_field = 'contact__name'
    
    def is_active(self, obj):
        return obj.contact.is_active
    is_active.short_description = 'Active'
    is_active.boolean = True
    is_active.admin_order_field = 'contact__is_active'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('contact')


@admin.register(PriceList)
class PriceListAdmin(admin.ModelAdmin):
    list_display = [
        'strain',
        'tier',
        'price_per_clone',
        'currency',
        'min_quantity',
        'is_active'
    ]
    list_filter = ['tier', 'is_active', 'currency']
    search_fields = ['strain__name']
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('strain', 'tier', 'is_active')
        }),
        ('Pricing', {
            'fields': ('price_per_clone', 'currency', 'min_quantity')
        }),
        ('Audit Trail', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('strain', 'currency')


@admin.register(Order)
class OrderAdmin(ImportExportModelAdmin):
    resource_classes = [OrderResource]
    list_display = [
        'order_number',
        'customer_name',
        'location',
        'order_date',
        'expected_delivery_date',
        'status',
        'total_amount'
    ]
    list_filter = ['status', 'location', 'order_date']
    search_fields = [
        'order_number',
        'customer__customer_code',
        'customer__contact__name'
    ]
    readonly_fields = [
        'created_at',
        'updated_at',
        'created_by',
        'updated_by'
    ]
    inlines = [OrderLineInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('order_number', 'customer', 'location', 'status')
        }),
        ('Dates', {
            'fields': ('order_date', 'expected_delivery_date')
        }),
        ('Totals', {
            'fields': ('total_amount',)
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Audit Trail', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_confirmed', 'mark_as_ready']
    
    def customer_name(self, obj):
        return obj.customer.contact.name
    customer_name.short_description = 'Customer'
    customer_name.admin_order_field = 'customer__contact__name'
    
    def mark_as_confirmed(self, request, queryset):
        updated = queryset.filter(status='draft').update(status='confirmed')
        self.message_user(
            request,
            f"Successfully confirmed {updated} order(s)."
        )
    mark_as_confirmed.short_description = "Mark selected orders as confirmed"
    
    def mark_as_ready(self, request, queryset):
        updated = queryset.filter(status='in_production').update(status='ready')
        self.message_user(
            request,
            f"Successfully marked {updated} order(s) as ready."
        )
    mark_as_ready.short_description = "Mark selected orders as ready for delivery"
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('customer__contact', 'location')


@admin.register(DeliveryNote)
class DeliveryNoteAdmin(ImportExportModelAdmin):
    resource_classes = [DeliveryNoteResource]
    list_display = [
        'delivery_note_number',
        'order_number',
        'customer_name',
        'delivery_date',
        'delivery_location',
        'status'
    ]
    list_filter = ['status', 'delivery_location', 'delivery_date']
    search_fields = [
        'delivery_note_number',
        'order__order_number',
        'order__customer__contact__name'
    ]
    readonly_fields = [
        'created_at',
        'updated_at',
        'created_by',
        'updated_by'
    ]
    inlines = [DeliveryNoteLineInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('delivery_note_number', 'order', 'status')
        }),
        ('Delivery Details', {
            'fields': (
                'delivery_date',
                'delivery_location',
                'delivered_by',
                'received_by'
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
    
    actions = ['mark_as_delivered']
    
    def order_number(self, obj):
        return obj.order.order_number
    order_number.short_description = 'Order'
    order_number.admin_order_field = 'order__order_number'
    
    def customer_name(self, obj):
        return obj.order.customer.contact.name
    customer_name.short_description = 'Customer'
    customer_name.admin_order_field = 'order__customer__contact__name'
    
    def mark_as_delivered(self, request, queryset):
        updated = queryset.filter(status='in_transit').update(status='delivered')
        self.message_user(
            request,
            f"Successfully marked {updated} delivery note(s) as delivered."
        )
    mark_as_delivered.short_description = "Mark selected delivery notes as delivered"
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('order__customer__contact', 'delivery_location')


@admin.register(SalesInvoice)
class SalesInvoiceAdmin(ImportExportModelAdmin):
    resource_classes = [SalesInvoiceResource]
    list_display = [
        'invoice_number',
        'customer_name',
        'invoice_date',
        'due_date',
        'total_amount',
        'paid_amount',
        'balance_due',
        'status'
    ]
    list_filter = ['status', 'invoice_date', 'due_date']
    search_fields = [
        'invoice_number',
        'order__order_number',
        'order__customer__contact__name'
    ]
    readonly_fields = [
        'balance_due',
        'created_at',
        'updated_at',
        'created_by',
        'updated_by'
    ]
    inlines = [PaymentInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('invoice_number', 'order', 'delivery_note', 'status')
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
                'balance_due'
            )
        }),
        ('Audit Trail', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_sent', 'mark_as_paid']
    
    def customer_name(self, obj):
        return obj.order.customer.contact.name
    customer_name.short_description = 'Customer'
    customer_name.admin_order_field = 'order__customer__contact__name'
    
    def mark_as_sent(self, request, queryset):
        updated = queryset.filter(status='draft').update(status='sent')
        self.message_user(
            request,
            f"Successfully marked {updated} invoice(s) as sent."
        )
    mark_as_sent.short_description = "Mark selected invoices as sent"
    
    def mark_as_paid(self, request, queryset):
        for invoice in queryset.filter(status__in=['sent', 'partially_paid']):
            if invoice.balance_due == 0:
                invoice.status = 'paid'
                invoice.save()
        self.message_user(
            request,
            f"Updated invoice statuses based on payments."
        )
    mark_as_paid.short_description = "Update status to paid (if balance is zero)"
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('order__customer__contact', 'delivery_note')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'payment_number',
        'invoice_number',
        'customer_name',
        'payment_date',
        'amount',
        'payment_method',
        'reference_number'
    ]
    list_filter = ['payment_method', 'payment_date']
    search_fields = [
        'payment_number',
        'invoice__invoice_number',
        'invoice__order__customer__contact__name',
        'reference_number'
    ]
    readonly_fields = [
        'created_at',
        'updated_at',
        'created_by',
        'updated_by'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('payment_number', 'invoice', 'payment_date')
        }),
        ('Payment Details', {
            'fields': ('amount', 'payment_method', 'reference_number')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Audit Trail', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )
    
    def invoice_number(self, obj):
        return obj.invoice.invoice_number
    invoice_number.short_description = 'Invoice'
    invoice_number.admin_order_field = 'invoice__invoice_number'
    
    def customer_name(self, obj):
        return obj.invoice.order.customer.contact.name
    customer_name.short_description = 'Customer'
    customer_name.admin_order_field = 'invoice__order__customer__contact__name'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('invoice__order__customer__contact')
