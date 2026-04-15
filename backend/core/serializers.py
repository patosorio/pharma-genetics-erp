"""
Core Serializers
User, Location, Contact, Currency, TaxType, CompanySettings
"""

from rest_framework import serializers
from .models import User, Location, Contact, Currency, TaxType, CompanySettings


class UserSerializer(serializers.ModelSerializer):
    location_name = serializers.CharField(source='location.name', read_only=True)
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'role', 'location', 'location_name', 'firebase_uid', 'is_active',
            'date_joined', 'last_login', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login', 'created_at', 'updated_at']
        extra_kwargs = {
            'password': {'write_only': True},
            'firebase_uid': {'required': False}
        }
    
    def get_full_name(self, obj):
        return obj.get_full_name()


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']


class ContactSerializer(serializers.ModelSerializer):
    contact_type_display = serializers.CharField(source='get_contact_type_display', read_only=True)
    
    class Meta:
        model = Contact
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = '__all__'

    def validate(self, data):
        is_default = data.get('is_default', getattr(self.instance, 'is_default', False))
        if is_default:
            qs = Currency.objects.filter(is_default=True)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                existing = qs.first()
                raise serializers.ValidationError(
                    f"'{existing.code}' is already the default currency. "
                    "Setting this currency as default will clear the existing one."
                )
        return data


class TaxTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaxType
        fields = '__all__'

    def validate_rate(self, value):
        if value <= 0:
            raise serializers.ValidationError("Tax rate must be greater than zero.")
        return value


class CompanySettingsSerializer(serializers.ModelSerializer):
    default_currency_code = serializers.CharField(source='default_currency.code', read_only=True)
    
    class Meta:
        model = CompanySettings
        fields = '__all__'


class RegistrationSerializer(serializers.Serializer):
    """
    Serializer for public user registration (access request).
    Creates user with is_active=False pending admin approval.
    """
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=8)
    
    def validate_email(self, value):
        """Ensure email is unique (used as username)."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value.lower()
    
    def create(self, validated_data):
        """Create inactive user pending admin approval."""
        user = User.objects.create_user(
            username=validated_data['email'],  # Use email as username
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password'],
            is_active=False,  # Requires admin approval
            role='viewer',  # Default role, admin can change
        )
        return user

