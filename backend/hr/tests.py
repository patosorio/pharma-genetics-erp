"""
HR App Tests
Tests for Department, Employee, PayrollPeriod, Payroll models and API endpoints
"""

from decimal import Decimal
from datetime import date
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from core.models import User, Location
from .models import Department, Employee, PayrollPeriod, Payroll


# ========================================
# MODEL TESTS
# ========================================

class DepartmentModelTest(TestCase):
    """Tests for Department model"""
    
    def test_create_department(self):
        """Test creating a department"""
        dept = Department.objects.create(
            name='Cultivation',
            code='CULT',
            is_active=True
        )
        self.assertEqual(dept.name, 'Cultivation')
        self.assertEqual(dept.code, 'CULT')
        self.assertTrue(dept.is_active)
    
    def test_department_str_representation(self):
        """Test department string representation"""
        dept = Department.objects.create(name='Sales', code='SALES')
        self.assertEqual(str(dept), 'SALES - Sales')
    
    def test_department_code_unique(self):
        """Test that department codes are unique"""
        Department.objects.create(name='Dept 1', code='D001')
        with self.assertRaises(Exception):
            Department.objects.create(name='Dept 2', code='D001')


class EmployeeModelTest(TestCase):
    """Tests for Employee model"""
    
    def setUp(self):
        self.location = Location.objects.create(
            name='Bangkok Facility',
            code='BKK',
            address='Bangkok, Thailand'
        )
        self.department = Department.objects.create(
            name='Cultivation',
            code='CULT'
        )
    
    def test_create_employee(self):
        """Test creating an employee"""
        employee = Employee.objects.create(
            employee_code='EMP-001',
            first_name='John',
            last_name='Smith',
            email='john.smith@example.com',
            phone='+66123456789',
            department=self.department,
            location=self.location,
            hire_date=date(2024, 1, 15),
            salary=Decimal('50000.00'),
            is_active=True
        )
        self.assertEqual(employee.employee_code, 'EMP-001')
        self.assertEqual(employee.first_name, 'John')
        self.assertEqual(employee.salary, Decimal('50000.00'))
    
    def test_employee_full_name(self):
        """Test employee full_name property"""
        employee = Employee.objects.create(
            employee_code='EMP-002',
            first_name='Jane',
            last_name='Doe',
            email='jane.doe@example.com',
            department=self.department,
            location=self.location,
            hire_date=date(2024, 1, 1),
            salary=Decimal('45000.00')
        )
        self.assertEqual(employee.full_name, 'Jane Doe')
    
    def test_employee_str_representation(self):
        """Test employee string representation"""
        employee = Employee.objects.create(
            employee_code='EMP-003',
            first_name='Bob',
            last_name='Johnson',
            email='bob@example.com',
            department=self.department,
            location=self.location,
            hire_date=date(2024, 1, 1),
            salary=Decimal('40000.00')
        )
        self.assertIn('EMP-003', str(employee))
        self.assertIn('Bob', str(employee))
    
    def test_employee_code_unique(self):
        """Test that employee codes are unique"""
        Employee.objects.create(
            employee_code='UNIQUE-001',
            first_name='Test',
            last_name='User',
            email='test@example.com',
            department=self.department,
            location=self.location,
            hire_date=date(2024, 1, 1),
            salary=Decimal('30000.00')
        )
        with self.assertRaises(Exception):
            Employee.objects.create(
                employee_code='UNIQUE-001',
                first_name='Another',
                last_name='User',
                email='another@example.com',
                department=self.department,
                location=self.location,
                hire_date=date(2024, 2, 1),
                salary=Decimal('35000.00')
            )
    
    def test_employee_with_user_account(self):
        """Test employee linked to a user account"""
        user = User.objects.create_user(
            username='johndoe',
            password='testpass123'
        )
        employee = Employee.objects.create(
            employee_code='EMP-004',
            user=user,
            first_name='John',
            last_name='Doe',
            email='john.doe@example.com',
            department=self.department,
            location=self.location,
            hire_date=date(2024, 1, 1),
            salary=Decimal('50000.00')
        )
        self.assertEqual(employee.user, user)


