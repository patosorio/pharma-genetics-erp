from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from core.models import AuditMixin, Location


class CostAllocationRule(AuditMixin):
    """
    Cost allocation rules - defines HOW to allocate actual costs from Purchasing and HR
    Does NOT store actual cost amounts - those come from Expense and Payroll records
    """
    location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name='cost_allocation_rules'
    )
    effective_date = models.DateField(
        null=False,
        blank=False,
        help_text='The date these allocation rules become effective'
    )
    end_date = models.DateField(
        null=True,
        blank=True,
        help_text='The date these rules are no longer effective (null for current)'
    )
    
    # Production capacity (for allocation basis)
    monthly_capacity_clones = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text='Monthly production capacity in clones (for overhead allocation)'
    )
    
    # Mother plant lifecycle assumptions (for COG allocation)
    mother_plant_lifecycle_days = models.IntegerField(
        default=133,
        help_text='Expected lifecycle for mother plant (for allocating mother plant costs)'
    )
    expected_clones_per_mother_lifecycle = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text='Expected total clones from one mother plant over its lifecycle'
    )
    
    # Department allocation rules (link to actual HR departments)
    direct_labor_departments = models.JSONField(
        default=list,
        help_text='Department codes that should be allocated as direct labor (e.g., ["CULT"])'
    )
    overhead_labor_departments = models.JSONField(
        default=list,
        help_text='Department codes that should be allocated as overhead (e.g., ["ADMIN", "SALES"])'
    )
    
    # Expense category allocation rules (link to actual expense categories)
    cogs_expense_categories = models.JSONField(
        default=list,
        help_text='Expense category codes that are COGS (e.g., ["MAT", "NUTR", "SUB"])'
    )
    variable_expense_categories = models.JSONField(
        default=list,
        help_text='Expense category codes that are variable OPEX (e.g., ["ELEC", "WATER"])'
    )
    fixed_expense_categories = models.JSONField(
        default=list,
        help_text='Expense category codes that are fixed OPEX (e.g., ["RENT", "INS"])'
    )
    
    notes = models.TextField(
        blank=True,
        help_text='Additional notes about these allocation rules'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Whether this allocation rule is currently active'
    )
    
    class Meta:
        db_table = 'cost_allocation_rules'
        verbose_name_plural = 'Cost Allocation Rules'
        ordering = ['-effective_date', 'location']
        indexes = [
            models.Index(fields=['location', 'effective_date']),
            models.Index(fields=['effective_date', 'is_active']),
        ]
    
    def __str__(self):
        location_code = self.location.code if self.location else 'Unknown'
        return f"{location_code} - {self.effective_date} (Allocation Rules)"


class PricingTier(AuditMixin):
    """
    Pricing structure by customer tier
    Defines pricing tiers (retail, wholesale, bulk) with quantity ranges
    """
    tier_name = models.CharField(
        max_length=50,
        choices=[
            ('retail', 'Retail'),
            ('wholesale', 'Wholesale'),
            ('bulk', 'Bulk'),
        ],
        help_text='Name of the pricing tier'
    )
    min_quantity = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text='Minimum quantity for this tier'
    )
    max_quantity = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text='Maximum quantity for this tier (null for unlimited)'
    )
    price_per_clone = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text='Price per clone for this tier'
    )
    effective_date = models.DateField(
        null=False,
        blank=False,
        help_text='Date when this pricing tier becomes effective'
    )
    end_date = models.DateField(
        null=True,
        blank=True,
        help_text='Date when this pricing tier ends (null for ongoing)'
    )
    annual_price_increase_pct = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text='Annual price increase percentage (e.g., 5.00 for 5%)'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Whether this pricing tier is currently active'
    )
    
    class Meta:
        db_table = 'pricing_tiers'
        verbose_name_plural = 'Pricing Tiers'
        ordering = ['min_quantity', 'tier_name']
        indexes = [
            models.Index(fields=['tier_name', 'is_active']),
            models.Index(fields=['effective_date', 'end_date']),
            models.Index(fields=['min_quantity', 'max_quantity']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(max_quantity__isnull=True) | models.Q(max_quantity__gte=models.F('min_quantity')),
                name='max_quantity_gte_min_quantity'
            ),
        ]
    
    def __str__(self):
        max_qty = f"-{self.max_quantity}" if self.max_quantity else "+"
        return f"{self.get_tier_name_display()} ({self.min_quantity}{max_qty}): {self.price_per_clone}"
    
    def get_price_for_date(self, target_date):
        """Calculate price for a specific date considering annual increases"""
        from datetime import date
        
        if target_date < self.effective_date:
            return None
        
        if self.end_date and target_date > self.end_date:
            return None
        
        years_since_effective = (target_date.year - self.effective_date.year)
        if years_since_effective <= 0:
            return self.price_per_clone
        
        increase_factor = (Decimal('1') + (self.annual_price_increase_pct / Decimal('100'))) ** years_since_effective
        return self.price_per_clone * increase_factor


class CostSnapshot(AuditMixin):
    """
    Snapshot of calculated costs at a point in time
    Stores calculated costs for historical reporting and analysis
    Useful for tracking cost trends over time
    """
    location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name='cost_snapshots'
    )
    snapshot_date = models.DateField(
        help_text='Date of this cost snapshot'
    )
    period_start = models.DateField(
        help_text='Start date of the period used for calculations'
    )
    period_end = models.DateField(
        help_text='End date of the period used for calculations'
    )
    
    # Production metrics for the period
    total_clones_produced = models.IntegerField(
        default=0,
        help_text='Total clones produced in this period'
    )
    capacity_utilization_pct = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text='Capacity utilization percentage for this period'
    )
    
    # Actual costs from Purchasing.Expense
    total_cogs_expenses = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text='Total COGS expenses from Purchasing for this period'
    )
    total_variable_opex = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text='Total variable OPEX from Purchasing for this period'
    )
    total_fixed_opex = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text='Total fixed OPEX from Purchasing for this period'
    )
    
    # Actual labor costs from HR.Payroll
    total_direct_labor = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text='Total direct labor costs from HR.Payroll for this period'
    )
    total_overhead_labor = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text='Total overhead labor costs from HR.Payroll for this period'
    )
    
    # Calculated per-clone costs
    cogs_per_clone = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text='COGS expenses per clone'
    )
    direct_labor_per_clone = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text='Direct labor per clone'
    )
    variable_base_per_clone = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text='Variable base cost per clone (COGS + direct labor + variable OPEX)'
    )
    overhead_per_clone = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text='Overhead per clone (fixed OPEX + overhead labor)'
    )
    total_cost_per_clone = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text='Total cost per clone (variable base + overhead)'
    )
    
    notes = models.TextField(
        blank=True,
        help_text='Additional notes about this snapshot'
    )
    
    class Meta:
        db_table = 'cost_snapshots'
        verbose_name_plural = 'Cost Snapshots'
        ordering = ['-snapshot_date', 'location']
        indexes = [
            models.Index(fields=['location', 'snapshot_date']),
            models.Index(fields=['snapshot_date']),
            models.Index(fields=['period_start', 'period_end']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['location', 'snapshot_date'],
                name='unique_location_snapshot_date'
            ),
        ]
    
    def __str__(self):
        location_code = self.location.code if self.location else 'Unknown'
        return f"{location_code} - {self.snapshot_date} (Cost Snapshot)"
