#!/usr/bin/env python3
"""Sync user stories from docs/STORIES/ to ClickUp.

This script reads user story markdown files from the docs/STORIES/ directory
and creates or updates corresponding tasks in ClickUp. It handles story points,
priorities, acceptance criteria, and sprint assignments.

Usage:
    python scripts/clickup/sync_stories.py [--folder-path FOLDER_PATH] [--dry-run]

Examples:
    # Sync all stories to ClickUp
    python scripts/clickup/sync_stories.py

    # Sync specific folder
    python scripts/clickup/sync_stories.py --folder-path docs/STORIES/SPRINT-01

    # Preview what would be synced without making changes
    python scripts/clickup/sync_stories.py --dry-run
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any

from clickup_client import get_client


def parse_story_file(file_path: Path) -> Optional[Dict[str, Any]]:
    """Parse a user story markdown file.

    Args:
        file_path: Path to the story markdown file.

    Returns:
        Dictionary containing story data, or None if parsing fails.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract story metadata
    story_data = {
        "file_path": str(file_path),
        "filename": file_path.name,
    }

    # Extract story ID from filename (e.g., US-001.md -> US-001)
    match = re.match(r"(US-\d+)\.md", file_path.name)
    if match:
        story_data["story_id"] = match.group(1)
    else:
        print(f"Warning: Could not extract story ID from {file_path.name}")
        return None

    # Extract title (first # heading)
    title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    if title_match:
        story_data["title"] = title_match.group(1).strip()
    else:
        story_data["title"] = story_data["story_id"]

    # Extract story points
    points_match = re.search(r"\*\*Story Points:\*\*\s*(\d+)", content)
    if points_match:
        story_data["points"] = int(points_match.group(1))

    # Extract priority
    priority_match = re.search(
        r"\*\*Priority:\*\*\s*(Must Have|Should Have|Could Have|Won't Have)",
        content,
        re.IGNORECASE,
    )
    if priority_match:
        priority_text = priority_match.group(1).lower().replace(" ", "_")
        story_data["priority_label"] = priority_text

    # Extract sprint assignment
    sprint_match = re.search(r"\*\*Sprint:\*\*\s*(.+)$", content, re.MULTILINE)
    if sprint_match:
        story_data["sprint"] = sprint_match.group(1).strip()

    # Extract status
    status_match = re.search(r"\*\*Status:\*\*\s*(.+)$", content, re.MULTILINE)
    if status_match:
        story_data["status"] = status_match.group(1).strip()

    # Extract description (text between first heading and ## sections)
    desc_match = re.search(r"^#\s+.+\n\n(.+?)(?=\n##|\Z)", content, re.MULTILINE | re.DOTALL)
    if desc_match:
        story_data["description"] = desc_match.group(1).strip()
    else:
        story_data["description"] = ""

    # Extract acceptance criteria
    ac_match = re.search(
        r"## Acceptance Criteria\n\n(.+?)(?=\n##|\Z)",
        content,
        re.MULTILINE | re.DOTALL,
    )
    if ac_match:
        story_data["acceptance_criteria"] = ac_match.group(1).strip()

    return story_data


def find_or_create_sprint_list(client, sprint_name: str, folder_id: str) -> Optional[str]:
    """Find or create a sprint list in ClickUp.

    Args:
        client: ClickUp client instance.
        sprint_name: Name of the sprint (e.g., "Sprint 01").
        folder_id: ClickUp folder ID for sprints.

    Returns:
        List ID if found or created, None otherwise.
    """
    lists = client.get_lists_in_folder(folder_id)

    for lst in lists:
        if sprint_name.lower() in lst["name"].lower():
            return lst["id"]

    # Sprint not found - would need to create it
    print(f"Warning: Sprint list '{sprint_name}' not found in folder {folder_id}")
    return None


def map_priority_to_clickup(priority_label: str, config: Dict) -> Optional[int]:
    """Map priority label to ClickUp priority number.

    Args:
        priority_label: Priority label (must_have, should_have, etc.).
        config: ClickUp configuration dictionary.

    Returns:
        ClickUp priority number (1-4) or None.
    """
    mapping = config.get("priority_mapping", {})
    return int(mapping.get(priority_label)) if priority_label in mapping else None


