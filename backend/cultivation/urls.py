"""
Cultivation URL Configuration
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    MotherPlantViewSet, ProductionBatchViewSet, CloneViewSet,
    ProductionAssumptionViewSet
)

router = DefaultRouter()
router.register(r'mother-plants', MotherPlantViewSet, basename='motherplant')
router.register(r'production-batches', ProductionBatchViewSet, basename='productionbatch')
router.register(r'clones', CloneViewSet, basename='clone')
router.register(r'production-assumptions', ProductionAssumptionViewSet, basename='productionassumption')

urlpatterns = [
    path('', include(router.urls)),
]

