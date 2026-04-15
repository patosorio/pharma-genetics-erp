"""
Pricing App Tests
Tests for CostAllocationRule, PricingTier, CostSnapshot models and API endpoints
"""

from decimal import Decimal
from datetime import date, timedelta
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from core.models import User, Location
from .models import CostAllocationRule, PricingTier, CostSnapshot


# ========================================
# MODEL TESTS
# ========================================

class CostAllocationRuleModelTest(TestCase):
    """Tests for CostAllocationRule model"""
    
    def setUp(self):
        self.location = Location.objects.create(
            name='Bangkok Facility',
            code='BKK',
            address='Bangkok, Thailand'
        )
    
    def test_create_cost_allocation_rule(self):
        """Test creating a cost allocation rule"""
        rule = CostAllocationRule.objects.create(
            location=self.location,
            effective_date=date.today(),
            monthly_capacity_clones=1200,
            mother_plant_lifecycle_days=133,
            expected_clones_per_mother_lifecycle=1560,
            direct_labor_departments=['CULT'],
            overhead_labor_departments=['ADMIN', 'SALES'],
            cogs_expense_categories=['MAT', 'NUTR'],
            variable_expense_categories=['ELEC', 'WATER'],
            fixed_expense_categories=['RENT', 'INS'],
            is_active=True
        )
        self.assertEqual(rule.monthly_capacity_clones, 1200)
        self.assertEqual(rule.direct_labor_departments, ['CULT'])
        self.assertTrue(rule.is_active)
    
    def test_cost_allocation_rule_str_representation(self):
        """Test cost allocation rule string representation"""
        rule = CostAllocationRule.objects.create(
            location=self.location,
            effective_date=date.today(),
            monthly_capacity_clones=1000
        )
        self.assertIn('BKK', str(rule))
        self.assertIn('Allocation Rules', str(rule))


class PricingTierModelTest(TestCase):
    """Tests for PricingTier model"""
    
    def test_create_pricing_tier(self):
        """Test creating a pricing tier"""
        tier = PricingTier.objects.create(
            tier_name='retail',
            min_quantity=1,
            max_quantity=99,
            price_per_clone=Decimal('200.00'),
            effective_date=date.today(),
            annual_price_increase_pct=Decimal('5.00'),
            is_active=True
        )
        self.assertEqual(tier.tier_name, 'retail')
        self.assertEqual(tier.price_per_clone, Decimal('200.00'))
    
    def test_pricing_tier_str_representation(self):
        """Test pricing tier string representation"""
        tier = PricingTier.objects.create(
            tier_name='wholesale',
            min_quantity=100,
            max_quantity=499,
            price_per_clone=Decimal('175.00'),
            effective_date=date.today()
        )
        self.assertIn('Wholesale', str(tier))
        self.assertIn('175.00', str(tier))
    
    def test_pricing_tier_get_price_for_date(self):
        """Test price calculation with annual increase"""
        tier = PricingTier.objects.create(
            tier_name='retail',
            min_quantity=1,
            price_per_clone=Decimal('100.00'),
            effective_date=date(2024, 1, 1),
            annual_price_increase_pct=Decimal('10.00')
        )
        
        # Price on effective date should be base price
        price = tier.get_price_for_date(date(2024, 1, 1))
        self.assertEqual(price, Decimal('100.00'))
        
        # Price after 1 year should be 10% higher
        price_year_later = tier.get_price_for_date(date(2025, 6, 1))
        self.assertEqual(price_year_later, Decimal('110.00'))
    
    def test_pricing_tier_no_max_quantity(self):
        """Test tier without max quantity (unlimited)"""
        tier = PricingTier.objects.create(
            tier_name='bulk',
            min_quantity=500,
            max_quantity=None,
            price_per_clone=Decimal('150.00'),
            effective_date=date.today()
        )
        self.assertIsNone(tier.max_quantity)
        self.assertIn('500+', str(tier))


