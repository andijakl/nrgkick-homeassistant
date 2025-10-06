#!/bin/bash
# Quick Start Script for Bronze Tier Preparation
# This script sets up and runs all code quality checks

set -e  # Exit on error

echo "🎯 NRGkick Bronze Tier Preparation Script"
echo "=========================================="
echo ""

# Check if we're in the right directory
if [ ! -f "custom_components/nrgkick/manifest.json" ]; then
    echo "❌ Error: Please run this script from the repository root"
    exit 1
fi

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "   Python version: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo ""
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo ""
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements_dev.txt > /dev/null 2>&1
pip install pre-commit > /dev/null 2>&1

# Install pre-commit hooks
echo ""
echo "🔗 Installing pre-commit hooks..."
pre-commit install

# Run pre-commit on all files
echo ""
echo "🔍 Running pre-commit checks on all files..."
echo "   (This may take a few minutes on first run)"
echo "   Note: Some warnings (like Pylint code duplication) are acceptable"
echo ""

# Run pre-commit, but allow it to continue with warnings
set +e  # Temporarily disable exit on error
pre-commit run --all-files
PRE_COMMIT_EXIT=$?
set -e  # Re-enable exit on error

if [ $PRE_COMMIT_EXIT -eq 0 ]; then
    echo ""
    echo "✅ All pre-commit checks passed!"
else
    echo ""
    echo "⚠️  Some pre-commit checks have warnings or made changes."
    echo "   Common acceptable warnings:"
    echo "   - Pylint: duplicate-code (structural similarities in entity classes)"
    echo "   - MyPy: abstract-method warnings (Home Assistant handles these)"
    echo ""
    echo "   Critical issues (must fix):"
    echo "   - Syntax errors"
    echo "   - Import errors"
    echo "   - Type errors preventing code execution"
    echo ""
    read -p "Continue with tests? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Exiting. Please review the warnings above."
        exit 1
    fi
fi

# Run tests
echo ""
echo "🧪 Running tests..."
if pytest tests/ -v --cov=custom_components.nrgkick --cov-report=term-missing; then
    echo ""
    echo "✅ All tests passed!"
else
    echo ""
    echo "❌ Some tests failed. Please review the output above."
    exit 1
fi

# Summary
echo ""
echo "=========================================="
echo "🎉 Bronze Tier Preparation Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Review any changes made by pre-commit hooks:"
echo "   git status"
echo "   git diff"
echo ""
echo "2. If changes look good, commit them:"
echo "   git add ."
echo "   git commit -m 'Apply code quality standards for Bronze Tier'"
echo ""
echo "3. Push to GitHub:"
echo "   git push"
echo ""
echo "4. Check that CI/CD workflows pass on GitHub"
echo ""
echo "📚 For more information, see:"
echo "   - BRONZE_TIER_SUMMARY.md - Overview and results"
echo "   - BRONZE_TIER_CHECKLIST.md - Detailed compliance review"
echo "   - ACTION_ITEMS.md - Step-by-step guide"
echo ""
