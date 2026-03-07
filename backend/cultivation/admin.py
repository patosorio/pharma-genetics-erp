# apps/cultivation/admin.py
from django.contrib import admin
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget
from .models import MotherPlant, ProductionBatch, Clone
from core.models import Location
from genetics.models import Strain


class MotherPlantResource(resources.ModelResource):
    strain = fields.Field(
        column_name='strain',
        attribute='strain',
        widget=ForeignKeyWidget(Strain, field='name'),
    )
    location = fields.Field(
        column_name='location',
        attribute='location',
        widget=ForeignKeyWidget(Location, field='code'),
    )

    class Meta:
        model = MotherPlant
        fields = (
            'id', 'code', 'strain', 'location', 'status', 'health_grade',
            'cultivation_date', 'expected_ready_date', 'actual_ready_date',
            'expected_retirement_date', 'actual_retirement_date',
            'clones_per_cycle_min', 'clones_per_cycle_avg', 'clones_per_cycle_max',
            'total_cycles_year', 'min_possible_clones_year', 'avg_clones_year',
            'max_possible_clones_year', 'notes',
        )
        export_order = fields
        import_id_fields = ['code']


def _make_status_action(status_value, status_label):
    """Factory that creates a bulk status-change admin action."""
    def action_fn(modeladmin, request, queryset):
        updated = queryset.update(status=status_value)
        modeladmin.message_user(request, f"Set {updated} plant(s) to '{status_label}'.")
    action_fn.__name__ = f'set_status_{status_value.lower()}'
    action_fn.short_description = f'Set status → {status_label}'
    return action_fn


@admin.register(MotherPlant)
class MotherPlantAdmin(ImportExportModelAdmin):
    resource_classes = [MotherPlantResource]
    list_display = ['code', 'strain', 'location', 'status', 'cultivation_date', 'health_grade', 'total_cuttings_taken']
    list_filter = ['health_grade', 'location', 'status']
    search_fields = ['code', 'strain__name']
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'updated_by', 'last_cut_date', 'total_cuttings_taken']
    actions = [
        'set_status_growing',
        'set_status_active_production',
        'set_status_recovery',
        'set_status_low_production',
        'set_status_quarantine',
        'set_status_retired',
        'set_status_under_treatment',
    ]

    fieldsets = (
        ('Basic Information', {
            'fields': ('code', 'strain', 'location')
        }),
        ('Lifecycle', {
            'fields': ('cultivation_date', 'expected_retirement_date', 'health_grade', 'status')
        }),
        ('Production Capacity', {
            'fields': (
                'clones_per_cycle_min', 'clones_per_cycle_avg', 'clones_per_cycle_max',
                'total_cycles_year',
                'min_possible_clones_year', 'avg_clones_year', 'max_possible_clones_year',
            )
        }),
        ('Production Stats', {
            'fields': ('total_cuttings_taken', 'last_cut_date')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Audit Trail', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )

    set_status_growing = _make_status_action('Growing', 'Growing')
    set_status_active_production = _make_status_action('Active_Production', 'Active Production')
    set_status_recovery = _make_status_action('Recovery', 'Recovery')
    set_status_low_production = _make_status_action('Low_Production', 'Low Production')
    set_status_quarantine = _make_status_action('Quarantine', 'Quarantine')
    set_status_retired = _make_status_action('Retired', 'Retired')
    set_status_under_treatment = _make_status_action('Under_Treatment', 'Under Treatment')

@admin.register(ProductionBatch)
class ProductionBatchAdmin(admin.ModelAdmin):
    list_display = [
        'batch_number', 
        'mother_plant', 
        'cutting_date', 
        'status', 
        'initial_clone_count', 
        'rooted_clone_count_display', 
        'survival_rate_display',
        'cost_per_clone'
    ]
    list_filter = ['status', 'location', 'cutting_date']
    search_fields = ['batch_number', 'mother_plant__code']
    readonly_fields = [
        'cost_per_clone',
        'rooted_clone_count_display',
        'survival_rate_display',
        'created_at', 
        'updated_at', 
        'created_by', 
        'updated_by'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('batch_number', 'mother_plant', 'location', 'status')
        }),
        ('Production Timeline', {
            'fields': ('cutting_date', 'expected_rooting_date')
        }),
        ('Production Metrics', {
            'fields': (
                'initial_clone_count', 
                'rooted_clone_count_display', 
                'survival_rate_display'
            )
        }),
        ('Costing', {
            'fields': ('total_batch_cost', 'cost_per_clone'),
            'description': 'Enter total_batch_cost manually. cost_per_clone is auto-calculated when batch is completed.'
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Audit Trail', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['complete_selected_batches']
    
    def rooted_clone_count_display(self, obj):
        return obj.rooted_clone_count
    rooted_clone_count_display.short_description = 'Rooted Count'
    
    def survival_rate_display(self, obj):
        return f"{obj.survival_rate:.1f}%"
    survival_rate_display.short_description = 'Survival Rate'
    
    def complete_selected_batches(self, request, queryset):
        """Complete batches and calculate costs"""
        completed_count = 0
        error_count = 0
        
        for batch in queryset.filter(status__in=['rooting', 'cutting']):
            try:
                if batch.total_batch_cost == 0:
                    self.message_user(
                        request,
                        f"Warning: {batch.batch_number} has zero cost. Please set total_batch_cost first.",
                        level='WARNING'
                    )
                    continue
                
                batch.complete_batch()
                completed_count += 1
                
                self.message_user(
                    request,
                    f"✓ Batch {batch.batch_number} completed. "
                    f"Rooted: {batch.rooted_clone_count}, "
                    f"Cost per clone: {batch.cost_per_clone:.2f} THB"
                )
            except Exception as e:
                error_count += 1
                self.message_user(
                    request,
                    f"✗ Error completing {batch.batch_number}: {str(e)}",
                    level='ERROR'
                )
        
        if completed_count > 0:
            self.message_user(
                request,
                f"Successfully completed {completed_count} batch(es)."
            )
        if error_count > 0:
            self.message_user(
                request,
                f"Failed to complete {error_count} batch(es).",
                level='ERROR'
            )
    
    complete_selected_batches.short_description = "Complete selected batches and calculate costs"

@admin.register(Clone)
class CloneAdmin(admin.ModelAdmin):
    list_display = [
        'code',
        'strain_display',
        'location_display',
        'status',
        'rooting_date',
        'age_display',
        'unit_cost',
        'batch_display'
    ]
    list_filter = [
        'status',
        'strain',  # ← Can filter directly because denormalized
        'location',  # ← Can filter directly
        'rooting_date'
    ]
    search_fields = [
        'code',
        'strain__name',  # ← Search by strain name
        'production_batch__batch_number'
    ]
    readonly_fields = [
        'strain',  # Auto-populated
        'location',  # Auto-populated
        'code',  # Auto-generated
        'created_at',
        'updated_at'
    ]
    
    def strain_display(self, obj):
        return obj.strain.name
    strain_display.short_description = 'Strain'
    strain_display.admin_order_field = 'strain__name'
    
    def location_display(self, obj):
        return obj.location.code
    location_display.short_description = 'Location'
    location_display.admin_order_field = 'location__code'
    
    def batch_display(self, obj):
        return obj.production_batch.batch_number
    batch_display.short_description = 'Batch'
    
    def age_display(self, obj):
        if obj.status == 'rooted' and obj.rooting_date:
            return f"{obj.age_in_days} days"
        return '-'
    age_display.short_description = 'Age'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related(
            'strain',
            'location',
            'production_batch'
        )