class PayrollPeriodModelTest(TestCase):
    """Tests for PayrollPeriod model"""
    
    def test_create_payroll_period(self):
        """Test creating a payroll period"""
        period = PayrollPeriod.objects.create(
            period_name='2025-01',
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 31),
            is_closed=False
        )
        self.assertEqual(period.period_name, '2025-01')
        self.assertFalse(period.is_closed)
    
    def test_payroll_period_str_representation(self):
        """Test payroll period string representation"""
        period = PayrollPeriod.objects.create(
            period_name='2025-02',
            start_date=date(2025, 2, 1),
            end_date=date(2025, 2, 28)
        )
        self.assertEqual(str(period), '2025-02')
    
    def test_payroll_period_date_validation(self):
        """Test that end_date must be after start_date"""
        with self.assertRaises(ValueError):
            PayrollPeriod.objects.create(
                period_name='Invalid',
                start_date=date(2025, 1, 31),
                end_date=date(2025, 1, 1)
            )


class PayrollModelTest(TestCase):
    """Tests for Payroll model"""
    
    def setUp(self):
        self.location = Location.objects.create(
            name='Bangkok Facility',
            code='BKK',
            address='Bangkok, Thailand'
        )
        self.department = Department.objects.create(
            name='Cultivation',
            code='CULT'
        )
        self.employee = Employee.objects.create(
            employee_code='EMP-001',
            first_name='John',
            last_name='Smith',
            email='john@example.com',
            department=self.department,
            location=self.location,
            hire_date=date(2024, 1, 1),
            salary=Decimal('50000.00')
        )
        self.period = PayrollPeriod.objects.create(
            period_name='2025-01',
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 31)
        )
    
    def test_create_payroll(self):
        """Test creating a payroll record"""
        payroll = Payroll.objects.create(
            employee=self.employee,
            period=self.period,
            base_salary=Decimal('50000.00'),
            deductions=Decimal('5000.00'),
            is_paid=False
        )
        self.assertEqual(payroll.base_salary, Decimal('50000.00'))
        self.assertEqual(payroll.deductions, Decimal('5000.00'))
    
    def test_payroll_net_salary_calculation(self):
        """Test that net salary is auto-calculated"""
        payroll = Payroll.objects.create(
            employee=self.employee,
            period=self.period,
            base_salary=Decimal('50000.00'),
            deductions=Decimal('5000.00')
        )
        self.assertEqual(payroll.net_salary, Decimal('45000.00'))
    
    def test_payroll_str_representation(self):
        """Test payroll string representation"""
        payroll = Payroll.objects.create(
            employee=self.employee,
            period=self.period,
            base_salary=Decimal('50000.00'),
            deductions=Decimal('5000.00')
        )
        self.assertIn('EMP-001', str(payroll))
        self.assertIn('2025-01', str(payroll))
    
    def test_payroll_unique_employee_period(self):
        """Test that employee-period combination is unique"""
        Payroll.objects.create(
            employee=self.employee,
            period=self.period,
            base_salary=Decimal('50000.00'),
            deductions=Decimal('0.00')
        )
        with self.assertRaises(Exception):
            Payroll.objects.create(
                employee=self.employee,
                period=self.period,
                base_salary=Decimal('50000.00'),
                deductions=Decimal('5000.00')
            )


# ========================================
# API TESTS
# ========================================

