"""
Purchasing signals
Rolls up PurchaseOrderItem line totals into PurchaseOrder.base_amount,
then re-triggers save() so tax_amount and total_amount stay consistent.
"""
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import PurchaseOrderItem


def _recalculate_po_base_amount(purchase_order):
    base = purchase_order.items.aggregate(s=models.Sum('line_total'))['s'] or 0
    purchase_order.base_amount = base
    purchase_order.save()


@receiver(post_save, sender=PurchaseOrderItem)
def purchase_order_item_saved(sender, instance, **kwargs):
    _recalculate_po_base_amount(instance.purchase_order)


@receiver(post_delete, sender=PurchaseOrderItem)
def purchase_order_item_deleted(sender, instance, **kwargs):
    _recalculate_po_base_amount(instance.purchase_order)
