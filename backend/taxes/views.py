"""
Taxes ViewSets
TaxReport, TaxJournalEntry
"""

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import TaxReport, TaxJournalEntry
from .serializers import TaxReportSerializer, TaxJournalEntrySerializer


class TaxReportViewSet(viewsets.ModelViewSet):
    """
    ViewSet for TaxReport model
    Tax reports for specific periods
    """
    queryset = TaxReport.objects.select_related('currency').prefetch_related('journal_entries').all()
    serializer_class = TaxReportSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'period_start', 'period_end']
    ordering_fields = ['period_end', 'report_number']
    ordering = ['-period_end']
    
    @action(detail=True, methods=['post'])
    def calculate_totals(self, request, pk=None):
        """
        Custom action to calculate tax totals from invoices
        """
        report = self.get_object()
        try:
            result = report.calculate_totals()
            return Response(result)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class TaxJournalEntryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for TaxJournalEntry model
    Individual tax journal entries
    """
    queryset = TaxJournalEntry.objects.select_related(
        'tax_report', 'sales_invoice', 'purchase_invoice', 'tax_type'
    ).all()
    serializer_class = TaxJournalEntrySerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['tax_report', 'entry_type', 'entry_date']
    ordering_fields = ['entry_date', 'tax_amount']
    ordering = ['-entry_date']
