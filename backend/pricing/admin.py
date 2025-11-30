from django.contrib import admin
from django.utils.html import format_html
from .models import CostAllocationRule, PricingTier, CostSnapshot


@admin.register(CostAllocationRule)
class CostAllocationRuleAdmin(admin.ModelAdmin):
    list_display = [
        'location',
        'effective_date',
        'end_date',
        'monthly_capacity_clones',
        'is_active'
    ]
    list_filter = ['location', 'is_active', 'effective_date']
    search_fields = ['location__code', 'location__name', 'notes']
    readonly_fields = [
        'created_at',
        'updated_at',
        'created_by',
        'updated_by'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('location', 'effective_date', 'end_date', 'is_active')
        }),
        ('Production Capacity', {
            'fields': (
                'monthly_capacity_clones',
            ),
            'description': 'Production capacity used for overhead allocation'
        }),
        ('Mother Plant Assumptions', {
            'fields': (
                'mother_plant_lifecycle_days',
                'expected_clones_per_mother_lifecycle'
            ),
            'description': 'Assumptions for allocating mother plant costs'
        }),
        ('Department Allocation Rules', {
            'fields': (
                'direct_labor_departments',
                'overhead_labor_departments'
            ),
            'description': 'Which HR departments are direct labor vs overhead. Use department codes like ["CULT", "PROD"]'
        }),
        ('Expense Category Allocation Rules', {
            'fields': (
                'cogs_expense_categories',
                'variable_expense_categories',
                'fixed_expense_categories'
            ),
            'description': 'Which expense categories from Purchasing are COGS vs OPEX. Use category codes like ["MAT", "NUTR"]'
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Audit Trail', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PricingTier)
class PricingTierAdmin(admin.ModelAdmin):
    list_display = [
        'tier_name',
        'quantity_range_display',
        'price_per_clone',
        'effective_date',
        'end_date',
        'annual_price_increase_pct',
        'is_active'
    ]
    list_filter = ['tier_name', 'is_active', 'effective_date']
    search_fields = ['tier_name']
    readonly_fields = [
        'created_at',
        'updated_at',
        'created_by',
        'updated_by'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('tier_name', 'is_active')
        }),
        ('Quantity Range', {
            'fields': ('min_quantity', 'max_quantity'),
            'description': 'Quantity range for this pricing tier'
        }),
        ('Pricing', {
            'fields': (
                'price_per_clone',
                'annual_price_increase_pct'
            )
        }),
        ('Effective Dates', {
            'fields': ('effective_date', 'end_date')
        }),
        ('Audit Trail', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )
    
    def quantity_range_display(self, obj):
        """Display quantity range"""
        max_qty = f"-{obj.max_quantity}" if obj.max_quantity else "+"
        return f"{obj.min_quantity}{max_qty}"
    quantity_range_display.short_description = 'Quantity Range'
    quantity_range_display.admin_order_field = 'min_quantity'


@admin.register(CostSnapshot)
class CostSnapshotAdmin(admin.ModelAdmin):
    list_display = [
        'location',
        'snapshot_date',
        'period_range_display',
        'total_clones_produced',
        'capacity_utilization_display',
        'total_cost_per_clone_display'
    ]
    list_filter = ['location', 'snapshot_date']
    search_fields = ['location__code', 'location__name', 'notes']
    readonly_fields = [
        'created_at',
        'updated_at',
        'created_by',
        'updated_by'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('location', 'snapshot_date', 'period_start', 'period_end')
        }),
        ('Production Metrics', {
            'fields': (
                'total_clones_produced',
                'capacity_utilization_pct'
            )
        }),
        ('Actual Expenses (from Purchasing)', {
            'fields': (
                'total_cogs_expenses',
                'total_variable_opex',
                'total_fixed_opex'
            ),
            'description': 'Actual expenses pulled from Purchasing.Expense'
        }),
        ('Actual Labor Costs (from HR)', {
            'fields': (
                'total_direct_labor',
                'total_overhead_labor'
            ),
            'description': 'Actual labor costs pulled from HR.Payroll'
        }),
        ('Calculated Per-Clone Costs', {
            'fields': (
                'cogs_per_clone',
                'direct_labor_per_clone',
                'variable_base_per_clone',
                'overhead_per_clone',
                'total_cost_per_clone'
            ),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Audit Trail', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )
    
    def period_range_display(self, obj):
        """Display period range"""
        return f"{obj.period_start} to {obj.period_end}"
    period_range_display.short_description = 'Period'
    
    def capacity_utilization_display(self, obj):
        """Display capacity utilization"""
        return f"{obj.capacity_utilization_pct:.1f}%"
    capacity_utilization_display.short_description = 'Capacity Utilization'
    capacity_utilization_display.admin_order_field = 'capacity_utilization_pct'
    
    def total_cost_per_clone_display(self, obj):
        """Display total cost per clone"""
        return format_html('<strong>{:.2f}</strong>', obj.total_cost_per_clone)
    total_cost_per_clone_display.short_description = 'Cost/Clone'
    total_cost_per_clone_display.admin_order_field = 'total_cost_per_clone'
    
    def get_queryset(self, request):
        """Optimize queries with select_related"""
        qs = super().get_queryset(request)
        return qs.select_related('location')