class DepartmentAPITest(APITestCase):
    """API tests for Department endpoints"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role='admin'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        self.department = Department.objects.create(
            name='Cultivation',
            code='CULT'
        )
    
    def test_list_departments(self):
        """Test listing departments"""
        url = reverse('department-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_create_department(self):
        """Test creating a department via API"""
        url = reverse('department-list')
        data = {
            'name': 'Sales',
            'code': 'SALES',
            'is_active': True
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_filter_departments_by_active(self):
        """Test filtering departments by active status"""
        Department.objects.create(name='Inactive Dept', code='INA', is_active=False)
        url = reverse('department-list')
        response = self.client.get(url, {'is_active': 'true'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for dept in response.data['results']:
            self.assertTrue(dept['is_active'])


class EmployeeAPITest(APITestCase):
    """API tests for Employee endpoints"""
    
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
        self.department = Department.objects.create(
            name='Cultivation',
            code='CULT'
        )
        self.employee = Employee.objects.create(
            employee_code='EMP-001',
            first_name='John',
            last_name='Smith',
            email='john@example.com',
            department=self.department,
            location=self.location,
            hire_date=date(2024, 1, 1),
            salary=Decimal('50000.00')
        )
    
    def test_list_employees(self):
        """Test listing employees"""
        url = reverse('employee-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_filter_employees_by_department(self):
        """Test filtering employees by department"""
        url = reverse('employee-list')
        response = self.client.get(url, {'department': self.department.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_filter_employees_by_location(self):
        """Test filtering employees by location"""
        url = reverse('employee-list')
        response = self.client.get(url, {'location': self.location.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_search_employees(self):
        """Test searching employees by name"""
        url = reverse('employee-list')
        response = self.client.get(url, {'search': 'John'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_retrieve_employee(self):
        """Test retrieving an employee"""
        url = reverse('employee-detail', args=[self.employee.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['employee_code'], 'EMP-001')
        self.assertEqual(response.data['full_name'], 'John Smith')
        self.assertEqual(response.data['department_name'], 'Cultivation')


class PayrollPeriodAPITest(APITestCase):
    """API tests for PayrollPeriod endpoints"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role='admin'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        self.period = PayrollPeriod.objects.create(
            period_name='2025-01',
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 31)
        )
    
    def test_list_payroll_periods(self):
        """Test listing payroll periods"""
        url = reverse('payrollperiod-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_create_payroll_period(self):
        """Test creating a payroll period"""
        url = reverse('payrollperiod-list')
        data = {
            'period_name': '2025-02',
            'start_date': '2025-02-01',
            'end_date': '2025-02-28',
            'is_closed': False
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_filter_periods_by_closed_status(self):
        """Test filtering periods by closed status"""
        PayrollPeriod.objects.create(
            period_name='2024-12',
            start_date=date(2024, 12, 1),
            end_date=date(2024, 12, 31),
            is_closed=True
        )
        url = reverse('payrollperiod-list')
        response = self.client.get(url, {'is_closed': 'false'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class PayrollAPITest(APITestCase):
    """API tests for Payroll endpoints"""
    
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
        self.department = Department.objects.create(
            name='Cultivation',
            code='CULT'
        )
        self.employee = Employee.objects.create(
            employee_code='EMP-001',
            first_name='John',
            last_name='Smith',
            email='john@example.com',
            department=self.department,
            location=self.location,
            hire_date=date(2024, 1, 1),
            salary=Decimal('50000.00')
        )
        self.period = PayrollPeriod.objects.create(
            period_name='2025-01',
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 31)
        )
        self.payroll = Payroll.objects.create(
            employee=self.employee,
            period=self.period,
            base_salary=Decimal('50000.00'),
            deductions=Decimal('5000.00')
        )
    
    def test_list_payrolls(self):
        """Test listing payrolls"""
        url = reverse('payroll-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_filter_payrolls_by_employee(self):
        """Test filtering payrolls by employee"""
        url = reverse('payroll-list')
        response = self.client.get(url, {'employee': self.employee.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_filter_payrolls_by_period(self):
        """Test filtering payrolls by period"""
        url = reverse('payroll-list')
        response = self.client.get(url, {'period': self.period.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_retrieve_payroll(self):
        """Test retrieving a payroll record"""
        url = reverse('payroll-detail', args=[self.payroll.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['employee_name'], 'John Smith')
        self.assertEqual(response.data['period_name'], '2025-01')
        self.assertEqual(Decimal(response.data['net_salary']), Decimal('45000.00'))
