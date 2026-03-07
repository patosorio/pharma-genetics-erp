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
        read_only_fields = ['id', 'employee_code', 'full_name', 'created_at', 'updated_at', 'created_by', 'updated_by']


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

    def validate(self, data):
        start = data.get('start_date') or (self.instance.start_date if self.instance else None)
        end = data.get('end_date') or (self.instance.end_date if self.instance else None)
        if start and end and end < start:
            raise serializers.ValidationError("end_date must be on or after start_date.")
        return data


class PayrollSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    period_name = serializers.CharField(source='period.period_name', read_only=True)
    net_salary = serializers.ReadOnlyField()

    class Meta:
        model = Payroll
        fields = '__all__'
        read_only_fields = ['id', 'net_salary', 'created_at', 'updated_at', 'created_by', 'updated_by']

    def validate(self, data):
        period = data.get('period') or (self.instance.period if self.instance else None)
        if period and period.is_closed:
            raise serializers.ValidationError(
                f"Cannot create or modify a payroll in a closed period ('{period.period_name}')."
            )
        return data

