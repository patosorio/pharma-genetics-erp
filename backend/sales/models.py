from django.db import models
from django.utils import timezone
from core.models import AuditMixin, Contact, Location, Currency, TaxType
from genetics.models import Strain


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


class Customer(AuditMixin):
    """
    Customer entity - extends Contact with customer-specific fields
    Each customer must have a corresponding Contact record
    """
    contact = models.OneToOneField(
        Contact,
        on_delete=models.PROTECT,
        related_name='customer_profile',
        limit_choices_to={'contact_type': 'customer'},
        help_text='Link to contact record (must be of type customer)'
    )
    customer_code = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        help_text='Unique customer identifier (auto-generated if blank)'
    )
    tier = models.CharField(
        max_length=50,
        choices=[
            ('retail', 'Retail'),
            ('wholesale', 'Wholesale'),
            ('bulk', 'Bulk'),
        ],
        default='retail',
        help_text='Customer pricing tier'
    )
    credit_limit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text='Maximum credit allowed'
    )
    payment_terms_days = models.IntegerField(
        default=0,
        help_text='Payment terms in days (0 = immediate)'
    )
    
    class Meta:
        db_table = 'customers'
        ordering = ['customer_code']
        indexes = [
            models.Index(fields=['customer_code']),
            models.Index(fields=['tier']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.customer_code:
            self.customer_code = _generate_number('CUST', Customer, 'customer_code')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.customer_code} - {self.contact.name}"


class PriceList(AuditMixin):
    """
    Pricing rules by strain and customer tier
    """
    strain = models.ForeignKey(
        Strain,
        on_delete=models.PROTECT,
        related_name='price_lists'
    )
    tier = models.CharField(
        max_length=50,
        choices=[
            ('retail', 'Retail'),
            ('wholesale', 'Wholesale'),
            ('bulk', 'Bulk'),
        ],
        help_text='Customer tier this price applies to'
    )
    price_per_clone = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Price per clone for this strain and tier'
    )
    currency = models.ForeignKey(
        Currency,
        on_delete=models.PROTECT,
        related_name='price_lists'
    )
    min_quantity = models.IntegerField(
        default=1,
        help_text='Minimum order quantity for this price'
    )
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'price_lists'
        ordering = ['strain', 'tier']
        indexes = [
            models.Index(fields=['strain', 'tier', 'is_active']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['strain', 'tier'],
                name='unique_strain_tier'
            ),
        ]
    
    def __str__(self):
        return f"{self.strain.name} - {self.tier}: {self.currency.symbol}{self.price_per_clone}"


