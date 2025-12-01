from django.db import models
from django.core.validators import MinValueValidator
from django.conf import settings
from core.models import AuditMixin, Location


class Department(AuditMixin):
    """
    Company departments
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text='Department name'
    )
    code = models.CharField(
        max_length=20,
        unique=True,
        help_text='Department code (e.g., CULT, SALES, ADMIN)'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Whether this department is currently active'
    )
    
    class Meta:
        db_table = 'departments'
        verbose_name_plural = 'Departments'
        ordering = ['code']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['is_active']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['code'],
                name='unique_department_code'
            ),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Employee(AuditMixin):
    """
    Employee records
    """
    employee_code = models.CharField(
        max_length=50,
        unique=True,
        help_text='Unique employee code'
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='employee_profile',
        null=True,
        blank=True,
        help_text='Associated user account (optional)'
    )
    first_name = models.CharField(
        max_length=100,
        help_text='Employee first name'
    )
    last_name = models.CharField(
        max_length=100,
        help_text='Employee last name'
    )
    email = models.EmailField(
        help_text='Employee email address'
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        help_text='Employee phone number'
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name='employees',
        help_text='Employee department'
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name='employees',
        help_text='Employee location'
    )
    hire_date = models.DateField(
        help_text='Employee hire date'
    )
    salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text='Monthly base salary'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Whether this employee is currently active'
    )
    
    class Meta:
        db_table = 'employees'
        verbose_name_plural = 'Employees'
        ordering = ['employee_code']
        indexes = [
            models.Index(fields=['employee_code']),
            models.Index(fields=['department', 'is_active']),
            models.Index(fields=['location', 'is_active']),
            models.Index(fields=['is_active']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['employee_code'],
                name='unique_employee_code'
            ),
        ]
    
    def __str__(self):
        return f"{self.employee_code} - {self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        """Get employee full name"""
        return f"{self.first_name} {self.last_name}"


class PayrollPeriod(models.Model):
    """
    Monthly payroll periods
    """
    period_name = models.CharField(
        max_length=50,
        unique=True,
        help_text='Period name (e.g., "2025-01")'
    )
    start_date = models.DateField(
        help_text='Period start date'
    )
    end_date = models.DateField(
        help_text='Period end date'
    )
    is_closed = models.BooleanField(
        default=False,
        help_text='Whether this payroll period is closed'
    )
    
    class Meta:
        db_table = 'payroll_periods'
        verbose_name_plural = 'Payroll Periods'
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['period_name']),
            models.Index(fields=['start_date', 'end_date']),
            models.Index(fields=['is_closed']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['period_name'],
                name='unique_payroll_period_name'
            ),
            models.CheckConstraint(
                check=models.Q(end_date__gte=models.F('start_date')),
                name='end_date_gte_start_date'
            ),
        ]
    
    def __str__(self):
        return self.period_name
    
    def save(self, *args, **kwargs):
        """Override save to validate dates"""
        if self.end_date < self.start_date:
            raise ValueError("end_date must be after or equal to start_date")
        super().save(*args, **kwargs)


class Payroll(AuditMixin):
    """
    Payroll records
    """
    employee = models.ForeignKey(
        Employee,
        on_delete=models.PROTECT,
        related_name='payrolls',
        help_text='Employee for this payroll'
    )
    period = models.ForeignKey(
        PayrollPeriod,
        on_delete=models.PROTECT,
        related_name='payrolls',
        help_text='Payroll period'
    )
    base_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text='Base salary for this period'
    )
    deductions = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text='Total deductions (taxes, benefits, etc.)'
    )
    net_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        editable=False,
        help_text='Net salary (base_salary - deductions) - auto-calculated'
    )
    payment_date = models.DateField(
        null=True,
        blank=True,
        help_text='Date when payment was made'
    )
    is_paid = models.BooleanField(
        default=False,
        help_text='Whether this payroll has been paid'
    )
    
    class Meta:
        db_table = 'payrolls'
        verbose_name_plural = 'Payrolls'
        ordering = ['-period__start_date', 'employee']
        indexes = [
            models.Index(fields=['employee', 'period']),
            models.Index(fields=['period', 'is_paid']),
            models.Index(fields=['is_paid']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['employee', 'period'],
                name='unique_employee_period'
            ),
        ]
    
    def __str__(self):
        return f"{self.employee.employee_code} - {self.period.period_name}"
    
    def save(self, *args, **kwargs):
        """Calculate net salary before saving"""
        self.net_salary = self.base_salary - self.deductions
        super().save(*args, **kwargs)
