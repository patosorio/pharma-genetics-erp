"""
Genetics Serializers
StrainCategory, Strain
"""

from rest_framework import serializers
from .models import StrainCategory, Strain


class StrainCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = StrainCategory
        fields = '__all__'


class StrainSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Strain
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']


class StrainListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Strain
        fields = [
            'id', 'name', 'slug', 'category', 'category_name', 
            'thc_percentage', 'cbd_percentage', 'terpene_profile',
            'is_active', 'catalogue_year'
        ]

