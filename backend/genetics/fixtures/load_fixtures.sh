#!/bin/bash

# Load Genetics Fixtures Script
# This script loads all genetics fixtures in the correct order

cd "$(dirname "$0")/../../" || exit

echo "🔄 Loading Strain Categories..."
python manage.py loaddata genetics/fixtures/strain_categories.json

if [ $? -eq 0 ]; then
    echo "✅ Strain categories loaded successfully"
else
    echo "❌ Failed to load strain categories"
    exit 1
fi

echo ""
echo "🔄 Loading Strains (2025 Catalogue)..."
python manage.py loaddata genetics/fixtures/all_strains_2025.json

if [ $? -eq 0 ]; then
    echo "✅ Strains loaded successfully"
else
    echo "❌ Failed to load strains"
    exit 1
fi

echo ""
echo "🎉 All genetics fixtures loaded successfully!"
echo ""
echo "Summary:"
python manage.py shell -c "
from genetics.models import StrainCategory, Strain
print(f'  - Strain Categories: {StrainCategory.objects.count()}')
print(f'  - Strains: {Strain.objects.count()}')
"

