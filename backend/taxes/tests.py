"""
Taxes App Tests
Tests for TaxReport and TaxJournalEntry models and API endpoints
"""

from decimal import Decimal
from datetime import date, timedelta
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from core.models import User, Location, Contact, Currency, TaxType
from sales.models import Customer, Order, SalesInvoice
from purchasing.models import Supplier, PurchaseInvoice
from .models import TaxReport, TaxJournalEntry


# ========================================
# MODEL TESTS
# ========================================

class TaxReportModelTest(TestCase):
    """Tests for TaxReport model"""
    
    def setUp(self):
        self.currency = Currency.objects.create(
            code='THB',
            name='Thai Baht',
            symbol='฿'
        )
    
    def test_create_tax_report(self):
        """Test creating a tax report"""
        report = TaxReport.objects.create(
            report_number='TAX-2025-01',
            period_start=date(2025, 1, 1),
            period_end=date(2025, 1, 31),
            status='draft',
            currency=self.currency,
            total_vat_payable=Decimal('70000.00'),
            total_vat_recoverable=Decimal('30000.00'),
            net_vat_position=Decimal('40000.00')
        )
        self.assertEqual(report.report_number, 'TAX-2025-01')
        self.assertEqual(report.net_vat_position, Decimal('40000.00'))
    
    def test_tax_report_str_representation(self):
        """Test tax report string representation"""
        report = TaxReport.objects.create(
            report_number='TAX-2025-02',
            period_start=date(2025, 2, 1),
            period_end=date(2025, 2, 28),
            currency=self.currency
        )
        self.assertIn('TAX-2025-02', str(report))
    
    def test_tax_report_is_payable(self):
        """Test is_payable property when we owe tax"""
        report = TaxReport.objects.create(
            report_number='TAX-PAYABLE',
            period_start=date(2025, 1, 1),
            period_end=date(2025, 1, 31),
            currency=self.currency,
            net_vat_position=Decimal('10000.00')  # Positive = owe tax
        )
        self.assertTrue(report.is_payable)
        self.assertFalse(report.is_recoverable)
    
    def test_tax_report_is_recoverable(self):
        """Test is_recoverable property when we have tax credit"""
        report = TaxReport.objects.create(
            report_number='TAX-CREDIT',
            period_start=date(2025, 1, 1),
            period_end=date(2025, 1, 31),
            currency=self.currency,
            net_vat_position=Decimal('-5000.00')  # Negative = tax credit
        )
        self.assertFalse(report.is_payable)
        self.assertTrue(report.is_recoverable)
    
    def test_tax_report_status_choices(self):
        """Test tax report status choices"""
        statuses = ['draft', 'finalized', 'filed', 'paid']
        for i, status_val in enumerate(statuses):
            report = TaxReport.objects.create(
                report_number=f'TAX-STATUS-{i}',
                period_start=date(2025, 1, 1),
                period_end=date(2025, 1, 31),
                currency=self.currency,
                status=status_val
            )
            self.assertEqual(report.status, status_val)


class TaxJournalEntryModelTest(TestCase):
    """Tests for TaxJournalEntry model"""
    
    def setUp(self):
        self.currency = Currency.objects.create(
            code='THB',
            name='Thai Baht',
            symbol='฿'
        )
        self.tax_type = TaxType.objects.create(
            name='VAT 7%',
            rate=Decimal('7.00')
        )
        self.tax_report = TaxReport.objects.create(
            report_number='TAX-2025-01',
            period_start=date(2025, 1, 1),
            period_end=date(2025, 1, 31),
            currency=self.currency
        )
        
        # Create sales invoice for payable entries
        self.contact = Contact.objects.create(
            contact_type='customer',
            name='Test Customer'
        )
        self.customer = Customer.objects.create(
            contact=self.contact,
            customer_code='CUST-001'
        )
        self.location = Location.objects.create(
            name='Bangkok',
            code='BKK',
            address='Bangkok'
        )
        self.order = Order.objects.create(
            order_number='ORD-001',
            customer=self.customer,
            location=self.location,
            order_date=date.today(),
            expected_delivery_date=date.today() + timedelta(days=7)
        )
        self.sales_invoice = SalesInvoice.objects.create(
            invoice_number='INV-001',
            order=self.order,
            invoice_date=date.today(),
            due_date=date.today() + timedelta(days=30),
            base_amount=Decimal('10000.00'),
            tax_amount=Decimal('700.00'),
            total_amount=Decimal('10700.00')
        )
        
        # Create purchase invoice for recoverable entries
        self.supplier_contact = Contact.objects.create(
            contact_type='supplier',
            name='Test Supplier'
        )
        self.supplier = Supplier.objects.create(
            contact=self.supplier_contact,
            supplier_code='SUP-001'
        )
        self.purchase_invoice = PurchaseInvoice.objects.create(
            invoice_number='PINV-001',
            supplier=self.supplier,
            invoice_date=date.today(),
            due_date=date.today() + timedelta(days=30),
            base_amount=Decimal('5000.00'),
            tax_amount=Decimal('350.00'),
            total_amount=Decimal('5350.00'),
            currency=self.currency
        )
    
    def test_create_payable_journal_entry(self):
        """Test creating a VAT payable journal entry"""
        entry = TaxJournalEntry.objects.create(
            tax_report=self.tax_report,
            entry_type='payable',
            sales_invoice=self.sales_invoice,
            tax_type=self.tax_type,
            base_amount=Decimal('10000.00'),
            tax_amount=Decimal('700.00'),
            entry_date=date.today()
        )
        self.assertEqual(entry.entry_type, 'payable')
        self.assertEqual(entry.tax_amount, Decimal('700.00'))
    
    def test_create_recoverable_journal_entry(self):
        """Test creating a VAT recoverable journal entry"""
        entry = TaxJournalEntry.objects.create(
            tax_report=self.tax_report,
            entry_type='recoverable',
            purchase_invoice=self.purchase_invoice,
            tax_type=self.tax_type,
            base_amount=Decimal('5000.00'),
            tax_amount=Decimal('350.00'),
            entry_date=date.today()
        )
        self.assertEqual(entry.entry_type, 'recoverable')
        self.assertEqual(entry.tax_amount, Decimal('350.00'))
    
    def test_journal_entry_str_representation_sales(self):
        """Test journal entry string representation for sales"""
        entry = TaxJournalEntry.objects.create(
            tax_report=self.tax_report,
            entry_type='payable',
            sales_invoice=self.sales_invoice,
            tax_type=self.tax_type,
            base_amount=Decimal('10000.00'),
            tax_amount=Decimal('700.00'),
            entry_date=date.today()
        )
        self.assertIn('payable', str(entry))
        self.assertIn('INV-001', str(entry))
    
    def test_journal_entry_str_representation_purchase(self):
        """Test journal entry string representation for purchases"""
        entry = TaxJournalEntry.objects.create(
            tax_report=self.tax_report,
            entry_type='recoverable',
            purchase_invoice=self.purchase_invoice,
            tax_type=self.tax_type,
            base_amount=Decimal('5000.00'),
            tax_amount=Decimal('350.00'),
            entry_date=date.today()
        )
        self.assertIn('recoverable', str(entry))
        self.assertIn('PINV-001', str(entry))


