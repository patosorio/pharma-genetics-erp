"""
Genetics ViewSets
StrainCategory, Strain
"""

from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend

from .models import StrainCategory, Strain
from .serializers import StrainCategorySerializer, StrainSerializer, StrainListSerializer


class StrainCategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for StrainCategory model
    """
    queryset = StrainCategory.objects.all()
    serializer_class = StrainCategorySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name']
    ordering = ['name']


class StrainViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Strain model
    Cannabis genetic strains with comprehensive filtering
    """
    queryset = Strain.objects.select_related('category').all()
    serializer_class = StrainSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_active', 'catalogue_year', 'terpene_profile']
    search_fields = ['name', 'slug', 'description', 'breeder', 'lineage']
    ordering_fields = ['name', 'catalogue_year', 'created_at']
    ordering = ['name']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return StrainListSerializer
        return StrainSerializer
