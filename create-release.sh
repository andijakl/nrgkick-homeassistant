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

# Ask if validation should be run
read -p "Run validation checks first? (recommended) (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -f "validate.sh" ]; then
        echo -e "${CYAN}Running validation...${NC}"
        echo ""
        bash validate.sh
        echo ""
        echo -e "${GREEN}Validation passed! Continuing with release...${NC}"
        echo ""
    else
        echo -e "${YELLOW}Warning: validate.sh not found, skipping validation${NC}"
        echo ""
    fi
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
echo "  2. If everything works, commit and tag the release:"
echo "     git add ."
echo "     git commit -m 'Release $VERSION_TAG'"
echo "     git tag -a $VERSION_TAG -m 'Release $VERSION_TAG'"
echo "     git push origin main --tags"
echo ""
echo "  3. Create GitHub release:"
echo "     - Go to: https://github.com/andijakl/nrgkick-homeassistant/releases/new"
echo "     - Select tag: $VERSION_TAG"
echo "     - Upload: $RELEASES_DIR/$ZIP_FILE_NAME"
echo "     - Add release notes"
echo "     - Publish release"
echo ""
