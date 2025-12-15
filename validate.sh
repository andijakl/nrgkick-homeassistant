#!/bin/bash
# Validation Script for NRGkick Integration
# This script runs all code quality checks and tests
# Usage: ./validate.sh

set -e  # Exit on error

echo "🎯 NRGkick Code Validation Script"
echo "=========================================="
echo "This will run all code quality checks and tests"
echo ""

# Check if we're in the right directory
if [ ! -f "custom_components/nrgkick/manifest.json" ]; then
    echo "❌ Error: Please run this script from the repository root"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo ""
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo ""
echo "🔧 Activating virtual environment..."
source venv/bin/activate || { echo "❌ Failed to activate virtual environment"; exit 1; }

# Verify virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "❌ Error: Virtual environment not activated"
    echo "   Please run: source venv/bin/activate"
    exit 1
fi
echo "   ✓ Virtual environment activated: $VIRTUAL_ENV"

# Check Python version (from venv)
echo ""
echo "📋 Checking Python version..."
python_version=$(python --version 2>&1 | awk '{print $2}')
python_major=$(echo $python_version | cut -d. -f1)
python_minor=$(echo $python_version | cut -d. -f2)
echo "   Python version: $python_version"

if [ "$python_major" -lt 3 ] || ([ "$python_major" -eq 3 ] && [ "$python_minor" -lt 13 ]); then
    echo "   ⚠️  Warning: Python 3.13+ is recommended for latest dependencies"
    echo "   Current version: $python_version"
    echo "   Some test dependencies require Python 3.13+"
    read -p "   Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Exiting. Please upgrade to Python 3.13+"
        exit 1
    fi
fi

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
echo "   Upgrading pip..."
pip install --upgrade pip --quiet || { echo "❌ Failed to upgrade pip"; exit 1; }
echo "   Installing development requirements..."
pip install -r requirements_dev.txt --quiet || { echo "❌ Failed to install requirements"; exit 1; }
echo "   Installing pre-commit..."
pip install pre-commit --quiet || { echo "❌ Failed to install pre-commit"; exit 1; }
echo "   ✓ Dependencies installed successfully"

# Install pre-commit hooks
echo ""
echo "🔗 Installing pre-commit hooks..."
pre-commit install > /dev/null 2>&1 || { echo "⚠️  Pre-commit hooks installation skipped (may already be installed)"; }

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
echo "   Running complete test suite (including integration tests)"
echo ""
if pytest tests/ -v --cov=custom_components.nrgkick --cov-report=term-missing; then
    echo ""
    echo "✅ All tests passed!"
else
    echo ""
    echo "❌ Some tests failed. Please review the output above."
    exit 1
fi

# Run mypy type checking
echo ""
echo "🔍 Running mypy strict type checking..."
if mypy custom_components/nrgkick; then
    echo ""
    echo "✅ Type checking passed!"
else
    echo ""
    echo "❌ Type errors found. Please review the output above."
    exit 1
fi

# Summary
echo ""
echo "=========================================="
echo "🎉 Validation Complete!"
echo "=========================================="
echo ""
echo "Your code passed all quality checks and tests."
echo ""
echo "Next steps:"
echo "1. Review any changes made by pre-commit hooks:"
echo "   git status"
echo "   git diff"
echo ""
echo "2. Stage and commit your changes:"
echo "   git add ."
echo "   git commit -m 'Your commit message'"
echo ""
echo "3. Push to GitHub:"
echo "   git push"
echo ""
echo "4. For releases, use: ./create-release.sh"
echo ""
