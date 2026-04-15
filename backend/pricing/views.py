"""
Pricing ViewSets
CostAllocationRule, PricingTier, CostSnapshot
"""

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from core.views import AuditViewSetMixin

from .models import CostAllocationRule, PricingTier, CostSnapshot
from .serializers import (
    CostAllocationRuleSerializer, PricingTierSerializer, CostSnapshotSerializer
)
from .services import PricingService


class CostAllocationRuleViewSet(AuditViewSetMixin, viewsets.ModelViewSet):
    queryset = CostAllocationRule.objects.select_related('location').all()
    serializer_class = CostAllocationRuleSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['location', 'is_active']
    ordering_fields = ['effective_date', 'location']
    ordering = ['-effective_date', 'location']


class PricingTierViewSet(AuditViewSetMixin, viewsets.ModelViewSet):
    queryset = PricingTier.objects.all()
    serializer_class = PricingTierSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['tier_name', 'is_active']
    ordering_fields = ['min_quantity', 'effective_date']
    ordering = ['min_quantity', 'tier_name']

    @action(detail=False, methods=['get'], url_path='for_quantity')
    def for_quantity(self, request):
        """
        GET /api/v1/pricing-tiers/for_quantity/?quantity=N
        Returns the applicable pricing tier for a given quantity.
        """
        quantity = request.query_params.get('quantity')
        if not quantity:
            return Response({'detail': 'quantity parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            quantity = int(quantity)
        except ValueError:
            return Response({'detail': 'quantity must be an integer.'}, status=status.HTTP_400_BAD_REQUEST)

        tier = PricingService.get_pricing_tier_for_quantity(quantity)
        if not tier:
            return Response({'detail': 'No matching pricing tier found for this quantity.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(PricingTierSerializer(tier).data)


class CostSnapshotViewSet(AuditViewSetMixin, viewsets.ReadOnlyModelViewSet):
    """
    CostSnapshot is read-only via plain CRUD — use the calculate action to generate one.
    """
    queryset = CostSnapshot.objects.select_related('location').all()
    serializer_class = CostSnapshotSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['location']
    ordering_fields = ['snapshot_date', 'location']
    ordering = ['-snapshot_date', 'location']

    @action(detail=False, methods=['post'], url_path='calculate')
    def calculate(self, request):
        """
        POST /api/v1/cost-snapshots/calculate/
        Body: { location_id, period_start (YYYY-MM-DD), period_end (YYYY-MM-DD) }
        Runs PricingService.create_cost_snapshot() and returns the snapshot.
        """
        location_id = request.data.get('location_id')
        period_start = request.data.get('period_start')
        period_end = request.data.get('period_end')

        if not all([location_id, period_start, period_end]):
            return Response(
                {'detail': 'location_id, period_start, and period_end are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from core.models import Location
        from datetime import date
        try:
            location = Location.objects.get(pk=location_id)
            start = date.fromisoformat(period_start)
            end = date.fromisoformat(period_end)
        except Location.DoesNotExist:
            return Response({'detail': 'Location not found.'}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        try:
            snapshot = PricingService.create_cost_snapshot(location, start, end)
        except Exception as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(CostSnapshotSerializer(snapshot).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], url_path='margin_analysis')
    def margin_analysis(self, request):
        """
        GET /api/v1/cost-snapshots/margin_analysis/?location_id=X&period_start=Y&period_end=Z&price=P
        """
        location_id = request.query_params.get('location_id')
        period_start = request.query_params.get('period_start')
        period_end = request.query_params.get('period_end')
        price = request.query_params.get('price')

        if not all([location_id, period_start, period_end, price]):
            return Response(
                {'detail': 'location_id, period_start, period_end, and price are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from core.models import Location
        from datetime import date
        from decimal import Decimal
        try:
            location = Location.objects.get(pk=location_id)
            start = date.fromisoformat(period_start)
            end = date.fromisoformat(period_end)
            price = Decimal(price)
        except Location.DoesNotExist:
            return Response({'detail': 'Location not found.'}, status=status.HTTP_404_NOT_FOUND)
        except (ValueError, Exception) as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        try:
            result = PricingService.calculate_margin_analysis(location, start, end, price)
        except Exception as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(result)

    @action(detail=False, methods=['get'], url_path='tier_margins')
    def tier_margins(self, request):
        """
        GET /api/v1/cost-snapshots/tier_margins/?location_id=X&period_start=Y&period_end=Z
        """
        location_id = request.query_params.get('location_id')
        period_start = request.query_params.get('period_start')
        period_end = request.query_params.get('period_end')

        if not all([location_id, period_start, period_end]):
            return Response(
                {'detail': 'location_id, period_start, and period_end are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from core.models import Location
        from datetime import date
        try:
            location = Location.objects.get(pk=location_id)
            start = date.fromisoformat(period_start)
            end = date.fromisoformat(period_end)
        except Location.DoesNotExist:
            return Response({'detail': 'Location not found.'}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        try:
            result = PricingService.calculate_tier_margins(location, start, end)
        except Exception as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(result)
