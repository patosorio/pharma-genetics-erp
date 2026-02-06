"""
HR ViewSets
Department, Employee, PayrollPeriod, Payroll
"""

from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend

from .models import Department, Employee, PayrollPeriod, Payroll
from .serializers import (
    DepartmentSerializer, EmployeeSerializer, EmployeeListSerializer,
    PayrollPeriodSerializer, PayrollSerializer
)


class DepartmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Department model
    """
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'code']
    ordering_fields = ['code', 'name']
    ordering = ['code']


class EmployeeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Employee model
    Employee records with department and location
    """
    queryset = Employee.objects.select_related('user', 'department', 'location').all()
    serializer_class = EmployeeSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['department', 'location', 'is_active']
    search_fields = ['employee_code', 'first_name', 'last_name', 'email']
    ordering_fields = ['employee_code', 'hire_date', 'last_name']
    ordering = ['employee_code']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return EmployeeListSerializer
        return EmployeeSerializer


class PayrollPeriodViewSet(viewsets.ModelViewSet):
    """
    ViewSet for PayrollPeriod model
    Monthly payroll periods
    """
    queryset = PayrollPeriod.objects.all()
    serializer_class = PayrollPeriodSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['is_closed']
    ordering_fields = ['start_date', 'period_name']
    ordering = ['-start_date']


class PayrollViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Payroll model
    Employee payroll records
    """
    queryset = Payroll.objects.select_related('employee', 'period').all()
    serializer_class = PayrollSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['employee', 'period', 'is_paid']
    ordering_fields = ['period__start_date', 'employee__employee_code']
    ordering = ['-period__start_date', 'employee__employee_code']
