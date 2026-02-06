"""
Purchasing App Tests
Tests for Supplier, ExpenseCategory, PurchaseOrder, PurchaseOrderItem, Expense, PurchaseInvoice
"""

from decimal import Decimal
from datetime import date, timedelta
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from core.models import User, Location, Contact, Currency, TaxType
from .models import (
    Supplier, ExpenseCategory, PurchaseOrder, PurchaseOrderItem,
    Expense, PurchaseInvoice
)


# ========================================
# MODEL TESTS
# ========================================

class SupplierModelTest(TestCase):
    """Tests for Supplier model"""
    
    def setUp(self):
        self.contact = Contact.objects.create(
            contact_type='supplier',
            name='Test Supplier Co.',
            email='supplier@example.com',
            phone='+66123456789'
        )
    
    def test_create_supplier(self):
        """Test creating a supplier"""
        supplier = Supplier.objects.create(
            contact=self.contact,
            supplier_code='SUP-001',
            payment_terms_days=30
        )
        self.assertEqual(supplier.supplier_code, 'SUP-001')
        self.assertEqual(supplier.payment_terms_days, 30)
    
    def test_supplier_str_representation(self):
        """Test supplier string representation"""
        supplier = Supplier.objects.create(
            contact=self.contact,
            supplier_code='SUP-002'
        )
        self.assertIn('SUP-002', str(supplier))
        self.assertIn('Test Supplier Co.', str(supplier))
    
    def test_supplier_code_unique(self):
        """Test that supplier codes are unique"""
        Supplier.objects.create(
            contact=self.contact,
            supplier_code='UNIQUE-SUP'
        )
        contact2 = Contact.objects.create(
            contact_type='supplier',
            name='Another Supplier'
        )
        with self.assertRaises(Exception):
            Supplier.objects.create(
                contact=contact2,
                supplier_code='UNIQUE-SUP'
            )


class ExpenseCategoryModelTest(TestCase):
    """Tests for ExpenseCategory model"""
    
    def test_create_expense_category(self):
        """Test creating an expense category"""
        category = ExpenseCategory.objects.create(
            name='Materials',
            code='MAT',
            category_type='cogs',
            description='Raw materials for production'
        )
        self.assertEqual(category.name, 'Materials')
        self.assertEqual(category.category_type, 'cogs')
    
    def test_expense_category_str_representation(self):
        """Test expense category string representation"""
        category = ExpenseCategory.objects.create(
            name='Rent',
            code='RENT',
            category_type='opex'
        )
        self.assertEqual(str(category), 'RENT - Rent')
    
    def test_expense_category_types(self):
        """Test expense category type choices"""
        types = ['opex', 'capex', 'cogs']
        for i, cat_type in enumerate(types):
            category = ExpenseCategory.objects.create(
                name=f'Category {i}',
                code=f'CAT{i}',
                category_type=cat_type
            )
            self.assertEqual(category.category_type, cat_type)


class PurchaseOrderModelTest(TestCase):
    """Tests for PurchaseOrder model"""
    
    def setUp(self):
        self.contact = Contact.objects.create(
            contact_type='supplier',
            name='Test Supplier'
        )
        self.supplier = Supplier.objects.create(
            contact=self.contact,
            supplier_code='SUP-001'
        )
        self.location = Location.objects.create(
            name='Bangkok Facility',
            code='BKK',
            address='Bangkok, Thailand'
        )
        self.currency = Currency.objects.create(
            code='THB',
            name='Thai Baht',
            symbol='฿'
        )
        self.tax_type = TaxType.objects.create(
            name='VAT 7%',
            rate=Decimal('7.00')
        )
    
    def test_create_purchase_order(self):
        """Test creating a purchase order"""
        po = PurchaseOrder.objects.create(
            po_number='PO-2025-001',
            supplier=self.supplier,
            location=self.location,
            order_date=date.today(),
            expected_delivery_date=date.today() + timedelta(days=7),
            status='draft',
            currency=self.currency,
            tax_type=self.tax_type,
            base_amount=Decimal('10000.00'),
            tax_amount=Decimal('700.00'),
            total_amount=Decimal('10700.00')
        )
        self.assertEqual(po.po_number, 'PO-2025-001')
        self.assertEqual(po.status, 'draft')
        self.assertEqual(po.total_amount, Decimal('10700.00'))
    
    def test_purchase_order_str_representation(self):
        """Test PO string representation"""
        po = PurchaseOrder.objects.create(
            po_number='PO-2025-002',
            supplier=self.supplier,
            location=self.location,
            order_date=date.today(),
            expected_delivery_date=date.today() + timedelta(days=7),
            currency=self.currency
        )
        self.assertIn('PO-2025-002', str(po))


