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

    def validate(self, data):
        sales_invoice = data.get('sales_invoice', getattr(self.instance, 'sales_invoice', None))
        purchase_invoice = data.get('purchase_invoice', getattr(self.instance, 'purchase_invoice', None))
        entry_type = data.get('entry_type', getattr(self.instance, 'entry_type', None))

        if sales_invoice and purchase_invoice:
            raise serializers.ValidationError(
                "A journal entry cannot reference both a sales invoice and a purchase invoice."
            )
        if not sales_invoice and not purchase_invoice:
            raise serializers.ValidationError(
                "A journal entry must reference either a sales invoice or a purchase invoice."
            )
        if entry_type == 'payable' and not sales_invoice:
            raise serializers.ValidationError(
                "A 'payable' journal entry must reference a sales invoice."
            )
        if entry_type == 'recoverable' and not purchase_invoice:
            raise serializers.ValidationError(
                "A 'recoverable' journal entry must reference a purchase invoice."
            )
        return data


class TaxReportSerializer(serializers.ModelSerializer):
    currency_code = serializers.CharField(source='currency.code', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_payable = serializers.ReadOnlyField()
    is_recoverable = serializers.ReadOnlyField()
    journal_entries = TaxJournalEntrySerializer(many=True, read_only=True)

    class Meta:
        model = TaxReport
        fields = '__all__'
        read_only_fields = [
            'id', 'report_number',
            'total_vat_payable', 'total_vat_recoverable', 'net_vat_position',
            'is_payable', 'is_recoverable',
            'created_at', 'updated_at', 'created_by', 'updated_by',
        ]

    def validate(self, data):
        period_start = data.get('period_start') or (self.instance.period_start if self.instance else None)
        period_end = data.get('period_end') or (self.instance.period_end if self.instance else None)

        if period_start and period_end and period_end < period_start:
            raise serializers.ValidationError("period_end must be on or after period_start.")

        # Overlap detection (only on create, or when dates change)
        if period_start and period_end:
            qs = TaxReport.objects.filter(
                period_start__lte=period_end,
                period_end__gte=period_start,
            )
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                overlap = qs.first()
                raise serializers.ValidationError(
                    f"This period overlaps with existing report '{overlap.report_number}' "
                    f"({overlap.period_start} – {overlap.period_end})."
                )
        return data
