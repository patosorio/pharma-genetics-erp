"""
Genetics App Tests
Tests for StrainCategory and Strain models and API endpoints
"""

from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from core.models import User
from .models import StrainCategory, Strain


# ========================================
# MODEL TESTS
# ========================================

class StrainCategoryModelTest(TestCase):
    """Tests for StrainCategory model"""
    
    def test_create_strain_category(self):
        """Test creating a strain category"""
        category = StrainCategory.objects.create(
            name='50/50 Hybrid',
            description='Balanced hybrid strain'
        )
        self.assertEqual(category.name, '50/50 Hybrid')
        self.assertEqual(category.description, 'Balanced hybrid strain')
    
    def test_strain_category_str_representation(self):
        """Test strain category string representation"""
        category = StrainCategory.objects.create(name='70/30 Indica')
        self.assertEqual(str(category), '70/30 Indica')
    
    def test_strain_category_name_unique(self):
        """Test that category names are unique"""
        StrainCategory.objects.create(name='Hybrid')
        with self.assertRaises(Exception):
            StrainCategory.objects.create(name='Hybrid')


class StrainModelTest(TestCase):
    """Tests for Strain model"""
    
    def setUp(self):
        self.category = StrainCategory.objects.create(
            name='50/50 Hybrid',
            description='Balanced hybrid'
        )
    
    def test_create_strain(self):
        """Test creating a strain"""
        strain = Strain.objects.create(
            name='OG Kush',
            slug='og-kush',
            catalogue_year=2025,
            category=self.category,
            description='Classic OG strain',
            thc_percentage=Decimal('22.50'),
            cbd_percentage=Decimal('0.50'),
            terpene_profile='earthy',
            breeder='Unknown Breeder',
            is_active=True
        )
        self.assertEqual(strain.name, 'OG Kush')
        self.assertEqual(strain.slug, 'og-kush')
        self.assertEqual(strain.thc_percentage, Decimal('22.50'))
        self.assertEqual(strain.terpene_profile, 'earthy')
        self.assertTrue(strain.is_active)
    
    def test_strain_str_representation(self):
        """Test strain string representation"""
        strain = Strain.objects.create(
            name='Blue Dream',
            slug='blue-dream',
            catalogue_year=2025,
            category=self.category
        )
        self.assertIn('Blue Dream', str(strain))
        self.assertIn('50/50 Hybrid', str(strain))
    
    def test_strain_slug_unique(self):
        """Test that strain slugs are unique"""
        Strain.objects.create(
            name='Strain 1',
            slug='strain-slug',
            catalogue_year=2025,
            category=self.category
        )
        with self.assertRaises(Exception):
            Strain.objects.create(
                name='Strain 2',
                slug='strain-slug',
                catalogue_year=2025,
                category=self.category
            )
    
    def test_strain_catalogue_year_validation(self):
        """Test catalogue year validators"""
        # Valid year
        strain = Strain.objects.create(
            name='Valid Strain',
            slug='valid-strain',
            catalogue_year=2025,
            category=self.category
        )
        self.assertEqual(strain.catalogue_year, 2025)
    
    def test_strain_terpene_choices(self):
        """Test terpene profile choices"""
        terpenes = ['aromatic', 'citrus', 'earthy', 'floral', 'herbal', 'pine']
        for i, terpene in enumerate(terpenes):
            strain = Strain.objects.create(
                name=f'Strain {terpene}',
                slug=f'strain-{terpene}',
                catalogue_year=2025,
                category=self.category,
                terpene_profile=terpene
            )
            self.assertEqual(strain.terpene_profile, terpene)


# ========================================
# API TESTS
# ========================================

