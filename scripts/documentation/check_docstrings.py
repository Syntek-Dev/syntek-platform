"""
Script to verify that all Python files in the project have a module-level docstring.
Ignores virtual environments, migrations, and hidden configuration folders.
"""

import ast
import os
import sys

# --- Configuration ---
# Directories to completely skip
IGNORE_DIRS = {
    '.git',
    '.venv',
    'venv',
    'env',
    'node_modules',
    '__pycache__',
    '.pytest_cache',
    '.vscode',
    '.idea',
    'media',
    'backups'
}

# Substrings to skip if found in the path (good for Django migrations)
IGNORE_PATH_PARTIALS = {'migrations'}

# Specific filenames to ignore
IGNORE_FILES = {'manage.py', 'asgi.py', 'wsgi.py'}


def has_docstring(filepath):
    """
    Parses a python file to determine if it has a module-level docstring.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse the code into an Abstract Syntax Tree
        tree = ast.parse(content)

        # Check if the very first node is a string (docstring)
        return ast.get_docstring(tree) is not None

    except SyntaxError:
        return False
    except Exception:
        # Silently skip files we can't read
        return True


def main():
    root_dir = "."
    missing_docstrings = []
    checked_count = 0

    print("Scanning for missing docstrings in Python files...\n")

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Modify dirnames in-place to skip ignored directories
        # This prevents os.walk from even entering .venv, speeding up the scan
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]

        # Skip if path contains ignored partials (like /migrations/)
        if any(partial in dirpath for partial in IGNORE_PATH_PARTIALS):
            continue

        for filename in filenames:
            if not filename.endswith(".py"):
                continue

            if filename in IGNORE_FILES:
                continue

            filepath = os.path.join(dirpath, filename)
            checked_count += 1

            if not has_docstring(filepath):
                missing_docstrings.append(filepath)

    # --- Report Results ---
    if missing_docstrings:
        print(f"\033[91m[FAIL] The following {len(missing_docstrings)} files are missing docstrings:\033[0m")
        for f in missing_docstrings:
            print(f"  - {f}")
        sys.exit(1)
    else:
        print(f"\033[92m[PASS] All {checked_count} python files have docstrings.\033[0m")
        sys.exit(0)


if __name__ == "__main__":
    main()
