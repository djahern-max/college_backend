#!/bin/bash
# Backend File Audit Script - Identifies unused files

echo "=========================================="
echo "MagicScholar Backend File Audit"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}1. Checking API Routes Used in main.py${NC}"
echo "------------------------------------------------"
grep "include_router" app/main.py | sed 's/.*import //' | sed 's/\.router.*//' 
echo ""

echo -e "${YELLOW}2. API Files in app/api/v1/${NC}"
echo "------------------------------------------------"
ls -1 app/api/v1/*.py | grep -v __
echo ""

echo -e "${YELLOW}3. Potentially Unused API Files${NC}"
echo "------------------------------------------------"
# List files in api/v1 that aren't imported in main.py
for file in app/api/v1/*.py; do
    filename=$(basename "$file" .py)
    if [ "$filename" != "__init__" ] && [ "$filename" != "deps" ]; then
        if ! grep -q "$filename" app/main.py; then
            echo -e "${RED}❌ $file - NOT imported in main.py${NC}"
        fi
    fi
done
echo ""

echo -e "${YELLOW}4. Old IPEDS/Processing Files${NC}"
echo "------------------------------------------------"
find . -name "*step2*" -o -name "*step3*" -o -name "*s2023*" -o -name "*ic2023*" 2>/dev/null
echo ""

echo -e "${YELLOW}5. Image Processing Services${NC}"
echo "------------------------------------------------"
ls -1 app/services/*image* 2>/dev/null
echo ""

echo -e "${YELLOW}6. Model Files${NC}"
echo "------------------------------------------------"
ls -1 app/models/*.py | grep -v __pycache__ | grep -v __init__
echo ""

echo -e "${YELLOW}7. Checking for Duplicate Models${NC}"
echo "------------------------------------------------"
# Check if college.py and institution.py both exist
if [ -f "app/models/college.py" ] && [ -f "app/models/institution.py" ]; then
    echo -e "${RED}⚠️  Both college.py and institution.py exist - likely duplicates${NC}"
fi

# Check for old IPEDS models
for model in "s2023_is" "step2_ic2023_ay" "step3_s2023_is"; do
    if [ -f "app/models/${model}.py" ]; then
        echo -e "${RED}⚠️  Old IPEDS model found: app/models/${model}.py${NC}"
    fi
done
echo ""

echo -e "${YELLOW}8. __pycache__ Directories (can be removed)${NC}"
echo "------------------------------------------------"
find . -type d -name "__pycache__" | wc -l
echo "directories found"
echo ""

echo -e "${YELLOW}9. .DS_Store Files (Mac artifacts - can be removed)${NC}"
echo "------------------------------------------------"
find . -name ".DS_Store" | wc -l
echo "files found"
echo ""

echo -e "${YELLOW}10. Scripts Directory${NC}"
echo "------------------------------------------------"
ls -1 scripts/*.py 2>/dev/null
echo ""

echo -e "${YELLOW}11. One-Time Import Scripts (likely removable)${NC}"
echo "------------------------------------------------"
for script in "import_step2" "fixed_tuition" "import_tuition" "upload_"; do
    find scripts/ -name "*${script}*" 2>/dev/null | while read file; do
        echo -e "${YELLOW}⚠️  $file - One-time import script${NC}"
    done
done
echo ""

echo -e "${YELLOW}12. Checking OAuth Providers in Use${NC}"
echo "------------------------------------------------"
if [ -f "app/api/v1/oauth.py" ]; then
    echo "OAuth providers configured:"
    grep -E "/(google|linkedin|tiktok|facebook|github)/" app/api/v1/oauth.py | sed 's/.*\/\([a-z]*\)\/.*/\1/' | sort -u
fi
echo ""

echo "=========================================="
echo "Audit Complete!"
echo "=========================================="
echo ""
echo "Next Steps:"
echo "1. Review files marked with ❌ or ⚠️"
echo "2. Create backup: tar -czf backup_\$(date +%Y%m%d).tar.gz app/ scripts/"
echo "3. Remove unused files carefully"
echo "4. Test application after each deletion"
