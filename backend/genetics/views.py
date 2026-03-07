"""
Genetics ViewSets
StrainCategory, Strain
"""

from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from core.views import AuditViewSetMixin

from .models import StrainCategory, Strain
from .serializers import StrainCategorySerializer, StrainSerializer, StrainListSerializer


class StrainCategoryViewSet(AuditViewSetMixin, viewsets.ModelViewSet):
    queryset = StrainCategory.objects.all()
    serializer_class = StrainCategorySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name']
    ordering = ['name']


class StrainViewSet(AuditViewSetMixin, viewsets.ModelViewSet):
    queryset = Strain.objects.select_related('category').all()
    serializer_class = StrainSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    # terpene_profile removed from filterset_fields — exact-match on comma-separated string
    # is useless; use search_fields instead
    filterset_fields = ['category', 'is_active', 'catalogue_year']
    search_fields = ['name', 'slug', 'description', 'breeder', 'lineage', 'terpene_profile']
    ordering_fields = ['name', 'catalogue_year', 'created_at']
    ordering = ['name']

    def get_serializer_class(self):
        if self.action == 'list':
            return StrainListSerializer
        return StrainSerializer
