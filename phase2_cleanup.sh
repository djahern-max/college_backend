#!/bin/bash
# Phase 2 Cleanup - Remove unused features based on user answers

echo "=========================================="
echo "MagicScholar Backend - Phase 2 Cleanup"
echo "=========================================="
echo ""

# Create backup first
echo "📦 Creating Phase 2 backup..."
tar -czf backup_phase2_$(date +%Y%m%d_%H%M%S).tar.gz app/ scripts/ alembic/ 2>/dev/null
echo "✅ Backup created: backup_phase2_$(date +%Y%m%d_%H%M%S).tar.gz"
echo ""

# Remove unused models
echo "🗑️  Removing unused models..."
rm -f app/models/essay.py
rm -f app/models/institution_match.py
echo "✅ Unused models removed (essay, institution_match)"
echo ""

# Remove all image extraction services (manually downloading images now)
echo "🗑️  Removing image extraction services..."
rm -f app/services/image_extractor.py
rm -f app/services/enhanced_image_extractor.py
rm -f app/services/scholarship_image_extractor.py
echo "✅ Image extraction services removed"
echo ""

# Remove image-related scripts
echo "🗑️  Removing image-related scripts..."
rm -f scripts/assign_curated_images.py
rm -f scripts/fix_missing_images.py
echo "✅ Image scripts removed"
echo ""

# Remove TikTok OAuth (keeping Google + LinkedIn)
echo "⚠️  Note: Edit app/api/v1/oauth.py manually to remove TikTok OAuth"
echo "   Lines to remove: /tiktok/url and /tiktok/callback endpoints"
echo ""

# Remove remaining one-time scripts
echo "🗑️  Removing remaining one-time scripts..."
rm -f scripts/import_college_data.py
echo "✅ One-time scripts removed"
echo ""

echo "=========================================="
echo "✨ Phase 2 Cleanup Complete!"
echo "=========================================="
echo ""
echo "Removed:"
echo "  - 2 unused models (essay, institution_match)"
echo "  - 3 image extraction services"
echo "  - 2 image-related scripts"
echo "  - 1 one-time import script"
echo ""
echo "Total: ~8 files removed"
echo ""
echo "⚠️  MANUAL STEPS REQUIRED:"
echo "1. Remove TikTok OAuth from app/api/v1/oauth.py"
echo "2. Drop unused database tables (see database_cleanup.sql)"
echo "3. Test your application thoroughly"
echo ""
