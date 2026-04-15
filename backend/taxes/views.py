"""
Taxes ViewSets
TaxReport, TaxJournalEntry
"""

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from core.views import AuditViewSetMixin

from .models import TaxReport, TaxJournalEntry
from .serializers import TaxReportSerializer, TaxJournalEntrySerializer


class TaxReportViewSet(AuditViewSetMixin, viewsets.ModelViewSet):
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
        """POST /api/v1/tax-reports/{id}/calculate_totals/ — recalculate summary totals."""
        report = self.get_object()
        try:
            result = report.calculate_totals()
            return Response(result)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='generate_entries')
    def generate_entries(self, request, pk=None):
        """
        POST /api/v1/tax-reports/{id}/generate_entries/
        Auto-creates TaxJournalEntry records from all invoices in the report period.
        Skips invoices that already have an entry in this report.
        """
        from .models import TaxJournalEntry
        from sales.models import SalesInvoice
        from purchasing.models import PurchaseInvoice

        report = self.get_object()
        created = 0

        existing_sales = set(
            TaxJournalEntry.objects.filter(
                tax_report=report, entry_type='payable'
            ).values_list('sales_invoice_id', flat=True)
        )
        existing_purchase = set(
            TaxJournalEntry.objects.filter(
                tax_report=report, entry_type='recoverable'
            ).values_list('purchase_invoice_id', flat=True)
        )

        sales_invoices = SalesInvoice.objects.filter(
            invoice_date__gte=report.period_start,
            invoice_date__lte=report.period_end,
            tax_amount__gt=0,
        ).exclude(status='cancelled').exclude(id__in=existing_sales)

        for inv in sales_invoices:
            TaxJournalEntry.objects.create(
                tax_report=report,
                entry_type='payable',
                sales_invoice=inv,
                tax_type=inv.tax_type,
                base_amount=inv.base_amount,
                tax_amount=inv.tax_amount,
                entry_date=inv.invoice_date,
            )
            created += 1

        purchase_invoices = PurchaseInvoice.objects.filter(
            invoice_date__gte=report.period_start,
            invoice_date__lte=report.period_end,
            tax_amount__gt=0,
        ).exclude(status='cancelled').exclude(id__in=existing_purchase)

        for inv in purchase_invoices:
            TaxJournalEntry.objects.create(
                tax_report=report,
                entry_type='recoverable',
                purchase_invoice=inv,
                tax_type=inv.tax_type,
                base_amount=inv.base_amount,
                tax_amount=inv.tax_amount,
                entry_date=inv.invoice_date,
            )
            created += 1

        report.calculate_totals()
        return Response({
            'created': created,
            'total_vat_payable': report.total_vat_payable,
            'total_vat_recoverable': report.total_vat_recoverable,
            'net_vat_position': report.net_vat_position,
        })


class TaxJournalEntryViewSet(AuditViewSetMixin, viewsets.ModelViewSet):
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
