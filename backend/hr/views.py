"""
HR ViewSets
Department, Employee, PayrollPeriod, Payroll
"""

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from core.views import AuditViewSetMixin

from .models import Department, Employee, PayrollPeriod, Payroll
from .serializers import (
    DepartmentSerializer, EmployeeSerializer, EmployeeListSerializer,
    PayrollPeriodSerializer, PayrollSerializer
)


class DepartmentViewSet(AuditViewSetMixin, viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'code']
    ordering_fields = ['code', 'name']
    ordering = ['code']


class EmployeeViewSet(AuditViewSetMixin, viewsets.ModelViewSet):
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


class PayrollPeriodViewSet(AuditViewSetMixin, viewsets.ModelViewSet):
    queryset = PayrollPeriod.objects.all()
    serializer_class = PayrollPeriodSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['is_closed']
    ordering_fields = ['start_date', 'period_name']
    ordering = ['-start_date']

    @action(detail=True, methods=['post'])
    def close_period(self, request, pk=None):
        """POST /api/v1/payroll-periods/{id}/close_period/ — close a period after all payrolls are paid."""
        period = self.get_object()
        if period.is_closed:
            return Response({'detail': 'Period is already closed.'}, status=status.HTTP_400_BAD_REQUEST)
        unpaid = period.payrolls.filter(is_paid=False).count()
        if unpaid:
            return Response(
                {'detail': f'Cannot close period: {unpaid} payroll(s) are still unpaid.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        period.is_closed = True
        period.save(update_fields=['is_closed'])
        return Response(PayrollPeriodSerializer(period).data)


class PayrollViewSet(AuditViewSetMixin, viewsets.ModelViewSet):
    queryset = Payroll.objects.select_related('employee', 'period').all()
    serializer_class = PayrollSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['employee', 'period', 'is_paid']
    ordering_fields = ['period__start_date', 'employee__employee_code']
    ordering = ['-period__start_date', 'employee__employee_code']

    @action(detail=True, methods=['post'])
    def mark_paid(self, request, pk=None):
        """POST /api/v1/payrolls/{id}/mark_paid/ — mark as paid and set payment_date."""
        payroll = self.get_object()
        if payroll.is_paid:
            return Response({'detail': 'Payroll is already marked as paid.'}, status=status.HTTP_400_BAD_REQUEST)
        payroll.is_paid = True
        payroll.payment_date = request.data.get('payment_date') or timezone.now().date()
        payroll.save(update_fields=['is_paid', 'payment_date'])
        return Response(PayrollSerializer(payroll).data)
