#!/usr/bin/env python3
"""Enhanced sync for user stories from docs/STORIES/ to ClickUp.

This script reads user story markdown files from the docs/STORIES/ directory
and creates or updates corresponding tasks in ClickUp with:
- Custom fields for Story Points and MoSCoW Priority
- Subtasks from the Tasks section
- ClickUp ID writeback to story files

Usage:
    python scripts/clickup/sync_stories_enhanced.py [options]

Examples:
    # Sync all stories to ClickUp
    python scripts/clickup/sync_stories_enhanced.py

    # Sync specific folder
    python scripts/clickup/sync_stories_enhanced.py --folder-path docs/STORIES

    # Preview what would be synced without making changes
    python scripts/clickup/sync_stories_enhanced.py --dry-run

    # Force update all stories even if they exist
    python scripts/clickup/sync_stories_enhanced.py --force
"""

import argparse
import contextlib
import json
import re
import sys
from pathlib import Path
from typing import Any

from clickup_client import get_client


def parse_story_file(file_path: Path) -> dict[str, Any] | None:
    """Parse a user story markdown file.

    Args:
        file_path: Path to the story markdown file.

    Returns:
        Dictionary containing story data, or None if parsing fails.
    """
    with Path(file_path).open(encoding="utf-8") as f:
        content = f.read()

    # Extract story metadata
    story_data = {
        "file_path": str(file_path),
        "filename": file_path.name,
    }

    # Extract story ID from filename (e.g., US-001-USER-AUTHENTICATION.md -> US-001)
    match = re.match(r"(US-\d+)", file_path.name, re.IGNORECASE)
    if match:
        story_data["story_id"] = match.group(1).upper()
    else:
        return None

    # Extract existing ClickUp ID if present
    clickup_id_match = re.search(r"<!--\s*CLICKUP_ID:\s*(\w+)\s*-->", content)
    if clickup_id_match:
        story_data["clickup_id"] = clickup_id_match.group(1)

    # Extract title (first # heading)
    title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    if title_match:
        story_data["title"] = title_match.group(1).strip()
        # Remove "User Story:" prefix if present
        story_data["title"] = re.sub(
            r"^User Story:\s*", "", story_data["title"], flags=re.IGNORECASE
        )
    else:
        story_data["title"] = story_data["story_id"]

    # Extract story points from ## Story Points section
    points_match = re.search(
        r"##\s+Story Points.*?\*\*Estimate:\*\*\s*(\d+)",
        content,
        re.IGNORECASE | re.DOTALL,
    )
    if points_match:
        story_data["points"] = int(points_match.group(1))
    else:
        # Fallback to inline format
        points_match_inline = re.search(r"\*\*Story Points:\*\*\s*(\d+)", content, re.IGNORECASE)
        if points_match_inline:
            story_data["points"] = int(points_match_inline.group(1))

    # Extract MoSCoW priority from ## MoSCoW Priority section
    moscow_section = re.search(
        r"##\s+MoSCoW Priority\s*\n(.*?)(?=\n##|\Z)",
        content,
        re.IGNORECASE | re.DOTALL,
    )
    if moscow_section:
        moscow_content = moscow_section.group(1)
        # Find the first Must/Should/Could/Won't Have
        for priority_type in ["Must Have", "Should Have", "Could Have", "Won't Have"]:
            if (
                f"**{priority_type}:**" in moscow_content
                or f"- **{priority_type}:**" in moscow_content
            ):
                story_data["moscow_priority"] = priority_type
                break

    # Extract description from ## Story section
    story_section = re.search(
        r"##\s+Story\s*\n(.*?)(?=\n##|\Z)",
        content,
        re.MULTILINE | re.DOTALL,
    )
    if story_section:
        story_data["description"] = story_section.group(1).strip()
    else:
        # Fallback: text after title and before first ##
        desc_match = re.search(r"^#\s+.+\n\n(.+?)(?=\n##|\Z)", content, re.MULTILINE | re.DOTALL)
        if desc_match:
            story_data["description"] = desc_match.group(1).strip()
        else:
            story_data["description"] = ""

    # Extract acceptance criteria
    ac_match = re.search(
        r"##\s+Acceptance Criteria\s*\n(.*?)(?=\n##|\Z)",
        content,
        re.MULTILINE | re.DOTALL,
    )
    if ac_match:
        story_data["acceptance_criteria"] = ac_match.group(1).strip()

    # Extract tasks
    tasks_match = re.search(
        r"##\s+Tasks\s*\n(.*?)(?=\n##|\Z)",
        content,
        re.MULTILINE | re.DOTALL,
    )
    if tasks_match:
        tasks_content = tasks_match.group(1)
        story_data["tasks"] = parse_tasks_section(tasks_content)

    return story_data


