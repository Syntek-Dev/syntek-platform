"""
Script to automatically append a placeholder 'Overview' section to markdown files
that are missing one.

This helps quickly bring documentation into compliance with project standards.
It skips ignored directories (e.g., .venv, node_modules) and checks for existing
headers like 'Overview' or 'Executive Summary' before modifying files.
"""

import os
import re

# Same ignore config as before to stay consistent
IGNORE_DIRS = {
    '.git',
    '.venv',
    'venv',
    'env',
    'node_modules',
    '.vscode',
    '.idea',
    'media',
    'backups',
    '.pytest_cache',
    '__pycache__',
    'dist',
    'build',
    'static'
}

TEMPLATE = """
## Overview
"""


def has_overview(content):
    """
    Checks if the content already has an Overview or Executive Summary header.
    """
    return bool(re.search(r'^#+\s+(Overview|Executive Summary)', content, re.MULTILINE | re.IGNORECASE))


def should_skip_file(filepath):
    """
    Returns True if the file should be skipped based on specific path patterns.
    Used for auto-generated test results that are read-only or shouldn't be edited.
    """
    norm_path = os.path.normpath(filepath)
    filename = os.path.basename(filepath)

    # Specific Ignore: Auto-generated test results
    # Pattern: docs/TESTS/RESULTS/test-*.md
    if "docs/TESTS/RESULTS" in norm_path and filename.startswith("test-"):
        return True

    return False


def fix_files(root_dir):
    """
    Walks the directory tree and appends the template to compliant missing files.
    """
    fixed_count = 0

    print("--- Auto-Appending 'Overview' sections ---")

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Filter directories in-place
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]

        for filename in filenames:
            if not filename.endswith(".md"):
                continue

            filepath = os.path.join(dirpath, filename)

            try:
                with open(filepath, 'r+', encoding='utf-8') as f:
                    content = f.read()

                    if not has_overview(content):
                        # Ensure we start on a new line if the file doesn't end with one
                        if content and not content.endswith('\n'):
                            f.write('\n')

                        f.write(TEMPLATE)
                        print(f"Fixed: {filepath}")
                        fixed_count += 1
            except Exception as e:
                print(f"Error fixing {filepath}: {e}")

    print(f"\nSuccessfully added placeholders to {fixed_count} files.")


if __name__ == "__main__":
    fix_files(".")
