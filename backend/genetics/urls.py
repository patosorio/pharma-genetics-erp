"""
Genetics URL Configuration
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import StrainCategoryViewSet, StrainViewSet

router = DefaultRouter()
router.register(r'strain-categories', StrainCategoryViewSet, basename='straincategory')
router.register(r'strains', StrainViewSet, basename='strain')

urlpatterns = [
    path('', include(router.urls)),
]

