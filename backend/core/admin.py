from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Location, Currency, CompanySettings

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
