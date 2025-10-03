#!/bin/bash
# Safe Cleanup Script - Removes definitely unused files

echo "=========================================="
echo "MagicScholar Backend - Safe Cleanup"
echo "=========================================="
echo ""

# Create backup first
echo "📦 Creating backup..."
tar -czf backup_$(date +%Y%m%d_%H%M%S).tar.gz app/ scripts/ alembic/ 2>/dev/null
echo "✅ Backup created: backup_$(date +%Y%m%d_%H%M%S).tar.gz"
echo ""

# Remove analysis files (development only)
echo "🗑️  Removing analysis files..."
rm -f profile_field_analysis.py
rm -f profile_field_report.txt
echo "✅ Analysis files removed"
echo ""

# Remove one-time import scripts
echo "🗑️  Removing one-time import scripts..."
rm -f scripts/import_step2_financial_data.py
rm -f scripts/1_fixed_tuition_processor.py
rm -f scripts/2_import_tuition_data.py
rm -f scripts/import_s2023_is.py
echo "✅ Import scripts removed"
echo ""

# Remove one-time image upload scripts
echo "🗑️  Removing one-time image upload scripts..."
rm -f scripts/upload_institution_images.py
rm -f scripts/upload_ma_institution_images.py
rm -f scripts/upload_nh_institution_images.py
rm -f scripts/upload_scholarship_images.py
rm -f scripts/test_upload.py
rm -f scripts/test_single_upload.py
echo "✅ Upload scripts removed"
echo ""

# Remove duplicate image extractor in scripts (keep the one in services)
echo "🗑️  Removing duplicate image extractor..."
rm -f scripts/enhanced_image_extractor.py
echo "✅ Duplicate removed"
echo ""

# Remove unused API endpoint
echo "🗑️  Removing unused API endpoint..."
rm -f app/api/v1/scholarship_images.py
echo "✅ Unused endpoint removed"
echo ""

# Clean any remaining cache
echo "🧹 Cleaning cache files..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null
find . -name ".DS_Store" -delete 2>/dev/null
echo "✅ Cache cleaned"
echo ""

echo "=========================================="
echo "✨ Cleanup Complete!"
echo "=========================================="
echo ""
echo "Removed:"
echo "  - 2 analysis files"
echo "  - 4 one-time import scripts"
echo "  - 6 one-time image upload scripts"
echo "  - 1 duplicate extractor"
echo "  - 1 unused API endpoint"
echo "  - All cache files"
echo ""
echo "Total: ~14 files removed"
echo ""
echo "Next steps:"
echo "1. Test your application: python run.py"
echo "2. If everything works, commit changes"
echo "3. If issues arise, restore from backup"
