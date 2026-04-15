# 🚀 Quick Start - Load Your Strain Fixtures

## What Changed?

The `terpene_profile` field now accepts **full terpene lists** like:
- `"Myrcene, Caryophyllene, Limonene"`
- `"Alpha-Pinene, Limonene, Caryophyllene, Beta-Pinene"`

Instead of limited choices like `"citrus"` or `"earthy"`.

---

## Run These Commands (Copy & Paste)

```bash
# Navigate to backend and activate virtual environment
cd /Users/patosorio/Projects/pharma-genetics-erp/backend
source ../env/bin/activate

# Create migration for model changes
python manage.py makemigrations genetics

# Apply migrations
python manage.py migrate

# Load fixtures
python manage.py loaddata genetics/fixtures/strain_categories.json
python manage.py loaddata genetics/fixtures/all_strains_2025.json

# Verify
python manage.py shell -c "from genetics.models import Strain; print(f'✅ Loaded {Strain.objects.count()} strains'); [print(f'  - {s.name}') for s in Strain.objects.all()]"
```

---

## Expected Output

```
✅ Loaded 9 strains
  - Chem De La Chem
  - Devil Driver
  - Sherbert Og Fruit
  - Tea Time
  - Tricko Jordan
  - Zunami
  - Watermelon Blast
  - Sour Melon
  - Super Boof
```

---

## Files Modified

1. ✅ **models.py** - Removed terpene choices, now accepts any text
2. ✅ **serializers.py** - Removed `terpene_profile_display` 
3. ✅ **all_strains_2025.json** - Ready to load with full terpene data
4. ✅ **strain_categories.json** - 7 categories ready to load

---

## Alternative: Use the Shell Script

```bash
cd /Users/patosorio/Projects/pharma-genetics-erp/backend
source ../env/bin/activate
python manage.py makemigrations genetics && python manage.py migrate
./genetics/fixtures/load_fixtures.sh
```

---

## Need Help?

See `LOADING_GUIDE.md` for detailed troubleshooting and step-by-step instructions.

