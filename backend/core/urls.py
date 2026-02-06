"""
Core URL Configuration
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    UserViewSet, LocationViewSet, ContactViewSet,
    CurrencyViewSet, TaxTypeViewSet, CompanySettingsViewSet,
    CurrentUserView, LogoutView, RegisterView
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'locations', LocationViewSet, basename='location')
router.register(r'contacts', ContactViewSet, basename='contact')
router.register(r'currencies', CurrencyViewSet, basename='currency')
router.register(r'tax-types', TaxTypeViewSet, basename='taxtype')
router.register(r'company-settings', CompanySettingsViewSet, basename='companysettings')

urlpatterns = [
    path('', include(router.urls)),
    path('me/', CurrentUserView.as_view(), name='current-user'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
]

