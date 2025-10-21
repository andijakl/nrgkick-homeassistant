#!/bin/bash
# Local HACS Validation Script
# This script performs similar checks to the HACS action
# Note: This is not identical to the official HACS action, but covers the main requirements

set -e

echo "🎯 HACS Local Validation Script"
echo "=========================================="
echo ""

INTEGRATION_PATH="custom_components/nrgkick"
ERRORS=0
WARNINGS=0

# Function to print status
print_check() {
    echo "  [$1] $2"
}

# Check if we're in the right directory
if [ ! -f "$INTEGRATION_PATH/manifest.json" ]; then
    echo "❌ Error: Please run this script from the repository root"
    exit 1
fi

echo "📋 Checking HACS Requirements..."
echo ""

# 1. Check if repository is archived (GitHub API would be needed for this)
echo "🔍 Repository Status Checks"
print_check "SKIP" "archived - Cannot check locally (requires GitHub API)"

# 2. Check repository has description (would need GitHub API)
print_check "SKIP" "description - Cannot check locally (requires GitHub API)"

# 3. Check repository has issues enabled (would need GitHub API)
print_check "SKIP" "issues - Cannot check locally (requires GitHub API)"

# 4. Check repository has topics (would need GitHub API)
print_check "SKIP" "topics - Cannot check locally (requires GitHub API)"

echo ""
echo "🔍 Required Files and Content Checks"

# 5. Check hacs.json exists
if [ -f "hacs.json" ]; then
    print_check "✅" "hacs.json exists"

    # Check hacs.json has required 'name' field
    if grep -q '"name"' hacs.json; then
        print_check "✅" "hacs.json contains 'name' field"
    else
        print_check "❌" "hacs.json missing 'name' field"
        ((ERRORS++))
    fi

    # Validate JSON syntax
    if python3 -c "import json; json.load(open('hacs.json'))" 2>/dev/null; then
        print_check "✅" "hacs.json is valid JSON"
    else
        print_check "❌" "hacs.json is invalid JSON"
        ((ERRORS++))
    fi
else
    print_check "❌" "hacs.json not found"
    ((ERRORS++))
fi

# 6. Check manifest.json exists and is valid
if [ -f "$INTEGRATION_PATH/manifest.json" ]; then
    print_check "✅" "manifest.json exists"

    # Validate JSON syntax
    if python3 -c "import json; json.load(open('$INTEGRATION_PATH/manifest.json'))" 2>/dev/null; then
        print_check "✅" "manifest.json is valid JSON"

        # Check required fields
        MANIFEST=$(cat "$INTEGRATION_PATH/manifest.json")
        REQUIRED_FIELDS=("domain" "name" "version" "documentation" "issue_tracker" "codeowners")

        for field in "${REQUIRED_FIELDS[@]}"; do
            if echo "$MANIFEST" | grep -q "\"$field\""; then
                print_check "✅" "manifest.json has '$field' field"
            else
                print_check "❌" "manifest.json missing '$field' field"
                ((ERRORS++))
            fi
        done
    else
        print_check "❌" "manifest.json is invalid JSON"
        ((ERRORS++))
    fi
else
    print_check "❌" "manifest.json not found"
    ((ERRORS++))
fi

# 7. Check for README or info.md
echo ""
echo "🔍 Documentation Checks"
if [ -f "README.md" ] || [ -f "readme.md" ]; then
    print_check "✅" "README.md exists"

    # Check if README has images (for plugins/themes, optional for integrations)
    if grep -qiE '!\[.*\]\(.*\)|<img' README.md 2>/dev/null; then
        print_check "INFO" "README contains images"
    else
        print_check "INFO" "README has no images (optional for integrations)"
    fi
elif [ -f "INFO.md" ] || [ -f "info.md" ]; then
    print_check "✅" "INFO.md exists"
else
    print_check "⚠️" "No README.md or INFO.md found (warning)"
    ((WARNINGS++))