class PurchaseOrderItemModelTest(TestCase):
    """Tests for PurchaseOrderItem model"""
    
    def setUp(self):
        self.contact = Contact.objects.create(
            contact_type='supplier',
            name='Test Supplier'
        )
        self.supplier = Supplier.objects.create(
            contact=self.contact,
            supplier_code='SUP-001'
        )
        self.location = Location.objects.create(
            name='Bangkok Facility',
            code='BKK',
            address='Bangkok, Thailand'
        )
        self.currency = Currency.objects.create(
            code='THB',
            name='Thai Baht',
            symbol='฿'
        )
        self.po = PurchaseOrder.objects.create(
            po_number='PO-2025-001',
            supplier=self.supplier,
            location=self.location,
            order_date=date.today(),
            expected_delivery_date=date.today() + timedelta(days=7),
            currency=self.currency
        )
        self.category = ExpenseCategory.objects.create(
            name='Materials',
            code='MAT',
            category_type='cogs'
        )
    
    def test_create_purchase_order_item(self):
        """Test creating a PO item"""
        item = PurchaseOrderItem.objects.create(
            purchase_order=self.po,
            expense_category=self.category,
            description='Nutrient Solution A',
            quantity=Decimal('100.00'),
            unit_price=Decimal('50.00'),
            line_total=Decimal('5000.00')
        )
        self.assertEqual(item.description, 'Nutrient Solution A')
        self.assertEqual(item.line_total, Decimal('5000.00'))
    
    def test_purchase_order_item_auto_calculate_total(self):
        """Test line total auto-calculation"""
        item = PurchaseOrderItem(
            purchase_order=self.po,
            expense_category=self.category,
            description='Test Item',
            quantity=Decimal('10.00'),
            unit_price=Decimal('25.00'),
            line_total=Decimal('0.00')  # Will be overwritten
        )
        item.save()
        self.assertEqual(item.line_total, Decimal('250.00'))


class ExpenseModelTest(TestCase):
    """Tests for Expense model"""
    
    def setUp(self):
        self.location = Location.objects.create(
            name='Bangkok Facility',
            code='BKK',
            address='Bangkok, Thailand'
        )
        self.currency = Currency.objects.create(
            code='THB',
            name='Thai Baht',
            symbol='฿'
        )
        self.category = ExpenseCategory.objects.create(
            name='Utilities',
            code='UTIL',
            category_type='opex'
        )
    
    def test_create_expense(self):
        """Test creating an expense"""
        expense = Expense.objects.create(
            expense_number='EXP-2025-001',
            category=self.category,
            location=self.location,
            expense_date=date.today(),
            amount=Decimal('5000.00'),
            currency=self.currency,
            description='Monthly electricity bill'
        )
        self.assertEqual(expense.expense_number, 'EXP-2025-001')
        self.assertEqual(expense.amount, Decimal('5000.00'))
    
    def test_expense_str_representation(self):
        """Test expense string representation"""
        expense = Expense.objects.create(
            expense_number='EXP-2025-002',
            category=self.category,
            location=self.location,
            expense_date=date.today(),
            amount=Decimal('3000.00'),
            currency=self.currency,
            description='Water bill'
        )
        self.assertIn('EXP-2025-002', str(expense))
        self.assertIn('Utilities', str(expense))


class PurchaseInvoiceModelTest(TestCase):
    """Tests for PurchaseInvoice model"""
    
    def setUp(self):
        self.contact = Contact.objects.create(
            contact_type='supplier',
            name='Test Supplier'
        )
        self.supplier = Supplier.objects.create(
            contact=self.contact,
            supplier_code='SUP-001'
        )
        self.currency = Currency.objects.create(
            code='THB',
            name='Thai Baht',
            symbol='฿'
        )
    
    def test_create_purchase_invoice(self):
        """Test creating a purchase invoice"""
        invoice = PurchaseInvoice.objects.create(
            invoice_number='INV-SUP-2025-001',
            supplier=self.supplier,
            invoice_date=date.today(),
            due_date=date.today() + timedelta(days=30),
            base_amount=Decimal('10000.00'),
            tax_amount=Decimal('700.00'),
            total_amount=Decimal('10700.00'),
            paid_amount=Decimal('0.00'),
            currency=self.currency,
            status='pending'
        )
        self.assertEqual(invoice.invoice_number, 'INV-SUP-2025-001')
        self.assertEqual(invoice.status, 'pending')
    
    def test_purchase_invoice_balance_due(self):
        """Test balance due calculation"""
        invoice = PurchaseInvoice.objects.create(
            invoice_number='INV-SUP-2025-002',
            supplier=self.supplier,
            invoice_date=date.today(),
            due_date=date.today() + timedelta(days=30),
            total_amount=Decimal('10000.00'),
            paid_amount=Decimal('3000.00'),
            currency=self.currency
        )
        self.assertEqual(invoice.balance_due, Decimal('7000.00'))


# ========================================
# API TESTS
# ========================================

