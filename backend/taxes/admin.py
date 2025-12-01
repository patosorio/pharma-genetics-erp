from django.contrib import admin
from django.utils.html import format_html
from .models import TaxReport, TaxJournalEntry


class TaxJournalEntryInline(admin.TabularInline):
    model = TaxJournalEntry
    extra = 0
    readonly_fields = ['created_at', 'created_by']
    fields = ['entry_type', 'tax_type', 'sales_invoice', 'purchase_invoice', 
              'base_amount', 'tax_amount', 'entry_date', 'notes']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('tax_type', 'sales_invoice', 'purchase_invoice')


@admin.register(TaxReport)
class TaxReportAdmin(admin.ModelAdmin):
    list_display = ['report_number', 'period_start', 'period_end', 'status', 
                    'display_vat_payable', 'display_vat_recoverable', 
                    'display_net_position', 'currency']
    list_filter = ['status', 'currency', 'period_start']
    search_fields = ['report_number']
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'updated_by',
                       'total_vat_payable', 'total_vat_recoverable', 'net_vat_position']
    date_hierarchy = 'period_end'
    inlines = [TaxJournalEntryInline]
    
    fieldsets = (
        ('Report Information', {
            'fields': ('report_number', 'period_start', 'period_end', 'status', 'currency')
        }),
        ('Tax Summary (Read-Only)', {
            'fields': ('total_vat_payable', 'total_vat_recoverable', 'net_vat_position'),
            'description': 'These fields are automatically calculated. Use "Calculate Totals" action to update.'
        }),
        ('Filing Information', {
            'fields': ('filing_date', 'payment_date', 'notes')
        }),
        ('Audit Trail', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['calculate_totals', 'finalize_reports']
    
    def display_vat_payable(self, obj):
        """Display VAT payable with currency symbol"""
        return format_html(
            '<span style="color: red; font-weight: bold;">{}{:,.2f}</span>',
            obj.currency.symbol,
            obj.total_vat_payable
        )
    display_vat_payable.short_description = 'VAT Payable'
    
    def display_vat_recoverable(self, obj):
        """Display VAT recoverable with currency symbol"""
        return format_html(
            '<span style="color: green; font-weight: bold;">{}{:,.2f}</span>',
            obj.currency.symbol,
            obj.total_vat_recoverable
        )
    display_vat_recoverable.short_description = 'VAT Recoverable'
    
    def display_net_position(self, obj):
        """Display net VAT position with color coding"""
        color = 'red' if obj.net_vat_position > 0 else 'green'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}{:,.2f}</span>',
            color,
            obj.currency.symbol,
            obj.net_vat_position
        )
    display_net_position.short_description = 'Net Position'
    
    def calculate_totals(self, request, queryset):
        """Action to recalculate totals for selected reports"""
        count = 0
        for report in queryset:
            report.calculate_totals()
            count += 1
        
        self.message_user(
            request,
            f'Successfully recalculated totals for {count} tax report(s).'
        )
    calculate_totals.short_description = 'Recalculate totals for selected reports'
    
    def finalize_reports(self, request, queryset):
        """Action to finalize draft reports"""
        count = queryset.filter(status='draft').update(status='finalized')
        self.message_user(
            request,
            f'Successfully finalized {count} tax report(s).'
        )
    finalize_reports.short_description = 'Finalize selected draft reports'


@admin.register(TaxJournalEntry)
class TaxJournalEntryAdmin(admin.ModelAdmin):
    list_display = ['tax_report', 'entry_type', 'entry_date', 'tax_type', 
                    'base_amount', 'tax_amount', 'get_source_document']
    list_filter = ['entry_type', 'tax_type', 'entry_date', 'tax_report__status']
    search_fields = ['tax_report__report_number', 'sales_invoice__invoice_number', 
                     'purchase_invoice__invoice_number']
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']
    date_hierarchy = 'entry_date'
    
    fieldsets = (
        ('Entry Information', {
            'fields': ('tax_report', 'entry_type', 'entry_date', 'tax_type')
        }),
        ('Source Document', {
            'fields': ('sales_invoice', 'purchase_invoice'),
            'description': 'Select ONLY ONE source document (either sales or purchase invoice)'
        }),
        ('Amounts', {
            'fields': ('base_amount', 'tax_amount')
        }),
        ('Additional Information', {
            'fields': ('notes',)
        }),
        ('Audit Trail', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )
    
    def get_source_document(self, obj):
        """Display the source document reference"""
        if obj.sales_invoice:
            return format_html(
                '<a href="/admin/sales/salesinvoice/{}/change/">Sales Invoice: {}</a>',
                obj.sales_invoice.id,
                obj.sales_invoice.invoice_number
            )
        elif obj.purchase_invoice:
            return format_html(
                '<a href="/admin/purchasing/purchaseinvoice/{}/change/">Purchase Invoice: {}</a>',
                obj.purchase_invoice.id,
                obj.purchase_invoice.invoice_number
            )
        return '-'
    get_source_document.short_description = 'Source Document'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related(
            'tax_report',
            'tax_type',
            'sales_invoice',
            'purchase_invoice'
        )
