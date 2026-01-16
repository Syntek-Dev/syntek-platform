#!/usr/bin/env python3
"""Sync sprints from docs/SPRINTS/ to ClickUp.

This script reads sprint markdown files from the docs/SPRINTS/ directory
and creates or updates corresponding lists in ClickUp's sprint folder.
It also links user stories to the sprint lists.

Usage:
    python scripts/clickup/sync_sprints.py [options]

Examples:
    # Sync all sprints to ClickUp
    python scripts/clickup/sync_sprints.py

    # Preview what would be synced without making changes
    python scripts/clickup/sync_sprints.py --dry-run

    # Force update all sprints even if they exist
    python scripts/clickup/sync_sprints.py --force
"""

import argparse
import contextlib
import json
import re
import sys
from pathlib import Path
from typing import Any

from clickup_client import get_client


def parse_sprint_file(file_path: Path) -> dict[str, Any] | None:
    """Parse a sprint markdown file.

    Args:
        file_path: Path to the sprint markdown file.

    Returns:
        Dictionary containing sprint data, or None if parsing fails.
    """
    with Path(file_path).open(encoding="utf-8") as f:
        content = f.read()

    # Extract sprint metadata
    sprint_data = {
        "file_path": str(file_path),
        "filename": file_path.name,
    }

    # Extract sprint ID from filename (e.g., SPRINT-01-CORE-AUTHENTICATION.md -> SPRINT-01)
    match = re.match(r"(SPRINT-\d+)", file_path.name, re.IGNORECASE)
    if match:
        sprint_data["sprint_id"] = match.group(1).upper()
        sprint_data["sprint_number"] = int(re.search(r"\d+", sprint_data["sprint_id"]).group())
    else:
        return None

    # Extract existing ClickUp list ID if present
    clickup_id_match = re.search(r"<!--\s*CLICKUP_LIST_ID:\s*(\w+)\s*-->", content)
    if clickup_id_match:
        sprint_data["clickup_list_id"] = clickup_id_match.group(1)

    # Extract title (first # heading)
    title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    if title_match:
        sprint_data["title"] = title_match.group(1).strip()
        # Remove "Sprint N:" prefix if present
        sprint_data["title"] = re.sub(
            r"^Sprint\s+\d+:\s*", "", sprint_data["title"], flags=re.IGNORECASE
        )
    else:
        sprint_data["title"] = sprint_data["sprint_id"]

    # Extract sprint metadata from front matter
    duration_match = re.search(r"\*\*Sprint Duration:\*\*\s*(.+)$", content, re.MULTILINE)
    if duration_match:
        sprint_data["duration"] = duration_match.group(1).strip()

    capacity_match = re.search(r"\*\*Capacity:\*\*\s*(.+)$", content, re.MULTILINE)
    if capacity_match:
        sprint_data["capacity"] = capacity_match.group(1).strip()

    status_match = re.search(r"\*\*Status:\*\*\s*(.+)$", content, re.MULTILINE)
    if status_match:
        sprint_data["status"] = status_match.group(1).strip()

    # Extract sprint goal
    goal_match = re.search(
        r"##\s+Sprint Goal\s*\n(.*?)(?=\n##|\Z)",
        content,
        re.MULTILINE | re.DOTALL,
    )
    if goal_match:
        sprint_data["goal"] = goal_match.group(1).strip()

    # Extract user stories from MoSCoW tables
    sprint_data["stories"] = []

    # Parse Must Have stories
    must_have_match = re.search(
        r"###\s+Must Have.*?\n\|.*?\n\|.*?\n((?:\|.*?\n)+)",
        content,
        re.MULTILINE | re.DOTALL,
    )
    if must_have_match:
        for row in must_have_match.group(1).split("\n"):
            story_match = re.search(r"\|\s*\[?(US-\d+)\]?", row)
            if story_match:
                sprint_data["stories"].append(
                    {
                        "story_id": story_match.group(1).upper(),
                        "priority": "Must Have",
                    }
                )

    # Parse Should Have stories
    should_have_match = re.search(
        r"###\s+Should Have.*?\n\|.*?\n\|.*?\n((?:\|.*?\n)+)",
        content,
        re.MULTILINE | re.DOTALL,
    )
    if should_have_match:
        for row in should_have_match.group(1).split("\n"):
            story_match = re.search(r"\|\s*\[?(US-\d+)\]?", row)
            if story_match:
                sprint_data["stories"].append(
                    {
                        "story_id": story_match.group(1).upper(),
                        "priority": "Should Have",
                    }
                )

    # Parse Could Have stories
    could_have_match = re.search(
        r"###\s+Could Have.*?\n\|.*?\n\|.*?\n((?:\|.*?\n)+)",
        content,
        re.MULTILINE | re.DOTALL,
    )
    if could_have_match:
        for row in could_have_match.group(1).split("\n"):
            story_match = re.search(r"\|\s*\[?(US-\d+)\]?", row)
            if story_match:
                sprint_data["stories"].append(
                    {
                        "story_id": story_match.group(1).upper(),
                        "priority": "Could Have",
                    }
                )

    return sprint_data


