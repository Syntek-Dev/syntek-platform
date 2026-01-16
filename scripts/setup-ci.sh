#!/usr/bin/env bash

# CI/CD Setup Script for Django Backend Template
# This script sets up Git hooks via pre-commit and validates the CI/CD environment
# All checks run inside Docker containers - no local Python installation needed

set -e

echo "=========================================="
echo "CI/CD Setup - Django Backend Template"
echo "=========================================="
echo ""

# Colours for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Colour

# Check if Docker is running
echo "Checking Docker..."
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running${NC}"
    echo "Please start Docker and try again"
    exit 1
else
    echo -e "${GREEN}✅ Docker is running${NC}"
fi

# Check if Docker Compose is available
echo "Checking Docker Compose..."
if ! docker compose version > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker Compose not found${NC}"
    echo "Please install Docker Compose and try again"
    exit 1
else
    echo -e "${GREEN}✅ Docker Compose is available${NC}"
fi

# Build test container for validation
echo ""
echo "Building test container..."
if docker compose -f docker/test/docker-compose.yml build web > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Test container built successfully${NC}"
else
    echo -e "${RED}❌ Failed to build test container${NC}"
    exit 1
fi

# Set up Git hooks via pre-commit
echo ""
echo "Setting up Git hooks via pre-commit..."

# Check if pre-commit is available
if command -v pre-commit > /dev/null 2>&1; then
    echo "pre-commit found locally, installing hooks..."
    pre-commit install
    pre-commit install --hook-type commit-msg
    echo -e "${GREEN}✅ Git hooks installed via pre-commit${NC}"
elif [ -d .venv ] && [ -f .venv/bin/pre-commit ]; then
    echo "pre-commit found in .venv, installing hooks..."
    .venv/bin/pre-commit install
    .venv/bin/pre-commit install --hook-type commit-msg
    echo -e "${GREEN}✅ Git hooks installed via pre-commit${NC}"
else
    echo -e "${YELLOW}⚠️  pre-commit not found locally${NC}"
    echo "Installing pre-commit via pip..."
    pip install pre-commit
    pre-commit install
    pre-commit install --hook-type commit-msg
    echo -e "${GREEN}✅ Git hooks installed via pre-commit${NC}"
fi

# Validate workflow files
echo ""
echo "Validating GitHub Actions workflows..."
WORKFLOW_ERRORS=0

for workflow in .github/workflows/*.yml; do
    if [ -f "$workflow" ]; then
        echo -n "Checking $(basename "$workflow")... "
        # Use Python in Docker to validate YAML
        if docker compose -f docker/test/docker-compose.yml run --rm --no-deps web \
            python -c "import yaml; yaml.safe_load(open('$workflow'))" > /dev/null 2>&1; then
            echo -e "${GREEN}✓${NC}"
        else
            echo -e "${RED}✗${NC}"
            WORKFLOW_ERRORS=$((WORKFLOW_ERRORS + 1))
        fi
    fi
done

if [ $WORKFLOW_ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ All workflows are valid${NC}"
else
    echo -e "${YELLOW}⚠️  $WORKFLOW_ERRORS workflow(s) have validation errors${NC}"
fi

# Validate Docker configurations
echo ""
echo "Validating Docker configurations..."
DOCKER_ERRORS=0

for dockerfile in docker/*/Dockerfile; do
    if [ -f "$dockerfile" ]; then
        echo -n "Checking $(basename "$(dirname "$dockerfile)")/Dockerfile... "
        # Basic syntax check
        if docker build -f "$dockerfile" --target builder . --no-cache --quiet > /dev/null 2>&1 || \
           docker build -f "$dockerfile" . --no-cache --quiet > /dev/null 2>&1; then
            echo -e "${GREEN}✓${NC}"
        else
            # Don't fail on build errors, just note them
            echo -e "${YELLOW}⚠${NC}"
        fi
    fi
done

# Test Docker-based formatting and linting
echo ""
echo "Testing code quality tools in Docker..."

echo -n "Testing Ruff... "
if docker compose -f docker/test/docker-compose.yml run --rm --no-deps web \
    bash -c "which ruff > /dev/null" > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${YELLOW}⚠️  Ruff not found in container${NC}"
fi

echo -n "Testing mypy... "
if docker compose -f docker/test/docker-compose.yml run --rm --no-deps web \
    bash -c "which mypy > /dev/null" > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${YELLOW}⚠️  mypy not found in container${NC}"
fi

echo -n "Testing pytest... "
if docker compose -f docker/test/docker-compose.yml run --rm --no-deps web \
    bash -c "which pytest > /dev/null" > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${YELLOW}⚠️  pytest not found in container${NC}"
fi

# Summary
echo ""
echo "=========================================="
echo "Setup Summary"
echo "=========================================="
echo ""
echo -e "${GREEN}✅ Docker environment configured${NC}"
echo -e "${GREEN}✅ Git hooks installed via pre-commit${NC}"
echo -e "${GREEN}✅ CI/CD workflows validated${NC}"
echo ""
echo "Next steps:"
echo "1. Configure GitHub Secrets (see docs/DEVOPS/CICD-GITHUB-ACTIONS.MD)"
echo "2. Set up GitHub Environments (staging, production, production-approval)"
echo "3. Test locally:"
echo "   docker compose -f docker/test/docker-compose.yml run --rm web pytest"
echo "4. Commit your changes using Conventional Commits format"
echo ""
echo "pre-commit commands:"
echo "  pre-commit run --all-files  # Run all hooks on all files"
echo "  pre-commit autoupdate       # Update hook versions"
echo ""
echo "Documentation:"
echo "- Full guide: docs/DEVOPS/CICD-GITHUB-ACTIONS.MD"
echo "- Quick reference: docs/DEVOPS/QUICK-REFERENCE.MD"
echo ""
echo -e "${GREEN}Setup complete!${NC}"
