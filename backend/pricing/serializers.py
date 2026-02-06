"""
Pricing Serializers
CostAllocationRule, PricingTier, CostSnapshot
"""

from rest_framework import serializers
from .models import CostAllocationRule, PricingTier, CostSnapshot


class CostAllocationRuleSerializer(serializers.ModelSerializer):
    location_code = serializers.CharField(source='location.code', read_only=True)
    
    class Meta:
        model = CostAllocationRule
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']


class PricingTierSerializer(serializers.ModelSerializer):
    tier_name_display = serializers.CharField(source='get_tier_name_display', read_only=True)
    
    class Meta:
        model = PricingTier
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']


class CostSnapshotSerializer(serializers.ModelSerializer):
    location_code = serializers.CharField(source='location.code', read_only=True)
    
    class Meta:
        model = CostSnapshot
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']

