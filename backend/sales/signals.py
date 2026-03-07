"""
Sales signals
Handles automatic updates for:
- Order.total_amount when OrderLines change
- SalesInvoice.paid_amount and status when Payments change
- Order.status when DeliveryNote is marked delivered
"""
from django.db import models
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver

from .models import OrderLine, Payment, DeliveryNote, SalesInvoice


# ---------------------------------------------------------------------------
# Order total
# ---------------------------------------------------------------------------

def _recalculate_order_total(order):
    total = order.order_lines.aggregate(s=models.Sum('line_total'))['s'] or 0
    order.total_amount = total
    order.save(update_fields=['total_amount'])


@receiver(post_save, sender=OrderLine)
def order_line_saved(sender, instance, **kwargs):
    _recalculate_order_total(instance.order)


@receiver(post_delete, sender=OrderLine)
def order_line_deleted(sender, instance, **kwargs):
    _recalculate_order_total(instance.order)


# ---------------------------------------------------------------------------
# Invoice paid_amount + status
# ---------------------------------------------------------------------------

def _recalculate_invoice_paid(invoice):
    paid = invoice.payments.aggregate(s=models.Sum('amount'))['s'] or 0
    invoice.paid_amount = paid

    if paid == 0:
        if invoice.status not in ('draft', 'cancelled'):
            invoice.status = 'sent'
    elif paid >= invoice.total_amount:
        invoice.status = 'paid'
    else:
        invoice.status = 'partially_paid'

    invoice.save(update_fields=['paid_amount', 'status'])


@receiver(post_save, sender=Payment)
def payment_saved(sender, instance, **kwargs):
    _recalculate_invoice_paid(instance.invoice)


@receiver(post_delete, sender=Payment)
def payment_deleted(sender, instance, **kwargs):
    _recalculate_invoice_paid(instance.invoice)


# ---------------------------------------------------------------------------
# Order status when DeliveryNote is delivered
# ---------------------------------------------------------------------------

@receiver(pre_save, sender=DeliveryNote)
def store_delivery_note_previous_status(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._previous_status = DeliveryNote.objects.get(pk=instance.pk).status
        except DeliveryNote.DoesNotExist:
            instance._previous_status = None
    else:
        instance._previous_status = None


@receiver(post_save, sender=DeliveryNote)
def delivery_note_status_changed(sender, instance, **kwargs):
    previous = getattr(instance, '_previous_status', None)
    if previous == instance.status:
        return

    if instance.status == 'delivered':
        order = instance.order
        if order.status not in ('delivered', 'cancelled'):
            order.status = 'delivered'
            order.save(update_fields=['status'])
    elif instance.status == 'partially_delivered':
        order = instance.order
        if order.status not in ('delivered', 'cancelled', 'partially_delivered'):
            order.status = 'partially_delivered'
            order.save(update_fields=['status'])
