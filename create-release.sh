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

# Get version from manifest.json if not provided
if [ -z "$VERSION" ]; then
    echo -e "${CYAN}No version specified, reading from manifest.json...${NC}"
    MANIFEST_PATH="custom_components/nrgkick/manifest.json"

    if [ ! -f "$MANIFEST_PATH" ]; then
        echo -e "${RED}ERROR: manifest.json not found at $MANIFEST_PATH${NC}"
        exit 1
    fi

    # Extract version from manifest.json using grep and sed
    VERSION=$(grep -o '"version"[[:space:]]*:[[:space:]]*"[^"]*"' "$MANIFEST_PATH" | sed 's/.*"\([^"]*\)".*/\1/')
    echo -e "${CYAN}Found version: $VERSION${NC}"
fi

# Validate version format
if ! [[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo -e "${RED}ERROR: Invalid version format. Expected: X.Y.Z (e.g., 0.1.0)${NC}"
    exit 1
fi

VERSION_TAG="v$VERSION"
ZIP_FILE_NAME="nrgkick-$VERSION_TAG.zip"
RELEASES_DIR="releases"
TEMP_DIR="release-temp"

echo ""
echo -e "${YELLOW}Creating release package for version $VERSION_TAG...${NC}"
echo ""

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
echo "  1. git add . && git commit -m 'Prepare release $VERSION_TAG'"
echo "  2. git tag -a $VERSION_TAG -m 'Release $VERSION_TAG'"
echo "  3. git push origin main --tags"
echo "  4. Create GitHub release at:"
echo "     https://github.com/andijakl/nrgkick-homeassistant/releases/new"
echo "  5. Upload $ZIP_FILE_NAME from $RELEASES_DIR/ as release asset"
echo ""
