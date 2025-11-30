from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Location, Currency, CompanySettings, Contact, TaxType

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'role', 'location', 'is_active', 'is_staff']
    list_filter = ['role', 'location', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Custom Fields', {
            'fields': ('role', 'location', 'firebase_uid')
        }),
    )

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'address', 'is_active']

@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'symbol', 'is_default']

@admin.register(CompanySettings)
class CompanySettingsAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'default_currency', 'break_even_price']

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['name', 'contact_type', 'email', 'phone', 'is_active']
    list_filter = ['contact_type', 'is_active']
    search_fields = ['name', 'email', 'phone', 'tax_id']
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('contact_type', 'name', 'is_active')
        }),
        ('Contact Details', {
            'fields': ('email', 'phone', 'address')
        }),
        ('Tax Information', {
            'fields': ('tax_id',)
        }),
        ('Audit Trail', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )


@admin.register(TaxType)
class TaxTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'rate', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']
    
    fieldsets = (
        ('Tax Type Information', {
            'fields': ('name', 'rate', 'is_active')
        }),
    )
