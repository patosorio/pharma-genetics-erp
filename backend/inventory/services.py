"""
Inventory service layer - Helper methods for inventory queries and operations
Provides FIFO/LIFO/Average cost calculations and inventory reporting
"""
from django.db.models import Avg, Sum, Count, F, Q
from django.db.models.functions import Coalesce
from cultivation.models import Clone
from genetics.models import Strain
from core.models import Location


class InventoryService:
    """
    Service class for inventory-related queries and operations
    Centralizes business logic for inventory management
    """
    
    @staticmethod
    def get_available_clones(strain=None, location=None, production_batch=None):
        """
        Get all available (rooted) clones with optional filters
        
        Args:
            strain: Strain instance or ID (optional)
            location: Location instance or ID (optional)
            production_batch: ProductionBatch instance or ID (optional)
            
        Returns:
            QuerySet of available clones
        """
        qs = Clone.objects.filter(status='rooted')
        
        if strain:
            qs = qs.filter(strain=strain)
        if location:
            qs = qs.filter(location=location)
        if production_batch:
            qs = qs.filter(production_batch=production_batch)
        
        return qs.select_related('strain', 'location', 'production_batch')
    
    @staticmethod
    def get_clones_fifo(strain, location, quantity):
        """
        Get clones using FIFO (First In, First Out) method
        Returns oldest clones first based on rooting_date
        
        Args:
            strain: Strain instance or ID
            location: Location instance or ID
            quantity: Number of clones needed
            
        Returns:
            QuerySet of clones (limited to quantity)
        """
        return Clone.objects.filter(
            status='rooted',
            strain=strain,
            location=location
        ).order_by('rooting_date', 'created_at')[:quantity]
    
    @staticmethod
    def get_clones_lifo(strain, location, quantity):
        """
        Get clones using LIFO (Last In, First Out) method
        Returns newest clones first based on rooting_date
        
        Args:
            strain: Strain instance or ID
            location: Location instance or ID
            quantity: Number of clones needed
            
        Returns:
            QuerySet of clones (limited to quantity)
        """
        return Clone.objects.filter(
            status='rooted',
            strain=strain,
            location=location
        ).order_by('-rooting_date', '-created_at')[:quantity]
    
    @staticmethod
    def get_average_cost(strain=None, location=None):
        """
        Calculate weighted average cost per clone
        
        Args:
            strain: Strain instance or ID (optional)
            location: Location instance or ID (optional)
            
        Returns:
            Decimal: Average unit cost, or 0 if no clones
        """
        qs = Clone.objects.filter(status='rooted')
        
        if strain:
            qs = qs.filter(strain=strain)
        if location:
            qs = qs.filter(location=location)
        
        result = qs.aggregate(avg_cost=Avg('unit_cost'))
        return result['avg_cost'] or 0
    
    @staticmethod
    def get_inventory_value(strain=None, location=None):
        """
        Calculate total inventory value (sum of unit_cost for all available clones)
        
        Args:
            strain: Strain instance or ID (optional)
            location: Location instance or ID (optional)
            
        Returns:
            Decimal: Total inventory value
        """
        qs = Clone.objects.filter(status='rooted')
        
        if strain:
            qs = qs.filter(strain=strain)
        if location:
            qs = qs.filter(location=location)
        
        result = qs.aggregate(total_value=Sum('unit_cost'))
        return result['total_value'] or 0
    
    @staticmethod
    def get_inventory_summary_by_strain(location=None):
        """
        Get inventory summary grouped by strain
        
        Args:
            location: Location instance or ID (optional)
            
        Returns:
            QuerySet with strain-level aggregations
        """
        qs = Clone.objects.filter(status='rooted')
        
        if location:
            qs = qs.filter(location=location)
        
        return qs.values(
            'strain__name',
            'strain__id'
        ).annotate(
            quantity=Count('id'),
            avg_cost=Avg('unit_cost'),
            total_value=Sum('unit_cost'),
            oldest_date=Min('rooting_date'),
            newest_date=Max('rooting_date')
        ).order_by('strain__name')
    
    @staticmethod
    def get_inventory_summary_by_location():
        """
        Get inventory summary grouped by location
        
        Returns:
            QuerySet with location-level aggregations
        """
        return Clone.objects.filter(
            status='rooted'
        ).values(
            'location__code',
            'location__name',
            'location__id'
        ).annotate(
            quantity=Count('id'),
            avg_cost=Avg('unit_cost'),
            total_value=Sum('unit_cost')
        ).order_by('location__code')
    
    @staticmethod
    def get_inventory_summary_by_batch(location=None):
        """
        Get inventory summary grouped by production batch
        
        Args:
            location: Location instance or ID (optional)
            
        Returns:
            QuerySet with batch-level aggregations
        """
        qs = Clone.objects.filter(status='rooted')
        
        if location:
            qs = qs.filter(location=location)
        
        return qs.values(
            'production_batch__batch_number',
            'production_batch__id',
            'strain__name'
        ).annotate(
            quantity=Count('id'),
            avg_cost=Avg('unit_cost'),
            total_value=Sum('unit_cost')
        ).order_by('-production_batch__cutting_date')
    
    @staticmethod
    def get_aging_report(strain=None, location=None):
        """
        Get inventory aging report
        Groups clones by age brackets (0-30, 31-60, 61-90, 90+ days)
        
        Args:
            strain: Strain instance or ID (optional)
            location: Location instance or ID (optional)
            
        Returns:
            Dict with age brackets and counts
        """
        from datetime import date, timedelta
        
        qs = Clone.objects.filter(status='rooted', rooting_date__isnull=False)
        
        if strain:
            qs = qs.filter(strain=strain)
        if location:
            qs = qs.filter(location=location)
        
        today = date.today()
        
        return {
            '0-30_days': qs.filter(
                rooting_date__gte=today - timedelta(days=30)
            ).count(),
            '31-60_days': qs.filter(
                rooting_date__gte=today - timedelta(days=60),
                rooting_date__lt=today - timedelta(days=30)
            ).count(),
            '61-90_days': qs.filter(
                rooting_date__gte=today - timedelta(days=90),
                rooting_date__lt=today - timedelta(days=60)
            ).count(),
            '90+_days': qs.filter(
                rooting_date__lt=today - timedelta(days=90)
            ).count(),
        }
    
    @staticmethod
    def reserve_clones(strain, location, quantity, order_id=None, method='fifo'):
        """
        Reserve clones for an order using specified method (FIFO/LIFO)
        
        Args:
            strain: Strain instance or ID
            location: Location instance or ID
            quantity: Number of clones to reserve
            order_id: Order reference (optional)
            method: 'fifo' or 'lifo' (default: 'fifo')
            
        Returns:
            List of reserved Clone instances
            
        Raises:
            ValueError: If insufficient inventory
        """
        # Check available quantity
        available = Clone.objects.filter(
            status='rooted',
            strain=strain,
            location=location
        ).count()
        
        if available < quantity:
            raise ValueError(
                f"Insufficient inventory. Available: {available}, Requested: {quantity}"
            )
        
        # Get clones based on method
        if method.lower() == 'lifo':
            clones = InventoryService.get_clones_lifo(strain, location, quantity)
        else:
            clones = InventoryService.get_clones_fifo(strain, location, quantity)
        
        # Reserve the clones
        reserved_clones = []
        for clone in clones:
            clone.status = 'reserved'
            clone.save()
            reserved_clones.append(clone)
        
        return reserved_clones
    
    @staticmethod
    def check_low_stock_alerts():
        """
        Check all active inventory alerts and return those below reorder point
        
        Returns:
            QuerySet of InventoryAlert instances that are below reorder point
        """
        from .models import InventoryAlert
        
        low_stock_alerts = []
        
        for alert in InventoryAlert.objects.filter(is_active=True):
            if alert.is_low_stock:
                low_stock_alerts.append({
                    'alert': alert,
                    'current_stock': alert.current_stock,
                    'reorder_point': alert.reorder_point,
                    'deficit': alert.stock_deficit
                })
        
        return low_stock_alerts


# Import for aging report aggregation
from django.db.models import Min, Max

