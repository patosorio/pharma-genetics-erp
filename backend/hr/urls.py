"""
HR URL Configuration
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    DepartmentViewSet, EmployeeViewSet, PayrollPeriodViewSet, PayrollViewSet
)

router = DefaultRouter()
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'employees', EmployeeViewSet, basename='employee')
router.register(r'payroll-periods', PayrollPeriodViewSet, basename='payrollperiod')
router.register(r'payrolls', PayrollViewSet, basename='payroll')

urlpatterns = [
    path('', include(router.urls)),
]