def find_or_create_sprint_list(
    client,
    sprint_data: dict[str, Any],
    config: dict,
    dry_run: bool = False,
) -> str | None:
    """Find or create a sprint list in ClickUp.

    Args:
        client: ClickUp client instance.
        sprint_data: Parsed sprint data.
        config: ClickUp configuration.
        dry_run: If True, only preview changes.

    Returns:
        List ID if found or created, None otherwise.
    """
    folder_id = config["folders"]["sprints"]["id"]

    # Check if list already exists
    if sprint_data.get("clickup_list_id"):
        try:
            list_data = client.get_list(sprint_data["clickup_list_id"])
            return list_data["id"]
        except Exception:
            pass

    # Search for existing list by name
    lists = client.get_lists_in_folder(folder_id)
    sprint_name = f"{sprint_data['sprint_id']}: {sprint_data['title']}"

    for lst in lists:
        if sprint_data["sprint_id"] in lst["name"]:
            return lst["id"]

    if dry_run:
        return None

    # Create new list

    try:
        description = build_sprint_description(sprint_data)
        new_list = client.create_list(
            folder_id=folder_id,
            name=sprint_name,
            content=description,
        )
        return new_list["id"]
    except Exception:
        return None


def build_sprint_description(sprint_data: dict[str, Any]) -> str:
    """Build formatted sprint description.

    Args:
        sprint_data: Parsed sprint data dictionary.

    Returns:
        Formatted markdown description for ClickUp.
    """
    parts = []

    if sprint_data.get("goal"):
        parts.append("## Sprint Goal\n\n")
        parts.append(sprint_data["goal"])

    if sprint_data.get("duration"):
        parts.append(f"\n\n**Duration:** {sprint_data['duration']}")

    if sprint_data.get("capacity"):
        parts.append(f"\n**Capacity:** {sprint_data['capacity']}")

    if sprint_data.get("stories"):
        parts.append("\n\n## User Stories\n\n")
        for story in sprint_data["stories"]:
            parts.append(f"- {story['story_id']} ({story['priority']})\n")

    parts.append(f"\n\n---\n*Sprint ID: {sprint_data['sprint_id']}*")
    parts.append(f"\n*File: {sprint_data['filename']}*")

    return "".join(parts)


def move_stories_to_sprint(
    client,
    sprint_data: dict[str, Any],
    list_id: str,
    story_mapping: dict[str, str],
    dry_run: bool = False,
):
    """Move user stories to the sprint list.

    Args:
        client: ClickUp client instance.
        sprint_data: Parsed sprint data.
        list_id: ClickUp list ID for the sprint.
        story_mapping: Mapping of story IDs to ClickUp task IDs.
        dry_run: If True, only preview changes.
    """
    if not sprint_data.get("stories"):
        return

    for story in sprint_data["stories"]:
        story_id = story["story_id"]
        clickup_task_id = story_mapping.get(story_id)

        if not clickup_task_id:
            continue

        if dry_run:
            continue

        with contextlib.suppress(Exception):
            client.move_task_to_list(clickup_task_id, list_id)


