"""
Inventory App Tests
Tests for InventoryAlert, StockMovement, InventoryAdjustment models and API endpoints
"""

from decimal import Decimal
from datetime import date, timedelta
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from core.models import User, Location
from genetics.models import StrainCategory, Strain
from cultivation.models import MotherPlant, ProductionBatch, Clone
from .models import InventoryAlert, StockMovement, InventoryAdjustment


# ========================================
# MODEL TESTS
# ========================================

class InventoryAlertModelTest(TestCase):
    """Tests for InventoryAlert model"""
    
    def setUp(self):
        self.location = Location.objects.create(
            name='Bangkok Facility',
            code='BKK',
            address='Bangkok, Thailand'
        )
        self.category = StrainCategory.objects.create(name='50/50 Hybrid')
        self.strain = Strain.objects.create(
            name='OG Kush',
            slug='og-kush',
            catalogue_year=2025,
            category=self.category
        )
    
    def test_create_inventory_alert(self):
        """Test creating an inventory alert"""
        alert = InventoryAlert.objects.create(
            strain=self.strain,
            location=self.location,
            reorder_point=50,
            alert_email='manager@example.com',
            is_active=True
        )
        self.assertEqual(alert.reorder_point, 50)
        self.assertTrue(alert.is_active)
    
    def test_inventory_alert_str_representation(self):
        """Test inventory alert string representation"""
        alert = InventoryAlert.objects.create(
            strain=self.strain,
            location=self.location,
            reorder_point=100
        )
        self.assertIn('OG Kush', str(alert))
        self.assertIn('BKK', str(alert))
        self.assertIn('100', str(alert))
    
    def test_inventory_alert_current_stock(self):
        """Test current_stock property"""
        alert = InventoryAlert.objects.create(
            strain=self.strain,
            location=self.location,
            reorder_point=50
        )
        # No clones yet
        self.assertEqual(alert.current_stock, 0)
        
        # Create some rooted clones
        mother = MotherPlant.objects.create(
            code='BKK-OGK-001',
            strain=self.strain,
            location=self.location,
            status='Active_Production',
            health_grade='A',
            cultivation_date=date.today(),
            expected_ready_date=date.today() + timedelta(days=30),
            expected_retirement_date=date.today() + timedelta(days=365),
            clones_per_cycle_min=50,
            clones_per_cycle_max=80,
            clones_per_cycle_avg=65,
            total_cycles_year=24,
            min_possible_clones_year=1200,
            max_possible_clones_year=1920,
            avg_clones_year=1560,
            total_cuttings_taken=0
        )
        batch = ProductionBatch.objects.create(
            batch_number='BATCH-001',
            mother_plant=mother,
            location=self.location,
            cutting_date=date.today(),
            expected_rooting_date=date.today() + timedelta(days=15),
            initial_clone_count=10
        )
        for i in range(5):
            Clone.objects.create(
                code=f'CLONE-{i}',
                production_batch=batch,
                status='rooted'
            )
        
        self.assertEqual(alert.current_stock, 5)
    
    def test_inventory_alert_is_low_stock(self):
        """Test is_low_stock property"""
        alert = InventoryAlert.objects.create(
            strain=self.strain,
            location=self.location,
            reorder_point=10
        )
        # No stock = low stock
        self.assertTrue(alert.is_low_stock)
    
    def test_inventory_alert_stock_deficit(self):
        """Test stock_deficit property"""
        alert = InventoryAlert.objects.create(
            strain=self.strain,
            location=self.location,
            reorder_point=20
        )
        # Need 20, have 0 = deficit of 20
        self.assertEqual(alert.stock_deficit, 20)


