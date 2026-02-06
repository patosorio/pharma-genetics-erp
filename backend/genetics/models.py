from django.db import models
from core.models import AuditMixin
from django.core.validators import MinValueValidator, MaxValueValidator

class StrainCategory(models.Model):
    """
    Strain category model: 
    - 50/50 Hybrid
    - 70/30 Indica
    - 70/30 Sativa
    - 30/70 Indica
    - 30/70 Sativa
    """
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    
    class Meta:
        db_table = 'strain_categories'
        verbose_name_plural = 'Strain Categories'
    
    def __str__(self):
        return self.name


class Strain(AuditMixin):
    """
    Strain model
    """
    name = models.CharField(
        max_length=255,
        null=False,
        blank=False,
        help_text='The name of the strain'
    )
    slug = models.SlugField(
        max_length=255,
        null=False,
        blank=False,
        unique=True
    )
    catalogue_year = models.IntegerField(
        null=False,
        blank=False,
        validators=[MinValueValidator(1900), MaxValueValidator(2100)],
        help_text='The catalogue year of the strain'
    )
    category = models.ForeignKey(StrainCategory, on_delete=models.CASCADE)
    description = models.TextField(blank=True)

    thc_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='The THC percentage of the strain'
    )
    cbd_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='The CBD percentage of the strain'
    )
    terpene_profile = models.CharField(
        max_length=255,
        blank=True,
        help_text='Comma-separated list of terpenes (e.g., Myrcene, Limonene, Caryophyllene)'
    )
    breeder = models.TextField(blank=True)
    lineage = models.TextField(blank=True)
    
    image = models.ImageField(upload_to='strains/', null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'strains'
        verbose_name_plural = 'Strains'
        ordering = ['slug']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['catalogue_year']),
            models.Index(fields=['category']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.category})"
