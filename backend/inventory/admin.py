from django.contrib import admin
from django.utils.html import format_html
from django import forms
from django.core.exceptions import ValidationError
from .models import InventoryAlert, StockMovement, InventoryAdjustment


@admin.register(InventoryAlert)
class InventoryAlertAdmin(admin.ModelAdmin):
    list_display = [
        'strain', 
        'location', 
        'reorder_point', 
        'current_stock_display', 
        'is_low_stock_display', 
        'is_active'
    ]
    list_filter = ['location', 'is_active']
    search_fields = ['strain__name']
    
    def current_stock_display(self, obj):
        """Display current stock count"""
        return obj.current_stock
    current_stock_display.short_description = 'Current Stock'
    current_stock_display.admin_order_field = 'strain'  # Note: Can't order by property
    
    def is_low_stock_display(self, obj):
        """Display low stock status with color coding"""
        is_low = obj.is_low_stock
        if is_low:
            return format_html(
                '<span style="color: red; font-weight: bold;">LOW STOCK</span>'
            )
        return format_html('<span style="color: green;">OK</span>')
    is_low_stock_display.short_description = 'Stock Status'
    is_low_stock_display.admin_order_field = 'reorder_point'


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = [
        'movement_date', 
        'movement_type', 
        'clone_code_display', 
        'strain_display', 
        'from_location', 
        'to_location', 
        'reference_type'
    ]
    list_filter = ['movement_type', 'movement_date', 'clone__location']
    search_fields = ['clone__code', 'reference_id']
    readonly_fields = [
        'clone',
        'movement_type',
        'from_location',
        'to_location',
        'movement_date',
        'reference_type',
        'reference_id',
        'notes',
        'performed_by',
        'created_at',
        'updated_at',
        'created_by',
        'updated_by'
    ]
    ordering = ['-movement_date']
    
    def has_add_permission(self, request):
        """Disable adding new stock movements (auto-created by signals)"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Disable editing stock movements (read-only audit log)"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Disable deleting stock movements (audit trail must be preserved)"""
        return False
    
    def clone_code_display(self, obj):
        return obj.clone_code
    clone_code_display.short_description = 'Clone Code'
    clone_code_display.admin_order_field = 'clone__code'
    
    def strain_display(self, obj):
        return obj.strain_name
    strain_display.short_description = 'Strain'
    strain_display.admin_order_field = 'clone__strain__name'
    
    def get_queryset(self, request):
        """Optimize queries with select_related"""
        qs = super().get_queryset(request)
        return qs.select_related('clone', 'clone__strain', 'from_location', 'to_location', 'performed_by')


class InventoryAdjustmentForm(forms.ModelForm):
    """Custom form with validation for InventoryAdjustment"""
    
    class Meta:
        model = InventoryAdjustment
        fields = '__all__'
    
    def clean(self):
        cleaned_data = super().clean()
        clone = cleaned_data.get('clone')
        approved_by = cleaned_data.get('approved_by')
        notes = cleaned_data.get('notes')
        
        # Validate clone status
        if clone:
            if clone.status not in ['rooted', 'reserved']:
                self.add_error(
                    'clone',
                    ValidationError(
                        f"Clone must be in 'rooted' or 'reserved' status. "
                        f"Current status: {clone.get_status_display()}"
                    )
                )
        
        # Validate manager approval
        if approved_by:
            if approved_by.role not in ['admin', 'cultivation_manager']:
                self.add_error(
                    'approved_by',
                    ValidationError(
                        f"Approval must be from a manager. "
                        f"User '{approved_by.get_full_name() or approved_by.username}' has role '{approved_by.get_role_display()}'"
                    )
                )
        
        # Validate notes
        if not notes or len(notes.strip()) < 10:
            self.add_error(
                'notes',
                ValidationError(
                    "Detailed notes are required explaining the reason for adjustment "
                    "(minimum 10 characters)"
                )
            )
        
        return cleaned_data


@admin.register(InventoryAdjustment)
class InventoryAdjustmentAdmin(admin.ModelAdmin):
    form = InventoryAdjustmentForm
    list_display = [
        'adjustment_date', 
        'clone_code_display', 
        'strain_display', 
        'reason', 
        'approved_by'
    ]
    list_filter = ['reason', 'adjustment_date', 'clone__location']
    search_fields = ['clone__code', 'notes']
    readonly_fields = [
        'created_at',
        'updated_at',
        'created_by',
        'updated_by'
    ]
    
    fieldsets = (
        ('Adjustment Details', {
            'fields': ('clone', 'adjustment_date', 'reason', 'notes', 'photo_url')
        }),
        ('Approval', {
            'fields': ('approved_by',)
        }),
        ('Audit Trail', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )
    
    def clone_code_display(self, obj):
        return obj.clone_code
    clone_code_display.short_description = 'Clone Code'
    clone_code_display.admin_order_field = 'clone__code'
    
    def strain_display(self, obj):
        return obj.strain_name
    strain_display.short_description = 'Strain'
    strain_display.admin_order_field = 'clone__strain__name'
    
    def get_queryset(self, request):
        """Optimize queries with select_related"""
        qs = super().get_queryset(request)
        return qs.select_related('clone', 'clone__strain', 'clone__location', 'approved_by')
    
    def save_model(self, request, obj, form, change):
        """Set created_by/updated_by on save"""
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
