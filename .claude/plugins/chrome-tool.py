#!/usr/bin/env python3
"""
chrome-tool.py

Detects Google Chrome installation across different operating systems (Linux, macOS, Windows).
Returns structured JSON output for integration with Claude Code agents.
Automatically finds the Chrome binary path and can generate environment variable configurations.
"""

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

# Chrome binary paths by operating system
CHROME_PATHS = {
    "linux": [
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable",
        "/usr/bin/google-chrome-beta",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
        "/snap/bin/chromium",
        "/opt/google/chrome/google-chrome",
        "/opt/google/chrome-beta/google-chrome-beta",
    ],
    "darwin": [  # macOS
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Google Chrome Beta.app/Contents/MacOS/Google Chrome Beta",
        "/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
    ],
    "windows": [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files\Google\Chrome Beta\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome Beta\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%PROGRAMFILES%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%PROGRAMFILES(X86)%\Google\Chrome\Application\chrome.exe"),
    ],
}


def get_os_type() -> str:
    """Get the current operating system type."""
    system = platform.system().lower()
    if system == "darwin":
        return "darwin"
    elif system == "windows":
        return "windows"
    else:
        return "linux"


def find_chrome_binary() -> dict[str, Any]:
    """
    Find Google Chrome binary on the current system.

    Returns:
        Dictionary containing Chrome path information and detection status
    """
    os_type = get_os_type()
    paths_to_check = CHROME_PATHS.get(os_type, CHROME_PATHS["linux"])

    found_binaries = []
    primary_binary = None

    # Check each known path
    for path in paths_to_check:
        expanded_path = os.path.expandvars(path)
        if Path(expanded_path).is_file() and os.access(expanded_path, os.X_OK):
            binary_info = {
                "path": expanded_path,
                "exists": True,
                "executable": True,
            }

            # Try to get version
            try:
                if os_type == "windows":
                    # Windows version detection
                    result = subprocess.run(
                        [expanded_path, "--version"], capture_output=True, text=True, timeout=5
                    )
                else:
                    result = subprocess.run(
                        [expanded_path, "--version"], capture_output=True, text=True, timeout=5
                    )
                if result.returncode == 0:
                    binary_info["version"] = result.stdout.strip()
            except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
                binary_info["version"] = "unknown"

            # Determine type (stable, beta, etc.)
            path_lower = expanded_path.lower()
            if "beta" in path_lower:
                binary_info["type"] = "beta"
            elif "canary" in path_lower:
                binary_info["type"] = "canary"
            elif "chromium" in path_lower:
                binary_info["type"] = "chromium"
            else:
                binary_info["type"] = "stable"

            found_binaries.append(binary_info)

            # Set primary (prefer stable over beta over others)
            if primary_binary is None or (
                binary_info["type"] == "stable" and primary_binary["type"] != "stable"
            ):
                primary_binary = binary_info

    # Also check using 'which' command on Unix-like systems
    if os_type != "windows":
        for cmd in ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser"]:
            which_path = shutil.which(cmd)
            if which_path and not any(b["path"] == which_path for b in found_binaries):
                binary_info = {
                    "path": which_path,
                    "exists": True,
                    "executable": True,
                    "type": "stable" if "stable" in cmd or cmd == "google-chrome" else "chromium",
                }
                try:
                    result = subprocess.run(
                        [which_path, "--version"], capture_output=True, text=True, timeout=5
                    )
                    if result.returncode == 0:
                        binary_info["version"] = result.stdout.strip()
                except (subprocess.TimeoutExpired, subprocess.SubprocessError):
                    binary_info["version"] = "unknown"

                found_binaries.append(binary_info)

                if primary_binary is None or (
                    binary_info["type"] == "stable" and primary_binary["type"] != "stable"
                ):
                    primary_binary = binary_info

    return {
        "os": os_type,
        "os_name": platform.system(),
        "os_version": platform.version(),
        "found": len(found_binaries) > 0,
        "primary": primary_binary,
        "all_binaries": found_binaries,
    }


def generate_env_config(chrome_info: dict[str, Any]) -> dict[str, str]:
    """
    Generate environment variable configuration for Chrome.

    Args:
        chrome_info: Chrome detection results from find_chrome_binary()

    Returns:
        Dictionary of environment variables to set
    """
    env_vars = {}

    if chrome_info.get("found") and chrome_info.get("primary"):
        path = chrome_info["primary"]["path"]
        env_vars["CHROME_PATH"] = path
        env_vars["CHROME_BINARY"] = path
        env_vars["BROWSER_BINARY"] = path
        env_vars["DUSK_CHROME_BINARY"] = path
        env_vars["PUPPETEER_EXECUTABLE_PATH"] = path
        env_vars["PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH"] = path

    return env_vars


def generate_env_file_content(env_vars: dict[str, str]) -> str:
    """
    Generate .env file content for Chrome configuration.

    Args:
        env_vars: Dictionary of environment variables

    Returns:
        String content for .env file
    """
    lines = [
        "# Chrome Configuration (auto-detected)",
        f"# Generated by chrome-tool.py on {platform.node()}",
        f"# OS: {platform.system()} {platform.version()}",
        "",
    ]

    for key, value in env_vars.items():
        lines.append(f"{key}={value}")

    return "\n".join(lines)


def write_env_file(env_vars: dict[str, str], file_path: str = ".env.chrome") -> dict[str, Any]:
    """
    Write Chrome environment variables to a file.

    Args:
        env_vars: Dictionary of environment variables
        file_path: Path to the env file (default: .env.chrome)

    Returns:
        Status dictionary
    """
    try:
        content = generate_env_file_content(env_vars)
        with Path(file_path).open("w") as f:
            f.write(content)
        return {
            "success": True,
            "file": file_path,
            "variables": list(env_vars.keys()),
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


def check_claude_chrome_extension() -> dict[str, Any]:
    """
    Check if Claude in Chrome extension requirements are met.

    Returns:
        Dictionary with extension compatibility information
    """
    chrome_info = find_chrome_binary()

    return {
        "chrome_installed": chrome_info.get("found", False),
        "chrome_path": (
            chrome_info.get("primary", {}).get("path") if chrome_info.get("found") else None
        ),
        "requirements": {
            "google_chrome": chrome_info.get("found", False),
            "extension_note": "Install 'Claude in Chrome' extension (v1.0.36+) from Chrome "
            "Web Store ",
            "claude_code_note": "Run 'claude update' to ensure Claude Code CLI v2.0.73+",
        },
        "setup_commands": [
            "claude update",
            "claude --chrome",
            "/chrome",
        ],
    }


def print_help():
    """Print help message."""


def main():
    command = "detect" if len(sys.argv) < 2 else sys.argv[1].lower()

    if command in ["detect", "status"]:
        result = find_chrome_binary()

    elif command == "env":
        chrome_info = find_chrome_binary()
        env_vars = generate_env_config(chrome_info)
        result = {
            "chrome_detected": chrome_info.get("found", False),
            "env_vars": env_vars,
            "env_content": generate_env_file_content(env_vars) if env_vars else None,
        }

    elif command == "write":
        chrome_info = find_chrome_binary()
        env_vars = generate_env_config(chrome_info)

        if not env_vars:
            result = {
                "success": False,
                "error": "No Chrome installation found",
            }
        else:
            file_path = sys.argv[2] if len(sys.argv) > 2 else ".env.chrome"
            result = write_env_file(env_vars, file_path)
            result["env_vars"] = env_vars

    elif command == "extension":
        result = check_claude_chrome_extension()

    elif command in ["help", "-h", "--help"]:
        print_help()

    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
