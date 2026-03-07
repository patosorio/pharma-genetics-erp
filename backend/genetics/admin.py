from django.contrib import admin
from .models import StrainCategory, Strain

@admin.register(StrainCategory)
class StrainCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']

@admin.register(Strain)
class StrainAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'slug',
        'catalogue_year',
        'category',
        'thc_percentage',
        'cbd_percentage',
        'terpene_profile',
        'breeder',
        'lineage',
        'image',
        'is_active'
    ]
    list_filter = [
        'category',
        'catalogue_year',
        'is_active'
    ]
    search_fields = [
        'name',
        'category__name',
        'breeder',
        'lineage',
        'terpene_profile',
    ]
    readonly_fields = [
        'created_at',
        'updated_at',
        'created_by',
        'updated_by'
    ]

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'catalogue_year', 'category', 'description', 'breeder', 'lineage', 'image', 'is_active')
        }),
        ('Genetic Profile', {
            'fields': ('thc_percentage', 'cbd_percentage', 'terpene_profile')
        }),
        ('Audit Information', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by')
        }),
    )