class StockMovementModelTest(TestCase):
    """Tests for StockMovement model"""
    
    def setUp(self):
        self.location = Location.objects.create(
            name='Bangkok Facility',
            code='BKK',
            address='Bangkok, Thailand'
        )
        self.category = StrainCategory.objects.create(name='50/50 Hybrid')
        self.strain = Strain.objects.create(
            name='OG Kush',
            slug='og-kush',
            catalogue_year=2025,
            category=self.category
        )
        self.mother = MotherPlant.objects.create(
            code='BKK-OGK-001',
            strain=self.strain,
            location=self.location,
            status='Active_Production',
            health_grade='A',
            cultivation_date=date.today(),
            expected_ready_date=date.today() + timedelta(days=30),
            expected_retirement_date=date.today() + timedelta(days=365),
            clones_per_cycle_min=50,
            clones_per_cycle_max=80,
            clones_per_cycle_avg=65,
            total_cycles_year=24,
            min_possible_clones_year=1200,
            max_possible_clones_year=1920,
            avg_clones_year=1560,
            total_cuttings_taken=0
        )
        self.batch = ProductionBatch.objects.create(
            batch_number='BATCH-001',
            mother_plant=self.mother,
            location=self.location,
            cutting_date=date.today(),
            expected_rooting_date=date.today() + timedelta(days=15),
            initial_clone_count=10
        )
        self.clone = Clone.objects.create(
            code='CLONE-001',
            production_batch=self.batch,
            status='rooted'
        )
    
    def test_create_stock_movement(self):
        """Test creating a stock movement"""
        movement = StockMovement.objects.create(
            clone=self.clone,
            movement_type='production_complete',
            to_location=self.location,
            movement_date=date.today(),
            reference_type='batch',
            reference_id='BATCH-001',
            notes='Clone rooted successfully'
        )
        self.assertEqual(movement.movement_type, 'production_complete')
        self.assertEqual(movement.to_location, self.location)
    
    def test_stock_movement_str_representation(self):
        """Test stock movement string representation"""
        movement = StockMovement.objects.create(
            clone=self.clone,
            movement_type='sold',
            from_location=self.location,
            movement_date=date.today()
        )
        self.assertIn('sold', str(movement))
        self.assertIn('CLONE-001', str(movement))
    
    def test_stock_movement_type_choices(self):
        """Test movement type choices"""
        types = ['production_complete', 'transfer', 'reserved', 'sold', 'adjustment', 'waste']
        for i, mov_type in enumerate(types):
            clone = Clone.objects.create(
                code=f'CLONE-{i+10}',
                production_batch=self.batch,
                status='rooted'
            )
            movement = StockMovement.objects.create(
                clone=clone,
                movement_type=mov_type,
                movement_date=date.today()
            )
            self.assertEqual(movement.movement_type, mov_type)
    
    def test_stock_movement_clone_code_property(self):
        """Test clone_code property"""
        movement = StockMovement.objects.create(
            clone=self.clone,
            movement_type='reserved',
            movement_date=date.today()
        )
        self.assertEqual(movement.clone_code, 'CLONE-001')
    
    def test_stock_movement_strain_name_property(self):
        """Test strain_name property"""
        movement = StockMovement.objects.create(
            clone=self.clone,
            movement_type='reserved',
            movement_date=date.today()
        )
        self.assertEqual(movement.strain_name, 'OG Kush')


