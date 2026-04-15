from django.db import models, transaction
from datetime import date
from core.models import AuditMixin, Location
from genetics.models import Strain
from sales.models import Order

class MotherPlant(AuditMixin):
    """
    Mother plant model
    """
    code = models.CharField(max_length=50, unique=True) 
    strain = models.ForeignKey(
        Strain,
        on_delete=models.PROTECT
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name='mother_plants'
    )
    status = models.CharField(
        max_length=50,
        choices=[
            ('Active_Production', 'Active Production'),
            ('Recovery', 'Recovery'),
            ('Low_Production', 'Low Production'),
            ('Quarantine', 'Quarantine'),
            ('Retired', 'Retired'),
            ('Under_Treatment', 'Under Treatment'),
            ('Growing', 'Growing'),
        ],
        default='Growing'
    )
    health_grade = models.CharField(
        max_length=50,
        choices=[
            ('A', 'A'),
            ('B', 'B'),
            ('C', 'C'),
            ('D', 'D'),
        ],
    )

    cultivation_date = models.DateField(
        null=False,
        blank=False,
        help_text='The date the mother plant was cultivated'
    )
    expected_ready_date = models.DateField(
        null=False,
        blank=False,
        help_text='The expected date the mother plant will be ready for production'
    )
    actual_ready_date = models.DateField(
        null=True,
        blank=True,
        help_text='The actual date the mother plant was ready for production'
    )
    expected_retirement_date = models.DateField(
        null=False,
        blank=False,
        help_text='The expected date the mother plant will be retired'
    )
    actual_retirement_date = models.DateField(
        null=True,
        blank=True,
        help_text='The actual date the mother plant was retired'
    )
    notes = models.TextField(
        blank=True,
        help_text='Additional notes about the mother plant'
    )
    
    clones_per_cycle_min = models.IntegerField(
        null=False,
        blank=False,
        help_text='The minimum number of clones per cycle'
    )
    clones_per_cycle_max = models.IntegerField(
        null=False,
        blank=False,
        help_text='The maximum number of clones per cycle'
    )
    clones_per_cycle_avg = models.IntegerField(
        null=False,
        blank=False,
        help_text='The default number of clones per cycle'
    )

    total_cycles_year = models.IntegerField(
        null=False,
        blank=False,
        help_text='The total number of cycles per year'
    )

    min_possible_clones_year = models.IntegerField(
        null=False,
        blank=False,
        help_text='The minimum number of clones per year'
    )
    max_possible_clones_year = models.IntegerField(
        null=False,
        blank=False,
        help_text='The maximum number of clones per year'
    )
    avg_clones_year = models.IntegerField(
        null=False,
        blank=False,
        help_text='The default number of clones per year'
    )

    last_cut_date = models.DateField(
        null=True,
        blank=True,
        help_text="Auto-updated from latest ProductionBatch"
    )
    total_cuttings_taken = models.IntegerField(
        default=0,
        help_text="Lifetime total cuttings"
    )

    # Computed properties
    # @property
    # def next_available_date(self):
    #     """Calculate when mother plant is ready for next cutting"""
    #     if not self.last_cut_date:
    #         return date.today()
    #     return self.last_cut_date + timedelta(days=15)
    
    # @property
    # def is_available(self):
    #     """Check if mother plant is ready for cutting"""
    #     if not self.is_active:
    #         return False
    #     if self.health_status in ['poor', 'retired']:
    #         return False
    #     return date.today() >= self.next_available_date
    
    # @property
    # def cuts_available(self):
    #     """Calculate how many cuts can be taken"""
    #     if not self.is_available:
    #         return 0
        
    #     # Business rules
    #     if self.health_status == 'excellent':
    #         return 80
    #     elif self.health_status == 'good':
    #         return 60
    #     elif self.health_status == 'fair':
    #         return 40
    #     return 0
    
    # @property
    # def days_until_available(self):
    #     """Days until next cutting possible"""
    #     if self.is_available:
    #         return 0
    #     delta = self.next_available_date - date.today()
    #     return delta.days

    class Meta:
        db_table = 'mother_plants'
        verbose_name_plural = 'Mother Plants'
        ordering = ['code']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['strain']),
            models.Index(fields=['location']),
            models.Index(fields=['status']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['code'],
                name='unique_code'
            ),
        ]

    def __str__(self):
        return f"{self.code} - {self.strain.name}"


class ProductionBatch(AuditMixin):
    """
    Production batch model
    """
    batch_number = models.CharField(max_length=50, unique=True)
    mother_plant = models.ForeignKey(
        MotherPlant,
        on_delete=models.PROTECT,
        related_name='production_batches'
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name='production_batches'
    )
    cutting_date = models.DateField()
    expected_rooting_date = models.DateField(
        help_text="15 days from cutting_date"
    )
    initial_clone_count = models.IntegerField(
        help_text="Number of cuttings taken"
    )
    status = models.CharField(
        max_length=50,
        choices=[
            ('cutting', 'Cutting Phase'),
            ('rooting', 'Rooting Phase'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ],
        default='cutting'
    )
    
    # Costing fields
    total_batch_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Labor + overhead allocated to this batch"
    )
    cost_per_clone = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="total_batch_cost / rooted_clone_count"
    )
    
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'production_batches'
        ordering = ['-cutting_date']
    
    def __str__(self):
        return f"{self.batch_number} ({self.status})"
    
    @property
    def rooted_clone_count(self):
        """Calculate from actual rooted clones"""
        return self.clones.filter(
            status__in=['rooted', 'reserved', 'sold']
        ).count()
    
    @property
    def survival_rate(self):
        if self.initial_clone_count == 0:
            return 0
        return (
            self.rooted_clone_count / self.initial_clone_count) * 100
    
    def complete_batch(self):
        """
        Mark batch as completed and calculate costs.
        Call this when rooting phase is done.
        """
        from django.core.exceptions import ValidationError
        if self.status == 'completed':
            raise ValidationError(
                f"Batch '{self.batch_number}' is already completed."
            )

        rooted_count = self.rooted_clone_count

        if rooted_count > 0:
            self.cost_per_clone = self.total_batch_cost / rooted_count

        self.status = 'completed'
        self.save()

        # Update unit_cost for all rooted clones
        self.clones.filter(
            status__in=['rooted', 'reserved']
        ).update(
            unit_cost=self.cost_per_clone
        )


