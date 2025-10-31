# apps/cultivation/admin.py
from django.contrib import admin
from .models import MotherPlant, ProductionBatch, Clone

@admin.register(MotherPlant)
class MotherPlantAdmin(admin.ModelAdmin):
    list_display = ['code', 'strain', 'location', 'status', 'cultivation_date', 'health_grade', 'total_cuttings_taken']
    list_filter = ['health_grade', 'location', 'status']
    search_fields = ['code', 'strain__name']
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('code', 'strain', 'location')
        }),
        ('Lifecycle', {
            'fields': ('cultivation_date', 'expected_end_date', 'health_status', 'is_active')
        }),
        ('Production Stats', {
            'fields': ('total_cuttings_taken',)
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )

@admin.register(ProductionBatch)
class ProductionBatchAdmin(admin.ModelAdmin):
    list_display = ['batch_number', 'mother_plant', 'cutting_date', 'status', 'initial_clone_count', 'rooted_clone_count', 'survival_rate']
    list_filter = ['status', 'location', 'cutting_date']
    search_fields = ['batch_number', 'mother_plant__code']
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']
    
    def survival_rate(self, obj):
        return f"{obj.survival_rate:.1f}%"
    survival_rate.short_description = 'Survival Rate'

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
    
    # Optimize queries
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related(
            'strain',
            'location',
            'production_batch'
        )