"""
Inventory signals for automatic stock movement tracking
"""
from datetime import date
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from cultivation.models import Clone
from .models import StockMovement


@receiver(pre_save, sender=Clone)
def store_previous_status(sender, instance, **kwargs):
    """
    Store previous status before save for comparison
    This allows us to detect status changes
    """
    if instance.pk:
        try:
            previous = Clone.objects.get(pk=instance.pk)
            instance._previous_status = previous.status
        except Clone.DoesNotExist:
            instance._previous_status = None
    else:
        instance._previous_status = None


@receiver(post_save, sender=Clone)
def create_stock_movement(sender, instance, created, **kwargs):
    """
    Auto-create StockMovement when Clone status changes
    Provides complete audit trail of inventory movements
    """
    
    # Skip if this is a new clone being created
    if created:
        return
    
    # Check if we have previous status stored
    if not hasattr(instance, '_previous_status'):
        return
    
    old_status = instance._previous_status
    new_status = instance.status
    
    # No change in status
    if old_status == new_status:
        return
    
    # Map status transitions to movement types
    movement_map = {
        ('cutting', 'rooting'): None,  # Internal production step, no inventory impact
        ('rooting', 'rooted'): 'production_complete',  # Clone enters inventory
        ('rooted', 'reserved'): 'reserved',  # Reserved for order
        ('reserved', 'sold'): 'sold',  # Sold to customer
        ('reserved', 'rooted'): 'reserved',  # Unreserved (back to available)
        ('rooted', 'died'): 'waste',  # Waste/loss
        ('reserved', 'died'): 'waste',  # Waste/loss
        ('cutting', 'died'): 'waste',  # Failed before rooting
        ('rooting', 'died'): 'waste',  # Failed during rooting
    }
    
    movement_type = movement_map.get((old_status, new_status))
    
    # Only create movement for mapped transitions
    if movement_type:
        StockMovement.objects.create(
            clone=instance,
            movement_type=movement_type,
            from_location=instance.location if movement_type != 'production_complete' else None,
            to_location=instance.location if movement_type in ['production_complete', 'reserved'] else None,
            movement_date=date.today(),
            reference_type='batch',
            reference_id=instance.production_batch.batch_number,
            notes=f"Auto-generated: Status changed from '{old_status}' to '{new_status}'"
        )


@receiver(post_save, sender=Clone)
def update_batch_on_clone_status(sender, instance, created, **kwargs):
    """
    Update production batch metrics when clone status changes
    Recalculates rooted_clone_count (though it's now a property)
    """
    # This is now less critical since rooted_clone_count is a property
    # But we keep it for potential future batch-level caching
    pass