def parse_tasks_section(tasks_content: str) -> list[dict[str, Any]]:
    """Parse tasks from the Tasks section.

    Args:
        tasks_content: Content of the Tasks section.

    Returns:
        List of task dictionaries grouped by category.
    """
    tasks = []
    current_category = None

    for line in tasks_content.split("\n"):
        line = line.strip()

        # Check for category header (### Backend Tasks, etc.)
        category_match = re.match(r"###\s+(.+)", line)
        if category_match:
            current_category = category_match.group(1).strip()
            continue

        # Check for task item (- [ ] Task description)
        task_match = re.match(r"-\s+\[([x ])\]\s+(.+)", line)
        if task_match:
            is_completed = task_match.group(1).lower() == "x"
            task_description = task_match.group(2).strip()

            tasks.append(
                {
                    "category": current_category,
                    "description": task_description,
                    "completed": is_completed,
                }
            )

    return tasks


def find_or_create_list(client, story_data: dict[str, Any], config: dict) -> str | None:
    """Find or create the appropriate list for a story.

    For now, all stories go to the backlog list. In future versions,
    this could be enhanced to handle sprint assignments.

    Args:
        client: ClickUp client instance.
        story_data: Parsed story data.
        config: ClickUp configuration.

    Returns:
        List ID if found or created, None otherwise.
    """
    # For now, use backlog list
    return config["folders"]["backlog"]["list_id"]


def get_moscow_priority_value(client, list_id: str, moscow_text: str) -> int | None:
    """Get the ClickUp dropdown option ID for a MoSCoW priority.

    Args:
        client: ClickUp client instance.
        list_id: ClickUp list ID.
        moscow_text: MoSCoW priority text (e.g., "Must Have").

    Returns:
        Option index for the dropdown field, or None if not found.
    """
    field = client.find_custom_field_by_name(list_id, "MoSCoW Priority")
    if not field:
        return None

    # Find the option that matches
    options = field.get("type_config", {}).get("options", [])
    for i, option in enumerate(options):
        if option.get("name", "").lower() == moscow_text.lower():
            return i

    return None


def build_task_description(story_data: dict[str, Any]) -> str:
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
    parts.append(f"\n*File: {story_data['filename']}*")

    return "".join(parts)


def sync_story_to_clickup(
    client,
    story_data: dict[str, Any],
    config: dict,
    dry_run: bool = False,
    force: bool = False,
) -> dict[str, Any] | None:
    """Sync a single story to ClickUp.

    Args:
        client: ClickUp client instance.
        story_data: Parsed story data.
        config: ClickUp configuration.
        dry_run: If True, only preview changes without creating tasks.
        force: If True, update even if task already exists.

    Returns:
        Created or updated task data, or None if skipped.
    """
    # Determine target list
    list_id = find_or_create_list(client, story_data, config)

    if not list_id:
        return None

    # Check if task already exists
    task = None
    if story_data.get("clickup_id"):
        with contextlib.suppress(Exception):
            task = client.get_task(story_data["clickup_id"])

    if not task:
        # Search by story ID in task name
        existing_tasks = client.search_tasks(
            query=story_data["story_id"],
            list_ids=[list_id],
        )
        if existing_tasks:
            task = existing_tasks[0]

    # Build task data
    task_name = f"{story_data['story_id']}: {story_data['title']}"
    description = build_task_description(story_data)
    tags = []

    if story_data.get("moscow_priority"):
        priority_label = story_data["moscow_priority"].lower().replace(" ", "_")
        if priority_label in config.get("labels", {}):
            tags.append(config["labels"][priority_label])

    if dry_run:
        return None

    if task and not force:
        return task

    if task:
        # Update existing task

        task = client.update_task(
            task_id=task["id"],
            name=task_name,
            description=description,
            status="Open",
        )
    else:
        # Create new task

        task = client.create_task(
            list_id=list_id,
            name=task_name,
            description=description,
            status="Open",
            tags=tags,
        )

    # Set custom fields
    try:
        # Story Points
        if story_data.get("points"):
            points_field = client.find_custom_field_by_name(list_id, "Story Points")
            if points_field:
                client.set_custom_field(task["id"], points_field["id"], story_data["points"])

        # MoSCoW Priority
        if story_data.get("moscow_priority"):
            moscow_field = client.find_custom_field_by_name(list_id, "MoSCoW Priority")
            if moscow_field:
                option_value = get_moscow_priority_value(
                    client, list_id, story_data["moscow_priority"]
                )
                if option_value is not None:
                    client.set_custom_field(task["id"], moscow_field["id"], option_value)
    except Exception:
        pass

    # Create subtasks
    if story_data.get("tasks"):
        for task_item in story_data["tasks"]:
            try:
                subtask_name = task_item["description"]
                if task_item.get("category"):
                    subtask_name = f"[{task_item['category']}] {subtask_name}"

                client.create_subtask(
                    parent_task_id=task["id"],
                    name=subtask_name,
                    status="Closed" if task_item.get("completed") else "Open",
                )
            except Exception:
                pass

    return task


