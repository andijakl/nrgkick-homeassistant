#!/bin/bash
# Test runner script for NRGkick integration
# Usage: ./run-tests.sh [option]

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

show_help() {
    echo -e "${BLUE}NRGkick Test Runner${NC}"
    echo ""
    echo "Usage: ./run-tests.sh [option]"
    echo ""
    echo "Options:"
    echo "  all              Run all tests (requires HA environment)"
    echo "  ci               Run only CI-compatible tests (no integration tests)"
    echo "  integration      Run only integration tests (local only)"
    echo "  api              Run only API tests"
    echo "  coverage         Run CI tests with HTML coverage report"
    echo "  coverage-all     Run all tests with HTML coverage report"
    echo "  help             Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./run-tests.sh ci              # Run what GitHub Actions runs"
    echo "  ./run-tests.sh all             # Run complete test suite"
    echo "  ./run-tests.sh coverage        # Generate coverage report"
}

check_venv() {
    if [[ -z "$VIRTUAL_ENV" ]]; then
        echo -e "${YELLOW}Warning: Virtual environment not activated${NC}"
        echo "Consider running: source venv/bin/activate"
        echo ""
    fi
}

run_all_tests() {
    echo -e "${BLUE}Running all tests...${NC}"
    pytest tests/ -v
}

run_ci_tests() {
    echo -e "${BLUE}Running CI-compatible tests (no integration tests)...${NC}"
    pytest tests/ -v -m "not requires_integration"
}

run_integration_tests() {
    echo -e "${BLUE}Running integration tests only...${NC}"
    echo -e "${YELLOW}Note: These require a full Home Assistant test environment${NC}"
    pytest tests/ -v -m "requires_integration"
}

run_api_tests() {
    echo -e "${BLUE}Running API tests only...${NC}"
    pytest tests/test_api.py -v
}

run_coverage() {
    echo -e "${BLUE}Running CI tests with coverage...${NC}"
    pytest tests/ -v -m "not requires_integration" \
        --cov=custom_components.nrgkick \
        --cov-report=html \
        --cov-report=term
    echo ""
    echo -e "${GREEN}Coverage report generated: htmlcov/index.html${NC}"
    echo "Open with: xdg-open htmlcov/index.html (Linux) or open htmlcov/index.html (macOS)"
}

run_coverage_all() {
    echo -e "${BLUE}Running all tests with coverage...${NC}"
    echo -e "${YELLOW}Note: Integration tests require a full Home Assistant environment${NC}"
    pytest tests/ -v \
        --cov=custom_components.nrgkick \
        --cov-report=html \
        --cov-report=term
    echo ""
    echo -e "${GREEN}Coverage report generated: htmlcov/index.html${NC}"
}

# Main script
check_venv

case "${1:-help}" in
    all)
        run_all_tests
        ;;
    ci)
        run_ci_tests
        ;;
    integration)
        run_integration_tests
        ;;
    api)
        run_api_tests
        ;;
    coverage)
        run_coverage
        ;;
    coverage-all)
        run_coverage_all
        ;;
    help|--help|-h|*)
        show_help
        ;;
esac

# Exit with pytest's exit code if it ran
exit ${?}
