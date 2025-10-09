@echo off
REM Quick Start Script for Commit Preparation (Windows)
REM This script sets up and runs all code quality checks

echo.
echo ====================================
echo NRGkick Commit Preparation
echo ====================================
echo.

REM Check if we're in the right directory
if not exist "custom_components\nrgkick\manifest.json" (
    echo ERROR: Please run this script from the repository root
    exit /b 1
)

REM Check Python version
echo Checking Python version...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python not found. Please install Python 3.11 or newer.
    exit /b 1
)
echo.

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.

REM Install dependencies
echo Installing dependencies...
python -m pip install --upgrade pip >nul 2>&1
pip install -r requirements_dev.txt >nul 2>&1
pip install pre-commit >nul 2>&1
echo Done.
echo.

REM Install pre-commit hooks
echo Installing pre-commit hooks...
pre-commit install
echo.

REM Run pre-commit on all files
echo Running pre-commit checks on all files...
echo (This may take a few minutes on first run)
echo.

pre-commit run --all-files
if %errorlevel% neq 0 (
    echo.
    echo WARNING: Some pre-commit checks failed or made changes.
    echo Review the output above and:
    echo 1. Check what was changed: git diff
    echo 2. Stage the changes: git add .
    echo 3. Re-run this script or commit your changes
    goto :tests
)

echo.
echo All pre-commit checks passed!

:tests
REM Run tests
echo.
echo Running tests...
pytest tests/ -v --cov=custom_components.nrgkick --cov-report=term-missing
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Some tests failed. Please review the output above.
    exit /b 1
)

echo.
echo All tests passed!

REM Summary
echo.
echo ========================================
echo Commit Preparation Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Review any changes made by pre-commit hooks:
echo    git status
echo    git diff
echo.
echo 2. If changes look good, commit them:
echo    git add .
echo    git commit -m "Your commit message"
echo.
echo 3. Push to GitHub:
echo    git push
echo.
echo 4. Check that CI/CD workflows pass on GitHub
echo.

pause
