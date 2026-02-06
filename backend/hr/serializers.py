"""
HR Serializers
Department, Employee, PayrollPeriod, Payroll
"""

from rest_framework import serializers
from .models import Department, Employee, PayrollPeriod, Payroll


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']


class EmployeeSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    location_name = serializers.CharField(source='location.name', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True, allow_null=True)
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = Employee
        fields = '__all__'
        read_only_fields = ['id', 'full_name', 'created_at', 'updated_at', 'created_by', 'updated_by']


class EmployeeListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views"""
    department_name = serializers.CharField(source='department.name', read_only=True)
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = Employee
        fields = ['id', 'employee_code', 'full_name', 'department', 'department_name', 'is_active', 'hire_date']


class PayrollPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayrollPeriod
        fields = '__all__'


class PayrollSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    period_name = serializers.CharField(source='period.period_name', read_only=True)
    
    class Meta:
        model = Payroll
        fields = '__all__'
        read_only_fields = ['id', 'net_salary', 'created_at', 'updated_at', 'created_by', 'updated_by']