class InventoryAdjustmentModelTest(TestCase):
    """Tests for InventoryAdjustment model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='manager',
            password='testpass123',
            role='admin'
        )
        self.location = Location.objects.create(
            name='Bangkok Facility',
            code='BKK',
            address='Bangkok, Thailand'
        )
        self.category = StrainCategory.objects.create(name='50/50 Hybrid')
        self.strain = Strain.objects.create(
            name='OG Kush',
            slug='og-kush',
            catalogue_year=2025,
            category=self.category
        )
        self.mother = MotherPlant.objects.create(
            code='BKK-OGK-001',
            strain=self.strain,
            location=self.location,
            status='Active_Production',
            health_grade='A',
            cultivation_date=date.today(),
            expected_ready_date=date.today() + timedelta(days=30),
            expected_retirement_date=date.today() + timedelta(days=365),
            clones_per_cycle_min=50,
            clones_per_cycle_max=80,
            clones_per_cycle_avg=65,
            total_cycles_year=24,
            min_possible_clones_year=1200,
            max_possible_clones_year=1920,
            avg_clones_year=1560,
            total_cuttings_taken=0
        )
        self.batch = ProductionBatch.objects.create(
            batch_number='BATCH-001',
            mother_plant=self.mother,
            location=self.location,
            cutting_date=date.today(),
            expected_rooting_date=date.today() + timedelta(days=15),
            initial_clone_count=10
        )
        self.clone = Clone.objects.create(
            code='CLONE-001',
            production_batch=self.batch,
            status='rooted'
        )
    
    def test_create_inventory_adjustment(self):
        """Test creating an inventory adjustment"""
        adjustment = InventoryAdjustment.objects.create(
            clone=self.clone,
            adjustment_date=date.today(),
            reason='died',
            notes='Clone died due to disease - detailed explanation here',
            approved_by=self.user
        )
        self.assertEqual(adjustment.reason, 'died')
        self.assertEqual(adjustment.approved_by, self.user)
    
    def test_inventory_adjustment_updates_clone_status(self):
        """Test that adjustment updates clone status to died"""
        adjustment = InventoryAdjustment.objects.create(
            clone=self.clone,
            adjustment_date=date.today(),
            reason='quality_issue',
            notes='Clone has quality issues and cannot be sold',
            approved_by=self.user
        )
        self.clone.refresh_from_db()
        self.assertEqual(self.clone.status, 'died')
    
    def test_inventory_adjustment_str_representation(self):
        """Test inventory adjustment string representation"""
        adjustment = InventoryAdjustment.objects.create(
            clone=self.clone,
            adjustment_date=date.today(),
            reason='damaged',
            notes='Physical damage during handling - detailed notes',
            approved_by=self.user
        )
        self.assertIn('CLONE-001', str(adjustment))
        self.assertIn('damaged', str(adjustment))
    
    def test_inventory_adjustment_requires_notes(self):
        """Test that adjustments require detailed notes"""
        with self.assertRaises(ValueError):
            InventoryAdjustment.objects.create(
                clone=self.clone,
                adjustment_date=date.today(),
                reason='died',
                notes='Too short',  # Less than 10 chars
                approved_by=self.user
            )
    
    def test_inventory_adjustment_reason_choices(self):
        """Test adjustment reason choices"""
        reasons = ['died', 'quality_issue', 'damaged', 'contamination', 'theft', 'other']
        for i, reason in enumerate(reasons):
            clone = Clone.objects.create(
                code=f'CLONE-{i+10}',
                production_batch=self.batch,
                status='rooted'
            )
            adjustment = InventoryAdjustment.objects.create(
                clone=clone,
                adjustment_date=date.today(),
                reason=reason,
                notes=f'Detailed explanation for {reason} - at least 10 characters',
                approved_by=self.user
            )
            self.assertEqual(adjustment.reason, reason)


# ========================================
# API TESTS
# ========================================

class InventoryAlertAPITest(APITestCase):
    """API tests for InventoryAlert endpoints"""
    
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
        self.category = StrainCategory.objects.create(name='50/50 Hybrid')
        self.strain = Strain.objects.create(
            name='OG Kush',
            slug='og-kush',
            catalogue_year=2025,
            category=self.category
        )
        self.alert = InventoryAlert.objects.create(
            strain=self.strain,
            location=self.location,
            reorder_point=50,
            is_active=True
        )
    
    def test_list_inventory_alerts(self):
        """Test listing inventory alerts"""
        url = reverse('inventoryalert-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_filter_alerts_by_strain(self):
        """Test filtering alerts by strain"""
        url = reverse('inventoryalert-list')
        response = self.client.get(url, {'strain': self.strain.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_filter_alerts_by_location(self):
        """Test filtering alerts by location"""
        url = reverse('inventoryalert-list')
        response = self.client.get(url, {'location': self.location.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_retrieve_inventory_alert(self):
        """Test retrieving an inventory alert"""
        url = reverse('inventoryalert-detail', args=[self.alert.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['strain_name'], 'OG Kush')
        self.assertEqual(response.data['location_code'], 'BKK')
        self.assertIn('current_stock', response.data)
        self.assertIn('is_low_stock', response.data)
    
    def test_low_stock_action(self):
        """Test custom low_stock action"""
        url = reverse('inventoryalert-low-stock')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class StockMovementAPITest(APITestCase):
    """API tests for StockMovement endpoints (read-only)"""
    
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
        self.category = StrainCategory.objects.create(name='50/50 Hybrid')
        self.strain = Strain.objects.create(
            name='OG Kush',
            slug='og-kush',
            catalogue_year=2025,
            category=self.category
        )
        self.mother = MotherPlant.objects.create(
            code='BKK-OGK-001',
            strain=self.strain,
            location=self.location,
            status='Active_Production',
            health_grade='A',
            cultivation_date=date.today(),
            expected_ready_date=date.today() + timedelta(days=30),
            expected_retirement_date=date.today() + timedelta(days=365),
            clones_per_cycle_min=50,
            clones_per_cycle_max=80,
            clones_per_cycle_avg=65,
            total_cycles_year=24,
            min_possible_clones_year=1200,
            max_possible_clones_year=1920,
            avg_clones_year=1560,
            total_cuttings_taken=0
        )
        self.batch = ProductionBatch.objects.create(
            batch_number='BATCH-001',
            mother_plant=self.mother,
            location=self.location,
            cutting_date=date.today(),
            expected_rooting_date=date.today() + timedelta(days=15),
            initial_clone_count=10
        )
        self.clone = Clone.objects.create(
            code='CLONE-001',
            production_batch=self.batch,
            status='rooted'
        )
        self.movement = StockMovement.objects.create(
            clone=self.clone,
            movement_type='production_complete',
            to_location=self.location,
            movement_date=date.today()
        )
    
    def test_list_stock_movements(self):
        """Test listing stock movements"""
        url = reverse('stockmovement-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_filter_movements_by_type(self):
        """Test filtering movements by type"""
        url = reverse('stockmovement-list')
        response = self.client.get(url, {'movement_type': 'production_complete'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_filter_movements_by_clone(self):
        """Test filtering movements by clone"""
        url = reverse('stockmovement-list')
        response = self.client.get(url, {'clone': self.clone.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_retrieve_stock_movement(self):
        """Test retrieving a stock movement"""
        url = reverse('stockmovement-detail', args=[self.movement.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['clone_code'], 'CLONE-001')
        self.assertEqual(response.data['strain_name'], 'OG Kush')
        self.assertEqual(response.data['movement_type_display'], 'Production Complete - Clone Rooted')


class InventoryAdjustmentAPITest(APITestCase):
    """API tests for InventoryAdjustment endpoints"""
    
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
        self.category = StrainCategory.objects.create(name='50/50 Hybrid')
        self.strain = Strain.objects.create(
            name='OG Kush',
            slug='og-kush',
            catalogue_year=2025,
            category=self.category
        )
        self.mother = MotherPlant.objects.create(
            code='BKK-OGK-001',
            strain=self.strain,
            location=self.location,
            status='Active_Production',
            health_grade='A',
            cultivation_date=date.today(),
            expected_ready_date=date.today() + timedelta(days=30),
            expected_retirement_date=date.today() + timedelta(days=365),
            clones_per_cycle_min=50,
            clones_per_cycle_max=80,
            clones_per_cycle_avg=65,
            total_cycles_year=24,
            min_possible_clones_year=1200,
            max_possible_clones_year=1920,
            avg_clones_year=1560,
            total_cuttings_taken=0
        )
        self.batch = ProductionBatch.objects.create(
            batch_number='BATCH-001',
            mother_plant=self.mother,
            location=self.location,
            cutting_date=date.today(),
            expected_rooting_date=date.today() + timedelta(days=15),
            initial_clone_count=10
        )
        self.clone = Clone.objects.create(
            code='CLONE-001',
            production_batch=self.batch,
            status='rooted'
        )
        self.adjustment = InventoryAdjustment.objects.create(
            clone=self.clone,
            adjustment_date=date.today(),
            reason='died',
            notes='Clone died due to disease - detailed explanation',
            approved_by=self.user
        )
    
    def test_list_inventory_adjustments(self):
        """Test listing inventory adjustments"""
        url = reverse('inventoryadjustment-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_filter_adjustments_by_reason(self):
        """Test filtering adjustments by reason"""
        url = reverse('inventoryadjustment-list')
        response = self.client.get(url, {'reason': 'died'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_retrieve_inventory_adjustment(self):
        """Test retrieving an inventory adjustment"""
        url = reverse('inventoryadjustment-detail', args=[self.adjustment.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['clone_code'], 'CLONE-001')
        self.assertEqual(response.data['reason'], 'died')
        self.assertEqual(response.data['reason_display'], 'Clone Died')
