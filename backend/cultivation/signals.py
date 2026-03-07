"""
Cultivation signals
Auto-updates MotherPlant metrics when a new ProductionBatch is created.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ProductionBatch


@receiver(post_save, sender=ProductionBatch)
def update_mother_plant_metrics(sender, instance, created, **kwargs):
    """Auto-update mother plant when new batch is created."""
    if not created:
        return

    mother = instance.mother_plant

    mother.last_cut_date = instance.cutting_date
    mother.total_cuttings_taken += instance.initial_clone_count

    mother.save(update_fields=['last_cut_date', 'total_cuttings_taken'])
