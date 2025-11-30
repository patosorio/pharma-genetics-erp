from django.db import models
from core.models import AuditMixin, Contact, Location, Currency, TaxType


class Supplier(AuditMixin):
    """
    Supplier entity - extends Contact with supplier-specific fields
    Each supplier must have a corresponding Contact record
    """
    contact = models.OneToOneField(
        Contact,
        on_delete=models.PROTECT,
        related_name='supplier_profile',
        limit_choices_to={'contact_type': 'supplier'},
        help_text='Link to contact record (must be of type supplier)'
    )
    supplier_code = models.CharField(
        max_length=50,
        unique=True,
        help_text='Unique supplier identifier'
    )
    payment_terms_days = models.IntegerField(
        default=30,
        help_text='Payment terms in days (default: 30)'
    )
    
    class Meta:
        db_table = 'suppliers'
        ordering = ['supplier_code']
        indexes = [
            models.Index(fields=['supplier_code']),
        ]
    
    def __str__(self):
        return f"{self.supplier_code} - {self.contact.name}"


class ExpenseCategory(models.Model):
    """
    Expense categories for OPEX, CAPEX, and COGS tracking
    """
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(
        max_length=20,
        unique=True,
        help_text='Short code for the category'
    )
    category_type = models.CharField(
        max_length=50,
        choices=[
            ('opex', 'Operating Expense'),
            ('capex', 'Capital Expense'),
            ('cogs', 'Cost of Goods Sold'),
        ],
        default='opex',
        help_text='Type of expense category'
    )
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'expense_categories'
        verbose_name = 'Expense Category'
        verbose_name_plural = 'Expense Categories'
        ordering = ['code']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['category_type', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class PurchaseOrder(AuditMixin):
    """
    Purchase orders to suppliers
    """
    po_number = models.CharField(
        max_length=50,
        unique=True,
        help_text='Unique purchase order number'
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name='purchase_orders'
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name='purchase_orders',
        help_text='Location where goods/services will be received'
    )
    order_date = models.DateField()
    expected_delivery_date = models.DateField(
        help_text='Expected delivery date'
    )
    status = models.CharField(
        max_length=50,
        choices=[
            ('draft', 'Draft'),
            ('sent', 'Sent'),
            ('confirmed', 'Confirmed'),
            ('delivered', 'Delivered'),
            ('cancelled', 'Cancelled'),
        ],
        default='draft'
    )
    
    # Tax fields
    tax_type = models.ForeignKey(
        TaxType,
        on_delete=models.PROTECT,
        related_name='purchase_orders',
        null=True,
        blank=True,
        help_text='Tax type applied (e.g., VAT 7%)'
    )
    base_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text='Base amount before tax'
    )
    tax_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text='Tax amount calculated from base_amount and tax_type'
    )
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text='Total purchase order amount (base_amount + tax_amount)'
    )
    
    currency = models.ForeignKey(
        Currency,
        on_delete=models.PROTECT,
        related_name='purchase_orders',
        help_text='Currency for this purchase order'
    )
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'purchase_orders'
        ordering = ['-order_date']
        indexes = [
            models.Index(fields=['po_number']),
            models.Index(fields=['supplier', 'order_date']),
            models.Index(fields=['status']),
            models.Index(fields=['expected_delivery_date']),
        ]
    
    def __str__(self):
        return f"{self.po_number} - {self.supplier.contact.name}"


class PurchaseOrderItem(models.Model):
    """
    Purchase order line items
    """
    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        related_name='items'
    )
    expense_category = models.ForeignKey(
        ExpenseCategory,
        on_delete=models.PROTECT,
        related_name='purchase_items'
    )
    description = models.CharField(
        max_length=200,
        help_text='Description of item/service'
    )
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Quantity ordered'
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Price per unit'
    )
    line_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text='Calculated as quantity * unit_price'
    )
    
    class Meta:
        db_table = 'purchase_order_items'
        indexes = [
            models.Index(fields=['purchase_order']),
            models.Index(fields=['expense_category']),
        ]
    
    def __str__(self):
        return f"{self.purchase_order.po_number} - {self.description}"
    
    def save(self, *args, **kwargs):
        """Auto-calculate line total"""
        self.line_total = self.quantity * self.unit_price
        super().save(*args, **kwargs)


class Expense(AuditMixin):
    """
    Individual expense records for OPEX/CAPEX/COGS tracking
    """
    expense_number = models.CharField(
        max_length=50,
        unique=True,
        help_text='Unique expense identifier'
    )
    category = models.ForeignKey(
        ExpenseCategory,
        on_delete=models.PROTECT,
        related_name='expenses'
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name='expenses',
        null=True,
        blank=True,
        help_text='Supplier (optional)'
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name='expenses'
    )
    expense_date = models.DateField()
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text='Expense amount'
    )
    currency = models.ForeignKey(
        Currency,
        on_delete=models.PROTECT,
        related_name='expenses',
        help_text='Currency for this expense'
    )
    description = models.TextField(
        help_text='Detailed description of the expense'
    )
    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.SET_NULL,
        related_name='expenses',
        null=True,
        blank=True,
        help_text='Related purchase order (optional)'
    )
    
    class Meta:
        db_table = 'expenses'
        ordering = ['-expense_date']
        indexes = [
            models.Index(fields=['expense_number']),
            models.Index(fields=['category', 'expense_date']),
            models.Index(fields=['supplier', 'expense_date']),
            models.Index(fields=['location', 'expense_date']),
        ]
    
    def __str__(self):
        return f"{self.expense_number} - {self.category.name}: {self.currency.symbol}{self.amount}"


class PurchaseInvoice(AuditMixin):
    """
    Supplier invoices for tracking payables
    """
    invoice_number = models.CharField(
        max_length=50,
        unique=True,
        help_text='Unique invoice number'
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name='invoices'
    )
    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.PROTECT,
        related_name='invoices',
        null=True,
        blank=True,
        help_text='Related purchase order (optional)'
    )
    invoice_date = models.DateField()
    due_date = models.DateField(
        help_text='Payment due date'
    )
    
    # Tax fields
    tax_type = models.ForeignKey(
        TaxType,
        on_delete=models.PROTECT,
        related_name='purchase_invoices',
        null=True,
        blank=True,
        help_text='Tax type applied (e.g., VAT 7%)'
    )
    base_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text='Base amount before tax'
    )
    tax_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text='Tax amount calculated from base_amount and tax_type'
    )
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text='Total invoice amount (base_amount + tax_amount)'
    )
    
    paid_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text='Amount paid so far'
    )
    currency = models.ForeignKey(
        Currency,
        on_delete=models.PROTECT,
        related_name='purchase_invoices',
        help_text='Currency for this invoice'
    )
    status = models.CharField(
        max_length=50,
        choices=[
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('paid', 'Paid'),
            ('partially_paid', 'Partially Paid'),
            ('overdue', 'Overdue'),
            ('cancelled', 'Cancelled'),
        ],
        default='pending'
    )
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'purchase_invoices'
        ordering = ['-invoice_date']
        indexes = [
            models.Index(fields=['invoice_number']),
            models.Index(fields=['supplier', 'invoice_date']),
            models.Index(fields=['invoice_date']),
            models.Index(fields=['due_date']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.invoice_number} - {self.supplier.contact.name}"
    
    @property
    def balance_due(self):
        """Calculate remaining balance"""
        return self.total_amount - self.paid_amount
