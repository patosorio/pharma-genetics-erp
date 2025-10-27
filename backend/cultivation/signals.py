# # apps/cultivation/signals.py
# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from .models import ProductionBatch

# @receiver(post_save, sender=ProductionBatch)
# def update_mother_plant_metrics(sender, instance, created, **kwargs):
#     """Auto-update mother plant when new batch created"""
#     if created:
#         mother = instance.mother_plant
        
#         # Update last cut date
#         mother.last_cut_date = instance.cutting_date
        
#         # Increment total cuttings
#         mother.total_cuttings_taken += instance.initial_clone_count
        
#         mother.save(update_fields=['last_cut_date', 'total_cuttings_taken'])