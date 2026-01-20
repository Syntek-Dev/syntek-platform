#!/bin/bash

# --- Configuration ---
# We use a robust 'find' command that prunes these directories specifically.
# Add any other folder names you want to ignore to the list inside the parentheses.
IGNORE_DIRS="-name .git -o -name .venv -o -name venv -o -name node_modules -o -name .vscode -o -name .idea -o -name .pytest_cache -o -name __pycache__ -o -name dist -o -name build -o -name backups -o -name media -o -name static"

# Specific File Paths to ignore (Files)
# We skip the auto-generated test results
IGNORE_FILES="! -path */docs/TESTS/RESULTS/test-*.md"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting Documentation Audit...${NC}\n"

# --- CHECK 1: Confirm READMEs have a tree structure ---
echo "1. Checking README.md files for Tree structure..."

# The logic: Find directories matching IGNORE_DIRS -> Prune them (stop looking)
# OR (-o) Find files named README.md -> Print them -> Pass to grep
MISSING_TREES=$(find . -type d \( $IGNORE_DIRS \) -prune -o -name "README.md" -print | xargs grep -L -E "├──|└──|search-result-tree")

if [ -z "$MISSING_TREES" ]; then
    echo -e "${GREEN}[PASS] All READMEs contain a tree structure.${NC}"
else
    echo -e "${RED}[FAIL] The following READMEs are missing a tree:${NC}"
    echo "$MISSING_TREES" | sed 's/^/  - /'
fi

echo ""

# --- CHECK 2: Confirm all .md files have an Overview ---
echo "2. Checking all .md files for Overview/Executive Summary..."

# Same prune logic, but looking for *.md files
# FIXED HERE: Added $IGNORE_FILES before -print
MISSING_OVERVIEWS=$(find . -type d \( $IGNORE_DIRS \) -prune -o -name "*.md" $IGNORE_FILES -print | xargs grep -L -E "^#+ (Overview|Executive Summary)")

if [ -z "$MISSING_OVERVIEWS" ]; then
    echo -e "${GREEN}[PASS] All .md files have an Overview or Executive Summary.${NC}"
else
    echo -e "${RED}[FAIL] The following files are missing an Overview/Exec Summary:${NC}"
    echo "$MISSING_OVERVIEWS" | sed 's/^/  - /'
fi

echo -e "\n${YELLOW}Audit complete.${NC}"
