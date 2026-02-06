"""
Inventory Serializers
InventoryAlert, StockMovement, InventoryAdjustment
"""

from rest_framework import serializers
from .models import InventoryAlert, StockMovement, InventoryAdjustment


class InventoryAlertSerializer(serializers.ModelSerializer):
    strain_name = serializers.CharField(source='strain.name', read_only=True)
    location_code = serializers.CharField(source='location.code', read_only=True)
    current_stock = serializers.ReadOnlyField()
    is_low_stock = serializers.ReadOnlyField()
    stock_deficit = serializers.ReadOnlyField()
    
    class Meta:
        model = InventoryAlert
        fields = '__all__'


class StockMovementSerializer(serializers.ModelSerializer):
    clone_code = serializers.ReadOnlyField()
    strain_name = serializers.ReadOnlyField()
    from_location_code = serializers.CharField(source='from_location.code', read_only=True, allow_null=True)
    to_location_code = serializers.CharField(source='to_location.code', read_only=True, allow_null=True)
    movement_type_display = serializers.CharField(source='get_movement_type_display', read_only=True)
    
    class Meta:
        model = StockMovement
        fields = '__all__'
        read_only_fields = ['id', 'clone_code', 'strain_name', 'created_at', 'updated_at', 'created_by', 'updated_by']


class InventoryAdjustmentSerializer(serializers.ModelSerializer):
    clone_code = serializers.ReadOnlyField()
    strain_name = serializers.ReadOnlyField()
    location_code = serializers.ReadOnlyField()
    reason_display = serializers.CharField(source='get_reason_display', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    
    class Meta:
        model = InventoryAdjustment
        fields = '__all__'
        read_only_fields = ['id', 'clone_code', 'strain_name', 'location_code', 'created_at', 'updated_at', 'created_by', 'updated_by']

