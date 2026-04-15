"""
Cultivation Serializers
MotherPlant, ProductionBatch, Clone, ProductionAssumption
"""

from rest_framework import serializers
from .models import MotherPlant, ProductionBatch, Clone, ProductionAssumption


class MotherPlantSerializer(serializers.ModelSerializer):
    strain_name = serializers.CharField(source='strain.name', read_only=True)
    location_code = serializers.CharField(source='location.code', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    health_grade_display = serializers.CharField(source='get_health_grade_display', read_only=True)
    
    class Meta:
        model = MotherPlant
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']


class MotherPlantListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views"""
    strain_name = serializers.CharField(source='strain.name', read_only=True)
    location_code = serializers.CharField(source='location.code', read_only=True)
    
    class Meta:
        model = MotherPlant
        fields = ['id', 'code', 'strain', 'strain_name', 'location', 'location_code', 'status', 'health_grade']


class ProductionBatchSerializer(serializers.ModelSerializer):
    mother_plant_code = serializers.CharField(source='mother_plant.code', read_only=True)
    location_code = serializers.CharField(source='location.code', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    rooted_clone_count = serializers.ReadOnlyField()
    survival_rate = serializers.ReadOnlyField()
    
    class Meta:
        model = ProductionBatch
        fields = '__all__'
        read_only_fields = ['id', 'rooted_clone_count', 'survival_rate', 'created_at', 'updated_at', 'created_by', 'updated_by']


class CloneSerializer(serializers.ModelSerializer):
    strain_name = serializers.CharField(source='strain.name', read_only=True)
    location_code = serializers.CharField(source='location.code', read_only=True)
    batch_number = serializers.CharField(source='production_batch.batch_number', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    age_in_days = serializers.ReadOnlyField()
    
    class Meta:
        model = Clone
        fields = '__all__'
        read_only_fields = [
            'id', 'strain', 'location', 'age_in_days',
            'created_at', 'updated_at', 'created_by', 'updated_by'
        ]


class CloneListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views"""
    strain_name = serializers.CharField(source='strain.name', read_only=True)
    location_code = serializers.CharField(source='location.code', read_only=True)
    
    class Meta:
        model = Clone
        fields = ['id', 'code', 'strain', 'strain_name', 'location', 'location_code', 'status', 'rooting_date', 'unit_cost']


class ProductionAssumptionSerializer(serializers.ModelSerializer):
    location_code = serializers.CharField(source='location.code', read_only=True)
    
    class Meta:
        model = ProductionAssumption
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']