# ========================================
# API TESTS
# ========================================

class TaxReportAPITest(APITestCase):
    """API tests for TaxReport endpoints"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role='admin'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        self.currency = Currency.objects.create(
            code='THB',
            name='Thai Baht',
            symbol='฿'
        )
        self.tax_report = TaxReport.objects.create(
            report_number='TAX-2025-01',
            period_start=date(2025, 1, 1),
            period_end=date(2025, 1, 31),
            currency=self.currency,
            status='draft',
            total_vat_payable=Decimal('70000.00'),
            total_vat_recoverable=Decimal('30000.00'),
            net_vat_position=Decimal('40000.00')
        )
    
    def test_list_tax_reports(self):
        """Test listing tax reports"""
        url = reverse('taxreport-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_filter_reports_by_status(self):
        """Test filtering reports by status"""
        url = reverse('taxreport-list')
        response = self.client.get(url, {'status': 'draft'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_retrieve_tax_report(self):
        """Test retrieving a tax report"""
        url = reverse('taxreport-detail', args=[self.tax_report.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['report_number'], 'TAX-2025-01')
        self.assertEqual(response.data['currency_code'], 'THB')
        self.assertTrue(response.data['is_payable'])
        self.assertFalse(response.data['is_recoverable'])
    
    def test_create_tax_report(self):
        """Test creating a tax report via API"""
        url = reverse('taxreport-list')
        data = {
            'report_number': 'TAX-2025-02',
            'period_start': '2025-02-01',
            'period_end': '2025-02-28',
            'currency': self.currency.id,
            'status': 'draft'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class TaxJournalEntryAPITest(APITestCase):
    """API tests for TaxJournalEntry endpoints"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role='admin'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        self.currency = Currency.objects.create(
            code='THB',
            name='Thai Baht',
            symbol='฿'
        )
        self.tax_type = TaxType.objects.create(
            name='VAT 7%',
            rate=Decimal('7.00')
        )
        self.tax_report = TaxReport.objects.create(
            report_number='TAX-2025-01',
            period_start=date(2025, 1, 1),
            period_end=date(2025, 1, 31),
            currency=self.currency
        )
        
        # Create sales invoice
        self.contact = Contact.objects.create(
            contact_type='customer',
            name='Test Customer'
        )
        self.customer = Customer.objects.create(
            contact=self.contact,
            customer_code='CUST-001'
        )
        self.location = Location.objects.create(
            name='Bangkok',
            code='BKK',
            address='Bangkok'
        )
        self.order = Order.objects.create(
            order_number='ORD-001',
            customer=self.customer,
            location=self.location,
            order_date=date.today(),
            expected_delivery_date=date.today() + timedelta(days=7)
        )
        self.sales_invoice = SalesInvoice.objects.create(
            invoice_number='INV-001',
            order=self.order,
            invoice_date=date.today(),
            due_date=date.today() + timedelta(days=30),
            total_amount=Decimal('10700.00')
        )
        
        self.journal_entry = TaxJournalEntry.objects.create(
            tax_report=self.tax_report,
            entry_type='payable',
            sales_invoice=self.sales_invoice,
            tax_type=self.tax_type,
            base_amount=Decimal('10000.00'),
            tax_amount=Decimal('700.00'),
            entry_date=date.today()
        )
    
    def test_list_journal_entries(self):
        """Test listing journal entries"""
        url = reverse('taxjournalentry-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_filter_entries_by_type(self):
        """Test filtering entries by type"""
        url = reverse('taxjournalentry-list')
        response = self.client.get(url, {'entry_type': 'payable'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_filter_entries_by_report(self):
        """Test filtering entries by report"""
        url = reverse('taxjournalentry-list')
        response = self.client.get(url, {'tax_report': self.tax_report.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_retrieve_journal_entry(self):
        """Test retrieving a journal entry"""
        url = reverse('taxjournalentry-detail', args=[self.journal_entry.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['entry_type'], 'payable')
        self.assertEqual(response.data['entry_type_display'], 'VAT Payable (Sales)')
        self.assertEqual(response.data['tax_type_name'], 'VAT 7%')