fi

# 8. Check for LICENSE file
if [ -f "LICENSE" ] || [ -f "LICENSE.md" ] || [ -f "LICENCE" ]; then
    print_check "✅" "LICENSE file exists"
else
    print_check "⚠️" "No LICENSE file found (warning)"
    ((WARNINGS++))
fi

# 9. Check Python files for basic syntax errors
echo ""
echo "🔍 Integration Code Checks"
PYTHON_FILES=$(find "$INTEGRATION_PATH" -name "*.py" -not -path "*/__pycache__/*")
SYNTAX_ERRORS=0

for file in $PYTHON_FILES; do
    if python3 -m py_compile "$file" 2>/dev/null; then
        :  # File is valid
    else
        print_check "❌" "Syntax error in $file"
        ((SYNTAX_ERRORS++))
        ((ERRORS++))
    fi
done

if [ $SYNTAX_ERRORS -eq 0 ]; then
    print_check "✅" "All Python files have valid syntax"
fi

# 10. Check for __init__.py
if [ -f "$INTEGRATION_PATH/__init__.py" ]; then
    print_check "✅" "__init__.py exists"
else
    print_check "❌" "__init__.py not found"
    ((ERRORS++))
fi

# 11. Check for strings.json or translations
if [ -f "$INTEGRATION_PATH/strings.json" ]; then
    print_check "✅" "strings.json exists"

    # Validate JSON
    if python3 -c "import json; json.load(open('$INTEGRATION_PATH/strings.json'))" 2>/dev/null; then
        print_check "✅" "strings.json is valid JSON"
    else
        print_check "❌" "strings.json is invalid JSON"
        ((ERRORS++))
    fi
else
    print_check "⚠️" "strings.json not found (warning)"
    ((WARNINGS++))
fi

# 12. Check content_in_root setting in hacs.json
echo ""
echo "🔍 HACS Configuration Checks"
if [ -f "hacs.json" ]; then
    if grep -q '"content_in_root".*true' hacs.json; then
        print_check "⚠️" "content_in_root is true - files should be in root"
        # For integrations, this should typically be false
        if [ -d "custom_components" ]; then
            print_check "INFO" "custom_components folder exists (content_in_root should be false)"
        fi
    else
        print_check "✅" "content_in_root is false (recommended for integrations)"
    fi
fi

# 13. Check for brands (integrations only)
echo ""
echo "🔍 Brands Repository Check"
print_check "INFO" "Brands check - After publishing, add your integration to:"
print_check "INFO" "  https://github.com/home-assistant/brands"
print_check "INFO" "  Required files: logo.png, icon.png, icon@2x.png"

# 14. Summary
echo ""
echo "=========================================="
echo "📊 Validation Summary"
echo "=========================================="
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo "✅ All local checks passed!"
    echo ""
    echo "Note: Some checks require GitHub API and cannot be validated locally:"
    echo "  - Repository archived status"
    echo "  - Repository description"
    echo "  - Issues enabled"
    echo "  - Repository topics"
    echo ""
    echo "These will be checked when you push to GitHub and the HACS action runs."
else
    if [ $ERRORS -gt 0 ]; then
        echo "❌ Found $ERRORS error(s) that must be fixed"
    fi
    if [ $WARNINGS -gt 0 ]; then
        echo "⚠️  Found $WARNINGS warning(s) (may be acceptable)"
    fi
    echo ""
fi

echo "Next steps:"
echo "1. Fix any errors listed above"
echo "2. Ensure your GitHub repository has:"
echo "   - A description"
echo "   - Issues enabled"
echo "   - Topics/tags set"
echo "   - Not archived"
echo "3. Push your code to GitHub"
echo "4. Check the HACS action results in the Actions tab"
echo "5. Create a release if you haven't already"
echo ""

if [ $ERRORS -gt 0 ]; then
    exit 1
else
    exit 0
fi
