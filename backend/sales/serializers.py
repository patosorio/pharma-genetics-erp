"""
Sales Serializers
Customer, PriceList, Order, OrderLine, DeliveryNote, DeliveryNoteLine, SalesInvoice, Payment
"""

from django.db import transaction
from django.db.models import Sum
from rest_framework import serializers
from .models import (
    Customer, PriceList, Order, OrderLine, DeliveryNote, DeliveryNoteLine,
    SalesInvoice, Payment
)


class CustomerSerializer(serializers.ModelSerializer):
    contact_name = serializers.CharField(source='contact.name', read_only=True)
    contact_email = serializers.CharField(source='contact.email', read_only=True)
    contact_phone = serializers.CharField(source='contact.phone', read_only=True)
    tier_display = serializers.CharField(source='get_tier_display', read_only=True)

    class Meta:
        model = Customer
        fields = '__all__'
        read_only_fields = ['id', 'customer_code', 'created_at', 'updated_at', 'created_by', 'updated_by']


class PriceListSerializer(serializers.ModelSerializer):
    strain_name = serializers.CharField(source='strain.name', read_only=True)
    currency_code = serializers.CharField(source='currency.code', read_only=True)
    tier_display = serializers.CharField(source='get_tier_display', read_only=True)

    class Meta:
        model = PriceList
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']


class OrderLineSerializer(serializers.ModelSerializer):
    strain_name = serializers.CharField(source='strain.name', read_only=True)

    class Meta:
        model = OrderLine
        fields = '__all__'
        read_only_fields = ['id', 'line_total']

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero.")
        return value

    def validate_unit_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Unit price must be greater than zero.")
        return value


class OrderSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.contact.name', read_only=True)
    location_name = serializers.CharField(source='location.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    order_lines = OrderLineSerializer(many=True, read_only=False, required=False)

    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = [
            'id', 'order_number', 'total_amount',
            'created_at', 'updated_at', 'created_by', 'updated_by',
        ]

    def validate(self, data):
        order_date = data.get('order_date') or (self.instance.order_date if self.instance else None)
        expected = data.get('expected_delivery_date') or (self.instance.expected_delivery_date if self.instance else None)
        if order_date and expected and expected < order_date:
            raise serializers.ValidationError(
                "expected_delivery_date must be on or after order_date."
            )
        return data

    def create(self, validated_data):
        lines_data = validated_data.pop('order_lines', [])
        with transaction.atomic():
            order = Order.objects.create(**validated_data)
            for line_data in lines_data:
                OrderLine.objects.create(order=order, **line_data)
        return order

    def update(self, instance, validated_data):
        validated_data.pop('order_lines', None)
        return super().update(instance, validated_data)


class OrderListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views"""
    customer_name = serializers.CharField(source='customer.contact.name', read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'order_number', 'customer', 'customer_name', 'order_date', 'status', 'total_amount']


class DeliveryNoteLineSerializer(serializers.ModelSerializer):
    order_line_strain = serializers.CharField(source='order_line.strain.name', read_only=True)

    class Meta:
        model = DeliveryNoteLine
        fields = '__all__'

    def validate(self, data):
        order_line = data.get('order_line') or (self.instance.order_line if self.instance else None)
        quantity_delivered = data.get('quantity_delivered', getattr(self.instance, 'quantity_delivered', None))

        if order_line and quantity_delivered is not None:
            already_delivered = (
                DeliveryNoteLine.objects
                .filter(order_line=order_line)
                .exclude(pk=self.instance.pk if self.instance else None)
                .aggregate(total=Sum('quantity_delivered'))
                ['total'] or 0
            )
            if already_delivered + quantity_delivered > order_line.quantity:
                remaining = order_line.quantity - already_delivered
                raise serializers.ValidationError(
                    f"quantity_delivered ({quantity_delivered}) exceeds remaining "
                    f"quantity to deliver ({remaining}) for this order line."
                )
        return data


class DeliveryNoteSerializer(serializers.ModelSerializer):
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    location_name = serializers.CharField(source='delivery_location.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    delivery_lines = DeliveryNoteLineSerializer(many=True, read_only=False, required=False)

    class Meta:
        model = DeliveryNote
        fields = '__all__'
        read_only_fields = [
            'id', 'delivery_note_number',
            'created_at', 'updated_at', 'created_by', 'updated_by',
        ]

    def validate(self, data):
        order = data.get('order') or (self.instance.order if self.instance else None)
        if order and not self.instance:
            if order.status not in ('ready', 'partially_delivered'):
                raise serializers.ValidationError(
                    f"A delivery note can only be created when the order is 'ready' or "
                    f"'partially_delivered' (current status: '{order.status}')."
                )
        return data

    def create(self, validated_data):
        lines_data = validated_data.pop('delivery_lines', [])
        with transaction.atomic():
            note = DeliveryNote.objects.create(**validated_data)
            for line_data in lines_data:
                DeliveryNoteLine.objects.create(delivery_note=note, **line_data)
        return note

    def update(self, instance, validated_data):
        validated_data.pop('delivery_lines', None)
        return super().update(instance, validated_data)


class SalesInvoiceSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='order.customer.contact.name', read_only=True)
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    balance_due = serializers.ReadOnlyField()

    class Meta:
        model = SalesInvoice
        fields = '__all__'
        read_only_fields = [
            'id', 'invoice_number', 'tax_amount', 'total_amount', 'paid_amount',
            'balance_due', 'created_at', 'updated_at', 'created_by', 'updated_by',
        ]

    def validate(self, data):
        invoice_date = data.get('invoice_date') or (self.instance.invoice_date if self.instance else None)
        due_date = data.get('due_date') or (self.instance.due_date if self.instance else None)
        if invoice_date and due_date and due_date < invoice_date:
            raise serializers.ValidationError("due_date must be on or after invoice_date.")

        delivery_note = data.get('delivery_note') or (self.instance.delivery_note if self.instance else None)
        if delivery_note and not self.instance:
            if delivery_note.status != 'delivered':
                raise serializers.ValidationError(
                    f"An invoice can only be created against a delivery note that has been "
                    f"'delivered' (current status: '{delivery_note.status}')."
                )
        return data


class PaymentSerializer(serializers.ModelSerializer):
    invoice_number = serializers.CharField(source='invoice.invoice_number', read_only=True)
    customer_name = serializers.CharField(source='invoice.order.customer.contact.name', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)

    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = [
            'id', 'payment_number',
            'created_at', 'updated_at', 'created_by', 'updated_by',
        ]

    def validate(self, data):
        invoice = data.get('invoice') or (self.instance.invoice if self.instance else None)
        amount = data.get('amount', getattr(self.instance, 'amount', None))

        if invoice and amount is not None:
            existing_paid = invoice.payments.exclude(
                pk=self.instance.pk if self.instance else None
            ).aggregate(total=Sum('amount'))['total'] or 0

            if existing_paid + amount > invoice.total_amount:
                remaining = invoice.total_amount - existing_paid
                raise serializers.ValidationError(
                    f"Payment amount ({amount}) exceeds remaining balance due ({remaining})."
                )
        return data
