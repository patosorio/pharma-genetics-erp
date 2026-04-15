"""
Data migration: seed expense categories and subcategories from the company's chart of accounts.
Source: CSV provided by user (Category, Subcategory, Type).
"""

from django.db import migrations

# (category_name, default_type, [(subcategory_name, expense_type), ...])
EXPENSE_DATA = [
    ("Alquiler", "opex", [
        ("Nave", "opex"),
    ]),
    ("Clones", "cogs", [
        ("Bandejas", "cogs"),
        ("Cubos Clones Lana de Roca", "cogs"),
        ("Cupulas", "cogs"),
        ("Clonex", "cogs"),
        ("Enraizantes", "cogs"),
        ("Packaging", "cogs"),
    ]),
    ("Construccion", "capex", [
        ("Ingenieria", "capex"),
        ("Revestimentos", "capex"),
        ("Obras", "capex"),
        ("Estudio proyecto Pattaya", "capex"),
    ]),
    ("Equipos Cultivo", "capex", [
        ("Paneles Sandwich", "capex"),
        ("Tecnico", "capex"),
        ("Karcher", "capex"),
        ("Par Meter", "capex"),
        ("LED Madres", "capex"),
        ("Aires Acondicionados", "capex"),
        ("Hi-Par", "capex"),
        ("Deshumificadores", "capex"),
        ("Goteros", "capex"),
        ("Cableado", "capex"),
        ("CO2", "capex"),
        ("Mano de obra y transportes", "capex"),
        ("Timer", "capex"),
        ("LED Clones", "capex"),
        ("Fertirigado", "capex"),
        ("Sensores", "capex"),
    ]),
    ("Gastos Bancarios", "opex", [
        ("Comisión divisa", "opex"),
    ]),
    ("Gastos Personal", "opex", [
        ("Sueldos", "opex"),
        ("Gastos Apto. Davide", "opex"),
        ("Apto. Davide", "opex"),
        ("Electricidad Apto. Davide", "opex"),
        ("Apartamento Davide", "opex"),
        ("Internet Apto. Davide", "opex"),
        ("Agua Apto. Davide", "opex"),
        ("Visado Davide", "opex"),
    ]),
    ("Instalaciones", "capex", [
        ("Electricas", "capex"),
        ("Seguridad", "capex"),
    ]),
    ("Legal", "opex", [
        ("Gastos Abogado", "opex"),
    ]),
    ("Licencias y Certificados", "capex", [
        ("Analisis Laboratorio", "capex"),
    ]),
    ("Logistica", "opex", [
        ("Transportes Entrega", "opex"),
    ]),
    ("Madres", "cogs", [
        ("Nutrients", "cogs"),
        ("Coco", "cogs"),
        ("Mantenimiento", "cogs"),
        ("Macetas", "cogs"),
        ("CO2", "cogs"),
    ]),
    ("Mobiliario", "capex", [
        ("Oficina", "capex"),
        ("Estanterias", "capex"),
    ]),
    ("Otos Aprov. Nave", "opex", [
        ("Material Almacen (CAPEX)", "capex"),
        ("Material Almacen (OPEX)", "opex"),
        ("Material Oficina", "opex"),
    ]),
    ("Otros aprovisionamientos", "opex", [
        ("Materiales Almacen", "opex"),
    ]),
    ("Produccion Madres / Clones", "opex", [
        ("Tratamientos", "opex"),
    ]),
    ("Reparaciones y conservación", "opex", [
        ("Maquinaria", "opex"),
        ("Reparacion Equipos Cultivo", "opex"),
    ]),
    ("Reparaciones y mantenimiento", "opex", [
        ("Reparaciones", "opex"),
        ("Reparaciones Instalaciones", "opex"),
    ]),
    ("Servicios externos", "opex", [
        ("Limpieza", "opex"),
        ("Contabilidad", "opex"),
    ]),
    ("Transportes", "opex", [
        ("Material Genetico", "opex"),
    ]),
    ("Utilidades", "opex", [
        ("Internet, Agua y Electricidad", "opex"),
        ("Electricidad Nave", "opex"),
        ("Gastos Varios", "opex"),
        ("Internet", "opex"),
    ]),
    ("Viajes", "opex", [
        ("Vuelos", "opex"),
        ("Alojamientos", "opex"),
        ("Seguros", "opex"),
    ]),
]


def seed_categories(apps, schema_editor):
    ExpenseCategory = apps.get_model('purchasing', 'ExpenseCategory')
    ExpenseSubcategory = apps.get_model('purchasing', 'ExpenseSubcategory')

    for cat_name, cat_type, subcats in EXPENSE_DATA:
        category, _ = ExpenseCategory.objects.get_or_create(
            name=cat_name,
            defaults={'category_type': cat_type, 'is_active': True},
        )
        # Update category_type if it already existed with a different default
        if category.category_type != cat_type:
            category.category_type = cat_type
            category.save(update_fields=['category_type'])

        for sub_name, sub_type in subcats:
            # Use get_or_create to avoid duplicates on re-runs
            ExpenseSubcategory.objects.get_or_create(
                category=category,
                name=sub_name,
                expense_type=sub_type,
                defaults={'is_active': True},
            )


def unseed_categories(apps, schema_editor):
    """Reverse: remove only the seeded subcategories (keep any user-created ones)."""
    ExpenseSubcategory = apps.get_model('purchasing', 'ExpenseSubcategory')
    seeded_names = set()
    for _, _, subcats in EXPENSE_DATA:
        for sub_name, _ in subcats:
            seeded_names.add(sub_name)
    ExpenseSubcategory.objects.filter(name__in=seeded_names).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('purchasing', '0004_expense_subcategory_unified_expense'),
    ]

    operations = [
        migrations.RunPython(seed_categories, unseed_categories),
    ]
