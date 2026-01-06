#!/usr/bin/env python3
"""Sync sprint stories - integrates sprint and story syncing.

This script coordinates the complete workflow:
1. Reads sprint files to identify which stories belong to each sprint
2. Updates story markdown files with Sprint metadata
3. Syncs stories to ClickUp (creates/updates in backlog)
4. Creates sprint lists in ClickUp
5. Links stories to their assigned sprint lists (stories remain in backlog too)

Stories are LINKED to sprint lists, not moved. This means each story appears
in both the backlog list AND its assigned sprint list.

Usage:
    python scripts/clickup/sync_sprint_stories.py [options]

Examples:
    # Full sync: update stories and move to sprints
    python scripts/clickup/sync_sprint_stories.py

    # Preview changes without syncing
    python scripts/clickup/sync_sprint_stories.py --dry-run

    # Sync specific sprint only
    python scripts/clickup/sync_sprint_stories.py --sprint SPRINT-01
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Set

from clickup_client import get_client


def parse_sprint_file(file_path: Path) -> Optional[Dict[str, Any]]:
    """Parse a sprint markdown file to extract story assignments.

    Args:
        file_path: Path to the sprint markdown file.

    Returns:
        Dictionary containing sprint data with story assignments.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    sprint_data = {
        "file_path": str(file_path),
        "filename": file_path.name,
    }

    # Extract sprint ID from filename
    match = re.match(r"(SPRINT-\d+)", file_path.name, re.IGNORECASE)
    if not match:
        print(f"Warning: Could not extract sprint ID from {file_path.name}")
        return None

    sprint_data["sprint_id"] = match.group(1).upper()
    sprint_data["sprint_number"] = int(re.search(r"\d+", sprint_data["sprint_id"]).group())

    # Extract existing ClickUp list ID if present
    clickup_id_match = re.search(r"<!--\s*CLICKUP_LIST_ID:\s*(\w+)\s*-->", content)
    if clickup_id_match:
        sprint_data["clickup_list_id"] = clickup_id_match.group(1)

    # Extract title
    title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    if title_match:
        sprint_data["title"] = title_match.group(1).strip()
        sprint_data["title"] = re.sub(
            r"^Sprint\s+\d+:\s*", "", sprint_data["title"], flags=re.IGNORECASE
        )
    else:
        sprint_data["title"] = sprint_data["sprint_id"]

    # Extract sprint metadata
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
                sprint_data["stories"].append({
                    "story_id": story_match.group(1).upper(),
                    "priority": "Must Have",
                })

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
                sprint_data["stories"].append({
                    "story_id": story_match.group(1).upper(),
                    "priority": "Should Have",
                })

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
                sprint_data["stories"].append({
                    "story_id": story_match.group(1).upper(),
                    "priority": "Could Have",
                })

    return sprint_data


