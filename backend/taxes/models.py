from django.db import models
from django.db.models import Sum, Q
from core.models import AuditMixin, TaxType, Currency
from sales.models import SalesInvoice
from purchasing.models import PurchaseInvoice


def _generate_report_number(period_start):
    """Return TAX-YYYY-MM based on the period_start date."""
    return f"TAX-{period_start.year}-{period_start.month:02d}"


class TaxReport(AuditMixin):
    """
    Tax report for a specific period
    Summarizes VAT payable and recoverable for financial reporting
    """
    report_number = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        help_text='Unique tax report identifier (auto-generated as TAX-YYYY-MM if blank)'
    )
    period_start = models.DateField(
        help_text='Start date of reporting period'
    )
    period_end = models.DateField(
        help_text='End date of reporting period'
    )
    status = models.CharField(
        max_length=50,
        choices=[
            ('draft', 'Draft'),
            ('finalized', 'Finalized'),
            ('filed', 'Filed'),
            ('paid', 'Paid'),
        ],
        default='draft'
    )
    currency = models.ForeignKey(
        Currency,
        on_delete=models.PROTECT,
        related_name='tax_reports',
        help_text='Currency for this report'
    )
    
    # Summary fields (calculated)
    total_vat_payable = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text='Total VAT collected from sales'
    )
    total_vat_recoverable = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text='Total VAT paid on purchases'
    )
    net_vat_position = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text='Net VAT position (payable - recoverable). Positive = owe tax, Negative = tax credit'
    )
    
    filing_date = models.DateField(
        null=True,
        blank=True,
        help_text='Date when report was filed with tax authority'
    )
    payment_date = models.DateField(
        null=True,
        blank=True,
        help_text='Date when tax was paid'
    )
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'tax_reports'
        ordering = ['-period_end']
        indexes = [
            models.Index(fields=['report_number']),
            models.Index(fields=['period_start', 'period_end']),
            models.Index(fields=['status']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.report_number and self.period_start:
            self.report_number = _generate_report_number(self.period_start)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.report_number} ({self.period_start} to {self.period_end})"

    def calculate_totals(self):
        """
        Calculate VAT payable, recoverable, and net position from invoices in period
        """
        # VAT Payable (from sales invoices)
        sales_invoices = SalesInvoice.objects.filter(
            invoice_date__gte=self.period_start,
            invoice_date__lte=self.period_end,
            status__in=['sent', 'paid', 'partially_paid', 'overdue']
        ).exclude(
            status='cancelled'
        )
        
        self.total_vat_payable = sales_invoices.aggregate(
            total=Sum('tax_amount')
        )['total'] or 0
        
        # VAT Recoverable (from purchase invoices)
        purchase_invoices = PurchaseInvoice.objects.filter(
            invoice_date__gte=self.period_start,
            invoice_date__lte=self.period_end,
            status__in=['approved', 'paid', 'partially_paid', 'overdue']
        ).exclude(
            status='cancelled'
        )
        
        self.total_vat_recoverable = purchase_invoices.aggregate(
            total=Sum('tax_amount')
        )['total'] or 0
        
        # Calculate net position
        self.net_vat_position = self.total_vat_payable - self.total_vat_recoverable
        
        self.save()
        return {
            'vat_payable': self.total_vat_payable,
            'vat_recoverable': self.total_vat_recoverable,
            'net_position': self.net_vat_position,
        }
    
    @property
    def is_payable(self):
        """Check if we owe tax (positive net position)"""
        return self.net_vat_position > 0
    
    @property
    def is_recoverable(self):
        """Check if we have tax credit (negative net position)"""
        return self.net_vat_position < 0


class TaxJournalEntry(AuditMixin):
    """
    Individual tax journal entries for detailed tracking
    Links to specific invoices (sales or purchase)
    """
    tax_report = models.ForeignKey(
        TaxReport,
        on_delete=models.PROTECT,
        related_name='journal_entries',
        help_text='Tax report this entry belongs to'
    )
    entry_type = models.CharField(
        max_length=50,
        choices=[
            ('payable', 'VAT Payable (Sales)'),
            ('recoverable', 'VAT Recoverable (Purchase)'),
        ],
        help_text='Type of VAT entry'
    )
    
    # Reference to source document
    sales_invoice = models.ForeignKey(
        SalesInvoice,
        on_delete=models.PROTECT,
        related_name='tax_entries',
        null=True,
        blank=True,
        help_text='Source sales invoice (for payable entries)'
    )
    purchase_invoice = models.ForeignKey(
        PurchaseInvoice,
        on_delete=models.PROTECT,
        related_name='tax_entries',
        null=True,
        blank=True,
        help_text='Source purchase invoice (for recoverable entries)'
    )
    
    tax_type = models.ForeignKey(
        TaxType,
        on_delete=models.PROTECT,
        related_name='journal_entries'
    )
    base_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text='Base amount (before tax)'
    )
    tax_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text='Tax amount'
    )
    entry_date = models.DateField(
        help_text='Date of the transaction'
    )
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'tax_journal_entries'
        verbose_name = 'Tax Journal Entry'
        verbose_name_plural = 'Tax Journal Entries'
        ordering = ['-entry_date']
        indexes = [
            models.Index(fields=['tax_report', 'entry_type']),
            models.Index(fields=['entry_type', 'entry_date']),
            models.Index(fields=['sales_invoice']),
            models.Index(fields=['purchase_invoice']),
        ]
        constraints = [
            # Ensure only one invoice reference is set
            models.CheckConstraint(
                check=(
                    Q(sales_invoice__isnull=False, purchase_invoice__isnull=True) |
                    Q(sales_invoice__isnull=True, purchase_invoice__isnull=False)
                ),
                name='only_one_invoice_reference'
            ),
        ]
    
    def save(self, *args, **kwargs):
        if self.sales_invoice_id and not self.pk:
            inv = self.sales_invoice
            if not self.base_amount:
                self.base_amount = inv.base_amount
            if not self.tax_amount:
                self.tax_amount = inv.tax_amount
            if not self.entry_date:
                self.entry_date = inv.invoice_date
            if not self.tax_type_id and inv.tax_type_id:
                self.tax_type_id = inv.tax_type_id
        elif self.purchase_invoice_id and not self.pk:
            inv = self.purchase_invoice
            if not self.base_amount:
                self.base_amount = inv.base_amount
            if not self.tax_amount:
                self.tax_amount = inv.tax_amount
            if not self.entry_date:
                self.entry_date = inv.invoice_date
            if not self.tax_type_id and inv.tax_type_id:
                self.tax_type_id = inv.tax_type_id
        super().save(*args, **kwargs)

    def __str__(self):
        if self.sales_invoice:
            return f"{self.entry_type} - {self.sales_invoice.invoice_number}: {self.tax_amount}"
        elif self.purchase_invoice:
            return f"{self.entry_type} - {self.purchase_invoice.invoice_number}: {self.tax_amount}"
        return f"{self.entry_type} - {self.entry_date}"

    def clean(self):
        """Validate that only one invoice type is set"""
        from django.core.exceptions import ValidationError
        
        if self.sales_invoice and self.purchase_invoice:
            raise ValidationError('Cannot reference both sales and purchase invoice')
        
        if not self.sales_invoice and not self.purchase_invoice:
            raise ValidationError('Must reference either sales or purchase invoice')
        
        # Validate entry_type matches invoice type
        if self.entry_type == 'payable' and not self.sales_invoice:
            raise ValidationError('Payable entries must reference a sales invoice')
        
        if self.entry_type == 'recoverable' and not self.purchase_invoice:
            raise ValidationError('Recoverable entries must reference a purchase invoice')
