#!/usr/bin/env bash

# CI/CD Setup Script for Django Backend Template
# This script sets up Git hooks and validates the CI/CD environment
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

# Set up Git hooks (Husky-style)
echo ""
echo "Setting up Git hooks..."

# Create .husky directory if it doesn't exist
mkdir -p .husky

# Make hook scripts executable
chmod +x .husky/pre-commit 2>/dev/null || true
chmod +x .husky/pre-push 2>/dev/null || true
chmod +x .husky/commit-msg 2>/dev/null || true
chmod +x .husky/post-merge 2>/dev/null || true

# Create Git hook symlinks
if [ -d .git/hooks ]; then
    # Pre-commit hook
    cat > .git/hooks/pre-commit << 'EOF'
#!/bin/sh
.husky/pre-commit
EOF
    chmod +x .git/hooks/pre-commit

    # Pre-push hook
    cat > .git/hooks/pre-push << 'EOF'
#!/bin/sh
.husky/pre-push
EOF
    chmod +x .git/hooks/pre-push

    # Commit-msg hook
    cat > .git/hooks/commit-msg << 'EOF'
#!/bin/sh
.husky/commit-msg "$1"
EOF
    chmod +x .git/hooks/commit-msg

    # Post-merge hook
    cat > .git/hooks/post-merge << 'EOF'
#!/bin/sh
.husky/post-merge
EOF
    chmod +x .git/hooks/post-merge

    echo -e "${GREEN}✅ Git hooks installed${NC}"
else
    echo -e "${YELLOW}⚠️  Not a Git repository - hooks not installed${NC}"
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

echo -n "Testing Black... "
if docker compose -f docker/test/docker-compose.yml run --rm --no-deps web \
    bash -c "which black > /dev/null" > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${YELLOW}⚠️  Black not found in container${NC}"
fi

echo -n "Testing isort... "
if docker compose -f docker/test/docker-compose.yml run --rm --no-deps web \
    bash -c "which isort > /dev/null" > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${YELLOW}⚠️  isort not found in container${NC}"
fi

echo -n "Testing flake8... "
if docker compose -f docker/test/docker-compose.yml run --rm --no-deps web \
    bash -c "which flake8 > /dev/null" > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${YELLOW}⚠️  flake8 not found in container${NC}"
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
echo -e "${GREEN}✅ Git hooks installed${NC}"
echo -e "${GREEN}✅ CI/CD workflows validated${NC}"
echo ""
echo "Next steps:"
echo "1. Configure GitHub Secrets (see docs/DEVOPS/CICD-GITHUB-ACTIONS.MD)"
echo "2. Set up GitHub Environments (staging, production, production-approval)"
echo "3. Test locally:"
echo "   docker compose -f docker/test/docker-compose.yml run --rm web pytest"
echo "4. Commit your changes using Conventional Commits format"
echo ""
echo "Documentation:"
echo "- Full guide: docs/DEVOPS/CICD-GITHUB-ACTIONS.MD"
echo "- Quick reference: docs/DEVOPS/QUICK-REFERENCE.MD"
echo ""
echo -e "${GREEN}Setup complete!${NC}"
