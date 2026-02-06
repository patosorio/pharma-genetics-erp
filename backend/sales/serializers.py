"""
Sales Serializers
Customer, PriceList, Order, OrderLine, DeliveryNote, DeliveryNoteLine, SalesInvoice, Payment
"""

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
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']


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


class OrderSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.contact.name', read_only=True)
    location_name = serializers.CharField(source='location.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    order_lines = OrderLineSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']


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


class DeliveryNoteSerializer(serializers.ModelSerializer):
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    location_name = serializers.CharField(source='delivery_location.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    delivery_lines = DeliveryNoteLineSerializer(many=True, read_only=True)
    
    class Meta:
        model = DeliveryNote
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']


class SalesInvoiceSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='order.customer.contact.name', read_only=True)
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    balance_due = serializers.ReadOnlyField()
    
    class Meta:
        model = SalesInvoice
        fields = '__all__'
        read_only_fields = ['id', 'balance_due', 'created_at', 'updated_at', 'created_by', 'updated_by']


class PaymentSerializer(serializers.ModelSerializer):
    invoice_number = serializers.CharField(source='invoice.invoice_number', read_only=True)
    customer_name = serializers.CharField(source='invoice.order.customer.contact.name', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']

