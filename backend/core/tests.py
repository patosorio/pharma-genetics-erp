"""
Core App Tests
Tests for User, Location, Contact, Currency, TaxType, CompanySettings models and API endpoints
"""

from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from .models import User, Location, Contact, Currency, TaxType, CompanySettings


# ========================================
# MODEL TESTS
# ========================================

class UserModelTest(TestCase):
    """Tests for User model"""
    
    def setUp(self):
        self.location = Location.objects.create(
            name='Bangkok Facility',
            code='BKK',
            address='123 Test Street, Bangkok'
        )
    
    def test_create_user(self):
        """Test creating a user"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role='viewer',
            location=self.location
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.role, 'viewer')
        self.assertEqual(user.location, self.location)
        self.assertTrue(user.is_active)
    
    def test_user_str_representation(self):
        """Test user string representation"""
        user = User.objects.create_user(
            username='johnsmith',
            email='john@example.com',
            password='testpass123',
            first_name='John',
            last_name='Smith',
            role='admin'
        )
        self.assertIn('John Smith', str(user))
        self.assertIn('admin', str(user))
    
    def test_user_roles(self):
        """Test user role choices"""
        roles = ['admin', 'cultivation_manager', 'sales_rep', 'accountant', 'viewer']
        for role in roles:
            user = User.objects.create_user(
                username=f'user_{role}',
                email=f'{role}@example.com',
                password='testpass123',
                role=role
            )
            self.assertEqual(user.role, role)


class LocationModelTest(TestCase):
    """Tests for Location model"""
    
    def test_create_location(self):
        """Test creating a location"""
        location = Location.objects.create(
            name='Bangkok Facility',
            code='BKK',
            address='123 Test Street, Bangkok'
        )
        self.assertEqual(location.name, 'Bangkok Facility')
        self.assertEqual(location.code, 'BKK')
        self.assertTrue(location.is_active)
    
    def test_location_str_representation(self):
        """Test location string representation"""
        location = Location.objects.create(
            name='Panama City',
            code='PTY',
            address='456 Panama St'
        )
        self.assertEqual(str(location), 'PTY - Panama City')
    
    def test_location_code_unique(self):
        """Test that location codes are unique"""
        Location.objects.create(name='Location 1', code='LOC1', address='Address 1')
        with self.assertRaises(Exception):
            Location.objects.create(name='Location 2', code='LOC1', address='Address 2')


class ContactModelTest(TestCase):
    """Tests for Contact model"""
    
    def test_create_customer_contact(self):
        """Test creating a customer contact"""
        contact = Contact.objects.create(
            contact_type='customer',
            name='Test Customer',
            email='customer@example.com',
            phone='+66123456789',
            address='Bangkok, Thailand',
            tax_id='1234567890'
        )
        self.assertEqual(contact.contact_type, 'customer')
        self.assertEqual(contact.name, 'Test Customer')
        self.assertTrue(contact.is_active)
    
    def test_create_supplier_contact(self):
        """Test creating a supplier contact"""
        contact = Contact.objects.create(
            contact_type='supplier',
            name='Test Supplier',
            email='supplier@example.com'
        )
        self.assertEqual(contact.contact_type, 'supplier')
    
    def test_contact_str_representation(self):
        """Test contact string representation"""
        contact = Contact.objects.create(
            contact_type='customer',
            name='ABC Corp'
        )
        self.assertIn('ABC Corp', str(contact))
        self.assertIn('Customer', str(contact))


class CurrencyModelTest(TestCase):
    """Tests for Currency model"""
    
    def test_create_currency(self):
        """Test creating a currency"""
        currency = Currency.objects.create(
            code='THB',
            name='Thai Baht',
            symbol='฿',
            is_default=True
        )
        self.assertEqual(currency.code, 'THB')
        self.assertEqual(currency.symbol, '฿')
        self.assertTrue(currency.is_default)
    
    def test_currency_str_representation(self):
        """Test currency string representation"""
        currency = Currency.objects.create(
            code='USD',
            name='US Dollar',
            symbol='$'
        )
        self.assertEqual(str(currency), 'USD ($)')


class TaxTypeModelTest(TestCase):
    """Tests for TaxType model"""
    
    def test_create_tax_type(self):
        """Test creating a tax type"""
        tax = TaxType.objects.create(
            name='VAT 7%',
            rate=Decimal('7.00'),
            is_active=True
        )
        self.assertEqual(tax.name, 'VAT 7%')
        self.assertEqual(tax.rate, Decimal('7.00'))
    
    def test_tax_type_str_representation(self):
        """Test tax type string representation"""
        tax = TaxType.objects.create(name='VAT', rate=Decimal('7.00'))
        self.assertIn('VAT', str(tax))
        self.assertIn('7.00', str(tax))


class CompanySettingsModelTest(TestCase):
    """Tests for CompanySettings model (singleton)"""
    
    def setUp(self):
        self.currency = Currency.objects.create(
            code='THB',
            name='Thai Baht',
            symbol='฿'
        )
    
    def test_create_company_settings(self):
        """Test creating company settings"""
        settings = CompanySettings.objects.create(
            company_name='Test Cannabis Co.',
            default_currency=self.currency,
            break_even_price=Decimal('150.00')
        )
        self.assertEqual(settings.company_name, 'Test Cannabis Co.')
        self.assertEqual(settings.break_even_price, Decimal('150.00'))
    
    def test_company_settings_singleton(self):
        """Test that only one settings record exists"""
        CompanySettings.objects.create(
            company_name='Company 1',
            default_currency=self.currency
        )
        # Creating another should update the first
        settings2 = CompanySettings(
            company_name='Company 2',
            default_currency=self.currency
        )
        settings2.save()
        
        self.assertEqual(CompanySettings.objects.count(), 1)
        self.assertEqual(CompanySettings.objects.first().company_name, 'Company 2')
    
    def test_get_settings_class_method(self):
        """Test the get_settings class method when settings exist"""
        # Create settings first since default_currency is required
        CompanySettings.objects.create(
            company_name='Test Company',
            default_currency=self.currency
        )
        settings = CompanySettings.get_settings()
        self.assertIsNotNone(settings)
        self.assertEqual(settings.company_name, 'Test Company')


# ========================================
# API TESTS
# ========================================

class LocationAPITest(APITestCase):
    """API tests for Location endpoints"""
    
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
    
    def test_list_locations(self):
        """Test listing locations"""
        url = reverse('location-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)
    
    def test_create_location(self):
        """Test creating a location via API"""
        url = reverse('location-list')
        data = {
            'name': 'Panama City',
            'code': 'PTY',
            'address': 'Panama City, Panama'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['code'], 'PTY')
    
    def test_retrieve_location(self):
        """Test retrieving a single location"""
        url = reverse('location-detail', args=[self.location.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 'BKK')
    
    def test_update_location(self):
        """Test updating a location"""
        url = reverse('location-detail', args=[self.location.id])
        data = {'name': 'Bangkok Main Facility', 'code': 'BKK', 'address': 'Updated Address'}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Bangkok Main Facility')
    
    def test_delete_location(self):
        """Test deleting a location"""
        url = reverse('location-detail', args=[self.location.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class ContactAPITest(APITestCase):
    """API tests for Contact endpoints"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role='admin'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        self.contact = Contact.objects.create(
            contact_type='customer',
            name='Test Customer',
            email='test@example.com'
        )
    
    def test_list_contacts(self):
        """Test listing contacts"""
        url = reverse('contact-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_filter_contacts_by_type(self):
        """Test filtering contacts by type"""
        Contact.objects.create(contact_type='supplier', name='Supplier 1')
        url = reverse('contact-list')
        response = self.client.get(url, {'contact_type': 'customer'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for contact in response.data['results']:
            self.assertEqual(contact['contact_type'], 'customer')
    
    def test_search_contacts(self):
        """Test searching contacts"""
        url = reverse('contact-list')
        response = self.client.get(url, {'search': 'Test Customer'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CurrencyAPITest(APITestCase):
    """API tests for Currency endpoints"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role='admin'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_create_currency(self):
        """Test creating a currency via API"""
        url = reverse('currency-list')
        data = {
            'code': 'THB',
            'name': 'Thai Baht',
            'symbol': '฿',
            'is_default': True
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_list_currencies(self):
        """Test listing currencies"""
        Currency.objects.create(code='THB', name='Thai Baht', symbol='฿')
        Currency.objects.create(code='USD', name='US Dollar', symbol='$')
        
        url = reverse('currency-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)


class UserAPITest(APITestCase):
    """API tests for User endpoints"""
    
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username='admin',
            password='adminpass123',
            role='admin'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin_user)
    
    def test_list_users(self):
        """Test listing users"""
        url = reverse('user-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_filter_users_by_role(self):
        """Test filtering users by role"""
        User.objects.create_user(username='viewer1', password='pass', role='viewer')
        User.objects.create_user(username='sales1', password='pass', role='sales_rep')
        
        url = reverse('user-list')
        response = self.client.get(url, {'role': 'viewer'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for user in response.data['results']:
            self.assertEqual(user['role'], 'viewer')


class TaxTypeAPITest(APITestCase):
    """API tests for TaxType endpoints"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role='admin'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_create_tax_type(self):
        """Test creating a tax type"""
        url = reverse('taxtype-list')
        data = {
            'name': 'VAT 7%',
            'rate': '7.00',
            'is_active': True
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_list_tax_types(self):
        """Test listing tax types"""
        TaxType.objects.create(name='VAT 7%', rate=Decimal('7.00'))
        
        url = reverse('taxtype-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
