# Code Review: Husky Hooks and CI Workflow Update

**Review Date**: 06/01/2026
**Reviewer**: Claude Code Review Agent
**Version**: 0.3.1
**Focus Areas**: CI workflow ruff migration, Husky hooks update, lock file tracking

---

## Table of Contents

- [Code Review: Husky Hooks and CI Workflow Update](#code-review-husky-hooks-and-ci-workflow-update)
  - [Table of Contents](#table-of-contents)
  - [Summary](#summary)
  - [CI Workflow Analysis](#ci-workflow-analysis)
    - [Ruff Migration (Completed)](#ruff-migration-completed)
    - [Missing Validation Steps](#missing-validation-steps)
  - [Husky Configuration Review](#husky-configuration-review)
    - [Critical Issues Found](#critical-issues-found)
    - [Lock File Tracking](#lock-file-tracking)
  - [Tool Configuration Files](#tool-configuration-files)
    - [Confirmed Configurations](#confirmed-configurations)
    - [Configuration Inconsistencies](#configuration-inconsistencies)
  - [Critical Issues](#critical-issues)
    - [1. Husky Pre-commit Hook Uses Deprecated flake8](#1-husky-pre-commit-hook-uses-deprecated-flake8)
    - [2. Missing uv.lock Tracking in post-merge Hook](#2-missing-uvlock-tracking-in-post-merge-hook)
    - [3. Pre-commit Config Still Uses flake8](#3-pre-commit-config-still-uses-flake8)
  - [Improvements](#improvements)
    - [4. Missing Type Checking in Pre-commit Hook](#4-missing-type-checking-in-pre-commit-hook)
    - [5. Missing Prettier and Markdown Linting](#5-missing-prettier-and-markdown-linting)
    - [6. Pre-commit Hook Performance Optimisation](#6-pre-commit-hook-performance-optimisation)
  - [Recommendations](#recommendations)
    - [Immediate Actions (Critical)](#immediate-actions-critical)
    - [Short-term Improvements](#short-term-improvements)
    - [Long-term Optimisations](#long-term-optimisations)
  - [Updated Husky Hook Files](#updated-husky-hook-files)
    - [1. Pre-commit Hook](#1-pre-commit-hook)
    - [2. Pre-push Hook](#2-pre-push-hook)
    - [3. Post-merge Hook](#3-post-merge-hook)
  - [Pre-commit Configuration Update](#pre-commit-configuration-update)
  - [Package.json Scripts Update](#packagejson-scripts-update)
  - [Positive Notes](#positive-notes)
  - [Verdict](#verdict)

---

## Summary

The CI workflow has successfully migrated from flake8 to ruff (commit 84b5047), but the Husky pre-commit
hooks are still referencing the old flake8 tool. Additionally, the hooks do not track or validate
`uv.lock` and `package-lock.json` files, which are present in the project. This creates inconsistency
between local pre-commit checks and CI pipeline validation.

**Key Finding:** The Husky hooks are outdated and will cause developer confusion when local checks
pass but CI fails (or vice versa).

---

## CI Workflow Analysis

### Ruff Migration (Completed)

**File:** `.github/workflows/ci.yml`

**Lines 57-60:**

```yaml
- name: Run Ruff linting
  run: |
    docker compose -f docker/test/docker-compose.yml run --rm web \
      ruff check .
```

**Status:** ✅ Successfully migrated from flake8 to ruff

**Changes Made:**

- Removed `flake8` linting step (previously lines 57-62)
- Removed `pylint` step (previously lines 64-69, was set to `continue-on-error: true`)
- Added `ruff check .` as the primary linter

### Missing Validation Steps

**Issue:** The CI workflow does not validate Markdown or Prettier formatting consistency.

**Current CI Steps:**

1. Black formatting check ✅
2. isort import sorting check ✅
3. Ruff linting ✅
4. mypy type checking ✅
5. Bandit security checks ✅
6. pytest test suite ✅
7. Hadolint Dockerfile linting ✅
8. YAML/JSON validation ✅

**Missing CI Steps:**

- ❌ Markdown linting (markdownlint)
- ❌ Prettier formatting check

---

## Husky Configuration Review

### Critical Issues Found

**File:** `.husky/pre-commit`

**Lines 31-35 - Using Deprecated flake8:**

```bash
echo "Running flake8 linting..."
if ! docker compose -f docker/test/docker-compose.yml run --rm web flake8 . 2>/dev/null; then
  echo "❌ flake8 linting failed"
  exit 1
fi
```

**Problem:** This will fail because flake8 is no longer installed in the Docker image
(replaced by ruff in `pyproject.toml` and CI workflow).

**Expected Behaviour:**

- Developer commits code
- Pre-commit hook runs flake8
- flake8 command fails with "command not found" error
- Commit is blocked even though code may be valid

---

**File:** `.husky/pre-commit`

**Missing:** Ruff linting, Prettier formatting, Markdown linting

**Lines 1-38 - Current Implementation:**

```bash
#!/bin/sh
. "$(dirname "$0")/_/husky.sh"

echo "Running pre-commit checks..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
  echo "⚠️  Docker is not running. Falling back to local pre-commit hooks."
  pre-commit run --all-files
  exit $?
fi

# Run formatting checks in Docker
echo "Checking code formatting with Black..."
if ! docker compose -f docker/test/docker-compose.yml run --rm web black --check . 2>/dev/null; then
  echo "❌ Black formatting check failed"
  echo "Run: docker compose -f docker/test/docker-compose.yml run --rm web black ."
  exit 1
fi

echo "Checking import sorting with isort..."
if ! docker compose -f docker/test/docker-compose.yml run --rm web isort --check-only . 2>/dev/null; then
  echo "❌ isort check failed"
  echo "Run: docker compose -f docker/test/docker-compose.yml run --rm web isort ."
  exit 1
fi

echo "Running flake8 linting..."  # ❌ OUTDATED
if ! docker compose -f docker/test/docker-compose.yml run --rm web flake8 . 2>/dev/null; then
  echo "❌ flake8 linting failed"
  exit 1
fi

echo "✅ All pre-commit checks passed"
exit 0
```

**Problems:**

1. Uses flake8 instead of ruff ❌
2. No Prettier formatting check ❌
3. No Markdown linting check ❌
4. No type checking (mypy) ❌

---

**File:** `.husky/pre-push`

**Current Implementation:** Runs pytest test suite

**Status:** ✅ Correctly implemented

**Note:** This is appropriate for pre-push hooks (tests before pushing to remote).

---

**File:** `.husky/commit-msg`

**Current Implementation:** Validates Conventional Commits format

**Status:** ✅ Correctly implemented

**Pattern:** `^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert|deps)(\(.+\))?: .{1,}`

---

**File:** `.husky/post-merge`

**Lines 12-16 - Missing uv.lock tracking:**

```bash
if echo "$CHANGED_FILES" | grep -q "pyproject.toml"; then
  echo "📦 Python dependencies changed (pyproject.toml)"
  echo "Please rebuild Docker containers:"
  echo "  docker compose -f docker/dev/docker-compose.yml build"
fi
```

**Problem:** Only tracks `pyproject.toml` but not `uv.lock`

**Lines 24-27 - Missing package-lock.json tracking:**

```bash
if echo "$CHANGED_FILES" | grep -q "package.json\|package-lock.json"; then
  echo "📦 Node.js dependencies changed"
  echo "Please run: npm install"
fi
```

**Status:** ✅ This is correctly tracking `package-lock.json`

---

### Lock File Tracking

**Files Present in Repository:**

```
-rw-rw-r--  1 sam-dev sam-dev  47794 Jan  6 16:10 package-lock.json
-rw-rw-r--  1 sam-dev sam-dev 151830 Jan  6 15:42 uv.lock
```

**Current Tracking:**

- ✅ `package-lock.json` - Tracked in `.husky/post-merge`
- ❌ `uv.lock` - Not tracked in any Husky hook

**Impact:** Developers may not rebuild containers after pulling changes that update Python
dependencies via `uv.lock`, leading to version mismatches and confusing errors.

---

## Tool Configuration Files

### Confirmed Configurations

**File:** `pyproject.toml`

**Lines 271-311 - Ruff Configuration:**

```toml
[tool.ruff]
line-length = 100
target-version = "py314"
exclude = [
    ".git",
    ".venv",
    "venv",
    "build",
    "dist",
    "migrations",
    "staticfiles",
    "media",
]

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "DJ",  # flake8-django
    "UP",  # pyupgrade
]
ignore = [
    "E501",  # line too long (handled by formatter)
    "B008",  # do not perform function calls in argument defaults
    "W191",  # indentation contains tabs
]

[tool.ruff.lint.per-file-ignores]
"__init__.py" = ["F401"]
"settings/*.py" = ["F405", "F403"]
```

**Status:** ✅ Properly configured

---

**File:** `.prettierrc`

**Lines 1-55:**

<!-- prettier-ignore -->
```json
{
  "semi": false,
  "singleQuote": true,
  "tabWidth": 2,
  "useTabs": false,
  "trailingComma": "es5",
  "bracketSpacing": true,
  "bracketSameLine": false,
  "arrowParens": "always",
  "printWidth": 100,
  "endOfLine": "lf",
  "plugins": ["prettier-plugin-jinja-template"],
  "overrides": []
}
```

**Status:** ✅ Properly configured

---

**File:** `.markdownlint.json`

**Lines 1-30:**

```json
{
  "$schema": "https://raw.githubusercontent.com/DavidAnson/markdownlint/main/schema/markdownlint-config-schema.json",
  "MD013": {
    "line_length": 120,
    "tables": false,
    "code_blocks": false,
    "headings": false
  }
}
```

**Status:** ✅ Properly configured

---

**File:** `package.json`

**Lines 6-14 - NPM Scripts:**

<!-- prettier-ignore -->
```json
{
  "scripts": {
    "format": "prettier --write .",
    "format:check": "prettier --check . && markdownlint-cli2 '**/*.md' '#node_modules'",
    "format:staged": "prettier --write $(git diff --cached --name-only --diff-filter=ACMR | grep -E '\\.(json|yaml|yml|md|html|css|js|graphql)$' | xargs)",
    "lint": "npm run lint:prettier && npm run lint:markdown",
    "lint:prettier": "prettier --check .",
    "lint:markdown": "markdownlint-cli2 '**/*.md' '#node_modules'",
    "lint:markdown:fix": "markdownlint-cli2 --fix '**/*.md' '#node_modules'",
    "precommit": "npm run format:staged"
  }
}
```

**Status:** ✅ Scripts are available but not integrated into Husky hooks

---

### Configuration Inconsistencies

**Issue 1: Pre-commit Hook vs CI Workflow**

| Tool          | Pre-commit Hook | CI Workflow | Status |
| ------------- | --------------- | ----------- | ------ |
| Black         | ✅ Checked      | ✅ Checked  | ✅     |
| isort         | ✅ Checked      | ✅ Checked  | ✅     |
| flake8        | ✅ Checked      | ❌ Removed  | ❌     |
| ruff          | ❌ Missing      | ✅ Checked  | ❌     |
| mypy          | ❌ Missing      | ✅ Checked  | ❌     |
| prettier      | ❌ Missing      | ❌ Missing  | ⚠️     |
| markdownlint  | ❌ Missing      | ❌ Missing  | ⚠️     |
| pytest        | ✅ Pre-push     | ✅ Checked  | ✅     |
| bandit        | ❌ Missing      | ✅ Checked  | ⚠️     |
| hadolint      | ❌ Missing      | ✅ Checked  | ⚠️     |
| YAML/JSON val | ❌ Missing      | ✅ Checked  | ⚠️     |

**Legend:**

- ✅ Consistent and correct
- ❌ Inconsistent (critical issue)
- ⚠️ Missing from both (improvement opportunity)

---

**Issue 2: Pre-commit Config vs Husky Hooks**

**File:** `.pre-commit-config.yaml`

**Lines 45-55 - flake8 configuration:**

```yaml
# Linting with flake8
- repo: https://github.com/pycqa/flake8
  rev: 7.1.1
  hooks:
    - id: flake8
      args: [--config=.flake8]
      additional_dependencies:
        - flake8-bugbear
        - flake8-django
        - flake8-docstrings
        - flake8-comprehensions
        - flake8-simplify
```

**Problem:** The `.pre-commit-config.yaml` file still references flake8 and does not include ruff.

**Impact:** If developers use `pre-commit run --all-files` (as the Husky fallback suggests),
they will use flake8 instead of ruff, creating further inconsistency.

---

## Critical Issues

### 1. Husky Pre-commit Hook Uses Deprecated flake8

**Location:** `.husky/pre-commit` lines 31-35

**Severity:** 🔴 Critical

**Why:** The pre-commit hook will fail on every commit attempt because flake8 is no longer
installed in the Docker image. This blocks all development work.

**Impact:**

- Developers cannot commit code
- Local validation uses different tool than CI
- Creates confusion and frustration
- Developers may bypass hooks with `--no-verify` flag

**Fix:**

```bash
# Replace lines 31-35
echo "Running Ruff linting..."
if ! docker compose -f docker/test/docker-compose.yml run --rm web ruff check . 2>/dev/null; then
  echo "❌ Ruff linting failed"
  echo "Run: docker compose -f docker/test/docker-compose.yml run --rm web ruff check . --fix"
  exit 1
fi
```

---

### 2. Missing uv.lock Tracking in post-merge Hook

**Location:** `.husky/post-merge` lines 12-16

**Severity:** 🔴 Critical

**Why:** The project uses `uv` for Python dependency management (evidenced by `uv.lock` file),
but the post-merge hook only warns about `pyproject.toml` changes, not `uv.lock` changes.

**Impact:**

- Developers pull changes with updated dependencies
- Their local environment uses outdated dependencies
- Tests fail with confusing errors
- Time wasted debugging version mismatches

**Fix:**

```bash
if echo "$CHANGED_FILES" | grep -q "pyproject.toml\|uv.lock"; then
  echo "📦 Python dependencies changed (pyproject.toml or uv.lock)"
  echo "Please rebuild Docker containers:"
  echo "  docker compose -f docker/dev/docker-compose.yml build"
  echo "Or sync dependencies with:"
  echo "  uv sync"
fi
```

---

### 3. Pre-commit Config Still Uses flake8

**Location:** `.pre-commit-config.yaml` lines 45-55

**Severity:** 🔴 Critical

**Why:** If developers use the pre-commit framework directly (via the fallback in Husky hooks
when Docker is not running), they will run flake8 instead of ruff.

**Impact:**

- Inconsistent validation between environments
- Developers with Docker down get different linting results
- CI may fail when local pre-commit passes

**Fix:** Replace flake8 hook with ruff in `.pre-commit-config.yaml`

```yaml
# Linting with Ruff (replaces flake8)
- repo: https://github.com/astral-sh/ruff-pre-commit
  rev: v0.8.6
  hooks:
    - id: ruff
      args: [--config=pyproject.toml]
    - id: ruff-format
```

---

## Improvements

### 4. Missing Type Checking in Pre-commit Hook

**Location:** `.husky/pre-commit`

**Severity:** ⚠️ Warning

**Why:** The CI runs mypy type checking, but the pre-commit hook does not. This means
developers can commit code that fails type checking in CI.

**Suggestion:** Add mypy check to pre-commit hook (but make it fast)

```bash
echo "Running mypy type checking..."
if ! docker compose -f docker/test/docker-compose.yml run --rm web \
  mypy --config-file=pyproject.toml apps/ api/ config/ 2>/dev/null; then
  echo "⚠️  mypy type checking found issues"
  echo "Run: docker compose -f docker/test/docker-compose.yml run --rm web mypy ."
  # Don't exit 1 - allow commit but warn developer
fi
```

**Note:** Type checking can be slow, so consider making this optional or running it in
pre-push instead.

---

### 5. Missing Prettier and Markdown Linting

**Location:** `.husky/pre-commit`

**Severity:** ⚠️ Warning

**Why:** The project has Prettier and markdownlint configurations, and the documentation
standards require their use, but they are not enforced in pre-commit hooks or CI.

**Suggestion:** Add Prettier and markdownlint checks

```bash
echo "Checking Prettier formatting..."
if ! npm run lint:prettier 2>/dev/null; then
  echo "⚠️  Prettier formatting issues found"
  echo "Run: npm run format"
  # Don't exit 1 - allow commit but warn developer
fi

echo "Checking Markdown linting..."
if ! npm run lint:markdown 2>/dev/null; then
  echo "⚠️  Markdown linting issues found"
  echo "Run: npm run lint:markdown:fix"
  # Don't exit 1 - allow commit but warn developer
fi
```

**Alternative:** Add these checks to CI workflow so they are enforced there.

---

### 6. Pre-commit Hook Performance Optimisation

**Location:** `.husky/pre-commit`

**Severity:** 💡 Nitpick

**Why:** Running Black, isort, and ruff checks on the entire codebase for every commit
is slow and wasteful. Only changed files should be checked.

**Suggestion:** Use `git diff --cached --name-only` to check only staged Python files

```bash
# Get list of staged Python files
STAGED_PY_FILES=$(git diff --cached --name-only --diff-filter=ACMR | grep '\.py$' | xargs)

if [ -n "$STAGED_PY_FILES" ]; then
  echo "Checking code formatting with Black on staged files..."
  if ! docker compose -f docker/test/docker-compose.yml run --rm web \
    black --check $STAGED_PY_FILES 2>/dev/null; then
    echo "❌ Black formatting check failed"
    echo "Run: docker compose -f docker/test/docker-compose.yml run --rm web black $STAGED_PY_FILES"
    exit 1
  fi

  echo "Checking import sorting with isort on staged files..."
  if ! docker compose -f docker/test/docker-compose.yml run --rm web \
    isort --check-only $STAGED_PY_FILES 2>/dev/null; then
    echo "❌ isort check failed"
    echo "Run: docker compose -f docker/test/docker-compose.yml run --rm web isort $STAGED_PY_FILES"
    exit 1
  fi

  echo "Running Ruff linting on staged files..."
  if ! docker compose -f docker/test/docker-compose.yml run --rm web \
    ruff check $STAGED_PY_FILES 2>/dev/null; then
    echo "❌ Ruff linting failed"
    echo "Run: docker compose -f docker/test/docker-compose.yml run --rm web ruff check $STAGED_PY_FILES --fix"
    exit 1
  fi
else
  echo "ℹ️  No Python files staged, skipping Python checks"
fi
```

**Trade-off:** More complex hook logic vs faster commit times. For large codebases,
this optimisation is worth it.

---

## Recommendations

### Immediate Actions (Critical)

1. **Update `.husky/pre-commit` to use ruff instead of flake8**
   - Replace flake8 command with `ruff check .`
   - Update error message to suggest `ruff check . --fix`

2. **Update `.husky/post-merge` to track uv.lock**
   - Add `uv.lock` to the Python dependency change detection
   - Add suggestion to run `uv sync` as an alternative to rebuilding containers

3. **Update `.pre-commit-config.yaml` to use ruff**
   - Replace flake8 hook with ruff-pre-commit
   - Remove flake8 dependencies
   - Ensure consistency with Husky hooks

### Short-term Improvements

4. **Add Prettier and markdownlint to CI workflow**
   - Add a new job to `.github/workflows/ci.yml` for formatting checks
   - Run `npm run lint:prettier` and `npm run lint:markdown`
   - This enforces documentation standards from CLAUDE.md

5. **Add mypy to pre-commit hook (optional warning)**
   - Run mypy in pre-commit but don't block commits
   - Provide helpful warning and fix instructions
   - Consider moving to pre-push for performance

6. **Optimise pre-commit hook to check only staged files**
   - Significantly improves commit speed
   - Reduces Docker container overhead
   - Maintains same validation quality

### Long-term Optimisations

7. **Consider using pre-commit framework exclusively**
   - The project has a comprehensive `.pre-commit-config.yaml`
   - Husky hooks could simply call `pre-commit run --hook-stage=commit`
   - This centralises tool configuration and reduces duplication

8. **Add cache invalidation hints to post-merge hook**
   - Detect changes to Docker Compose files
   - Suggest clearing Docker build cache if performance degrades
   - Detect changes to static files and suggest collectstatic

9. **Add git hook to enforce lock file commits**
   - If `pyproject.toml` is staged, ensure `uv.lock` is also staged
   - If `package.json` is staged, ensure `package-lock.json` is also staged
   - Prevents dependency drift issues

---

## Updated Husky Hook Files

### 1. Pre-commit Hook

**File:** `.husky/pre-commit`

```bash
#!/bin/sh
. "$(dirname "$0")/_/husky.sh"

# Pre-commit hook for Django backend
# This hook runs linting and formatting checks before allowing commits

echo "🔍 Running pre-commit checks..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
  echo "⚠️  Docker is not running. Falling back to pre-commit framework."
  if command -v pre-commit &> /dev/null; then
    pre-commit run --hook-stage=commit
    exit $?
  else
    echo "❌ Docker not running and pre-commit not installed"
    echo "Install pre-commit: pip install pre-commit && pre-commit install"
    exit 1
  fi
fi

# Get list of staged Python files
STAGED_PY_FILES=$(git diff --cached --name-only --diff-filter=ACMR | grep '\.py$' | tr '\n' ' ')

if [ -n "$STAGED_PY_FILES" ]; then
  echo "📝 Checking Python files..."

  # Run formatting checks in Docker
  echo "  → Checking code formatting with Black..."
  if ! docker compose -f docker/test/docker-compose.yml run --rm web \
    black --check $STAGED_PY_FILES 2>/dev/null; then
    echo "❌ Black formatting check failed"
    echo "Fix with: docker compose -f docker/test/docker-compose.yml run --rm web black $STAGED_PY_FILES"
    exit 1
  fi

  echo "  → Checking import sorting with isort..."
  if ! docker compose -f docker/test/docker-compose.yml run --rm web \
    isort --check-only $STAGED_PY_FILES 2>/dev/null; then
    echo "❌ isort check failed"
    echo "Fix with: docker compose -f docker/test/docker-compose.yml run --rm web isort $STAGED_PY_FILES"
    exit 1
  fi

  echo "  → Running Ruff linting..."
  if ! docker compose -f docker/test/docker-compose.yml run --rm web \
    ruff check $STAGED_PY_FILES 2>/dev/null; then
    echo "❌ Ruff linting failed"
    echo "Fix with: docker compose -f docker/test/docker-compose.yml run --rm web ruff check $STAGED_PY_FILES --fix"
    exit 1
  fi
else
  echo "ℹ️  No Python files staged, skipping Python checks"
fi

# Get list of staged files for Prettier/Markdown
STAGED_FORMAT_FILES=$(git diff --cached --name-only --diff-filter=ACMR | grep -E '\.(json|yaml|yml|md|html|css|js|graphql)$' | tr '\n' ' ')

if [ -n "$STAGED_FORMAT_FILES" ]; then
  echo "💅 Checking formatting with Prettier and markdownlint..."

  # Run Prettier check
  if command -v npm &> /dev/null; then
    if ! npm run format:staged 2>/dev/null; then
      echo "⚠️  Prettier formatting issues found (auto-fixed)"
      git add $STAGED_FORMAT_FILES
    fi

    # Run markdownlint on Markdown files
    STAGED_MD_FILES=$(echo "$STAGED_FORMAT_FILES" | tr ' ' '\n' | grep '\.md$' | tr '\n' ' ')
    if [ -n "$STAGED_MD_FILES" ]; then
      if ! npx markdownlint-cli2 $STAGED_MD_FILES 2>/dev/null; then
        echo "⚠️  Markdown linting issues found"
        echo "Fix with: npm run lint:markdown:fix"
        # Don't block commit for markdown issues
      fi
    fi
  else
    echo "⚠️  npm not found, skipping Prettier and markdownlint checks"
  fi
else
  echo "ℹ️  No formatting files staged, skipping Prettier checks"
fi

echo "✅ All pre-commit checks passed"
exit 0
```

---

### 2. Pre-push Hook

**File:** `.husky/pre-push`

```bash
#!/bin/sh
. "$(dirname "$0")/_/husky.sh"

# Pre-push hook for Django backend
# This hook runs tests before allowing pushes

echo "🧪 Running pre-push checks..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
  echo "⚠️  Docker is not running. Skipping Docker-based tests."
  echo "⚠️  Ensure tests pass in CI before merging."
  exit 0
fi

# Check if any test files exist
TEST_COUNT=$(find . -type f \( -name "test_*.py" -o -name "*_test.py" \) -not -path "*/node_modules/*" | wc -l)

if [ "$TEST_COUNT" -eq 0 ]; then
  echo "ℹ️  No test files found, skipping test suite"
  exit 0
fi

# Run tests in Docker
echo "🐳 Starting test services in Docker..."
if ! docker compose -f docker/test/docker-compose.yml up -d db redis mailpit 2>/dev/null; then
  echo "❌ Failed to start test services"
  exit 1
fi

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
for i in {1..30}; do
  if docker compose -f docker/test/docker-compose.yml exec -T db pg_isready -U backend_template 2>/dev/null; then
    echo "✅ Database is ready"
    break
  fi
  if [ $i -eq 30 ]; then
    echo "❌ Database failed to start"
    docker compose -f docker/test/docker-compose.yml down -v 2>/dev/null
    exit 1
  fi
  sleep 2
done

# Run migrations
echo "🔄 Running migrations..."
if ! docker compose -f docker/test/docker-compose.yml run --rm web python manage.py migrate --noinput 2>/dev/null; then
  echo "⚠️  Migrations failed, but continuing with tests"
fi

# Run tests
echo "🧪 Running test suite..."
if ! docker compose -f docker/test/docker-compose.yml run --rm web pytest -x --maxfail=3 2>/dev/null; then
  echo "❌ Tests failed"
  docker compose -f docker/test/docker-compose.yml down -v 2>/dev/null
  exit 1
fi

# Cleanup
echo "🧹 Cleaning up test services..."
docker compose -f docker/test/docker-compose.yml down -v 2>/dev/null

echo "✅ All pre-push checks passed"
exit 0
```

---

### 3. Post-merge Hook

**File:** `.husky/post-merge`

```bash
#!/bin/sh
. "$(dirname "$0")/_/husky.sh"

# Post-merge hook for Django backend
# Runs after git merge or git pull to update dependencies

echo "🔄 Running post-merge checks..."

# Check if requirements files changed
CHANGED_FILES=$(git diff-tree -r --name-only --no-commit-id ORIG_HEAD HEAD)

# Check for Python dependency changes
if echo "$CHANGED_FILES" | grep -q "pyproject.toml\|uv.lock"; then
  echo "📦 Python dependencies changed (pyproject.toml or uv.lock)"
  echo ""
  echo "Please update your environment:"
  echo "  Option 1 (Recommended): Rebuild Docker containers"
  echo "    docker compose -f docker/dev/docker-compose.yml build"
  echo "  Option 2: Sync dependencies with uv"
  echo "    uv sync"
  echo ""
fi

# Check for database migrations
if echo "$CHANGED_FILES" | grep -q "migrations/"; then
  echo "🔄 Migration files changed"
  echo ""
  echo "Please run migrations:"
  echo "  docker compose -f docker/dev/docker-compose.yml run --rm web python manage.py migrate"
  echo "Or use the helper script:"
  echo "  ./scripts/env/dev.sh migrate"
  echo ""
fi

# Check for Node.js dependency changes
if echo "$CHANGED_FILES" | grep -q "package.json\|package-lock.json"; then
  echo "📦 Node.js dependencies changed"
  echo ""
  echo "Please run: npm install"
  echo ""
fi

# Check for Docker Compose changes
if echo "$CHANGED_FILES" | grep -q "docker.*docker-compose.yml"; then
  echo "🐳 Docker Compose configuration changed"
  echo ""
  echo "Please restart containers:"
  echo "  docker compose -f docker/dev/docker-compose.yml down"
  echo "  docker compose -f docker/dev/docker-compose.yml up -d"
  echo ""
fi

# Check for environment example changes
if echo "$CHANGED_FILES" | grep -q "\.env.*\.example"; then
  echo "⚙️  Environment example files changed"
  echo ""
  echo "Please review and update your .env files:"
  echo "  - .env.dev"
  echo "  - .env.test"
  echo ""
fi

exit 0
```

---

## Pre-commit Configuration Update

**File:** `.pre-commit-config.yaml`

**Replace lines 45-67 with:**

```yaml
# Linting with Ruff (replaces flake8 and pylint)
- repo: https://github.com/astral-sh/ruff-pre-commit
  rev: v0.8.6
  hooks:
    - id: ruff
      args: [--config=pyproject.toml]
    - id: ruff-format

# Type checking with mypy
- repo: https://github.com/pre-commit/mirrors-mypy
  rev: v1.14.1
  hooks:
    - id: mypy
      args: [--config-file=pyproject.toml]
      additional_dependencies:
        - django-stubs
        - djangorestframework-stubs
        - types-requests
        - types-PyYAML
      exclude: ^(migrations|tests)/
```

**Remove the flake8 section entirely (lines 45-55)**

---

## Package.json Scripts Update

No changes needed to `package.json` - the scripts are already correct and comprehensive.

**Confirmed Scripts:**

<!-- prettier-ignore -->
```json
{
  "format": "prettier --write .",
  "format:check": "prettier --check . && markdownlint-cli2 '**/*.md' '#node_modules'",
  "format:staged": "prettier --write $(git diff --cached --name-only --diff-filter=ACMR | grep -E '\\.(json|yaml|yml|md|html|css|js|graphql)$' | xargs)",
  "lint": "npm run lint:prettier && npm run lint:markdown",
  "lint:prettier": "prettier --check .",
  "lint:markdown": "markdownlint-cli2 '**/*.md' '#node_modules'",
  "lint:markdown:fix": "markdownlint-cli2 --fix '**/*.md' '#node_modules'",
  "precommit": "npm run format:staged"
}
```

**Status:** ✅ No action required

---

## Positive Notes

What is done well in this project:

1. **Comprehensive CI Workflow**
   - Well-structured with multiple jobs for different concerns
   - Uses Docker BuildKit caching for performance
   - Includes security scanning with Bandit
   - Validates all configuration files (YAML, JSON)
   - Handles missing tests gracefully

2. **Proper Ruff Configuration**
   - Well-configured in `pyproject.toml`
   - Appropriate rule selection for Django projects
   - Sensible per-file ignores for Django conventions

3. **Good Lock File Discipline**
   - Both `uv.lock` and `package-lock.json` are tracked
   - Demonstrates proper dependency management practices

4. **Conventional Commits Enforcement**
   - Commit message validation is comprehensive
   - Provides helpful error messages and examples
   - Enforces consistent commit history

5. **Environment-specific Scripts**
   - Well-organised `scripts/env/` directory structure
   - Proper separation of dev/test/staging/production environments
   - Documented in CLAUDE.md

6. **Documentation Standards**
   - Comprehensive coding standards in CLAUDE.md
   - Properly configured Prettier and markdownlint
   - British English localisation correctly specified

---

## Verdict

**Status:** ❌ Request changes (critical issues found)

**Critical Issues:**

1. Husky pre-commit hook uses deprecated flake8 (will break all commits)
2. uv.lock not tracked in post-merge hook (will cause dependency drift)
3. Pre-commit config still references flake8 (inconsistent fallback behaviour)

**Improvements Needed:**

1. Add type checking to pre-commit hooks
2. Add Prettier and markdownlint to CI or pre-commit
3. Optimise pre-commit hooks to check only staged files

**Priority:**

1. **Critical (Must Fix Immediately):** Update pre-commit hook to use ruff
2. **Critical (Must Fix Immediately):** Track uv.lock in post-merge hook
3. **Critical (Must Fix Immediately):** Update pre-commit config to use ruff
4. **High Priority:** Add formatting checks to CI workflow
5. **Medium Priority:** Optimise pre-commit hook performance
6. **Low Priority:** Add type checking to pre-commit hooks

---

**Next Steps:**

1. Run `/syntek-dev-suite:refactor` to implement the updated Husky hooks
2. Test hooks locally by making a commit and ensuring all checks pass
3. Update `.pre-commit-config.yaml` to replace flake8 with ruff
4. Consider adding Prettier and markdownlint to CI workflow
5. Run `/syntek-dev-suite:completion` to mark this review as complete

## Overview