def build_task_description(story_data: Dict[str, Any]) -> str:
    """Build formatted task description from story data.

    Args:
        story_data: Parsed story data dictionary.

    Returns:
        Formatted markdown description for ClickUp.
    """
    parts = []

    if story_data.get("description"):
        parts.append(story_data["description"])

    if story_data.get("acceptance_criteria"):
        parts.append("\n\n## Acceptance Criteria\n\n")
        parts.append(story_data["acceptance_criteria"])

    parts.append(f"\n\n---\n*Story ID: {story_data['story_id']}*")

    return "".join(parts)


def sync_story_to_clickup(
    client,
    story_data: Dict[str, Any],
    config: Dict,
    dry_run: bool = False,
) -> Optional[Dict[str, Any]]:
    """Sync a single story to ClickUp.

    Args:
        client: ClickUp client instance.
        story_data: Parsed story data.
        config: ClickUp configuration.
        dry_run: If True, only preview changes without creating tasks.

    Returns:
        Created or updated task data, or None if skipped.
    """
    # Determine target list (sprint or backlog)
    if story_data.get("sprint"):
        list_id = find_or_create_sprint_list(
            client,
            story_data["sprint"],
            config["folders"]["sprints"]["id"],
        )
    else:
        list_id = config["folders"]["backlog"]["list_id"]

    if not list_id:
        print(f"Error: Could not determine list for story {story_data['story_id']}")
        return None

    # Check if task already exists by searching for story ID
    existing_tasks = client.search_tasks(
        query=story_data["story_id"],
        list_ids=[list_id],
    )

    # Map priority
    priority = None
    if story_data.get("priority_label"):
        priority = map_priority_to_clickup(story_data["priority_label"], config)

    # Build task data
    task_name = f"{story_data['story_id']}: {story_data['title']}"
    description = build_task_description(story_data)
    tags = [config["labels"].get(story_data.get("priority_label", ""))]
    tags = [t for t in tags if t]  # Remove None values

    if dry_run:
        print(f"\n[DRY RUN] Would sync story: {story_data['story_id']}")
        print(f"  Title: {task_name}")
        print(f"  List ID: {list_id}")
        print(f"  Priority: {priority}")
        print(f"  Tags: {tags}")
        print(f"  Status: {story_data.get('status', 'Open')}")
        return None

    if existing_tasks:
        # Update existing task
        task_id = existing_tasks[0]["id"]
        print(f"Updating existing task: {story_data['story_id']} (ID: {task_id})")

        task = client.update_task(
            task_id=task_id,
            name=task_name,
            description=description,
            status=story_data.get("status", "Open"),
            priority=priority,
        )
    else:
        # Create new task
        print(f"Creating new task: {story_data['story_id']}")

        task = client.create_task(
            list_id=list_id,
            name=task_name,
            description=description,
            status=story_data.get("status", "Open"),
            priority=priority,
            tags=tags,
        )

    print(f"  ClickUp URL: {task['url']}")
    return task


def main():
    """Main entry point for story sync script."""
    parser = argparse.ArgumentParser(description="Sync user stories from docs to ClickUp")
    parser.add_argument(
        "--folder-path",
        default="docs/STORIES",
        help="Path to stories folder (default: docs/STORIES)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without syncing to ClickUp",
    )

    args = parser.parse_args()

    # Initialize ClickUp client
    try:
        client = get_client()
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Check if stories folder exists
    stories_path = Path(args.folder_path)
    if not stories_path.exists():
        print(f"Error: Stories folder not found: {stories_path}")
        sys.exit(1)

    # Find all story files
    story_files = list(stories_path.glob("**/*.md"))
    if not story_files:
        print(f"No story files found in {stories_path}")
        sys.exit(0)

    print(f"Found {len(story_files)} story files")

    # Sync each story
    success_count = 0
    error_count = 0

    for story_file in story_files:
        try:
            story_data = parse_story_file(story_file)
            if story_data:
                result = sync_story_to_clickup(
                    client,
                    story_data,
                    client.config,
                    dry_run=args.dry_run,
                )
                if result or args.dry_run:
                    success_count += 1
            else:
                error_count += 1
        except Exception as e:
            print(f"Error processing {story_file.name}: {e}")
            error_count += 1

    print(f"\n{'[DRY RUN] ' if args.dry_run else ''}Summary:")
    print(f"  Success: {success_count}")
    print(f"  Errors: {error_count}")


if __name__ == "__main__":
    main()
