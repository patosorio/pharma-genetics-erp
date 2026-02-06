"""
Pricing URL Configuration
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CostAllocationRuleViewSet, PricingTierViewSet, CostSnapshotViewSet
)

router = DefaultRouter()
router.register(r'cost-allocation-rules', CostAllocationRuleViewSet, basename='costallocationrule')
router.register(r'pricing-tiers', PricingTierViewSet, basename='pricingtier')
router.register(r'cost-snapshots', CostSnapshotViewSet, basename='costsnapshot')

urlpatterns = [
    path('', include(router.urls)),
]

