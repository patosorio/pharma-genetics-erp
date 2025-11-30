"""
Pricing service layer - Calculates actual costs from Purchasing and HR data
NO manual cost entry - all costs pulled from actual Expense and Payroll records
"""
from decimal import Decimal
from datetime import date, timedelta
from django.db.models import Q, Sum
from django.utils import timezone
from .models import CostAllocationRule, PricingTier, CostSnapshot
from core.models import Location


class PricingService:
    """
    Service class for pricing calculations based on ACTUAL data
    Queries Purchasing.Expense and HR.Payroll for real costs
    """
    
    @staticmethod
    def get_active_allocation_rule(location, target_date=None):
        """
        Get active cost allocation rule for a location
        
        Args:
            location: Location instance or ID
            target_date: Date to check (defaults to today)
            
        Returns:
            CostAllocationRule instance or None
        """
        if target_date is None:
            target_date = date.today()
        
        return CostAllocationRule.objects.filter(
            location=location,
            effective_date__lte=target_date,
            is_active=True
        ).filter(
            Q(end_date__isnull=True) | Q(end_date__gte=target_date)
        ).order_by('-effective_date').first()
    
    @staticmethod
    def get_actual_cogs_expenses(location, start_date, end_date):
        """
        Get actual COGS expenses from Purchasing.Expense
        
        Args:
            location: Location instance or ID
            start_date: Start date for query
            end_date: End date for query
            
        Returns:
            Decimal: Total COGS expenses
        """
        from purchasing.models import Expense
        
        allocation_rule = PricingService.get_active_allocation_rule(location, end_date)
        if not allocation_rule or not allocation_rule.cogs_expense_categories:
            return Decimal('0.00')
        
        expenses = Expense.objects.filter(
            location=location,
            expense_date__gte=start_date,
            expense_date__lte=end_date,
            category__code__in=allocation_rule.cogs_expense_categories
        ).aggregate(total=Sum('amount'))
        
        return expenses['total'] or Decimal('0.00')
    
    @staticmethod
    def get_actual_variable_opex(location, start_date, end_date):
        """
        Get actual variable OPEX from Purchasing.Expense
        
        Args:
            location: Location instance or ID
            start_date: Start date for query
            end_date: End date for query
            
        Returns:
            Decimal: Total variable OPEX
        """
        from purchasing.models import Expense
        
        allocation_rule = PricingService.get_active_allocation_rule(location, end_date)
        if not allocation_rule or not allocation_rule.variable_expense_categories:
            return Decimal('0.00')
        
        expenses = Expense.objects.filter(
            location=location,
            expense_date__gte=start_date,
            expense_date__lte=end_date,
            category__code__in=allocation_rule.variable_expense_categories
        ).aggregate(total=Sum('amount'))
        
        return expenses['total'] or Decimal('0.00')
    
    @staticmethod
    def get_actual_fixed_opex(location, start_date, end_date):
        """
        Get actual fixed OPEX from Purchasing.Expense
        
        Args:
            location: Location instance or ID
            start_date: Start date for query
            end_date: End date for query
            
        Returns:
            Decimal: Total fixed OPEX
        """
        from purchasing.models import Expense
        
        allocation_rule = PricingService.get_active_allocation_rule(location, end_date)
        if not allocation_rule or not allocation_rule.fixed_expense_categories:
            return Decimal('0.00')
        
        expenses = Expense.objects.filter(
            location=location,
            expense_date__gte=start_date,
            expense_date__lte=end_date,
            category__code__in=allocation_rule.fixed_expense_categories
        ).aggregate(total=Sum('amount'))
        
        return expenses['total'] or Decimal('0.00')
    
    @staticmethod
    def get_actual_direct_labor(location, start_date, end_date):
        """
        Get actual direct labor costs from HR.Payroll
        
        Args:
            location: Location instance or ID
            start_date: Start date for query
            end_date: End date for query
            
        Returns:
            Decimal: Total direct labor costs
        """
        from hr.models import Payroll
        
        allocation_rule = PricingService.get_active_allocation_rule(location, end_date)
        if not allocation_rule or not allocation_rule.direct_labor_departments:
            return Decimal('0.00')
        
        payrolls = Payroll.objects.filter(
            employee__location=location,
            employee__department__code__in=allocation_rule.direct_labor_departments,
            period__start_date__gte=start_date,
            period__end_date__lte=end_date
        ).aggregate(total=Sum('net_salary'))
        
        return payrolls['total'] or Decimal('0.00')
    
    @staticmethod
    def get_actual_overhead_labor(location, start_date, end_date):
        """
        Get actual overhead labor costs from HR.Payroll
        
        Args:
            location: Location instance or ID
            start_date: Start date for query
            end_date: End date for query
            
        Returns:
            Decimal: Total overhead labor costs
        """
        from hr.models import Payroll
        
        allocation_rule = PricingService.get_active_allocation_rule(location, end_date)
        if not allocation_rule or not allocation_rule.overhead_labor_departments:
            return Decimal('0.00')
        
        payrolls = Payroll.objects.filter(
            employee__location=location,
            employee__department__code__in=allocation_rule.overhead_labor_departments,
            period__start_date__gte=start_date,
            period__end_date__lte=end_date
        ).aggregate(total=Sum('net_salary'))
        
        return payrolls['total'] or Decimal('0.00')
    
    @staticmethod
    def get_actual_production_volume(location, start_date, end_date):
        """
        Get actual production volume (rooted clones) for the period
        
        Args:
            location: Location instance or ID
            start_date: Start date for query
            end_date: End date for query
            
        Returns:
            int: Number of clones rooted in this period
        """
        from cultivation.models import Clone
        
        count = Clone.objects.filter(
            location=location,
            status__in=['rooted', 'reserved', 'sold'],
            rooting_date__gte=start_date,
            rooting_date__lte=end_date
        ).count()
        
        return count
    
    @staticmethod
    def calculate_actual_cost_per_clone(location, start_date, end_date):
        """
        Calculate actual cost per clone based on real data from Purchasing and HR
        
        Args:
            location: Location instance or ID
            start_date: Start date for calculation period
            end_date: End date for calculation period
            
        Returns:
            Dict with detailed cost breakdown
        """
        # Get actual expenses
        cogs_expenses = PricingService.get_actual_cogs_expenses(location, start_date, end_date)
        variable_opex = PricingService.get_actual_variable_opex(location, start_date, end_date)
        fixed_opex = PricingService.get_actual_fixed_opex(location, start_date, end_date)
        
        # Get actual labor costs
        direct_labor = PricingService.get_actual_direct_labor(location, start_date, end_date)
        overhead_labor = PricingService.get_actual_overhead_labor(location, start_date, end_date)
        
        # Get actual production volume
        clones_produced = PricingService.get_actual_production_volume(location, start_date, end_date)
        
        # Calculate per-clone costs
        if clones_produced == 0:
            return {
                'error': 'No production in this period',
                'clones_produced': 0,
                'cogs_per_clone': Decimal('0.00'),
                'direct_labor_per_clone': Decimal('0.00'),
                'variable_base_per_clone': Decimal('0.00'),
                'overhead_per_clone': Decimal('0.00'),
                'total_cost_per_clone': Decimal('0.00')
            }
        
        cogs_per_clone = cogs_expenses / Decimal(str(clones_produced))
        direct_labor_per_clone = direct_labor / Decimal(str(clones_produced))
        variable_opex_per_clone = variable_opex / Decimal(str(clones_produced))
        
        variable_base_per_clone = cogs_per_clone + direct_labor_per_clone + variable_opex_per_clone
        
        # Overhead = fixed OPEX + overhead labor
        total_overhead = fixed_opex + overhead_labor
        overhead_per_clone = total_overhead / Decimal(str(clones_produced))
        
        total_cost_per_clone = variable_base_per_clone + overhead_per_clone
        
        # Calculate capacity utilization
        allocation_rule = PricingService.get_active_allocation_rule(location, end_date)
        capacity_utilization_pct = Decimal('0.00')
        if allocation_rule and allocation_rule.monthly_capacity_clones > 0:
            # Calculate period length in months
            period_days = (end_date - start_date).days
            period_months = Decimal(str(period_days)) / Decimal('30')
            expected_capacity = allocation_rule.monthly_capacity_clones * period_months
            if expected_capacity > 0:
                capacity_utilization_pct = (Decimal(str(clones_produced)) / expected_capacity) * Decimal('100')
        
        return {
            'location': location,
            'period_start': start_date,
            'period_end': end_date,
            'clones_produced': clones_produced,
            'capacity_utilization_pct': capacity_utilization_pct,
            
            # Totals
            'total_cogs_expenses': cogs_expenses,
            'total_variable_opex': variable_opex,
            'total_fixed_opex': fixed_opex,
            'total_direct_labor': direct_labor,
            'total_overhead_labor': overhead_labor,
            
            # Per-clone costs
            'cogs_per_clone': cogs_per_clone,
            'direct_labor_per_clone': direct_labor_per_clone,
            'variable_opex_per_clone': variable_opex_per_clone,
            'variable_base_per_clone': variable_base_per_clone,
            'overhead_per_clone': overhead_per_clone,
            'total_cost_per_clone': total_cost_per_clone
        }
    
    @staticmethod
    def create_cost_snapshot(location, start_date, end_date, snapshot_date=None):
        """
        Create a cost snapshot for historical tracking
        
        Args:
            location: Location instance or ID
            start_date: Start date for calculation period
            end_date: End date for calculation period
            snapshot_date: Date of snapshot (defaults to today)
            
        Returns:
            CostSnapshot instance
        """
        if snapshot_date is None:
            snapshot_date = date.today()
        
        cost_data = PricingService.calculate_actual_cost_per_clone(location, start_date, end_date)
        
        if 'error' in cost_data:
            raise ValueError(cost_data['error'])
        
        snapshot = CostSnapshot.objects.create(
            location=location,
            snapshot_date=snapshot_date,
            period_start=start_date,
            period_end=end_date,
            total_clones_produced=cost_data['clones_produced'],
            capacity_utilization_pct=cost_data['capacity_utilization_pct'],
            total_cogs_expenses=cost_data['total_cogs_expenses'],
            total_variable_opex=cost_data['total_variable_opex'],
            total_fixed_opex=cost_data['total_fixed_opex'],
            total_direct_labor=cost_data['total_direct_labor'],
            total_overhead_labor=cost_data['total_overhead_labor'],
            cogs_per_clone=cost_data['cogs_per_clone'],
            direct_labor_per_clone=cost_data['direct_labor_per_clone'],
            variable_base_per_clone=cost_data['variable_base_per_clone'],
            overhead_per_clone=cost_data['overhead_per_clone'],
            total_cost_per_clone=cost_data['total_cost_per_clone']
        )
        
        return snapshot
    
    @staticmethod
    def get_pricing_tier_for_quantity(quantity, target_date=None):
        """
        Get appropriate pricing tier for a given quantity
        
        Args:
            quantity: Number of clones
            target_date: Date to check (defaults to today)
            
        Returns:
            PricingTier instance or None
        """
        if target_date is None:
            target_date = date.today()
        
        return PricingTier.objects.filter(
            min_quantity__lte=quantity,
            is_active=True,
            effective_date__lte=target_date
        ).filter(
            Q(max_quantity__isnull=True) | Q(max_quantity__gte=quantity)
        ).filter(
            Q(end_date__isnull=True) | Q(end_date__gte=target_date)
        ).order_by('-min_quantity').first()
    
    @staticmethod
    def calculate_margin_analysis(location, start_date, end_date, price_per_clone):
        """
        Calculate margin analysis based on actual costs
        
        Args:
            location: Location instance or ID
            start_date: Start date for cost calculation
            end_date: End date for cost calculation
            price_per_clone: Selling price per clone
            
        Returns:
            Dict with margin analysis
        """
        cost_data = PricingService.calculate_actual_cost_per_clone(location, start_date, end_date)
        
        if 'error' in cost_data:
            return cost_data
        
        variable_base = cost_data['variable_base_per_clone']
        total_cost = cost_data['total_cost_per_clone']
        
        # Calculate margins
        margin_amount = price_per_clone - total_cost
        margin_pct = (margin_amount / price_per_clone * 100) if price_per_clone > 0 else Decimal('0.00')
        
        # Price vs variable (contribution margin)
        price_vs_variable = price_per_clone - variable_base
        contribution_margin_pct = (
            (price_vs_variable / price_per_clone * 100) 
            if price_per_clone > 0 else Decimal('0.00')
        )
        
        # Break-even calculation
        total_overhead = cost_data['total_fixed_opex'] + cost_data['total_overhead_labor']
        break_even_quantity = Decimal('0.00')
        if price_vs_variable > 0:
            break_even_quantity = total_overhead / price_vs_variable
        
        return {
            'price_per_clone': price_per_clone,
            'variable_base': variable_base,
            'overhead': cost_data['overhead_per_clone'],
            'total_cost': total_cost,
            'margin_amount': margin_amount,
            'margin_pct': margin_pct,
            'price_vs_variable': price_vs_variable,
            'contribution_margin_pct': contribution_margin_pct,
            'break_even_quantity': break_even_quantity,
            'capacity_utilization_pct': cost_data['capacity_utilization_pct']
        }
    
    @staticmethod
    def calculate_tier_margins(location, start_date, end_date, target_date=None):
        """
        Calculate margins for each pricing tier based on actual costs
        
        Args:
            location: Location instance or ID
            start_date: Start date for cost calculation
            end_date: End date for cost calculation
            target_date: Date for tier selection (defaults to today)
            
        Returns:
            List of dicts with tier margin analysis
        """
        if target_date is None:
            target_date = date.today()
        
        tiers = PricingTier.objects.filter(
            is_active=True,
            effective_date__lte=target_date
        ).filter(
            Q(end_date__isnull=True) | Q(end_date__gte=target_date)
        ).order_by('min_quantity')
        
        cost_data = PricingService.calculate_actual_cost_per_clone(location, start_date, end_date)
        
        if 'error' in cost_data:
            return []
        
        tier_results = []
        for tier in tiers:
            # Get price for target date (considering annual increases)
            price = tier.get_price_for_date(target_date)
            if price is None:
                continue
            
            margin_analysis = PricingService.calculate_margin_analysis(
                location, start_date, end_date, price
            )
            
            tier_results.append({
                'tier': tier,
                'tier_name': tier.get_tier_name_display(),
                'quantity_range': f"{tier.min_quantity}-{tier.max_quantity or '∞'}",
                'price_per_clone': price,
                'total_cost': cost_data['total_cost_per_clone'],
                'margin_amount': margin_analysis['margin_amount'],
                'margin_pct': margin_analysis['margin_pct'],
                'price_vs_variable': margin_analysis['price_vs_variable'],
                'contribution_margin_pct': margin_analysis['contribution_margin_pct']
            })
        
        return tier_results
