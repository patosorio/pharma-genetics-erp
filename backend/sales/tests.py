"""
Sales App Tests
Tests for Customer, PriceList, Order, OrderLine, DeliveryNote, SalesInvoice, Payment
"""

from decimal import Decimal
from datetime import date, timedelta
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from core.models import User, Location, Contact, Currency, TaxType
from genetics.models import StrainCategory, Strain
from .models import (
    Customer, PriceList, Order, OrderLine, DeliveryNote, DeliveryNoteLine,
    SalesInvoice, Payment
)


# ========================================
# MODEL TESTS
# ========================================

class CustomerModelTest(TestCase):
    """Tests for Customer model"""
    
    def setUp(self):
        self.contact = Contact.objects.create(
            contact_type='customer',
            name='Test Customer',
            email='customer@example.com',
            phone='+66123456789'
        )
    
    def test_create_customer(self):
        """Test creating a customer"""
        customer = Customer.objects.create(
            contact=self.contact,
            customer_code='CUST-001',
            tier='retail',
            credit_limit=Decimal('100000.00'),
            payment_terms_days=30
        )
        self.assertEqual(customer.customer_code, 'CUST-001')
        self.assertEqual(customer.tier, 'retail')
    
    def test_customer_str_representation(self):
        """Test customer string representation"""
        customer = Customer.objects.create(
            contact=self.contact,
            customer_code='CUST-002'
        )
        self.assertIn('CUST-002', str(customer))
        self.assertIn('Test Customer', str(customer))
    
    def test_customer_tier_choices(self):
        """Test customer tier choices"""
        tiers = ['retail', 'wholesale', 'bulk']
        for i, tier in enumerate(tiers):
            contact = Contact.objects.create(
                contact_type='customer',
                name=f'Customer {tier}'
            )
            customer = Customer.objects.create(
                contact=contact,
                customer_code=f'TIER-{i}',
                tier=tier
            )
            self.assertEqual(customer.tier, tier)


class PriceListModelTest(TestCase):
    """Tests for PriceList model"""
    
    def setUp(self):
        self.category = StrainCategory.objects.create(name='50/50 Hybrid')
        self.strain = Strain.objects.create(
            name='OG Kush',
            slug='og-kush',
            catalogue_year=2025,
            category=self.category
        )
        self.currency = Currency.objects.create(
            code='THB',
            name='Thai Baht',
            symbol='฿'
        )
    
    def test_create_price_list(self):
        """Test creating a price list entry"""
        price_list = PriceList.objects.create(
            strain=self.strain,
            tier='retail',
            price_per_clone=Decimal('200.00'),
            currency=self.currency,
            min_quantity=1,
            is_active=True
        )
        self.assertEqual(price_list.price_per_clone, Decimal('200.00'))
        self.assertEqual(price_list.tier, 'retail')
    
    def test_price_list_str_representation(self):
        """Test price list string representation"""
        price_list = PriceList.objects.create(
            strain=self.strain,
            tier='wholesale',
            price_per_clone=Decimal('175.00'),
            currency=self.currency
        )
        self.assertIn('OG Kush', str(price_list))
        self.assertIn('175.00', str(price_list))


class OrderModelTest(TestCase):
    """Tests for Order model"""
    
    def setUp(self):
        self.contact = Contact.objects.create(
            contact_type='customer',
            name='Test Customer'
        )
        self.customer = Customer.objects.create(
            contact=self.contact,
            customer_code='CUST-001'
        )
        self.location = Location.objects.create(
            name='Bangkok Facility',
            code='BKK',
            address='Bangkok, Thailand'
        )
    
    def test_create_order(self):
        """Test creating an order"""
        order = Order.objects.create(
            order_number='ORD-2025-001',
            customer=self.customer,
            location=self.location,
            order_date=date.today(),
            expected_delivery_date=date.today() + timedelta(days=7),
            status='draft',
            total_amount=Decimal('20000.00')
        )
        self.assertEqual(order.order_number, 'ORD-2025-001')
        self.assertEqual(order.status, 'draft')
    
    def test_order_str_representation(self):
        """Test order string representation"""
        order = Order.objects.create(
            order_number='ORD-2025-002',
            customer=self.customer,
            location=self.location,
            order_date=date.today(),
            expected_delivery_date=date.today() + timedelta(days=7)
        )
        self.assertIn('ORD-2025-002', str(order))
    
    def test_order_status_choices(self):
        """Test order status choices"""
        statuses = ['draft', 'confirmed', 'in_production', 'ready', 'delivered', 'cancelled']
        for i, status_val in enumerate(statuses):
            order = Order.objects.create(
                order_number=f'ORD-STATUS-{i}',
                customer=self.customer,
                location=self.location,
                order_date=date.today(),
                expected_delivery_date=date.today() + timedelta(days=7),
                status=status_val
            )
            self.assertEqual(order.status, status_val)


