"""
Taxes URL Configuration
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import TaxReportViewSet, TaxJournalEntryViewSet

router = DefaultRouter()
router.register(r'tax-reports', TaxReportViewSet, basename='taxreport')
router.register(r'tax-journal-entries', TaxJournalEntryViewSet, basename='taxjournalentry')

urlpatterns = [
    path('', include(router.urls)),
]