class Clone(AuditMixin):
    """
    Clone model
    """
    code = models.CharField(max_length=50, unique=True, null=False)
    production_batch = models.ForeignKey(
        ProductionBatch,
        on_delete=models.PROTECT,
        related_name='clones'
    )
    strain = models.ForeignKey(
        Strain,
        on_delete=models.PROTECT,
        related_name='clones',
        null=True,
        blank=True,
        editable=False  # Auto-populated
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name='clones',
        null=True,
        blank=True,
        editable=False  # Auto-populated
    )
    status = models.CharField(
        max_length=50,
        choices=[
            ('cutting', 'Cutting'),
            ('rooting', 'Rooting'),
            ('rooted', 'Available'),
            ('reserved', 'Reserved'),
            ('sold', 'Sold'),
            ('died', 'Died'),
        ],
        default='cutting'
    )
    rooting_date = models.DateField(null=True, blank=True)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    reserved_for_order = models.ForeignKey(
        'sales.Order',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    sold_to_order = models.ForeignKey(
        'sales.Order',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='sold_clones'
    )
    sold_date = models.DateField(null=True, blank=True)


    class Meta:
        db_table = 'clones'
        ordering = ['code']
        indexes = [
            models.Index(fields=['status', 'strain', 'location']),
            models.Index(fields=['rooting_date']),
        ]
    
    def __str__(self):
        strain_name = self.strain.name if self.strain else 'Unknown'
        return f"{self.code} ({strain_name})"
    
    def save(self, *args, **kwargs):
        if self.production_batch:
            self.strain = self.production_batch.mother_plant.strain
            self.location = self.production_batch.location
            
            # Auto-generate code if not provided — wrapped in atomic so the
            # select_for_update lock covers both the count query and the INSERT.
            if not self.code:
                with transaction.atomic():
                    self.code = self._generate_code()
                    super().save(*args, **kwargs)
                return
        
        super().save(*args, **kwargs)
    
    def _generate_code(self):
        """Generate readable code: BKK-OGK-20250127-001.

        Uses select_for_update() to prevent duplicate codes when multiple
        workers create clones in the same batch concurrently.
        Must be called inside a transaction.atomic() block.
        """
        batch = self.production_batch
        strain_slug = batch.mother_plant.strain.slug[:3].upper()
        location_code = batch.location.code
        date_str = batch.cutting_date.strftime('%Y%m%d')
        
        existing = Clone.objects.select_for_update().filter(
            production_batch=batch
        ).count()
        
        return f"{location_code}-{strain_slug}-{date_str}-{existing + 1:03d}"
    
    @property
    def age_in_days(self):
        if self.rooting_date:
            return (date.today() - self.rooting_date).days
        return 0


class ProductionAssumption(AuditMixin):
    """
    Core production parameters model
    """
    location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name='production_assumptions'
    )
    effective_date = models.DateField(
        null=False,
        blank=False,
        help_text='The date these assumptions become effective'
    )
    mother_plants_count = models.IntegerField(
        null=False,
        blank=False,
        help_text='Number of mother plants'
    )
    clones_per_mother_per_cycle = models.IntegerField(
        null=False,
        blank=False,
        help_text='Number of clones per mother plant per cycle'
    )
    cycle_duration_days = models.IntegerField(
        null=False,
        blank=False,
        help_text='Duration of each production cycle in days'
    )
    survival_rate_pct = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=False,
        blank=False,
        help_text='Survival rate percentage (0.00 to 100.00)'
    )
    ramp_up_months = models.IntegerField(
        null=False,
        blank=False,
        help_text='Number of months to ramp up to full capacity'
    )
    target_capacity_utilization_pct = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=False,
        blank=False,
        help_text='Target capacity utilization percentage (0.00 to 100.00)'
    )
    annual_cycles = models.IntegerField(
        null=False,
        blank=False,
        help_text='Number of production cycles per year'
    )
    max_monthly_capacity = models.IntegerField(
        null=False,
        blank=False,
        help_text='Maximum monthly production capacity'
    )
    version = models.IntegerField(
        null=False,
        blank=False,
        default=1,
        help_text='Version number for tracking assumption changes'
    )

    class Meta:
        db_table = 'production_assumptions'
        verbose_name_plural = 'Production Assumptions'
        ordering = ['-effective_date', 'location']
        indexes = [
            models.Index(fields=['location', 'effective_date']),
            models.Index(fields=['effective_date']),
            models.Index(fields=['version']),
        ]
    
    def __str__(self):
        location_code = self.location.code if self.location else 'Unknown'
        return f"{location_code} - {self.effective_date} (v{self.version})"
