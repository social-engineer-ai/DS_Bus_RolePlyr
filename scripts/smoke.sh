#!/bin/bash

# StakeholderSim Smoke Test
# Run this to verify the stack is working correctly

set -e

echo "=================================="
echo "StakeholderSim Smoke Test"
echo "=================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"
FRONTEND_URL="${FRONTEND_URL:-http://localhost:3000}"

PASSED=0
FAILED=0

# Test function
test_endpoint() {
    local name="$1"
    local url="$2"
    local expected_status="${3:-200}"

    echo -n "Testing: $name... "

    response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")

    if [ "$response" = "$expected_status" ]; then
        echo -e "${GREEN}PASS${NC} (HTTP $response)"
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}FAIL${NC} (Expected $expected_status, got $response)"
        FAILED=$((FAILED + 1))
    fi
}

# Test JSON response
test_json_endpoint() {
    local name="$1"
    local url="$2"
    local key="$3"

    echo -n "Testing: $name... "

    response=$(curl -s "$url" 2>/dev/null || echo "{}")

    if echo "$response" | grep -q "\"$key\""; then
        echo -e "${GREEN}PASS${NC}"
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}FAIL${NC} (Missing key: $key)"
        FAILED=$((FAILED + 1))
    fi
}

echo "Backend Tests"
echo "-------------"

# Health checks
test_endpoint "Health Check" "$BACKEND_URL/health"
test_json_endpoint "Health Response" "$BACKEND_URL/health" "status"

# Readiness check (may fail if DB not ready)
test_endpoint "Readiness Check" "$BACKEND_URL/health/ready"

# Mock auth endpoints
test_json_endpoint "Mock Users List" "$BACKEND_URL/api/v1/auth/mock-users" "users"

# API docs (only in development)
test_endpoint "API Docs" "$BACKEND_URL/docs"

echo ""
echo "Frontend Tests"
echo "--------------"

# Frontend availability
test_endpoint "Frontend Home" "$FRONTEND_URL"

echo ""
echo "=================================="
echo "Results: ${GREEN}$PASSED passed${NC}, ${RED}$FAILED failed${NC}"
echo "=================================="

if [ $FAILED -gt 0 ]; then
    exit 1
fi

echo -e "${GREEN}All smoke tests passed!${NC}"
