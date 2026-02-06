# Loading Genetics Fixtures - Step-by-Step Guide

## Changes Made

✅ **Model Updated**: Removed `terpene_profile` choices to allow full terpene data
✅ **Serializer Updated**: Removed `terpene_profile_display` field
✅ **Fixtures Ready**: `strain_categories.json` and `all_strains_2025.json`

---

## Step 1: Create Migration for Model Changes

```bash
cd backend
source ../env/bin/activate
python manage.py makemigrations genetics -n "update_terpene_profile_field"
```

This will create a new migration file for the terpene_profile field change.

---

## Step 2: Apply Migrations

```bash
python manage.py migrate
```

---

## Step 3: Load Strain Categories First

```bash
python manage.py loaddata genetics/fixtures/strain_categories.json
```

Expected output:
```
Installed 7 object(s) from 1 fixture(s)
```

---

## Step 4: Load Strains

```bash
python manage.py loaddata genetics/fixtures/all_strains_2025.json
```

Expected output:
```
Installed 9 object(s) from 1 fixture(s)
```

---

## Step 5: Verify Data Loaded

```bash
python manage.py shell
```

Then in the Django shell:
```python
from genetics.models import StrainCategory, Strain

# Check categories
print(f"Categories: {StrainCategory.objects.count()}")
StrainCategory.objects.all().values_list('name', flat=True)

# Check strains
print(f"Strains: {Strain.objects.count()}")
for strain in Strain.objects.all():
    print(f"  - {strain.name} ({strain.category.name})")

# Check a specific strain with terpenes
strain = Strain.objects.first()
print(f"\n{strain.name}:")
print(f"  THC: {strain.thc_percentage}%")
print(f"  Terpenes: {strain.terpene_profile}")

exit()
```

---

## Quick Load Script

Alternatively, use the provided script:

```bash
cd backend
source ../env/bin/activate
./genetics/fixtures/load_fixtures.sh
```

**Note**: You may need to update `load_fixtures.sh` to reference `all_strains_2025.json` instead of `strains.json`.

---

## All-in-One Command

If you want to do everything at once:

```bash
cd backend && \
source ../env/bin/activate && \
python manage.py makemigrations genetics && \
python manage.py migrate && \
python manage.py loaddata genetics/fixtures/strain_categories.json && \
python manage.py loaddata genetics/fixtures/all_strains_2025.json && \
echo "✅ All done!"
```

---

## Troubleshooting

### Issue: "No module named 'django'"
**Solution**: Activate the virtual environment first:
```bash
source ../env/bin/activate
```

### Issue: "No such table: strain_categories"
**Solution**: Run migrations first:
```bash
python manage.py migrate
```

### Issue: "Duplicate key value"
**Solution**: Clear existing data first:
```bash
python manage.py shell -c "from genetics.models import Strain, StrainCategory; Strain.objects.all().delete(); StrainCategory.objects.all().delete()"
```

### Issue: Permission denied on .env file
**Solution**: Run with proper permissions or check .env file permissions:
```bash
chmod 644 backend/.env
```

---

## Expected Results

After loading:
- **7 Strain Categories**: 50/50 Hybrid, 70/30 Indica, 70/30 Sativa, etc.
- **9 Strains for 2025**: Chem De La Chem, Devil Driver, Sherbert Og Fruit, Tea Time, Tricko Jordan, Zunami, Watermelon Blast, Sour Melon, Super Boof

---

## Next Steps

1. Access Django Admin: `http://localhost:8000/admin`
2. View strains via API: `http://localhost:8000/api/v1/strains/`
3. Add more strains using the template or admin interface

