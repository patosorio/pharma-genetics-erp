"""
Inventory ViewSets
InventoryAlert, StockMovement, InventoryAdjustment
"""

from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import InventoryAlert, StockMovement, InventoryAdjustment
from .serializers import (
    InventoryAlertSerializer, StockMovementSerializer, InventoryAdjustmentSerializer
)


class InventoryAlertViewSet(viewsets.ModelViewSet):
    """
    ViewSet for InventoryAlert model
    Reorder point alerts for low stock
    """
    queryset = InventoryAlert.objects.select_related('strain', 'location').all()
    serializer_class = InventoryAlertSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['strain', 'location', 'is_active']
    ordering_fields = ['reorder_point']
    ordering = ['strain', 'location']
    
    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """
        Get all alerts with low stock
        """
        alerts = self.get_queryset().filter(is_active=True)
        low_stock_alerts = [alert for alert in alerts if alert.is_low_stock]
        
        serializer = self.get_serializer(low_stock_alerts, many=True)
        return Response(serializer.data)


class StockMovementViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for StockMovement model (read-only)
    Audit trail for inventory movements
    """
    queryset = StockMovement.objects.select_related(
        'clone', 'from_location', 'to_location', 'performed_by'
    ).all()
    serializer_class = StockMovementSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['movement_type', 'clone', 'from_location', 'to_location', 'movement_date']
    ordering_fields = ['movement_date', 'created_at']
    ordering = ['-movement_date', '-created_at']


class InventoryAdjustmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for InventoryAdjustment model
    Manual inventory adjustments
    """
    queryset = InventoryAdjustment.objects.select_related(
        'clone', 'approved_by'
    ).all()
    serializer_class = InventoryAdjustmentSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['reason', 'adjustment_date', 'approved_by']
    ordering_fields = ['adjustment_date']
    ordering = ['-adjustment_date']
