#!/usr/bin/env bash

#######################################
# Prettier Setup Script
# Installs Prettier and dependencies for formatting
#######################################

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Prettier Setup for Backend Template${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}Error: Node.js is not installed${NC}"
    echo "Please install Node.js (v20+) from https://nodejs.org/"
    exit 1
fi

NODE_VERSION=$(node --version)
echo -e "${GREEN}✓ Node.js found:${NC} $NODE_VERSION"

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo -e "${RED}Error: npm is not installed${NC}"
    exit 1
fi

NPM_VERSION=$(npm --version)
echo -e "${GREEN}✓ npm found:${NC} $NPM_VERSION"
echo ""

# Navigate to project root
cd "$PROJECT_ROOT"

# Install npm dependencies
echo -e "${YELLOW}Installing npm dependencies...${NC}"
npm install

echo ""
echo -e "${GREEN}✓ Prettier installed successfully${NC}"
echo ""

# Check if pre-commit is installed
if command -v pre-commit &> /dev/null; then
    echo -e "${YELLOW}Updating pre-commit hooks...${NC}"
    pre-commit install
    echo -e "${GREEN}✓ Pre-commit hooks installed${NC}"
else
    echo -e "${YELLOW}Note: pre-commit not found. Install with: pip install pre-commit${NC}"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Available commands:"
echo "  npm run format          - Format all files"
echo "  npm run format:check    - Check formatting without changes"
echo "  npm run format:staged   - Format only staged files"
echo ""
echo "Prettier will automatically format on:"
echo "  - Save in VS Code (if Prettier extension installed)"
echo "  - Git commit (via pre-commit hooks)"
echo ""
echo -e "${GREEN}Happy coding!${NC}"
