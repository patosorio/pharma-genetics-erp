"""
Cultivation ViewSets
MotherPlant, ProductionBatch, Clone, ProductionAssumption
"""

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from core.views import AuditViewSetMixin

from .models import MotherPlant, ProductionBatch, Clone, ProductionAssumption
from .serializers import (
    MotherPlantSerializer, MotherPlantListSerializer,
    ProductionBatchSerializer, CloneSerializer, CloneListSerializer,
    ProductionAssumptionSerializer
)


class MotherPlantViewSet(AuditViewSetMixin, viewsets.ModelViewSet):
    """
    ViewSet for MotherPlant model
    Mother plants used for clone production
    """
    queryset = MotherPlant.objects.select_related('strain', 'location').all()
    serializer_class = MotherPlantSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['strain', 'location', 'status', 'health_grade']
    search_fields = ['code']
    ordering_fields = ['code', 'cultivation_date', 'last_cut_date']
    ordering = ['code']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return MotherPlantListSerializer
        return MotherPlantSerializer


class ProductionBatchViewSet(AuditViewSetMixin, viewsets.ModelViewSet):
    """
    ViewSet for ProductionBatch model
    Production batches from mother plants
    """
    queryset = ProductionBatch.objects.select_related('mother_plant', 'location').all()
    serializer_class = ProductionBatchSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'location', 'mother_plant']
    search_fields = ['batch_number']
    ordering_fields = ['cutting_date', 'batch_number']
    ordering = ['-cutting_date']
    
    @action(detail=True, methods=['post'])
    def complete_batch(self, request, pk=None):
        """
        Custom action to complete a production batch
        Calculates cost per clone and updates clone unit costs
        """
        batch = self.get_object()
        try:
            batch.complete_batch()
            serializer = self.get_serializer(batch)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class CloneViewSet(AuditViewSetMixin, viewsets.ModelViewSet):
    """
    ViewSet for Clone model
    Individual clone plants with comprehensive filtering
    """
    queryset = Clone.objects.select_related(
        'production_batch', 'strain', 'location',
        'reserved_for_order', 'sold_to_order'
    ).all()
    serializer_class = CloneSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'strain', 'location', 'production_batch']
    search_fields = ['code']
    ordering_fields = ['code', 'rooting_date', 'unit_cost']
    ordering = ['code']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CloneListSerializer
        return CloneSerializer
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """
        Get available clones (status='rooted')
        """
        available_clones = self.get_queryset().filter(status='rooted')
        
        # Apply filters
        strain = request.query_params.get('strain')
        location = request.query_params.get('location')
        
        if strain:
            available_clones = available_clones.filter(strain_id=strain)
        if location:
            available_clones = available_clones.filter(location_id=location)
        
        page = self.paginate_queryset(available_clones)
        if page is not None:
            serializer = CloneListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = CloneListSerializer(available_clones, many=True)
        return Response(serializer.data)


class ProductionAssumptionViewSet(AuditViewSetMixin, viewsets.ModelViewSet):
    """
    ViewSet for ProductionAssumption model
    Production capacity assumptions and planning
    """
    queryset = ProductionAssumption.objects.select_related('location').all()
    serializer_class = ProductionAssumptionSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['location', 'version']
    ordering_fields = ['effective_date', 'version']
    ordering = ['-effective_date', 'location']
