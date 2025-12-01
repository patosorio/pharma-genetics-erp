from django.contrib import admin
from django.utils.html import format_html
from .models import Department, Employee, PayrollPeriod, Payroll


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = [
        'code',
        'name',
        'employee_count',
        'is_active'
    ]
    list_filter = ['is_active']
    search_fields = ['code', 'name']
    readonly_fields = [
        'created_at',
        'updated_at',
        'created_by',
        'updated_by'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('code', 'name', 'is_active')
        }),
        ('Audit Trail', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )
    
    def employee_count(self, obj):
        """Display number of active employees in this department"""
        return obj.employees.filter(is_active=True).count()
    employee_count.short_description = 'Active Employees'


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = [
        'employee_code',
        'full_name_display',
        'department',
        'location',
        'hire_date',
        'salary',
        'is_active'
    ]
    list_filter = [
        'department',
        'location',
        'is_active',
        'hire_date'
    ]
    search_fields = [
        'employee_code',
        'first_name',
        'last_name',
        'email',
        'phone'
    ]
    readonly_fields = [
        'full_name_display',
        'created_at',
        'updated_at',
        'created_by',
        'updated_by'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'employee_code',
                'user',
                'first_name',
                'last_name',
                'email',
                'phone'
            )
        }),
        ('Employment Details', {
            'fields': (
                'department',
                'location',
                'hire_date',
                'salary',
                'is_active'
            )
        }),
        ('Audit Trail', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )
    
    def full_name_display(self, obj):
        """Display full name"""
        return obj.full_name
    full_name_display.short_description = 'Full Name'
    full_name_display.admin_order_field = 'last_name'
    
    def get_queryset(self, request):
        """Optimize queries with select_related"""
        qs = super().get_queryset(request)
        return qs.select_related('department', 'location', 'user')


@admin.register(PayrollPeriod)
class PayrollPeriodAdmin(admin.ModelAdmin):
    list_display = [
        'period_name',
        'start_date',
        'end_date',
        'payroll_count',
        'is_closed'
    ]
    list_filter = ['is_closed', 'start_date']
    search_fields = ['period_name']
    readonly_fields = [
        'payroll_count',
        'total_payroll_amount'
    ]
    
    fieldsets = (
        ('Period Information', {
            'fields': (
                'period_name',
                'start_date',
                'end_date',
                'is_closed'
            )
        }),
        ('Statistics', {
            'fields': (
                'payroll_count',
                'total_payroll_amount'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def payroll_count(self, obj):
        """Display number of payrolls in this period"""
        return obj.payrolls.count()
    payroll_count.short_description = 'Payrolls'
    
    def total_payroll_amount(self, obj):
        """Display total payroll amount for this period"""
        total = sum(p.net_salary for p in obj.payrolls.all())
        return format_html('<strong>{:.2f}</strong>', total)
    total_payroll_amount.short_description = 'Total Payroll Amount'


@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = [
        'employee_display',
        'period',
        'base_salary',
        'deductions',
        'net_salary_display',
        'payment_date',
        'is_paid'
    ]
    list_filter = [
        'period',
        'is_paid',
        'payment_date',
        'employee__department',
        'employee__location'
    ]
    search_fields = [
        'employee__employee_code',
        'employee__first_name',
        'employee__last_name',
        'period__period_name'
    ]
    readonly_fields = [
        'net_salary_display',
        'created_at',
        'updated_at',
        'created_by',
        'updated_by'
    ]
    
    fieldsets = (
        ('Payroll Information', {
            'fields': (
                'employee',
                'period'
            )
        }),
        ('Salary Details', {
            'fields': (
                'base_salary',
                'deductions',
                'net_salary_display'
            )
        }),
        ('Payment', {
            'fields': (
                'payment_date',
                'is_paid'
            )
        }),
        ('Audit Trail', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )
    
    def employee_display(self, obj):
        """Display employee code and name"""
        return f"{obj.employee.employee_code} - {obj.employee.full_name}"
    employee_display.short_description = 'Employee'
    employee_display.admin_order_field = 'employee__employee_code'
    
    def net_salary_display(self, obj):
        """Display net salary with formatting"""
        return format_html('<strong>{:.2f}</strong>', obj.net_salary)
    net_salary_display.short_description = 'Net Salary'
    
    def get_queryset(self, request):
        """Optimize queries with select_related"""
        qs = super().get_queryset(request)
        return qs.select_related('employee', 'employee__department', 'employee__location', 'period')
    
    def save_model(self, request, obj, form, change):
        """Set created_by/updated_by on save"""
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
