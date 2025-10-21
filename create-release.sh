#!/bin/bash
# Create Release Package Script for NRGkick Home Assistant Integration
# Usage: ./create-release.sh [version]
# Example: ./create-release.sh 0.1.0

set -e  # Exit on error

VERSION="$1"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

MANIFEST_PATH="custom_components/nrgkick/manifest.json"

# Check manifest.json exists
if [ ! -f "$MANIFEST_PATH" ]; then
    echo -e "${RED}ERROR: manifest.json not found at $MANIFEST_PATH${NC}"
    exit 1
fi

# Get current version from manifest.json
CURRENT_VERSION=$(grep -o '"version"[[:space:]]*:[[:space:]]*"[^"]*"' "$MANIFEST_PATH" | sed 's/.*"\([^"]*\)".*/\1/')

# Determine if we need to update the version
if [ -z "$VERSION" ]; then
    # No version provided, use current version from manifest
    VERSION="$CURRENT_VERSION"
    echo -e "${CYAN}Using version from manifest.json: $VERSION${NC}"
else
    # Version provided as parameter
    # Validate version format
    if ! [[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        echo -e "${RED}ERROR: Invalid version format. Expected: X.Y.Z (e.g., 0.1.0)${NC}"
        exit 1
    fi

    # Check if version is different from current
    if [ "$VERSION" != "$CURRENT_VERSION" ]; then
        echo -e "${YELLOW}Current version in manifest.json: $CURRENT_VERSION${NC}"
        echo -e "${YELLOW}New version specified: $VERSION${NC}"
        echo ""
        read -p "Update manifest.json to version $VERSION? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            # Update version in manifest.json
            sed -i.bak "s/\"version\": \"$CURRENT_VERSION\"/\"version\": \"$VERSION\"/" "$MANIFEST_PATH"
            rm -f "$MANIFEST_PATH.bak"
            echo -e "${GREEN}[OK] Updated manifest.json to version $VERSION${NC}"
            echo ""
        else
            echo -e "${RED}Aborted. Version not updated.${NC}"
            exit 1
        fi
    else
        echo -e "${CYAN}Version $VERSION matches manifest.json${NC}"
    fi
fi

# Final version validation
if ! [[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo -e "${RED}ERROR: Invalid version format in manifest.json. Expected: X.Y.Z${NC}"
    exit 1
fi

VERSION_TAG="v$VERSION"
ZIP_FILE_NAME="nrgkick-$VERSION_TAG.zip"
RELEASES_DIR="releases"
TEMP_DIR="release-temp"

echo ""
echo -e "${YELLOW}=========================================${NC}"
echo -e "${YELLOW}Creating release package for $VERSION_TAG${NC}"
echo -e "${YELLOW}=========================================${NC}"
echo ""

# Ask if pre-commit hooks should be updated
read -p "Update pre-commit hooks to latest versions? (recommended) (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if command -v pre-commit &> /dev/null; then
        echo -e "${CYAN}Updating pre-commit hooks...${NC}"
        echo ""
        pre-commit autoupdate
        echo ""
        echo -e "${GREEN}[OK] Pre-commit hooks updated${NC}"
        echo ""

        # Check if there are changes to commit
        if ! git diff --quiet .pre-commit-config.yaml; then
            echo -e "${YELLOW}Note: .pre-commit-config.yaml has been updated${NC}"
            echo -e "${YELLOW}These changes will need to be committed separately${NC}"
            echo ""
        fi
    else
        echo -e "${YELLOW}Warning: pre-commit not found, skipping hook updates${NC}"
        echo ""
    fi
else
    echo -e "${YELLOW}Skipping pre-commit hook updates${NC}"
    echo ""
fi

# Ask if validation should be run
read -p "Run validation checks first? (recommended) (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${CYAN}Running validation (excluding integration tests)...${NC}"
    echo ""

    # Activate virtual environment if it exists
    if [ -d "venv" ]; then
        source venv/bin/activate
    else
        echo -e "${YELLOW}Warning: Virtual environment not found at ./venv${NC}"
        echo -e "${YELLOW}Creating virtual environment...${NC}"
        python3 -m venv venv
        source venv/bin/activate
        echo -e "${GREEN}[OK] Virtual environment created${NC}"
    fi

    # Install dependencies
    echo -e "${CYAN}Installing dependencies...${NC}"
    pip install --upgrade pip > /dev/null 2>&1
    pip install -r requirements_dev.txt > /dev/null 2>&1
    echo -e "${GREEN}[OK] Dependencies installed${NC}"
    echo ""

    # Run pre-commit checks
    echo -e "${CYAN}Running pre-commit checks...${NC}"
    if command -v pre-commit &> /dev/null; then
        pre-commit install > /dev/null 2>&1

        # Run pre-commit, but allow it to continue with warnings
        set +e  # Temporarily disable exit on error
        pre-commit run --all-files
        PRE_COMMIT_EXIT=$?
        set -e  # Re-enable exit on error

        if [ $PRE_COMMIT_EXIT -eq 0 ]; then
            echo ""
            echo -e "${GREEN}[OK] All pre-commit checks passed${NC}"
        else
            echo ""
            echo -e "${YELLOW}⚠️  Some pre-commit checks have warnings or made changes${NC}"
            echo -e "${YELLOW}   Review output above for any critical issues${NC}"
        fi
    else
        echo -e "${YELLOW}Warning: pre-commit not found, skipping pre-commit checks${NC}"
    fi
    echo ""

    # Run CI-compatible tests only (excludes integration tests)
    echo -e "${CYAN}Running tests (excluding integration tests that require Home Assistant)...${NC}"
    echo ""

    # Run pytest with marker to exclude integration tests
    set +e  # Temporarily disable exit on error
    pytest tests/ -v -m "not requires_integration" --cov=custom_components.nrgkick --cov-report=term-missing
    PYTEST_EXIT=$?
    set -e  # Re-enable exit on error

    echo ""
    if [ $PYTEST_EXIT -eq 0 ]; then
        echo -e "${GREEN}✅ All CI-compatible tests passed!${NC}"
    else
        echo -e "${RED}❌ Some tests failed${NC}"
        echo ""
        echo -e "${YELLOW}Note: Integration tests requiring Home Assistant are excluded${NC}"
        echo -e "${YELLOW}To run all tests including integration tests, use: ./validate.sh${NC}"
        echo ""
        read -p "Continue with release creation anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo -e "${RED}Release creation aborted${NC}"
            exit 1
        fi
    fi

    echo ""
    echo -e "${GREEN}Validation complete! Continuing with release...${NC}"
    echo ""
else
    echo -e "${YELLOW}Skipping validation. Use ./validate.sh to validate manually.${NC}"
    echo ""
fi

# Create releases directory if it doesn't exist
if [ ! -d "$RELEASES_DIR" ]; then
    mkdir -p "$RELEASES_DIR"
    echo -e "${GREEN}[OK] Created releases directory${NC}"
fi

# Clean up any existing temp directory
if [ -d "$TEMP_DIR" ]; then
    rm -rf "$TEMP_DIR"
fi

# Create temp directory structure
mkdir -p "$TEMP_DIR/nrgkick"

# Copy integration files
echo -e "${CYAN}Copying integration files...${NC}"
SOURCE_DIR="custom_components/nrgkick"

if [ ! -d "$SOURCE_DIR" ]; then
    echo -e "${RED}ERROR: Source directory not found: $SOURCE_DIR${NC}"
    exit 1
fi

cp -r "$SOURCE_DIR"/* "$TEMP_DIR/nrgkick/"
echo -e "${GREEN}[OK] Files copied to temp directory${NC}"

# Create ZIP file
echo -e "${CYAN}Creating ZIP archive...${NC}"
ZIP_PATH="$RELEASES_DIR/$ZIP_FILE_NAME"

if [ -f "$ZIP_PATH" ]; then
    rm -f "$ZIP_PATH"
fi

# Create ZIP archive from temp directory
cd "$TEMP_DIR" && zip -r "../$ZIP_PATH" nrgkick/ > /dev/null && cd ..
echo -e "${GREEN}[OK] ZIP archive created${NC}"

# Clean up temp directory
rm -rf "$TEMP_DIR"
echo -e "${GREEN}[OK] Cleaned up temp directory${NC}"

# Get file size
FILE_SIZE_KB=$(du -k "$ZIP_PATH" | cut -f1)

# Summary
echo ""
echo -e "${YELLOW}================================================${NC}"
echo -e "${YELLOW}  Release Package Created Successfully!${NC}"
echo -e "${YELLOW}================================================${NC}"
echo ""
echo -e "${WHITE}  Version:  $VERSION_TAG${NC}"
echo -e "${WHITE}  File:     $ZIP_FILE_NAME${NC}"
echo -e "${WHITE}  Location: $RELEASES_DIR/${NC}"
echo -e "${WHITE}  Size:     $FILE_SIZE_KB KB${NC}"
echo ""
echo -e "${YELLOW}================================================${NC}"
echo ""
echo -e "${CYAN}Next steps:${NC}"
echo ""
echo "  1. Test the release package by installing it in Home Assistant"
echo ""
echo "  2. Run full validation including integration tests (optional):"
echo "     ./validate.sh"
echo ""
echo "  3. If everything works, commit and tag the release:"
echo "     git add ."
echo "     git commit -m 'Release $VERSION_TAG'"
echo "     git tag -a $VERSION_TAG -m 'Release $VERSION_TAG'"
echo "     git push origin main --tags"
echo ""
echo "  4. Create GitHub release:"
echo "     - Go to: https://github.com/andijakl/nrgkick-homeassistant/releases/new"
echo "     - Select tag: $VERSION_TAG"
echo "     - Upload: $RELEASES_DIR/$ZIP_FILE_NAME"
echo "     - Add release notes"
echo "     - Publish release"
echo ""