def write_clickup_list_id_to_file(file_path: Path, list_id: str):
    """Write ClickUp list ID to the sprint file.

    Args:
        file_path: Path to the sprint file.
        list_id: ClickUp list ID to write.
    """
    with Path(file_path).open(encoding="utf-8") as f:
        content = f.read()

    # Check if ID already exists
    if re.search(r"<!--\s*CLICKUP_LIST_ID:", content):
        # Update existing ID
        content = re.sub(
            r"<!--\s*CLICKUP_LIST_ID:\s*\w+\s*-->",
            f"<!-- CLICKUP_LIST_ID: {list_id} -->",
            content,
        )
    else:
        # Add ID after the first heading
        content = re.sub(
            r"(^#\s+.+$)",
            f"\\1\n\n<!-- CLICKUP_LIST_ID: {list_id} -->",
            content,
            count=1,
            flags=re.MULTILINE,
        )

    with Path(file_path).open("w", encoding="utf-8") as f:
        f.write(content)


def main():
    """Main entry point for sprint sync script."""
    parser = argparse.ArgumentParser(description="Sync sprints from docs to ClickUp")
    parser.add_argument(
        "--folder-path",
        default="docs/SPRINTS",
        help="Path to sprints folder (default: docs/SPRINTS)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without syncing to ClickUp",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force update existing sprint lists",
    )

    args = parser.parse_args()

    # Initialize ClickUp client
    try:
        client = get_client()
    except ValueError:
        sys.exit(1)

    # Load story mapping
    mapping_file = Path("config/clickup-story-mapping.json")
    story_mapping = {}
    if mapping_file.exists():
        with Path(mapping_file).open(encoding="utf-8") as f:
            story_mapping = json.load(f)
    else:
        pass

    # Check if sprints folder exists
    sprints_path = Path(args.folder_path)
    if not sprints_path.exists():
        sys.exit(1)

    # Find all sprint files (only SPRINT-*.md files)
    sprint_files = [
        f for f in sprints_path.glob("*.md") if re.match(r"SPRINT-\d+", f.name, re.IGNORECASE)
    ]

    if not sprint_files:
        sys.exit(0)

    # Sync each sprint
    success_count = 0
    error_count = 0
    results = []

    for sprint_file in sorted(sprint_files):
        try:
            sprint_data = parse_sprint_file(sprint_file)
            if sprint_data:
                list_id = find_or_create_sprint_list(
                    client,
                    sprint_data,
                    client.config,
                    dry_run=args.dry_run,
                )

                if list_id:
                    # Move stories to sprint
                    move_stories_to_sprint(
                        client,
                        sprint_data,
                        list_id,
                        story_mapping,
                        dry_run=args.dry_run,
                    )

                    success_count += 1
                    results.append(
                        {
                            "sprint_id": sprint_data["sprint_id"],
                            "clickup_list_id": list_id,
                            "file_path": sprint_file,
                        }
                    )

                    # Write ClickUp list ID back to file
                    if not args.dry_run:
                        write_clickup_list_id_to_file(sprint_file, list_id)
                elif args.dry_run:
                    success_count += 1
                else:
                    error_count += 1
            else:
                error_count += 1
        except Exception:
            import traceback

            traceback.print_exc()
            error_count += 1

    if results and not args.dry_run:
        # Save sprint mapping file
        mapping_file = Path("config/clickup-sprint-mapping.json")
        mapping = {}
        if mapping_file.exists():
            with Path(mapping_file).open(encoding="utf-8") as f:
                mapping = json.load(f)

        for result in results:
            mapping[result["sprint_id"]] = result["clickup_list_id"]

        with Path(mapping_file).open("w", encoding="utf-8") as f:
            json.dump(mapping, f, indent=2)


if __name__ == "__main__":
    main()