class OrderLineModelTest(TestCase):
    """Tests for OrderLine model"""
    
    def setUp(self):
        self.contact = Contact.objects.create(
            contact_type='customer',
            name='Test Customer'
        )
        self.customer = Customer.objects.create(
            contact=self.contact,
            customer_code='CUST-001'
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
        self.order = Order.objects.create(
            order_number='ORD-2025-001',
            customer=self.customer,
            location=self.location,
            order_date=date.today(),
            expected_delivery_date=date.today() + timedelta(days=7)
        )
    
    def test_create_order_line(self):
        """Test creating an order line"""
        line = OrderLine.objects.create(
            order=self.order,
            strain=self.strain,
            quantity=100,
            unit_price=Decimal('200.00'),
            line_total=Decimal('20000.00')
        )
        self.assertEqual(line.quantity, 100)
        self.assertEqual(line.line_total, Decimal('20000.00'))
    
    def test_order_line_auto_calculate_total(self):
        """Test line total auto-calculation"""
        line = OrderLine(
            order=self.order,
            strain=self.strain,
            quantity=50,
            unit_price=Decimal('200.00'),
            line_total=Decimal('0.00')  # Will be overwritten
        )
        line.save()
        self.assertEqual(line.line_total, Decimal('10000.00'))


class SalesInvoiceModelTest(TestCase):
    """Tests for SalesInvoice model"""
    
    def setUp(self):
        self.contact = Contact.objects.create(
            contact_type='customer',
            name='Test Customer'
        )
        self.customer = Customer.objects.create(
            contact=self.contact,
            customer_code='CUST-001'
        )
        self.location = Location.objects.create(
            name='Bangkok Facility',
            code='BKK',
            address='Bangkok, Thailand'
        )
        self.order = Order.objects.create(
            order_number='ORD-2025-001',
            customer=self.customer,
            location=self.location,
            order_date=date.today(),
            expected_delivery_date=date.today() + timedelta(days=7)
        )
    
    def test_create_sales_invoice(self):
        """Test creating a sales invoice"""
        invoice = SalesInvoice.objects.create(
            invoice_number='INV-2025-001',
            order=self.order,
            invoice_date=date.today(),
            due_date=date.today() + timedelta(days=30),
            base_amount=Decimal('10000.00'),
            tax_amount=Decimal('700.00'),
            total_amount=Decimal('10700.00'),
            status='draft'
        )
        self.assertEqual(invoice.invoice_number, 'INV-2025-001')
        self.assertEqual(invoice.total_amount, Decimal('10700.00'))
    
    def test_sales_invoice_balance_due(self):
        """Test balance due calculation"""
        invoice = SalesInvoice.objects.create(
            invoice_number='INV-2025-002',
            order=self.order,
            invoice_date=date.today(),
            due_date=date.today() + timedelta(days=30),
            total_amount=Decimal('10000.00'),
            paid_amount=Decimal('4000.00')
        )
        self.assertEqual(invoice.balance_due, Decimal('6000.00'))


class PaymentModelTest(TestCase):
    """Tests for Payment model"""
    
    def setUp(self):
        self.contact = Contact.objects.create(
            contact_type='customer',
            name='Test Customer'
        )
        self.customer = Customer.objects.create(
            contact=self.contact,
            customer_code='CUST-001'
        )
        self.location = Location.objects.create(
            name='Bangkok Facility',
            code='BKK',
            address='Bangkok, Thailand'
        )
        self.order = Order.objects.create(
            order_number='ORD-2025-001',
            customer=self.customer,
            location=self.location,
            order_date=date.today(),
            expected_delivery_date=date.today() + timedelta(days=7)
        )
        self.invoice = SalesInvoice.objects.create(
            invoice_number='INV-2025-001',
            order=self.order,
            invoice_date=date.today(),
            due_date=date.today() + timedelta(days=30),
            total_amount=Decimal('10000.00')
        )
    
    def test_create_payment(self):
        """Test creating a payment"""
        payment = Payment.objects.create(
            payment_number='PAY-2025-001',
            invoice=self.invoice,
            payment_date=date.today(),
            amount=Decimal('5000.00'),
            payment_method='bank_transfer',
            reference_number='REF123456'
        )
        self.assertEqual(payment.payment_number, 'PAY-2025-001')
        self.assertEqual(payment.amount, Decimal('5000.00'))
        self.assertEqual(payment.payment_method, 'bank_transfer')


# ========================================
# API TESTS
# ========================================

class CustomerAPITest(APITestCase):
    """API tests for Customer endpoints"""
    
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
            email='customer@example.com'
        )
        self.customer = Customer.objects.create(
            contact=self.contact,
            customer_code='CUST-001',
            tier='retail'
        )
    
    def test_list_customers(self):
        """Test listing customers"""
        url = reverse('customer-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_filter_customers_by_tier(self):
        """Test filtering customers by tier"""
        url = reverse('customer-list')
        response = self.client.get(url, {'tier': 'retail'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_retrieve_customer(self):
        """Test retrieving a customer"""
        url = reverse('customer-detail', args=[self.customer.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['customer_code'], 'CUST-001')
        self.assertEqual(response.data['contact_name'], 'Test Customer')


class OrderAPITest(APITestCase):
    """API tests for Order endpoints"""
    
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
            name='Test Customer'
        )
        self.customer = Customer.objects.create(
            contact=self.contact,
            customer_code='CUST-001'
        )
        self.location = Location.objects.create(
            name='Bangkok Facility',
            code='BKK',
            address='Bangkok, Thailand'
        )
        self.order = Order.objects.create(
            order_number='ORD-2025-001',
            customer=self.customer,
            location=self.location,
            order_date=date.today(),
            expected_delivery_date=date.today() + timedelta(days=7),
            status='confirmed',
            total_amount=Decimal('20000.00')
        )
    
    def test_list_orders(self):
        """Test listing orders"""
        url = reverse('order-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_filter_orders_by_status(self):
        """Test filtering orders by status"""
        url = reverse('order-list')
        response = self.client.get(url, {'status': 'confirmed'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_filter_orders_by_customer(self):
        """Test filtering orders by customer"""
        url = reverse('order-list')
        response = self.client.get(url, {'customer': self.customer.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_retrieve_order(self):
        """Test retrieving an order"""
        url = reverse('order-detail', args=[self.order.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['order_number'], 'ORD-2025-001')
        self.assertEqual(response.data['customer_name'], 'Test Customer')


class SalesInvoiceAPITest(APITestCase):
    """API tests for SalesInvoice endpoints"""
    
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
            name='Test Customer'
        )
        self.customer = Customer.objects.create(
            contact=self.contact,
            customer_code='CUST-001'
        )
        self.location = Location.objects.create(
            name='Bangkok Facility',
            code='BKK',
            address='Bangkok, Thailand'
        )
        self.order = Order.objects.create(
            order_number='ORD-2025-001',
            customer=self.customer,
            location=self.location,
            order_date=date.today(),
            expected_delivery_date=date.today() + timedelta(days=7)
        )
        self.invoice = SalesInvoice.objects.create(
            invoice_number='INV-2025-001',
            order=self.order,
            invoice_date=date.today(),
            due_date=date.today() + timedelta(days=30),
            total_amount=Decimal('10000.00'),
            status='sent'
        )
    
    def test_list_sales_invoices(self):
        """Test listing sales invoices"""
        url = reverse('salesinvoice-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_filter_invoices_by_status(self):
        """Test filtering invoices by status"""
        url = reverse('salesinvoice-list')
        response = self.client.get(url, {'status': 'sent'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_retrieve_sales_invoice(self):
        """Test retrieving a sales invoice"""
        url = reverse('salesinvoice-detail', args=[self.invoice.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['invoice_number'], 'INV-2025-001')
        self.assertIn('balance_due', response.data)


class PaymentAPITest(APITestCase):
    """API tests for Payment endpoints"""
    
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
            name='Test Customer'
        )
        self.customer = Customer.objects.create(
            contact=self.contact,
            customer_code='CUST-001'
        )
        self.location = Location.objects.create(
            name='Bangkok Facility',
            code='BKK',
            address='Bangkok, Thailand'
        )
        self.order = Order.objects.create(
            order_number='ORD-2025-001',
            customer=self.customer,
            location=self.location,
            order_date=date.today(),
            expected_delivery_date=date.today() + timedelta(days=7)
        )
        self.invoice = SalesInvoice.objects.create(
            invoice_number='INV-2025-001',
            order=self.order,
            invoice_date=date.today(),
            due_date=date.today() + timedelta(days=30),
            total_amount=Decimal('10000.00')
        )
        self.payment = Payment.objects.create(
            payment_number='PAY-2025-001',
            invoice=self.invoice,
            payment_date=date.today(),
            amount=Decimal('5000.00'),
            payment_method='bank_transfer'
        )
    
    def test_list_payments(self):
        """Test listing payments"""
        url = reverse('payment-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_filter_payments_by_method(self):
        """Test filtering payments by method"""
        url = reverse('payment-list')
        response = self.client.get(url, {'payment_method': 'bank_transfer'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_retrieve_payment(self):
        """Test retrieving a payment"""
        url = reverse('payment-detail', args=[self.payment.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['payment_number'], 'PAY-2025-001')
        self.assertEqual(response.data['invoice_number'], 'INV-2025-001')