class Order(AuditMixin):
    """
    Customer orders for clones
    """
    order_number = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        help_text='Unique order identifier (auto-generated if blank)'
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name='orders'
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name='orders',
        help_text='Location where order will be fulfilled'
    )
    order_date = models.DateField()
    expected_delivery_date = models.DateField()
    status = models.CharField(
        max_length=50,
        choices=[
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('in_production', 'In Production'),
            ('ready', 'Ready for Delivery'),
            ('partially_delivered', 'Partially Delivered'),
            ('delivered', 'Delivered'),
            ('cancelled', 'Cancelled'),
        ],
        default='draft'
    )
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text='Total order amount'
    )
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'orders'
        ordering = ['-order_date']
        indexes = [
            models.Index(fields=['order_number']),
            models.Index(fields=['customer', 'order_date']),
            models.Index(fields=['status']),
            models.Index(fields=['expected_delivery_date']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = _generate_number('ORD', Order, 'order_number')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.order_number} - {self.customer.contact.name}"


class OrderLine(models.Model):
    """
    Order line items - individual products in an order
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='order_lines'
    )
    strain = models.ForeignKey(
        Strain,
        on_delete=models.PROTECT,
        related_name='order_lines'
    )
    quantity = models.IntegerField(
        help_text='Number of clones ordered'
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Price per clone'
    )
    line_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text='Calculated as quantity * unit_price'
    )
    
    class Meta:
        db_table = 'order_lines'
        indexes = [
            models.Index(fields=['order', 'strain']),
        ]
    
    def __str__(self):
        return f"{self.order.order_number} - {self.strain.name}: {self.quantity}"
    
    def save(self, *args, **kwargs):
        """Auto-calculate line total"""
        self.line_total = self.quantity * self.unit_price
        super().save(*args, **kwargs)


class DeliveryNote(AuditMixin):
    """
    Delivery note - documents the physical delivery of an order
    Created after order is ready, before sales invoice
    """
    delivery_note_number = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        help_text='Unique delivery note identifier (auto-generated if blank)'
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.PROTECT,
        related_name='delivery_notes',
        help_text='Order being delivered'
    )
    delivery_date = models.DateField(
        help_text='Actual delivery date'
    )
    delivered_by = models.CharField(
        max_length=200,
        blank=True,
        help_text='Person who delivered the order'
    )
    received_by = models.CharField(
        max_length=200,
        blank=True,
        help_text='Person who received the order'
    )
    delivery_location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name='deliveries',
        help_text='Location where delivery occurred'
    )
    status = models.CharField(
        max_length=50,
        choices=[
            ('draft', 'Draft'),
            ('in_transit', 'In Transit'),
            ('delivered', 'Delivered'),
            ('partially_delivered', 'Partially Delivered'),
            ('cancelled', 'Cancelled'),
        ],
        default='draft'
    )
    notes = models.TextField(
        blank=True,
        help_text='Delivery notes or special instructions'
    )
    
    class Meta:
        db_table = 'delivery_notes'
        ordering = ['-delivery_date']
        indexes = [
            models.Index(fields=['delivery_note_number']),
            models.Index(fields=['order']),
            models.Index(fields=['delivery_date']),
            models.Index(fields=['status']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.delivery_note_number:
            self.delivery_note_number = _generate_number('DN', DeliveryNote, 'delivery_note_number')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.delivery_note_number} - {self.order.order_number}"


class DeliveryNoteLine(models.Model):
    """
    Delivery note line items - tracks what was actually delivered
    May differ from order lines if partial delivery
    """
    delivery_note = models.ForeignKey(
        DeliveryNote,
        on_delete=models.CASCADE,
        related_name='delivery_lines'
    )
    order_line = models.ForeignKey(
        OrderLine,
        on_delete=models.PROTECT,
        related_name='delivery_lines',
        help_text='Reference to original order line'
    )
    quantity_delivered = models.IntegerField(
        help_text='Actual quantity delivered'
    )
    notes = models.TextField(
        blank=True,
        help_text='Notes about this specific line item'
    )
    
    class Meta:
        db_table = 'delivery_note_lines'
        indexes = [
            models.Index(fields=['delivery_note', 'order_line']),
        ]
    
    def __str__(self):
        return f"{self.delivery_note.delivery_note_number} - {self.order_line.strain.name}: {self.quantity_delivered}"


class SalesInvoice(AuditMixin):
    """
    Sales invoices - financial document for payment
    References both order and delivery note
    """
    invoice_number = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        help_text='Unique invoice identifier (auto-generated if blank)'
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.PROTECT,
        related_name='invoices',
        help_text='Order this invoice is for'
    )
    delivery_note = models.ForeignKey(
        DeliveryNote,
        on_delete=models.PROTECT,
        related_name='invoices',
        null=True,
        blank=True,
        help_text='Delivery note this invoice is based on (optional)'
    )
    invoice_date = models.DateField()
    due_date = models.DateField(
        help_text='Payment due date'
    )
    
    # Tax fields
    tax_type = models.ForeignKey(
        TaxType,
        on_delete=models.PROTECT,
        related_name='sales_invoices',
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
        help_text='Total including tax (base_amount + tax_amount)'
    )
    
    paid_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text='Amount paid so far'
    )
    status = models.CharField(
        max_length=50,
        choices=[
            ('draft', 'Draft'),
            ('sent', 'Sent'),
            ('paid', 'Paid'),
            ('partially_paid', 'Partially Paid'),
            ('overdue', 'Overdue'),
            ('cancelled', 'Cancelled'),
        ],
        default='draft'
    )
    
    class Meta:
        db_table = 'sales_invoices'
        ordering = ['-invoice_date']
        indexes = [
            models.Index(fields=['invoice_number']),
            models.Index(fields=['order']),
            models.Index(fields=['invoice_date']),
            models.Index(fields=['due_date']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.invoice_number} - {self.order.customer.contact.name}"
    
    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = _generate_number('INV', SalesInvoice, 'invoice_number')
        if self.tax_type_id:
            from decimal import Decimal
            rate = Decimal(str(self.tax_type.rate)) / Decimal('100')
            self.tax_amount = (self.base_amount * rate).quantize(Decimal('0.01'))
        else:
            self.tax_amount = 0
        self.total_amount = self.base_amount + self.tax_amount
        super().save(*args, **kwargs)

    @property
    def balance_due(self):
        """Calculate remaining balance"""
        return self.total_amount - self.paid_amount


class Payment(AuditMixin):
    """
    Customer payments against invoices
    """
    payment_number = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        help_text='Unique payment identifier (auto-generated if blank)'
    )
    invoice = models.ForeignKey(
        SalesInvoice,
        on_delete=models.PROTECT,
        related_name='payments'
    )
    payment_date = models.DateField()
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text='Payment amount'
    )
    payment_method = models.CharField(
        max_length=50,
        choices=[
            ('cash', 'Cash'),
            ('bank_transfer', 'Bank Transfer'),
            ('check', 'Check'),
            ('credit_card', 'Credit Card'),
            ('other', 'Other'),
        ]
    )
    reference_number = models.CharField(
        max_length=100,
        blank=True,
        help_text='Bank reference, check number, etc.'
    )
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'payments'
        ordering = ['-payment_date']
        indexes = [
            models.Index(fields=['payment_number']),
            models.Index(fields=['invoice']),
            models.Index(fields=['payment_date']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.payment_number:
            self.payment_number = _generate_number('PAY', Payment, 'payment_number')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.payment_number} - {self.invoice.order.customer.contact.name}: {self.amount}"