def add_sprint_metadata_to_story(story_file: Path, sprint_name: str, dry_run: bool = False):
    """Add or update Sprint metadata in a story file.

    Args:
        story_file: Path to the story markdown file.
        sprint_name: Sprint name (e.g., "Sprint 01").
        dry_run: If True, only preview changes.
    """
    with open(story_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Check if Sprint metadata already exists
    if re.search(r"\*\*Sprint:\*\*", content):
        # Update existing Sprint field
        new_content = re.sub(
            r"\*\*Sprint:\*\*\s*[^\n]*",
            f"**Sprint:** {sprint_name}",
            content
        )
        action = "Updated"
    else:
        # Add Sprint field after MoSCoW Priority section
        moscow_section = re.search(
            r"(##\s+MoSCoW Priority\s*\n.*?)(\n##|\Z)",
            content,
            re.MULTILINE | re.DOTALL
        )
        if moscow_section:
            new_content = content[:moscow_section.end(1)] + \
                f"\n\n**Sprint:** {sprint_name}\n" + \
                content[moscow_section.end(1):]
            action = "Added"
        else:
            # Fallback: add after first heading
            new_content = re.sub(
                r"(^#\s+.+$\n\n(?:<!--.*?-->\n\n)?)",
                f"\\1**Sprint:** {sprint_name}\n\n",
                content,
                count=1,
                flags=re.MULTILINE
            )
            action = "Added"

    if dry_run:
        print(f"  [DRY RUN] Would {action.lower()} Sprint field in {story_file.name}")
    else:
        with open(story_file, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"  {action} Sprint field in {story_file.name}")


def find_or_create_sprint_list(
    client,
    sprint_data: Dict[str, Any],
    config: Dict,
    dry_run: bool = False,
) -> Optional[str]:
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

    # Check if list already exists in mapping
    if sprint_data.get("clickup_list_id"):
        try:
            list_data = client.get_list(sprint_data["clickup_list_id"])
            print(f"  Found existing sprint list: {sprint_data['sprint_id']} (ID: {list_data['id']})")
            return list_data["id"]
        except Exception:
            print(f"  ClickUp list ID in file is invalid, will search by name")

    # Search for existing list by name
    lists = client.get_lists_in_folder(folder_id)
    sprint_name = f"{sprint_data['sprint_id']}: {sprint_data['title']}"

    for lst in lists:
        if sprint_data["sprint_id"] in lst["name"]:
            print(f"  Found existing sprint list by name: {sprint_data['sprint_id']} (ID: {lst['id']})")
            return lst["id"]

    if dry_run:
        print(f"  [DRY RUN] Would create sprint list: {sprint_name}")
        return "dry-run-list-id"

    # Create new list
    print(f"  Creating new sprint list: {sprint_name}")

    try:
        description = build_sprint_description(sprint_data)
        new_list = client.create_list(
            folder_id=folder_id,
            name=sprint_name,
            content=description,
        )
        print(f"    Created list: {new_list['id']}")
        return new_list["id"]
    except Exception as e:
        print(f"    ERROR creating list: {e}")
        return None


def build_sprint_description(sprint_data: Dict[str, Any]) -> str:
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


def link_stories_to_sprint(
    client,
    sprint_data: Dict[str, Any],
    list_id: str,
    story_mapping: Dict[str, str],
    dry_run: bool = False,
):
    """Link user stories to the sprint list (keeps them in backlog too).

    This adds stories to the sprint list as additional references, so they
    appear in both the backlog and the sprint list.

    Args:
        client: ClickUp client instance.
        sprint_data: Parsed sprint data.
        list_id: ClickUp list ID for the sprint.
        story_mapping: Mapping of story IDs to ClickUp task IDs.
        dry_run: If True, only preview changes.
    """
    if not sprint_data.get("stories"):
        print(f"  No stories assigned to this sprint")
        return

    print(f"  Linking {len(sprint_data['stories'])} stories to sprint list...")

    linked_count = 0
    skipped_count = 0

    for story in sprint_data["stories"]:
        story_id = story["story_id"]
        clickup_task_id = story_mapping.get(story_id)

        if not clickup_task_id:
            print(f"    Warning: Story {story_id} not found in mapping, skipping")
            skipped_count += 1
            continue

        if dry_run:
            print(f"    [DRY RUN] Would link {story_id} to list {list_id}")
            linked_count += 1
            continue

        try:
            # Get current task to check if already linked to this list
            task = client.get_task(clickup_task_id)

            # Check if task is already in this list (primary or linked)
            task_list_ids = [task.get("list", {}).get("id")]
            # ClickUp returns linked lists in the 'folder' or additional fields
            # but the primary check is the list.id

            if task.get("list", {}).get("id") == list_id:
                print(f"    {story_id} already linked to sprint list, skipping")
                skipped_count += 1
                continue

            # Add task to sprint list (link, not move)
            client.add_task_to_list(clickup_task_id, list_id)
            print(f"    Linked {story_id} to sprint")
            linked_count += 1
        except Exception as e:
            error_msg = str(e)
            if "already" in error_msg.lower() or "exists" in error_msg.lower():
                print(f"    {story_id} already linked to sprint list, skipping")
                skipped_count += 1
            else:
                print(f"    Error linking {story_id}: {e}")
                skipped_count += 1

    print(f"  Summary: {linked_count} linked, {skipped_count} skipped")


def write_clickup_list_id_to_file(file_path: Path, list_id: str):
    """Write ClickUp list ID to the sprint file.

    Args:
        file_path: Path to the sprint file.
        list_id: ClickUp list ID to write.
    """
    with open(file_path, "r", encoding="utf-8") as f:
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

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


def main():
    """Main entry point for integrated sprint/story sync."""
    parser = argparse.ArgumentParser(
        description="Sync sprints and stories to ClickUp with proper list assignment"
    )
    parser.add_argument(
        "--sprint",
        help="Sync specific sprint only (e.g., SPRINT-01)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without syncing to ClickUp",
    )
    parser.add_argument(
        "--skip-story-metadata",
        action="store_true",
        help="Skip updating story files with Sprint metadata",
    )

    args = parser.parse_args()

    # Initialize ClickUp client
    try:
        client = get_client()
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Load story mapping
    mapping_file = Path("config/clickup-story-mapping.json")
    story_mapping = {}
    if mapping_file.exists():
        with open(mapping_file, "r", encoding="utf-8") as f:
            story_mapping = json.load(f)
    else:
        print("Warning: Story mapping file not found")
        print("Run sync_stories_enhanced.py first to create story tasks")
        print("Then run this script to assign them to sprints")
        sys.exit(1)

    # Check if sprints folder exists
    sprints_path = Path("docs/SPRINTS")
    if not sprints_path.exists():
        print(f"Error: Sprints folder not found: {sprints_path}")
        sys.exit(1)

    # Find sprint files
    if args.sprint:
        sprint_files = [
            f for f in sprints_path.glob("*.md")
            if f.name.upper().startswith(args.sprint.upper())
        ]
    else:
        sprint_files = [
            f for f in sprints_path.glob("*.md")
            if re.match(r"SPRINT-\d+", f.name, re.IGNORECASE)
        ]

    if not sprint_files:
        print(f"No sprint files found")
        sys.exit(0)

    print(f"Found {len(sprint_files)} sprint file(s)")
    print(f"Loaded {len(story_mapping)} story mappings\n")

    # Process each sprint
    success_count = 0
    error_count = 0
    sprint_mapping = {}

    # Load existing sprint mapping
    sprint_mapping_file = Path("config/clickup-sprint-mapping.json")
    if sprint_mapping_file.exists():
        with open(sprint_mapping_file, "r", encoding="utf-8") as f:
            sprint_mapping = json.load(f)

    for sprint_file in sorted(sprint_files):
        try:
            print(f"{'='*60}")
            sprint_data = parse_sprint_file(sprint_file)
            if not sprint_data:
                error_count += 1
                continue

            print(f"Processing: {sprint_data['sprint_id']} - {sprint_data['title']}")
            print(f"Stories in sprint: {len(sprint_data.get('stories', []))}")

            # Step 1: Update story files with Sprint metadata
            if not args.skip_story_metadata and sprint_data.get("stories"):
                print(f"\nStep 1: Updating story files with Sprint metadata...")
                stories_path = Path("docs/STORIES")
                sprint_name = f"Sprint {sprint_data['sprint_number']:02d}"

                for story in sprint_data["stories"]:
                    story_id = story["story_id"]
                    # Find story file
                    story_files = list(stories_path.glob(f"{story_id}-*.md"))
                    if story_files:
                        add_sprint_metadata_to_story(
                            story_files[0],
                            sprint_name,
                            dry_run=args.dry_run
                        )
                    else:
                        print(f"  Warning: Story file not found for {story_id}")

            # Step 2: Create or find sprint list
            print(f"\nStep 2: Creating/finding sprint list in ClickUp...")
            list_id = find_or_create_sprint_list(
                client,
                sprint_data,
                client.config,
                dry_run=args.dry_run,
            )

            if not list_id:
                print(f"  ERROR: Could not create/find sprint list")
                error_count += 1
                continue

            # Step 3: Link stories to sprint list (keeps them in backlog too)
            print(f"\nStep 3: Linking stories to sprint list...")
            link_stories_to_sprint(
                client,
                sprint_data,
                list_id,
                story_mapping,
                dry_run=args.dry_run,
            )

            # Step 4: Write list ID back to sprint file
            if not args.dry_run:
                write_clickup_list_id_to_file(sprint_file, list_id)
                print(f"\nStep 4: Updated sprint file with ClickUp list ID")

            success_count += 1
            sprint_mapping[sprint_data["sprint_id"]] = list_id

        except Exception as e:
            print(f"Error processing {sprint_file.name}: {e}")
            import traceback
            traceback.print_exc()
            error_count += 1

    # Save updated sprint mapping
    if not args.dry_run and sprint_mapping:
        with open(sprint_mapping_file, "w", encoding="utf-8") as f:
            json.dump(sprint_mapping, f, indent=2)
        print(f"\nUpdated sprint mapping file: {sprint_mapping_file}")

    print(f"\n{'='*60}")
    print(f"{'[DRY RUN] ' if args.dry_run else ''}Summary:")
    print(f"  Success: {success_count}")
    print(f"  Errors: {error_count}")

    if args.dry_run:
        print(f"\nRun without --dry-run to apply changes")


if __name__ == "__main__":
    main()
