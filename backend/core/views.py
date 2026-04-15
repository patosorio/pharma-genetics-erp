"""
Core ViewSets
User, Location, Contact, Currency, TaxType, CompanySettings
"""

from rest_framework import viewsets, filters, status
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, BasePermission
from django_filters.rest_framework import DjangoFilterBackend


class IsAdminRole(BasePermission):
    """Allow full access only to users whose role == 'admin'."""
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == 'admin'
        )


class AuditViewSetMixin:
    """
    Mixin that automatically sets created_by and updated_by on every save.
    Apply to any ModelViewSet whose model inherits AuditMixin.
    """
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

from .models import User, Location, Contact, Currency, TaxType, CompanySettings
from .serializers import (
    UserSerializer, LocationSerializer, ContactSerializer,
    CurrencySerializer, TaxTypeSerializer, CompanySettingsSerializer,
    RegistrationSerializer
)


class CurrentUserView(APIView):
    """
    Get the currently authenticated user's details
    GET /api/v1/me/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class LogoutView(APIView):
    """
    Logout - delete the user's auth token
    POST /api/v1/logout/
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # Delete the token to logout
        if hasattr(request.user, 'auth_token'):
            request.user.auth_token.delete()
        return Response({'detail': 'Successfully logged out.'}, status=status.HTTP_200_OK)


class RegisterView(APIView):
    """
    Public registration endpoint for access requests.
    Creates user with is_active=False pending admin approval.
    POST /api/v1/register/
    """
    permission_classes = []  # Public endpoint
    authentication_classes = []  # No auth required
    
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    'detail': 'Registration submitted successfully. Pending admin approval.',
                    'email': user.email,
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(AuditViewSetMixin, viewsets.ModelViewSet):
    """
    ViewSet for User model — admin role only.
    """
    queryset = User.objects.select_related('location').all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminRole]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['role', 'is_active', 'location']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['username', 'date_joined', 'last_login']
    ordering = ['-date_joined']


class LocationViewSet(AuditViewSetMixin, viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'code']
    search_fields = ['name', 'code', 'address']
    ordering_fields = ['code', 'name']
    ordering = ['code']


class ContactViewSet(AuditViewSetMixin, viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['contact_type', 'is_active']
    search_fields = ['name', 'email', 'phone', 'tax_id']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class CurrencyViewSet(AuditViewSetMixin, viewsets.ModelViewSet):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['code', 'name']
    ordering_fields = ['code', 'name']
    ordering = ['code']


class TaxTypeViewSet(AuditViewSetMixin, viewsets.ModelViewSet):
    queryset = TaxType.objects.all()
    serializer_class = TaxTypeSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name']
    ordering_fields = ['name', 'rate']
    ordering = ['name']


class CompanySettingsViewSet(RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    """
    ViewSet for CompanySettings (singleton) — retrieve and partial update.
    Auto-creates the singleton record on first access if it doesn't exist.
    """
    queryset = CompanySettings.objects.all()
    serializer_class = CompanySettingsSerializer
    http_method_names = ['get', 'patch', 'head', 'options']

    def get_object(self):
        obj, _ = CompanySettings.objects.get_or_create(
            pk=1,
            defaults={'default_currency': Currency.objects.first()},
        )
        return obj
