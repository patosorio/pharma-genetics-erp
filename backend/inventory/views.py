"""
Inventory ViewSets
InventoryAlert, StockMovement, InventoryAdjustment
"""

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from core.views import AuditViewSetMixin

from .models import InventoryAlert, StockMovement, InventoryAdjustment
from .serializers import (
    InventoryAlertSerializer, StockMovementSerializer, InventoryAdjustmentSerializer
)
from .services import InventoryService


class InventoryAlertViewSet(AuditViewSetMixin, viewsets.ModelViewSet):
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


class InventoryAdjustmentViewSet(AuditViewSetMixin, viewsets.ModelViewSet):
    queryset = InventoryAdjustment.objects.select_related('clone', 'approved_by').all()
    serializer_class = InventoryAdjustmentSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['reason', 'adjustment_date', 'approved_by']
    ordering_fields = ['adjustment_date']
    ordering = ['-adjustment_date']


class InventorySummaryView(APIView):
    """
    Inventory summary endpoints backed by InventoryService.
    GET /api/v1/inventory/summary/by_strain/?location_id=X
    GET /api/v1/inventory/summary/by_location/
    GET /api/v1/inventory/summary/by_batch/?location_id=X
    GET /api/v1/inventory/summary/aging/?strain_id=X&location_id=Y
    GET /api/v1/inventory/summary/value/?strain_id=X&location_id=Y
    GET /api/v1/inventory/summary/average_cost/?strain_id=X&location_id=Y
    """
    permission_classes = [IsAuthenticated]

    def _parse_fk(self, request, param, model_class):
        pk = request.query_params.get(param)
        if not pk:
            return None, None
        try:
            return model_class.objects.get(pk=pk), None
        except model_class.DoesNotExist:
            return None, Response(
                {'detail': f'{model_class.__name__} with id={pk} not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

    def get(self, request, report_type=None):
        from core.models import Location
        from genetics.models import Strain

        if report_type == 'by_strain':
            location, err = self._parse_fk(request, 'location_id', Location)
            if err:
                return err
            data = list(InventoryService.get_inventory_summary_by_strain(location=location))
            return Response(data)

        if report_type == 'by_location':
            data = list(InventoryService.get_inventory_summary_by_location())
            return Response(data)

        if report_type == 'by_batch':
            location, err = self._parse_fk(request, 'location_id', Location)
            if err:
                return err
            data = list(InventoryService.get_inventory_summary_by_batch(location=location))
            return Response(data)

        if report_type == 'aging':
            strain, err = self._parse_fk(request, 'strain_id', Strain)
            if err:
                return err
            location, err = self._parse_fk(request, 'location_id', Location)
            if err:
                return err
            return Response(InventoryService.get_aging_report(strain=strain, location=location))

        if report_type == 'value':
            strain, err = self._parse_fk(request, 'strain_id', Strain)
            if err:
                return err
            location, err = self._parse_fk(request, 'location_id', Location)
            if err:
                return err
            return Response({'total_value': InventoryService.get_inventory_value(strain=strain, location=location)})

        if report_type == 'average_cost':
            strain, err = self._parse_fk(request, 'strain_id', Strain)
            if err:
                return err
            location, err = self._parse_fk(request, 'location_id', Location)
            if err:
                return err
            return Response({'average_cost': InventoryService.get_average_cost(strain=strain, location=location)})

        return Response({'detail': 'Unknown report type.'}, status=status.HTTP_404_NOT_FOUND)


class ReserveClonesView(APIView):
    """
    POST /api/v1/inventory/reserve_clones/
    Body: { strain_id, location_id, quantity, order_id (optional), method (fifo/lifo) }
    Atomically reserves clones for an order.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        from core.models import Location
        from genetics.models import Strain

        strain_id = request.data.get('strain_id')
        location_id = request.data.get('location_id')
        quantity = request.data.get('quantity')
        order_id = request.data.get('order_id')
        method = request.data.get('method', 'fifo')

        if not all([strain_id, location_id, quantity]):
            return Response(
                {'detail': 'strain_id, location_id, and quantity are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            strain = Strain.objects.get(pk=strain_id)
        except Strain.DoesNotExist:
            return Response({'detail': 'Strain not found.'}, status=status.HTTP_404_NOT_FOUND)
        try:
            location = Location.objects.get(pk=location_id)
        except Location.DoesNotExist:
            return Response({'detail': 'Location not found.'}, status=status.HTTP_404_NOT_FOUND)
        try:
            quantity = int(quantity)
        except (ValueError, TypeError):
            return Response({'detail': 'quantity must be an integer.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            reserved = InventoryService.reserve_clones(strain, location, quantity, order_id=order_id, method=method)
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'reserved': len(reserved),
            'clone_codes': [c.code for c in reserved],
        }, status=status.HTTP_200_OK)
