"""
Pricing ViewSets
CostAllocationRule, PricingTier, CostSnapshot
"""

from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend

from .models import CostAllocationRule, PricingTier, CostSnapshot
from .serializers import (
    CostAllocationRuleSerializer, PricingTierSerializer, CostSnapshotSerializer
)


class CostAllocationRuleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for CostAllocationRule model
    """
    queryset = CostAllocationRule.objects.select_related('location').all()
    serializer_class = CostAllocationRuleSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['location', 'is_active']
    ordering_fields = ['effective_date', 'location']
    ordering = ['-effective_date', 'location']


class PricingTierViewSet(viewsets.ModelViewSet):
    """
    ViewSet for PricingTier model
    """
    queryset = PricingTier.objects.all()
    serializer_class = PricingTierSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['tier_name', 'is_active']
    ordering_fields = ['min_quantity', 'effective_date']
    ordering = ['min_quantity', 'tier_name']


class CostSnapshotViewSet(viewsets.ModelViewSet):
    """
    ViewSet for CostSnapshot model
    Historical cost snapshots
    """
    queryset = CostSnapshot.objects.select_related('location').all()
    serializer_class = CostSnapshotSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['location']
    ordering_fields = ['snapshot_date', 'location']
    ordering = ['-snapshot_date', 'location']
