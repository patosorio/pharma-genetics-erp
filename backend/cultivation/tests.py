"""
Cultivation App Tests
Tests for MotherPlant, ProductionBatch, Clone, ProductionAssumption models and API endpoints
"""

from decimal import Decimal
from datetime import date, timedelta
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from core.models import User, Location
from genetics.models import StrainCategory, Strain
from .models import MotherPlant, ProductionBatch, Clone, ProductionAssumption


# ========================================
# MODEL TESTS
# ========================================

class MotherPlantModelTest(TestCase):
    """Tests for MotherPlant model"""
    
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
    
    def test_create_mother_plant(self):
        """Test creating a mother plant"""
        mother = MotherPlant.objects.create(
            code='BKK-OGK-001',
            strain=self.strain,
            location=self.location,
            status='Active_Production',
            health_grade='A',
            cultivation_date=date.today() - timedelta(days=90),
            expected_ready_date=date.today() - timedelta(days=60),
            expected_retirement_date=date.today() + timedelta(days=270),
            clones_per_cycle_min=50,
            clones_per_cycle_max=80,
            clones_per_cycle_avg=65,
            total_cycles_year=24,
            min_possible_clones_year=1200,
            max_possible_clones_year=1920,
            avg_clones_year=1560,
            total_cuttings_taken=0
        )
        self.assertEqual(mother.code, 'BKK-OGK-001')
        self.assertEqual(mother.strain, self.strain)
        self.assertEqual(mother.status, 'Active_Production')
        self.assertEqual(mother.health_grade, 'A')
    
    def test_mother_plant_str_representation(self):
        """Test mother plant string representation"""
        mother = MotherPlant.objects.create(
            code='BKK-OGK-002',
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
        self.assertIn('BKK-OGK-002', str(mother))
        self.assertIn('OG Kush', str(mother))
    
    def test_mother_plant_code_unique(self):
        """Test that mother plant codes are unique"""
        MotherPlant.objects.create(
            code='UNIQUE-001',
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
        with self.assertRaises(Exception):
            MotherPlant.objects.create(
                code='UNIQUE-001',
                strain=self.strain,
                location=self.location,
                status='Active_Production',
                health_grade='B',
                cultivation_date=date.today(),
                expected_ready_date=date.today() + timedelta(days=30),
                expected_retirement_date=date.today() + timedelta(days=365),
                clones_per_cycle_min=40,
                clones_per_cycle_max=70,
                clones_per_cycle_avg=55,
                total_cycles_year=24,
                min_possible_clones_year=960,
                max_possible_clones_year=1680,
                avg_clones_year=1320,
                total_cuttings_taken=0
            )


class ProductionBatchModelTest(TestCase):
    """Tests for ProductionBatch model"""
    
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
        self.mother_plant = MotherPlant.objects.create(
            code='BKK-OGK-001',
            strain=self.strain,
            location=self.location,
            status='Active_Production',
            health_grade='A',
            cultivation_date=date.today() - timedelta(days=90),
            expected_ready_date=date.today() - timedelta(days=60),
            expected_retirement_date=date.today() + timedelta(days=270),
            clones_per_cycle_min=50,
            clones_per_cycle_max=80,
            clones_per_cycle_avg=65,
            total_cycles_year=24,
            min_possible_clones_year=1200,
            max_possible_clones_year=1920,
            avg_clones_year=1560,
            total_cuttings_taken=0
        )
    
    def test_create_production_batch(self):
        """Test creating a production batch"""
        batch = ProductionBatch.objects.create(
            batch_number='BATCH-2025-001',
            mother_plant=self.mother_plant,
            location=self.location,
            cutting_date=date.today(),
            expected_rooting_date=date.today() + timedelta(days=15),
            initial_clone_count=60,
            status='cutting'
        )
        self.assertEqual(batch.batch_number, 'BATCH-2025-001')
        self.assertEqual(batch.initial_clone_count, 60)
        self.assertEqual(batch.status, 'cutting')
    
    def test_production_batch_str_representation(self):
        """Test batch string representation"""
        batch = ProductionBatch.objects.create(
            batch_number='BATCH-2025-002',
            mother_plant=self.mother_plant,
            location=self.location,
            cutting_date=date.today(),
            expected_rooting_date=date.today() + timedelta(days=15),
            initial_clone_count=50,
            status='rooting'
        )
        self.assertIn('BATCH-2025-002', str(batch))
        self.assertIn('rooting', str(batch))
    
    def test_production_batch_rooted_clone_count(self):
        """Test rooted clone count property"""
        batch = ProductionBatch.objects.create(
            batch_number='BATCH-2025-003',
            mother_plant=self.mother_plant,
            location=self.location,
            cutting_date=date.today(),
            expected_rooting_date=date.today() + timedelta(days=15),
            initial_clone_count=10,
            status='rooting'
        )
        
        # Create some clones with different statuses
        Clone.objects.create(code='C001', production_batch=batch, status='rooted')
        Clone.objects.create(code='C002', production_batch=batch, status='rooted')
        Clone.objects.create(code='C003', production_batch=batch, status='sold')
        Clone.objects.create(code='C004', production_batch=batch, status='died')
        
        self.assertEqual(batch.rooted_clone_count, 3)  # rooted + sold
    
    def test_production_batch_survival_rate(self):
        """Test survival rate calculation"""
        batch = ProductionBatch.objects.create(
            batch_number='BATCH-2025-004',
            mother_plant=self.mother_plant,
            location=self.location,
            cutting_date=date.today(),
            expected_rooting_date=date.today() + timedelta(days=15),
            initial_clone_count=10,
            status='rooting'
        )
        
        # Create 8 successful clones out of 10
        for i in range(8):
            Clone.objects.create(code=f'C{i:03d}', production_batch=batch, status='rooted')
        for i in range(8, 10):
            Clone.objects.create(code=f'C{i:03d}', production_batch=batch, status='died')
        
        self.assertEqual(batch.survival_rate, 80.0)


class CloneModelTest(TestCase):
    """Tests for Clone model"""
    
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
        self.mother_plant = MotherPlant.objects.create(
            code='BKK-OGK-001',
            strain=self.strain,
            location=self.location,
            status='Active_Production',
            health_grade='A',
            cultivation_date=date.today() - timedelta(days=90),
            expected_ready_date=date.today() - timedelta(days=60),
            expected_retirement_date=date.today() + timedelta(days=270),
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
            batch_number='BATCH-2025-001',
            mother_plant=self.mother_plant,
            location=self.location,
            cutting_date=date.today(),
            expected_rooting_date=date.today() + timedelta(days=15),
            initial_clone_count=60,
            status='cutting'
        )
    
    def test_create_clone(self):
        """Test creating a clone"""
        clone = Clone.objects.create(
            code='BKK-OGK-20250101-001',
            production_batch=self.batch,
            status='cutting'
        )
        self.assertEqual(clone.code, 'BKK-OGK-20250101-001')
        self.assertEqual(clone.status, 'cutting')
        # Auto-populated fields
        self.assertEqual(clone.strain, self.strain)
        self.assertEqual(clone.location, self.location)
    
    def test_clone_inherits_strain_from_batch(self):
        """Test that clone inherits strain from production batch"""
        clone = Clone.objects.create(
            code='TEST-CLONE-001',
            production_batch=self.batch,
            status='rooted'
        )
        self.assertEqual(clone.strain, self.batch.mother_plant.strain)
    
    def test_clone_inherits_location_from_batch(self):
        """Test that clone inherits location from production batch"""
        clone = Clone.objects.create(
            code='TEST-CLONE-002',
            production_batch=self.batch,
            status='rooted'
        )
        self.assertEqual(clone.location, self.batch.location)
    
    def test_clone_age_in_days(self):
        """Test clone age calculation"""
        clone = Clone.objects.create(
            code='TEST-CLONE-003',
            production_batch=self.batch,
            status='rooted',
            rooting_date=date.today() - timedelta(days=10)
        )
        self.assertEqual(clone.age_in_days, 10)
    
    def test_clone_age_in_days_no_rooting_date(self):
        """Test clone age when no rooting date set"""
        clone = Clone.objects.create(
            code='TEST-CLONE-004',
            production_batch=self.batch,
            status='cutting'
        )
        self.assertEqual(clone.age_in_days, 0)
    
    def test_clone_status_choices(self):
        """Test clone status transitions"""
        statuses = ['cutting', 'rooting', 'rooted', 'reserved', 'sold', 'died']
        for i, status_val in enumerate(statuses):
            clone = Clone.objects.create(
                code=f'STATUS-{i}',
                production_batch=self.batch,
                status=status_val
            )
            self.assertEqual(clone.status, status_val)


class ProductionAssumptionModelTest(TestCase):
    """Tests for ProductionAssumption model"""
    
    def setUp(self):
        self.location = Location.objects.create(
            name='Bangkok Facility',
            code='BKK',
            address='Bangkok, Thailand'
        )
    
    def test_create_production_assumption(self):
        """Test creating a production assumption"""
        assumption = ProductionAssumption.objects.create(
            location=self.location,
            effective_date=date.today(),
            mother_plants_count=10,
            clones_per_mother_per_cycle=60,
            cycle_duration_days=15,
            survival_rate_pct=Decimal('85.00'),
            ramp_up_months=3,
            target_capacity_utilization_pct=Decimal('80.00'),
            annual_cycles=24,
            max_monthly_capacity=1200,
            version=1
        )
        self.assertEqual(assumption.mother_plants_count, 10)
        self.assertEqual(assumption.survival_rate_pct, Decimal('85.00'))
    
    def test_production_assumption_str_representation(self):
        """Test production assumption string representation"""
        assumption = ProductionAssumption.objects.create(
            location=self.location,
            effective_date=date.today(),
            mother_plants_count=10,
            clones_per_mother_per_cycle=60,
            cycle_duration_days=15,
            survival_rate_pct=Decimal('85.00'),
            ramp_up_months=3,
            target_capacity_utilization_pct=Decimal('80.00'),
            annual_cycles=24,
            max_monthly_capacity=1200,
            version=1
        )
        self.assertIn('BKK', str(assumption))
        self.assertIn('v1', str(assumption))


# ========================================
# API TESTS
# ========================================

class MotherPlantAPITest(APITestCase):
    """API tests for MotherPlant endpoints"""
    
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
        self.mother_plant = MotherPlant.objects.create(
            code='BKK-OGK-001',
            strain=self.strain,
            location=self.location,
            status='Active_Production',
            health_grade='A',
            cultivation_date=date.today() - timedelta(days=90),
            expected_ready_date=date.today() - timedelta(days=60),
            expected_retirement_date=date.today() + timedelta(days=270),
            clones_per_cycle_min=50,
            clones_per_cycle_max=80,
            clones_per_cycle_avg=65,
            total_cycles_year=24,
            min_possible_clones_year=1200,
            max_possible_clones_year=1920,
            avg_clones_year=1560,
            total_cuttings_taken=0
        )
    
    def test_list_mother_plants(self):
        """Test listing mother plants"""
        url = reverse('motherplant-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_filter_mother_plants_by_status(self):
        """Test filtering mother plants by status"""
        url = reverse('motherplant-list')
        response = self.client.get(url, {'status': 'Active_Production'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_filter_mother_plants_by_location(self):
        """Test filtering mother plants by location"""
        url = reverse('motherplant-list')
        response = self.client.get(url, {'location': self.location.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_retrieve_mother_plant(self):
        """Test retrieving a single mother plant"""
        url = reverse('motherplant-detail', args=[self.mother_plant.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 'BKK-OGK-001')
        self.assertEqual(response.data['strain_name'], 'OG Kush')


class ProductionBatchAPITest(APITestCase):
    """API tests for ProductionBatch endpoints"""
    
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
        self.mother_plant = MotherPlant.objects.create(
            code='BKK-OGK-001',
            strain=self.strain,
            location=self.location,
            status='Active_Production',
            health_grade='A',
            cultivation_date=date.today() - timedelta(days=90),
            expected_ready_date=date.today() - timedelta(days=60),
            expected_retirement_date=date.today() + timedelta(days=270),
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
            batch_number='BATCH-2025-001',
            mother_plant=self.mother_plant,
            location=self.location,
            cutting_date=date.today(),
            expected_rooting_date=date.today() + timedelta(days=15),
            initial_clone_count=60,
            status='cutting'
        )
    
    def test_list_production_batches(self):
        """Test listing production batches"""
        url = reverse('productionbatch-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_filter_batches_by_status(self):
        """Test filtering batches by status"""
        url = reverse('productionbatch-list')
        response = self.client.get(url, {'status': 'cutting'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_retrieve_production_batch(self):
        """Test retrieving a production batch"""
        url = reverse('productionbatch-detail', args=[self.batch.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['batch_number'], 'BATCH-2025-001')
        self.assertIn('rooted_clone_count', response.data)
        self.assertIn('survival_rate', response.data)


class CloneAPITest(APITestCase):
    """API tests for Clone endpoints"""
    
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
        self.mother_plant = MotherPlant.objects.create(
            code='BKK-OGK-001',
            strain=self.strain,
            location=self.location,
            status='Active_Production',
            health_grade='A',
            cultivation_date=date.today() - timedelta(days=90),
            expected_ready_date=date.today() - timedelta(days=60),
            expected_retirement_date=date.today() + timedelta(days=270),
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
            batch_number='BATCH-2025-001',
            mother_plant=self.mother_plant,
            location=self.location,
            cutting_date=date.today(),
            expected_rooting_date=date.today() + timedelta(days=15),
            initial_clone_count=60,
            status='cutting'
        )
        self.clone = Clone.objects.create(
            code='BKK-OGK-001-001',
            production_batch=self.batch,
            status='rooted',
            rooting_date=date.today() - timedelta(days=5),
            unit_cost=Decimal('126.78')
        )
    
    def test_list_clones(self):
        """Test listing clones"""
        url = reverse('clone-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_filter_clones_by_status(self):
        """Test filtering clones by status"""
        url = reverse('clone-list')
        response = self.client.get(url, {'status': 'rooted'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_filter_clones_by_strain(self):
        """Test filtering clones by strain"""
        url = reverse('clone-list')
        response = self.client.get(url, {'strain': self.strain.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_available_clones_action(self):
        """Test custom action to get available clones"""
        url = reverse('clone-available')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should only return rooted clones
        for clone in response.data.get('results', response.data):
            self.assertEqual(clone['status'], 'rooted')
    
    def test_retrieve_clone(self):
        """Test retrieving a clone"""
        url = reverse('clone-detail', args=[self.clone.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 'BKK-OGK-001-001')
        self.assertEqual(response.data['strain_name'], 'OG Kush')
        self.assertIn('age_in_days', response.data)
