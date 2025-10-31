from django.db import models
from core.models import AuditMixin, Location
from genetics.models import Strain

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
        default='active'
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
        null=False,
        blank=False,
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
    rooted_clone_count = models.IntegerField(
        default=0,
        help_text="Number that successfully rooted"
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
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'production_batches'
        ordering = ['-cutting_date']
    
    def __str__(self):
        return f"{self.batch_number} ({self.status})"
    
    @property
    def survival_rate(self):
        if self.initial_clone_count == 0:
            return 0
        return (
            self.rooted_clone_count / self.initial_clone_count) * 100


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
    # reserved_for_order = models.ForeignKey(
    #     'sales.Order',
    #     null=True,
    #     blank=True,
    #     on_delete=models.SET_NULL
    # )


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
        # Auto-populate denormalized fields
        if self.production_batch:
            self.strain = self.production_batch.mother_plant.strain
            self.location = self.production_batch.location
            
            # Auto-generate code if not provided
            if not self.code:
                self.code = self._generate_code()
        
        super().save(*args, **kwargs)
    
    def _generate_code(self):
        """Generate readable code: BKK-OGK-20250127-001"""
        batch = self.production_batch
        strain_slug = batch.mother_plant.strain.slug[:3].upper()  # First 3 chars of slug
        location_code = batch.location.code
        date_str = batch.cutting_date.strftime('%Y%m%d')
        
        # Get next sequential number
        existing = Clone.objects.filter(
            production_batch=batch
        ).count()
        
        return f"{location_code}-{strain_slug}-{date_str}-{existing + 1:03d}"
    
    # @property
    # def age_in_days(self):
    #     if self.rooting_date:
    #         return (date.today() - self.rooting_date).days
    #     return 0