class CostSnapshotModelTest(TestCase):
    """Tests for CostSnapshot model"""
    
    def setUp(self):
        self.location = Location.objects.create(
            name='Bangkok Facility',
            code='BKK',
            address='Bangkok, Thailand'
        )
    
    def test_create_cost_snapshot(self):
        """Test creating a cost snapshot"""
        snapshot = CostSnapshot.objects.create(
            location=self.location,
            snapshot_date=date.today(),
            period_start=date.today() - timedelta(days=30),
            period_end=date.today(),
            total_clones_produced=1000,
            capacity_utilization_pct=Decimal('83.33'),
            total_cogs_expenses=Decimal('50000.00'),
            total_variable_opex=Decimal('20000.00'),
            total_fixed_opex=Decimal('30000.00'),
            total_direct_labor=Decimal('25000.00'),
            total_overhead_labor=Decimal('15000.00'),
            cogs_per_clone=Decimal('50.00'),
            direct_labor_per_clone=Decimal('25.00'),
            variable_base_per_clone=Decimal('95.00'),
            overhead_per_clone=Decimal('45.00'),
            total_cost_per_clone=Decimal('140.00')
        )
        self.assertEqual(snapshot.total_clones_produced, 1000)
        self.assertEqual(snapshot.total_cost_per_clone, Decimal('140.00'))
    
    def test_cost_snapshot_str_representation(self):
        """Test cost snapshot string representation"""
        snapshot = CostSnapshot.objects.create(
            location=self.location,
            snapshot_date=date.today(),
            period_start=date.today() - timedelta(days=30),
            period_end=date.today()
        )
        self.assertIn('BKK', str(snapshot))
        self.assertIn('Cost Snapshot', str(snapshot))


# ========================================
# API TESTS
# ========================================

class CostAllocationRuleAPITest(APITestCase):
    """API tests for CostAllocationRule endpoints"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role='admin'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        self.location = Location.objects.create(
            name='Bangkok Facility',
            code='BKK',
            address='Bangkok, Thailand'
        )
        self.rule = CostAllocationRule.objects.create(
            location=self.location,
            effective_date=date.today(),
            monthly_capacity_clones=1200,
            is_active=True
        )
    
    def test_list_cost_allocation_rules(self):
        """Test listing cost allocation rules"""
        url = reverse('costallocationrule-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_filter_rules_by_location(self):
        """Test filtering rules by location"""
        url = reverse('costallocationrule-list')
        response = self.client.get(url, {'location': self.location.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_filter_rules_by_active(self):
        """Test filtering rules by active status"""
        url = reverse('costallocationrule-list')
        response = self.client.get(url, {'is_active': 'true'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_retrieve_cost_allocation_rule(self):
        """Test retrieving a cost allocation rule"""
        url = reverse('costallocationrule-detail', args=[self.rule.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['location_code'], 'BKK')


class PricingTierAPITest(APITestCase):
    """API tests for PricingTier endpoints"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role='admin'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        self.tier = PricingTier.objects.create(
            tier_name='retail',
            min_quantity=1,
            max_quantity=99,
            price_per_clone=Decimal('200.00'),
            effective_date=date.today(),
            is_active=True
        )
    
    def test_list_pricing_tiers(self):
        """Test listing pricing tiers"""
        url = reverse('pricingtier-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_create_pricing_tier(self):
        """Test creating a pricing tier"""
        url = reverse('pricingtier-list')
        data = {
            'tier_name': 'wholesale',
            'min_quantity': 100,
            'max_quantity': 499,
            'price_per_clone': '175.00',
            'effective_date': str(date.today()),
            'is_active': True
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_filter_tiers_by_name(self):
        """Test filtering tiers by tier name"""
        url = reverse('pricingtier-list')
        response = self.client.get(url, {'tier_name': 'retail'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_retrieve_pricing_tier(self):
        """Test retrieving a pricing tier"""
        url = reverse('pricingtier-detail', args=[self.tier.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['tier_name_display'], 'Retail')


class CostSnapshotAPITest(APITestCase):
    """API tests for CostSnapshot endpoints"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role='admin'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        self.location = Location.objects.create(
            name='Bangkok Facility',
            code='BKK',
            address='Bangkok, Thailand'
        )
        self.snapshot = CostSnapshot.objects.create(
            location=self.location,
            snapshot_date=date.today(),
            period_start=date.today() - timedelta(days=30),
            period_end=date.today(),
            total_clones_produced=1000,
            total_cost_per_clone=Decimal('140.00')
        )
    
    def test_list_cost_snapshots(self):
        """Test listing cost snapshots"""
        url = reverse('costsnapshot-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_filter_snapshots_by_location(self):
        """Test filtering snapshots by location"""
        url = reverse('costsnapshot-list')
        response = self.client.get(url, {'location': self.location.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_retrieve_cost_snapshot(self):
        """Test retrieving a cost snapshot"""
        url = reverse('costsnapshot-detail', args=[self.snapshot.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['location_code'], 'BKK')
        self.assertEqual(response.data['total_clones_produced'], 1000)