def write_clickup_id_to_file(file_path: Path, clickup_id: str):
    """Write ClickUp ID to the story file.

    Args:
        file_path: Path to the story file.
        clickup_id: ClickUp task ID to write.
    """
    with Path(file_path).open(encoding="utf-8") as f:
        content = f.read()

    # Check if ID already exists
    if re.search(r"<!--\s*CLICKUP_ID:", content):
        # Update existing ID
        content = re.sub(
            r"<!--\s*CLICKUP_ID:\s*\w+\s*-->",
            f"<!-- CLICKUP_ID: {clickup_id} -->",
            content,
        )
    else:
        # Add ID after the first heading
        content = re.sub(
            r"(^#\s+.+$)",
            f"\\1\n\n<!-- CLICKUP_ID: {clickup_id} -->",
            content,
            count=1,
            flags=re.MULTILINE,
        )

    with Path(file_path).open("w", encoding="utf-8") as f:
        f.write(content)


def main():
    """Main entry point for enhanced story sync script."""
    parser = argparse.ArgumentParser(
        description="Sync user stories from docs to ClickUp with custom fields and subtasks"
    )
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
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force update existing tasks",
    )

    args = parser.parse_args()

    # Initialize ClickUp client
    try:
        client = get_client()
    except ValueError:
        sys.exit(1)

    # Check if stories folder exists
    stories_path = Path(args.folder_path)
    if not stories_path.exists():
        sys.exit(1)

    # Find all story files (only US-*.md files, not README or other docs)
    story_files = [
        f for f in stories_path.glob("*.md") if re.match(r"US-\d+", f.name, re.IGNORECASE)
    ]

    if not story_files:
        sys.exit(0)

    # Sync each story
    success_count = 0
    error_count = 0
    results = []

    for story_file in sorted(story_files):
        try:
            story_data = parse_story_file(story_file)
            if story_data:
                result = sync_story_to_clickup(
                    client,
                    story_data,
                    client.config,
                    dry_run=args.dry_run,
                    force=args.force,
                )
                if result:
                    success_count += 1
                    results.append(
                        {
                            "story_id": story_data["story_id"],
                            "clickup_id": result["id"],
                            "file_path": story_file,
                        }
                    )

                    # Write ClickUp ID back to file
                    if not args.dry_run:
                        write_clickup_id_to_file(story_file, result["id"])
                elif args.dry_run:
                    success_count += 1
            else:
                error_count += 1
        except Exception:
            import traceback

            traceback.print_exc()
            error_count += 1

    if results and not args.dry_run:
        # Save mapping file
        mapping_file = Path("config/clickup-story-mapping.json")
        mapping = {}
        if mapping_file.exists():
            with Path(mapping_file).open(encoding="utf-8") as f:
                mapping = json.load(f)

        for result in results:
            mapping[result["story_id"]] = result["clickup_id"]

        with Path(mapping_file).open("w", encoding="utf-8") as f:
            json.dump(mapping, f, indent=2)


if __name__ == "__main__":
    main()
