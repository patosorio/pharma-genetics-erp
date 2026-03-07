"""
Migration 0004: Expense subcategory model + unified Expense (adds invoice fields)
- Makes ExpenseCategory.code optional (non-unique)
- Adds ExpenseSubcategory table
- Extends Expense with: document_type, subcategory FK, invoice fields
"""

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_backend_gaps_phase1'),
        ('purchasing', '0003_backend_gaps_phase1'),
    ]

    operations = [
        # 1. Make ExpenseCategory.code optional and non-unique
        migrations.AlterField(
            model_name='expensecategory',
            name='code',
            field=models.CharField(
                blank=True,
                default='',
                help_text='Optional short code for the category',
                max_length=20,
            ),
        ),
        # Update category_type choices to 3-char max
        migrations.AlterField(
            model_name='expensecategory',
            name='category_type',
            field=models.CharField(
                choices=[('opex', 'OPEX'), ('capex', 'CAPEX'), ('cogs', 'COGS')],
                default='opex',
                help_text='Default expense type for this category',
                max_length=10,
            ),
        ),
        # Remove the unique index on code (Django handles this via AlterField removing unique=True)

        # 2. Create ExpenseSubcategory
        migrations.CreateModel(
            name='ExpenseSubcategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('expense_type', models.CharField(
                    choices=[('opex', 'OPEX'), ('capex', 'CAPEX'), ('cogs', 'COGS')],
                    default='opex',
                    help_text='Expense classification type (OPEX / CAPEX / COGS)',
                    max_length=10,
                )),
                ('is_active', models.BooleanField(default=True)),
                ('category', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='subcategories',
                    to='purchasing.expensecategory',
                )),
            ],
            options={
                'verbose_name': 'Expense Subcategory',
                'verbose_name_plural': 'Expense Subcategories',
                'db_table': 'expense_subcategories',
                'ordering': ['category__name', 'name'],
            },
        ),
        migrations.AddIndex(
            model_name='expensesubcategory',
            index=models.Index(fields=['category', 'expense_type'], name='expense_sub_cat_type_idx'),
        ),
        migrations.AddIndex(
            model_name='expensesubcategory',
            index=models.Index(fields=['expense_type', 'is_active'], name='expense_sub_type_active_idx'),
        ),

        # 3. Add new fields to Expense
        migrations.AddField(
            model_name='expense',
            name='document_type',
            field=models.CharField(
                choices=[('expense', 'Expense'), ('invoice', 'Invoice')],
                default='expense',
                help_text='Expense = simple spend; Invoice = supplier invoice with tax',
                max_length=10,
            ),
        ),
        migrations.AddField(
            model_name='expense',
            name='subcategory',
            field=models.ForeignKey(
                blank=True,
                help_text='Specific subcategory within the category',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='expenses',
                to='purchasing.expensesubcategory',
            ),
        ),
        migrations.AddField(
            model_name='expense',
            name='invoice_reference',
            field=models.CharField(
                blank=True,
                help_text='External supplier invoice number',
                max_length=50,
            ),
        ),
        migrations.AddField(
            model_name='expense',
            name='due_date',
            field=models.DateField(
                blank=True,
                help_text='Payment due date (invoices only)',
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='expense',
            name='tax_type',
            field=models.ForeignKey(
                blank=True,
                help_text='VAT / tax type (invoices only)',
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='purchase_expenses',
                to='core.taxtype',
            ),
        ),
        migrations.AddField(
            model_name='expense',
            name='vat_amount',
            field=models.DecimalField(decimal_places=2, default=0, help_text='Calculated VAT amount', max_digits=12),
        ),
        migrations.AddField(
            model_name='expense',
            name='retention_amount',
            field=models.DecimalField(decimal_places=2, default=0, help_text='Retention withheld (invoices only)', max_digits=12),
        ),
        migrations.AddField(
            model_name='expense',
            name='total_amount',
            field=models.DecimalField(decimal_places=2, default=0, help_text='Total after tax and retention', max_digits=12),
        ),
        migrations.AddField(
            model_name='expense',
            name='paid_amount',
            field=models.DecimalField(decimal_places=2, default=0, help_text='Amount paid so far (invoices only)', max_digits=12),
        ),
        migrations.AddField(
            model_name='expense',
            name='status',
            field=models.CharField(
                blank=True,
                choices=[
                    ('pending', 'Pending'), ('approved', 'Approved'), ('paid', 'Paid'),
                    ('partially_paid', 'Partially Paid'), ('overdue', 'Overdue'), ('cancelled', 'Cancelled'),
                ],
                default='',
                help_text='Payment status (invoices only)',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='expense',
            name='payment_date',
            field=models.DateField(blank=True, help_text='Date fully paid', null=True),
        ),

        # 4. Update ExpenseCategory ordering
        migrations.AlterModelOptions(
            name='expensecategory',
            options={
                'ordering': ['name'],
                'verbose_name': 'Expense Category',
                'verbose_name_plural': 'Expense Categories',
            },
        ),

        # 5. Add new Expense indexes
        migrations.AddIndex(
            model_name='expense',
            index=models.Index(fields=['document_type', 'expense_date'], name='expense_doc_type_date_idx'),
        ),
        migrations.AddIndex(
            model_name='expense',
            index=models.Index(fields=['status'], name='expense_status_idx'),
        ),
    ]
