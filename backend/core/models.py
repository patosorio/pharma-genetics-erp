from decimal import Decimal
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.conf import settings


class AuditMixin(models.Model):
    """
    Abstract base class for audit trails
    All your models should inherit this
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='%(class)s_created',
        null=True,  # Allow null for system-created records
        blank=True
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='%(class)s_updated',
        null=True,
        blank=True
    )
    
    class Meta:
        abstract = True


class User(AbstractUser):
    
    role = models.CharField(
        max_length=255,
        choices=[
            ('admin', 'Administrator'),
            ('cultivation_manager', 'Cultivation'),
            ('sales_rep', 'Sales Representative'),
            ('accountant', 'Accountant'),
            ('viewer', 'Viewer Only'),
        ],
        default='viewer',
    )

    location = models.ForeignKey(
        'Location',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='users',
    )

    firebase_uid = models.CharField(
        max_length=128,
        blank=True,
        null=True,
        unique=True,
        help_text='Firebase UID for authentication'
    )

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    # Audit fields

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='created_users',
    )
    updated_by = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='updated_users',
    )

    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"


class Location(AuditMixin):
    """Base location model - needed before User"""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)  # BKK, PTY
    address = models.TextField()
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'locations'
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Contact(AuditMixin):
    """Unified contact model for customers, suppliers, and other entities"""
    contact_type = models.CharField(
        max_length=50,
        choices=[
            ('customer', 'Customer'),
            ('supplier', 'Supplier'),
            ('vendor', 'Vendor'),
            ('other', 'Other'),
        ],
        help_text='Type of contact'
    )
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    tax_id = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'contacts'
        ordering = ['name']
        indexes = [
            models.Index(fields=['contact_type', 'is_active']),
            models.Index(fields=['name']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_contact_type_display()})"


class Currency(AuditMixin):
    """Currency types (THB, USD, etc.)"""
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=50)
    symbol = models.CharField(max_length=5)
    is_default = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'currencies'
        verbose_name_plural = 'Currencies'
    
    def save(self, *args, **kwargs):
        if self.is_default:
            Currency.objects.exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.code} ({self.symbol})"


class TaxType(AuditMixin):
    """Tax types (VAT, etc.)"""
    name = models.CharField(max_length=100, unique=True)
    rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text='Tax rate as a percentage (e.g. 7.00 for 7%)',
    )
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'tax_types'
        verbose_name = 'Tax Type'
        verbose_name_plural = 'Tax Types'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.rate}%)"


class CompanySettings(models.Model):
    """Global company settings (singleton pattern)"""
    company_name = models.CharField(
        max_length=200,
        default="Thai Cannabis Genetics Co.",
        help_text='Company name'
    )
    tax_id = models.CharField(max_length=50, blank=True)
    default_currency = models.ForeignKey(
        Currency,
        on_delete=models.PROTECT,
        related_name='+'
    )
    fiscal_year_start_month = models.IntegerField(default=1)
    
    # Break-even pricing
    break_even_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        default=126.78,
        help_text="Minimum price per clone to break even"
    )
    
    class Meta:
        db_table = 'company_settings'
        verbose_name = 'Company Settings'
        verbose_name_plural = 'Company Settings'
    
    def __str__(self):
        return self.company_name
    
    def save(self, *args, **kwargs):
        # Ensure only one settings record exists (singleton)
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
