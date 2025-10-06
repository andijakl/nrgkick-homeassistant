#!/usr/bin/env pwsh
# Create Release Package Script for NRGkick Home Assistant Integration
# Usage: .\create-release.ps1 [version]
# Example: .\create-release.ps1 0.1.0

param(
    [Parameter(Mandatory=$false)]
    [string]$Version
)

$ErrorActionPreference = "Stop"

# Get version from manifest.json if not provided
if (-not $Version) {
    Write-Host "No version specified, reading from manifest.json..." -ForegroundColor Cyan
    $manifestPath = "custom_components\nrgkick\manifest.json"

    if (-not (Test-Path $manifestPath)) {
        Write-Host "ERROR: manifest.json not found at $manifestPath" -ForegroundColor Red
        exit 1
    }

    $manifest = Get-Content $manifestPath -Raw | ConvertFrom-Json
    $Version = $manifest.version
    Write-Host "Found version: $Version" -ForegroundColor Cyan
}

# Validate version format
if ($Version -notmatch '^\d+\.\d+\.\d+$') {
    Write-Host "ERROR: Invalid version format. Expected: X.Y.Z (e.g., 0.1.0)" -ForegroundColor Red
    exit 1
}

$versionTag = "v$Version"
$zipFileName = "nrgkick-$versionTag.zip"
$releasesDir = "releases"
$tempDir = "release-temp"

Write-Host ""
Write-Host "Creating release package for version $versionTag..." -ForegroundColor Yellow
Write-Host ""

# Create releases directory if it doesn't exist
if (-not (Test-Path $releasesDir)) {
    New-Item -ItemType Directory -Path $releasesDir -Force | Out-Null
    Write-Host "[OK] Created releases directory" -ForegroundColor Green
}

# Clean up any existing temp directory
if (Test-Path $tempDir) {
    Remove-Item -Path $tempDir -Recurse -Force
}

# Create temp directory structure
New-Item -ItemType Directory -Path "$tempDir\nrgkick" -Force | Out-Null

# Copy integration files
Write-Host "Copying integration files..." -ForegroundColor Cyan
$sourceDir = "custom_components\nrgkick"

if (-not (Test-Path $sourceDir)) {
    Write-Host "ERROR: Source directory not found: $sourceDir" -ForegroundColor Red
    exit 1
}

Copy-Item -Path "$sourceDir\*" -Destination "$tempDir\nrgkick\" -Recurse -Force
Write-Host "[OK] Files copied to temp directory" -ForegroundColor Green

# Create ZIP file
Write-Host "Creating ZIP archive..." -ForegroundColor Cyan
$zipPath = Join-Path $releasesDir $zipFileName

if (Test-Path $zipPath) {
    Remove-Item -Path $zipPath -Force
}

# Use .NET compression for better compatibility
Add-Type -Assembly System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::CreateFromDirectory(
    (Resolve-Path "$tempDir\nrgkick").Path,
    (Join-Path (Get-Location).Path "$releasesDir\$zipFileName")
)

Write-Host "[OK] ZIP archive created" -ForegroundColor Green

# Clean up temp directory
Remove-Item -Path $tempDir -Recurse -Force
Write-Host "[OK] Cleaned up temp directory" -ForegroundColor Green

# Get file size
$fileInfo = Get-Item (Join-Path $releasesDir $zipFileName)
$fileSizeKB = [math]::Round($fileInfo.Length / 1KB, 2)

# Summary
Write-Host ""
Write-Host "================================================" -ForegroundColor Yellow
Write-Host "  Release Package Created Successfully!" -ForegroundColor Yellow
Write-Host "================================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "  Version:  $versionTag" -ForegroundColor White
Write-Host "  File:     $zipFileName" -ForegroundColor White
Write-Host "  Location: $releasesDir\" -ForegroundColor White
Write-Host "  Size:     $fileSizeKB KB" -ForegroundColor White
Write-Host ""
Write-Host "================================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. git add . && git commit -m 'Prepare release $versionTag'"
Write-Host "  2. git tag -a $versionTag -m 'Release $versionTag'"
Write-Host "  3. git push origin main --tags"
Write-Host "  4. Create GitHub release at:"
Write-Host "     https://github.com/andijakl/nrgkick-homeassistant/releases/new"
Write-Host "  5. Upload $zipFileName from $releasesDir\ as release asset"
Write-Host ""
