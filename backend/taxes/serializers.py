"""
Taxes Serializers
TaxReport, TaxJournalEntry
"""

from rest_framework import serializers
from .models import TaxReport, TaxJournalEntry


class TaxJournalEntrySerializer(serializers.ModelSerializer):
    entry_type_display = serializers.CharField(source='get_entry_type_display', read_only=True)
    tax_type_name = serializers.CharField(source='tax_type.name', read_only=True)
    
    class Meta:
        model = TaxJournalEntry
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']


class TaxReportSerializer(serializers.ModelSerializer):
    currency_code = serializers.CharField(source='currency.code', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_payable = serializers.ReadOnlyField()
    is_recoverable = serializers.ReadOnlyField()
    journal_entries = TaxJournalEntrySerializer(many=True, read_only=True)
    
    class Meta:
        model = TaxReport
        fields = '__all__'
        read_only_fields = ['id', 'is_payable', 'is_recoverable', 'created_at', 'updated_at', 'created_by', 'updated_by']