class SupplierAPITest(APITestCase):
    """API tests for Supplier endpoints"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role='admin'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        self.contact = Contact.objects.create(
            contact_type='supplier',
            name='Test Supplier Co.',
            email='supplier@example.com'
        )
        self.supplier = Supplier.objects.create(
            contact=self.contact,
            supplier_code='SUP-001'
        )
    
    def test_list_suppliers(self):
        """Test listing suppliers"""
        url = reverse('supplier-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_search_suppliers(self):
        """Test searching suppliers"""
        url = reverse('supplier-list')
        response = self.client.get(url, {'search': 'Test Supplier'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_retrieve_supplier(self):
        """Test retrieving a supplier"""
        url = reverse('supplier-detail', args=[self.supplier.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['supplier_code'], 'SUP-001')
        self.assertEqual(response.data['contact_name'], 'Test Supplier Co.')


class ExpenseCategoryAPITest(APITestCase):
    """API tests for ExpenseCategory endpoints"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role='admin'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        self.category = ExpenseCategory.objects.create(
            name='Materials',
            code='MAT',
            category_type='cogs'
        )
    
    def test_list_expense_categories(self):
        """Test listing expense categories"""
        url = reverse('expensecategory-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_filter_categories_by_type(self):
        """Test filtering categories by type"""
        url = reverse('expensecategory-list')
        response = self.client.get(url, {'category_type': 'cogs'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class PurchaseOrderAPITest(APITestCase):
    """API tests for PurchaseOrder endpoints"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role='admin'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        self.contact = Contact.objects.create(
            contact_type='supplier',
            name='Test Supplier'
        )
        self.supplier = Supplier.objects.create(
            contact=self.contact,
            supplier_code='SUP-001'
        )
        self.location = Location.objects.create(
            name='Bangkok Facility',
            code='BKK',
            address='Bangkok, Thailand'
        )
        self.currency = Currency.objects.create(
            code='THB',
            name='Thai Baht',
            symbol='฿'
        )
        self.po = PurchaseOrder.objects.create(
            po_number='PO-2025-001',
            supplier=self.supplier,
            location=self.location,
            order_date=date.today(),
            expected_delivery_date=date.today() + timedelta(days=7),
            currency=self.currency,
            status='draft'
        )
    
    def test_list_purchase_orders(self):
        """Test listing purchase orders"""
        url = reverse('purchaseorder-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_filter_pos_by_status(self):
        """Test filtering POs by status"""
        url = reverse('purchaseorder-list')
        response = self.client.get(url, {'status': 'draft'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_filter_pos_by_supplier(self):
        """Test filtering POs by supplier"""
        url = reverse('purchaseorder-list')
        response = self.client.get(url, {'supplier': self.supplier.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_retrieve_purchase_order(self):
        """Test retrieving a purchase order"""
        url = reverse('purchaseorder-detail', args=[self.po.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['po_number'], 'PO-2025-001')
        self.assertEqual(response.data['supplier_name'], 'Test Supplier')


class ExpenseAPITest(APITestCase):
    """API tests for Expense endpoints"""
    
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
        self.currency = Currency.objects.create(
            code='THB',
            name='Thai Baht',
            symbol='฿'
        )
        self.category = ExpenseCategory.objects.create(
            name='Utilities',
            code='UTIL',
            category_type='opex'
        )
        self.expense = Expense.objects.create(
            expense_number='EXP-2025-001',
            category=self.category,
            location=self.location,
            expense_date=date.today(),
            amount=Decimal('5000.00'),
            currency=self.currency,
            description='Electricity'
        )
    
    def test_list_expenses(self):
        """Test listing expenses"""
        url = reverse('expense-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_filter_expenses_by_category(self):
        """Test filtering expenses by category"""
        url = reverse('expense-list')
        response = self.client.get(url, {'category': self.category.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_retrieve_expense(self):
        """Test retrieving an expense"""
        url = reverse('expense-detail', args=[self.expense.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['expense_number'], 'EXP-2025-001')


class PurchaseInvoiceAPITest(APITestCase):
    """API tests for PurchaseInvoice endpoints"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role='admin'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        self.contact = Contact.objects.create(
            contact_type='supplier',
            name='Test Supplier'
        )
        self.supplier = Supplier.objects.create(
            contact=self.contact,
            supplier_code='SUP-001'
        )
        self.currency = Currency.objects.create(
            code='THB',
            name='Thai Baht',
            symbol='฿'
        )
        self.invoice = PurchaseInvoice.objects.create(
            invoice_number='INV-SUP-2025-001',
            supplier=self.supplier,
            invoice_date=date.today(),
            due_date=date.today() + timedelta(days=30),
            total_amount=Decimal('10000.00'),
            currency=self.currency,
            status='pending'
        )
    
    def test_list_purchase_invoices(self):
        """Test listing purchase invoices"""
        url = reverse('purchaseinvoice-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_filter_invoices_by_status(self):
        """Test filtering invoices by status"""
        url = reverse('purchaseinvoice-list')
        response = self.client.get(url, {'status': 'pending'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_retrieve_purchase_invoice(self):
        """Test retrieving a purchase invoice"""
        url = reverse('purchaseinvoice-detail', args=[self.invoice.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['invoice_number'], 'INV-SUP-2025-001')
        self.assertIn('balance_due', response.data)