class StrainCategoryAPITest(APITestCase):
    """API tests for StrainCategory endpoints"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role='admin'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        self.category = StrainCategory.objects.create(
            name='50/50 Hybrid',
            description='Balanced hybrid'
        )
    
    def test_list_strain_categories(self):
        """Test listing strain categories"""
        url = reverse('straincategory-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)
    
    def test_create_strain_category(self):
        """Test creating a strain category via API"""
        url = reverse('straincategory-list')
        data = {
            'name': '70/30 Indica',
            'description': 'Indica dominant hybrid'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], '70/30 Indica')
    
    def test_retrieve_strain_category(self):
        """Test retrieving a single strain category"""
        url = reverse('straincategory-detail', args=[self.category.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], '50/50 Hybrid')
    
    def test_update_strain_category(self):
        """Test updating a strain category"""
        url = reverse('straincategory-detail', args=[self.category.id])
        data = {'name': '50/50 Hybrid Updated', 'description': 'Updated description'}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], '50/50 Hybrid Updated')
    
    def test_delete_strain_category(self):
        """Test deleting a strain category"""
        category_to_delete = StrainCategory.objects.create(name='To Delete')
        url = reverse('straincategory-detail', args=[category_to_delete.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class StrainAPITest(APITestCase):
    """API tests for Strain endpoints"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role='admin'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        self.category = StrainCategory.objects.create(
            name='50/50 Hybrid',
            description='Balanced hybrid'
        )
        
        self.strain = Strain.objects.create(
            name='OG Kush',
            slug='og-kush',
            catalogue_year=2025,
            category=self.category,
            thc_percentage=Decimal('22.50'),
            terpene_profile='earthy',
            is_active=True
        )
    
    def test_list_strains(self):
        """Test listing strains"""
        url = reverse('strain-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)
    
    def test_list_strains_returns_lightweight_serializer(self):
        """Test that list view returns lightweight fields"""
        url = reverse('strain-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # List serializer should have limited fields
        strain_data = response.data['results'][0]
        self.assertIn('name', strain_data)
        self.assertIn('slug', strain_data)
        self.assertIn('category_name', strain_data)
    
    def test_create_strain(self):
        """Test creating a strain via API"""
        url = reverse('strain-list')
        data = {
            'name': 'Blue Dream',
            'slug': 'blue-dream',
            'catalogue_year': 2025,
            'category': self.category.id,
            'thc_percentage': '20.00',
            'terpene_profile': 'citrus',
            'is_active': True
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Blue Dream')
    
    def test_retrieve_strain(self):
        """Test retrieving a single strain"""
        url = reverse('strain-detail', args=[self.strain.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'OG Kush')
        self.assertEqual(response.data['category_name'], '50/50 Hybrid')
    
    def test_filter_strains_by_category(self):
        """Test filtering strains by category"""
        url = reverse('strain-list')
        response = self.client.get(url, {'category': self.category.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for strain in response.data['results']:
            self.assertEqual(strain['category'], self.category.id)
    
    def test_filter_strains_by_active_status(self):
        """Test filtering strains by active status"""
        Strain.objects.create(
            name='Inactive Strain',
            slug='inactive-strain',
            catalogue_year=2025,
            category=self.category,
            is_active=False
        )
        
        url = reverse('strain-list')
        response = self.client.get(url, {'is_active': 'true'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for strain in response.data['results']:
            self.assertTrue(strain['is_active'])
    
    def test_filter_strains_by_catalogue_year(self):
        """Test filtering strains by catalogue year"""
        Strain.objects.create(
            name='2024 Strain',
            slug='2024-strain',
            catalogue_year=2024,
            category=self.category
        )
        
        url = reverse('strain-list')
        response = self.client.get(url, {'catalogue_year': 2025})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for strain in response.data['results']:
            self.assertEqual(strain['catalogue_year'], 2025)
    
    def test_filter_strains_by_terpene_profile(self):
        """Test filtering strains by terpene profile"""
        url = reverse('strain-list')
        response = self.client.get(url, {'terpene_profile': 'earthy'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_search_strains(self):
        """Test searching strains by name"""
        url = reverse('strain-list')
        response = self.client.get(url, {'search': 'OG'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)
    
    def test_update_strain(self):
        """Test updating a strain"""
        url = reverse('strain-detail', args=[self.strain.id])
        data = {
            'name': 'OG Kush Premium',
            'slug': 'og-kush',
            'catalogue_year': 2025,
            'category': self.category.id,
            'thc_percentage': '25.00'
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'OG Kush Premium')
    
    def test_delete_strain(self):
        """Test deleting a strain"""
        strain_to_delete = Strain.objects.create(
            name='To Delete',
            slug='to-delete',
            catalogue_year=2025,
            category=self.category
        )
        url = reverse('strain-detail', args=[strain_to_delete.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    
    def test_strain_ordering(self):
        """Test strain ordering"""
        Strain.objects.create(
            name='AAA Strain',
            slug='aaa-strain',
            catalogue_year=2025,
            category=self.category
        )
        
        url = reverse('strain-list')
        response = self.client.get(url, {'ordering': 'name'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        names = [s['name'] for s in response.data['results']]
        self.assertEqual(names, sorted(names))
