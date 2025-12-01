from django.db import models
from django.conf import settings
from core.models import AuditMixin, Location
from genetics.models import Strain


class InventoryAlert(models.Model):
    """
    Reorder point alerts for low stock
    Triggers notification when available
    clones fall below threshold
    """
    strain = models.ForeignKey(
        Strain,
        on_delete=models.CASCADE,
        related_name='inventory_alerts'
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        related_name='inventory_alerts'
    )
    reorder_point = models.IntegerField(
        help_text="Alert when available clones fall below this number"
    )
    alert_email = models.EmailField(
        blank=True,
        help_text="Email address to notify (optional, uses default if empty)"
    )
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'inventory_alerts'
        unique_together = ['strain', 'location']
        verbose_name = 'Inventory Alert'
        verbose_name_plural = 'Inventory Alerts'
    
    def __str__(self):
        return f"{self.strain.name} @ {self.location.code} (reorder at {self.reorder_point})"
    
    @property
    def current_stock(self):
        """Get current available stock for this strain/location"""
        from cultivation.models import Clone
        return Clone.objects.filter(
            status='rooted',
            strain=self.strain,
            location=self.location
        ).count()
    
    @property
    def is_low_stock(self):
        """Check if current stock is below reorder point"""
        return self.current_stock < self.reorder_point
    
    @property
    def stock_deficit(self):
        """How many clones needed to reach reorder point"""
        deficit = self.reorder_point - self.current_stock
        return deficit if deficit > 0 else 0


class StockMovement(AuditMixin):
    """
    Audit trail for all inventory movements
    Auto-created by signals when clone status changes
    """
    clone = models.ForeignKey(
        'cultivation.Clone',
        on_delete=models.PROTECT,
        related_name='stock_movements'
    )
    movement_type = models.CharField(
        max_length=50,
        choices=[
            ('production_complete', 'Production Complete - Clone Rooted'),
            ('transfer', 'Transfer Between Locations'),
            ('reserved', 'Reserved for Order'),
            ('sold', 'Sold to Customer'),
            ('adjustment', 'Manual Adjustment'),
            ('waste', 'Waste/Died'),
        ]
    )
    from_location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name='stock_movements_out',
        null=True,
        blank=True,
        help_text="Location clone moved from (null for production)"
    )
    to_location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name='stock_movements_in',
        null=True,
        blank=True,
        help_text="Location clone moved to (null for sale/waste)"
    )
    movement_date = models.DateField()
    
    # Reference to related record
    reference_type = models.CharField(
        max_length=50,
        blank=True,
        help_text="Type of reference: order, batch, adjustment"
    )
    reference_id = models.CharField(
        max_length=100,
        blank=True,
        help_text="ID of referenced record (order number, batch number, etc.)"
    )
    
    notes = models.TextField(blank=True)
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='stock_movements_performed',
        null=True,
        blank=True
    )
    
    class Meta:
        db_table = 'stock_movements'
        ordering = ['-movement_date', '-created_at']
        indexes = [
            models.Index(fields=['movement_date', 'movement_type']),
            models.Index(fields=['clone', 'movement_date']),
        ]
        verbose_name = 'Stock Movement'
        verbose_name_plural = 'Stock Movements'
    
    def __str__(self):
        return f"{self.movement_type} - {self.clone.code} on {self.movement_date}"
    
    @property
    def strain_name(self):
        return self.clone.strain.name
    
    @property
    def clone_code(self):
        return self.clone.code


class InventoryAdjustment(AuditMixin):
    """
    Manual inventory adjustments for dead clones, quality issues, etc.
    Requires manager approval and detailed notes
    """
    clone = models.ForeignKey(
        'cultivation.Clone',
        on_delete=models.PROTECT,
        related_name='adjustments'
    )
    adjustment_date = models.DateField()
    reason = models.CharField(
        max_length=50,
        choices=[
            ('died', 'Clone Died'),
            ('quality_issue', 'Quality Issue - Not Saleable'),
            ('damaged', 'Physical Damage'),
            ('contamination', 'Contamination/Disease'),
            ('theft', 'Theft/Loss'),
            ('other', 'Other (explain in notes)'),
        ]
    )
    notes = models.TextField(
        help_text="Required: Explain reason for adjustment"
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='inventory_adjustments_approved',
        help_text="Manager who approved this adjustment"
    )
    # TODO: attach photos/documentation
    photo_url = models.URLField(
        blank=True,
        help_text="URL to photo documentation (optional)"
    )
    
    class Meta:
        db_table = 'inventory_adjustments'
        ordering = ['-adjustment_date']
        verbose_name = 'Inventory Adjustment'
        verbose_name_plural = 'Inventory Adjustments'
    
    def __str__(self):
        return f"{self.clone.code} - {self.reason} on {self.adjustment_date}"
    
    @property
    def clone_code(self):
        return self.clone.code
    
    @property
    def strain_name(self):
        return self.clone.strain.name
    
    @property
    def location_code(self):
        return self.clone.location.code
    
    def save(self, *args, **kwargs):
        """
        Validate and update clone status when adjustment is saved
        """
        # Mandatory notes
        if not self.notes or len(self.notes) < 10:
            raise ValueError(
                "Detailed notes required for inventory adjustment "
                "(minimum 10 characters)"
            )
        
        # Update clone status based on reason
        if self.reason in [
            'died', 
            'quality_issue', 
            'damaged', 
            'contamination', 
            'theft',
            'other'
        ]:
            self.clone.status = 'died'
            self.clone.save(update_fields=['status'])
        
        super().save(*args, **kwargs)