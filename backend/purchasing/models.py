from decimal import Decimal
from django.db import models
from django.utils import timezone
from core.models import AuditMixin, Contact, Location, Currency, TaxType


def _generate_number(prefix, model_class, field_name):
    """Return the next sequential document number in the format PREFIX-YYYY-NNN."""
    year = timezone.now().year
    pattern = f"{prefix}-{year}-"
    last = (
        model_class.objects
        .filter(**{f"{field_name}__startswith": pattern})
        .order_by(field_name)
        .values_list(field_name, flat=True)
        .last()
    )
    if last:
        try:
            seq = int(last.split('-')[-1]) + 1
        except (ValueError, IndexError):
            seq = 1
    else:
        seq = 1
    return f"{pattern}{seq:03d}"


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
    Top-level expense category grouping (e.g. Clones, Construccion, Utilidades).
    category_type is the default type for subcategories in this group.
    """
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(
        max_length=20,
        blank=True,
        default='',
        help_text='Optional short code for the category'
    )
    category_type = models.CharField(
        max_length=10,
        choices=[
            ('opex', 'OPEX'),
            ('capex', 'CAPEX'),
            ('cogs', 'COGS'),
        ],
        default='opex',
        help_text='Default expense type for this category'
    )
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'expense_categories'
        verbose_name = 'Expense Category'
        verbose_name_plural = 'Expense Categories'
        ordering = ['name']
        indexes = [
            models.Index(fields=['category_type', 'is_active']),
        ]

    def __str__(self):
        return self.name


class ExpenseSubcategory(models.Model):
    """
    Subcategory within an ExpenseCategory.
    expense_type here is the actual OPEX/CAPEX/COGS classification for reporting.
    """
    category = models.ForeignKey(
        ExpenseCategory,
        on_delete=models.CASCADE,
        related_name='subcategories',
    )
    name = models.CharField(max_length=100)
    expense_type = models.CharField(
        max_length=10,
        choices=[
            ('opex', 'OPEX'),
            ('capex', 'CAPEX'),
            ('cogs', 'COGS'),
        ],
        default='opex',
        help_text='Expense classification type (OPEX / CAPEX / COGS)'
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'expense_subcategories'
        verbose_name = 'Expense Subcategory'
        verbose_name_plural = 'Expense Subcategories'
        ordering = ['category__name', 'name']
        indexes = [
            models.Index(fields=['category', 'expense_type']),
            models.Index(fields=['expense_type', 'is_active']),
        ]

    def __str__(self):
        return f"{self.category.name} / {self.name} ({self.expense_type.upper()})"


class PurchaseOrder(AuditMixin):
    """
    Purchase orders to suppliers
    """
    po_number = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        help_text='Unique purchase order number (auto-generated if blank)'
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

    def save(self, *args, **kwargs):
        if not self.po_number:
            self.po_number = _generate_number('PO', PurchaseOrder, 'po_number')
        if self.tax_type_id:
            rate = Decimal(str(self.tax_type.rate)) / Decimal('100')
            self.tax_amount = (self.base_amount * rate).quantize(Decimal('0.01'))
        else:
            self.tax_amount = Decimal('0')
        self.total_amount = self.base_amount + self.tax_amount
        super().save(*args, **kwargs)

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
        self.line_total = self.quantity * self.unit_price
        super().save(*args, **kwargs)


EXPENSE_STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('approved', 'Approved'),
    ('paid', 'Paid'),
    ('partially_paid', 'Partially Paid'),
    ('overdue', 'Overdue'),
    ('cancelled', 'Cancelled'),
]


class Expense(AuditMixin):
    """
    Unified expense / supplier invoice ledger.

    document_type='expense'  → simple operational/capital spend (EXP-YYYY-NNN)
    document_type='invoice'  → supplier invoice with VAT/retention/due date (INV-YYYY-NNN)

    Invoice-specific fields (vat_amount, retention_amount, total_amount,
    paid_amount, due_date, tax_type, status, payment_date) are only
    meaningful when document_type='invoice'.
    """
    expense_number = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        help_text='Auto-generated: EXP-YYYY-NNN or INV-YYYY-NNN'
    )
    document_type = models.CharField(
        max_length=10,
        choices=[('expense', 'Expense'), ('invoice', 'Invoice')],
        default='expense',
        help_text='Expense = simple spend; Invoice = supplier invoice with tax'
    )

    # Categorisation
    category = models.ForeignKey(
        ExpenseCategory,
        on_delete=models.PROTECT,
        related_name='expenses'
    )
    subcategory = models.ForeignKey(
        ExpenseSubcategory,
        on_delete=models.SET_NULL,
        related_name='expenses',
        null=True,
        blank=True,
        help_text='Specific subcategory within the category'
    )

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name='expenses',
        null=True,
        blank=True,
        help_text='Supplier (optional for plain expenses, usually set for invoices)'
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name='expenses'
    )
    expense_date = models.DateField(
        help_text='Date of the expense or invoice date'
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text='Base amount (before tax)'
    )
    currency = models.ForeignKey(
        Currency,
        on_delete=models.PROTECT,
        related_name='expenses'
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

    # --- Invoice-specific fields ---
    invoice_reference = models.CharField(
        max_length=50,
        blank=True,
        help_text='External supplier invoice number'
    )
    due_date = models.DateField(
        null=True,
        blank=True,
        help_text='Payment due date (invoices only)'
    )
    tax_type = models.ForeignKey(
        TaxType,
        on_delete=models.PROTECT,
        related_name='purchase_expenses',
        null=True,
        blank=True,
        help_text='VAT / tax type (invoices only)'
    )
    vat_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text='Calculated VAT amount'
    )
    retention_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text='Retention withheld (invoices only)'
    )
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text='Total after tax and retention'
    )
    paid_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text='Amount paid so far (invoices only)'
    )
    status = models.CharField(
        max_length=20,
        choices=EXPENSE_STATUS_CHOICES,
        blank=True,
        default='',
        help_text='Payment status (invoices only)'
    )
    payment_date = models.DateField(
        null=True,
        blank=True,
        help_text='Date fully paid'
    )

    class Meta:
        db_table = 'expenses'
        ordering = ['-expense_date']
        indexes = [
            models.Index(fields=['expense_number']),
            models.Index(fields=['document_type', 'expense_date']),
            models.Index(fields=['category', 'expense_date']),
            models.Index(fields=['supplier', 'expense_date']),
            models.Index(fields=['location', 'expense_date']),
            models.Index(fields=['status']),
        ]

    def save(self, *args, **kwargs):
        if not self.expense_number:
            prefix = 'INV' if self.document_type == 'invoice' else 'EXP'
            self.expense_number = _generate_number(prefix, Expense, 'expense_number')

        if self.document_type == 'invoice':
            if self.tax_type_id:
                rate = Decimal(str(self.tax_type.rate)) / Decimal('100')
                self.vat_amount = (self.amount * rate).quantize(Decimal('0.01'))
            else:
                self.vat_amount = Decimal('0')
            self.total_amount = self.amount + self.vat_amount - self.retention_amount
            if not self.status:
                self.status = 'pending'
        else:
            self.vat_amount = Decimal('0')
            self.total_amount = self.amount

        super().save(*args, **kwargs)

    @property
    def balance_due(self):
        if self.document_type == 'invoice':
            return self.total_amount - self.paid_amount
        return Decimal('0')

    def __str__(self):
        return f"{self.expense_number} - {self.category.name}: {self.currency.symbol}{self.amount}"


class PurchaseInvoice(AuditMixin):
    """
    Supplier invoices for tracking payables.
    NOTE: New invoices should be recorded as Expense(document_type='invoice').
    This model is kept for historical data.
    """
    invoice_number = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        help_text='Unique invoice number (auto-generated if blank)'
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
        default=0,
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

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = _generate_number('PINV', PurchaseInvoice, 'invoice_number')
        if self.tax_type_id:
            rate = Decimal(str(self.tax_type.rate)) / Decimal('100')
            self.tax_amount = (self.base_amount * rate).quantize(Decimal('0.01'))
        else:
            self.tax_amount = Decimal('0')
        self.total_amount = self.base_amount + self.tax_amount
        super().save(*args, **kwargs)

    @property
    def balance_due(self):
        return self.total_amount - self.paid_amount
