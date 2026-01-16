#!/usr/bin/env python3
"""Pull tasks from ClickUp and save IDs for local reference.

This script fetches all tasks from ClickUp sprints and backlog, extracting
task IDs, names, statuses, and URLs. The data is saved to a JSON file for
use by other scripts and GitHub Actions workflows.

Usage:
    python scripts/clickup/pull_tasks.py [--output OUTPUT_FILE] [--include-closed]

Examples:
    # Pull all open tasks
    python scripts/clickup/pull_tasks.py

    # Pull all tasks including closed ones
    python scripts/clickup/pull_tasks.py --include-closed

    # Save to custom location
    python scripts/clickup/pull_tasks.py --output /tmp/clickup_tasks.json
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from clickup_client import get_client


def fetch_all_tasks(client, include_closed: bool = False) -> list[dict[str, Any]]:
    """Fetch all tasks from ClickUp workspace.

    Args:
        client: ClickUp client instance.
        include_closed: Whether to include closed tasks.

    Returns:
        List of task dictionaries with extracted data.
    """
    tasks = []
    config = client.config

    # Fetch from sprints folder
    sprints_folder_id = config["folders"]["sprints"]["id"]
    sprint_lists = client.get_lists_in_folder(sprints_folder_id)

    for sprint_list in sprint_lists:
        list_id = sprint_list["id"]
        list_name = sprint_list["name"]

        list_tasks = client.get_tasks_in_list(list_id, include_closed=include_closed)

        for task in list_tasks:
            tasks.append(
                {
                    "id": task["id"],
                    "custom_id": task.get("custom_id"),
                    "name": task["name"],
                    "status": task["status"]["status"],
                    "priority": task.get("priority"),
                    "url": task["url"],
                    "list_id": list_id,
                    "list_name": list_name,
                    "folder": "sprints",
                    "assignees": [
                        {
                            "id": a["id"],
                            "username": a.get("username", ""),
                            "email": a.get("email", ""),
                        }
                        for a in task.get("assignees", [])
                    ],
                    "tags": [t["name"] for t in task.get("tags", [])],
                    "date_created": task.get("date_created"),
                    "date_updated": task.get("date_updated"),
                }
            )

    # Fetch from backlog
    backlog_list_id = config["folders"]["backlog"]["list_id"]

    backlog_tasks = client.get_tasks_in_list(backlog_list_id, include_closed=include_closed)

    for task in backlog_tasks:
        tasks.append(
            {
                "id": task["id"],
                "custom_id": task.get("custom_id"),
                "name": task["name"],
                "status": task["status"]["status"],
                "priority": task.get("priority"),
                "url": task["url"],
                "list_id": backlog_list_id,
                "list_name": "Backlog",
                "folder": "backlog",
                "assignees": [
                    {
                        "id": a["id"],
                        "username": a.get("username", ""),
                        "email": a.get("email", ""),
                    }
                    for a in task.get("assignees", [])
                ],
                "tags": [t["name"] for t in task.get("tags", [])],
                "date_created": task.get("date_created"),
                "date_updated": task.get("date_updated"),
            }
        )

    return tasks


def save_tasks(tasks: list[dict[str, Any]], output_file: str):
    """Save tasks to JSON file.

    Args:
        tasks: List of task dictionaries.
        output_file: Path to output JSON file.
    """
    data = {
        "fetched_at": datetime.utcnow().isoformat(),
        "task_count": len(tasks),
        "tasks": tasks,
    }

    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def extract_task_id_mapping(tasks: list[dict[str, Any]]) -> dict[str, str]:
    """Extract mapping of story IDs to ClickUp task IDs.

    Args:
        tasks: List of task dictionaries.

    Returns:
        Dictionary mapping story IDs (US-XXX) to ClickUp task IDs.
    """
    import re

    mapping = {}

    for task in tasks:
        # Extract story ID from task name (e.g., "US-001: Feature Name")
        match = re.match(r"(US-\d+):", task["name"])
        if match:
            story_id = match.group(1)
            mapping[story_id] = task["id"]

    return mapping


def main():
    """Main entry point for pull tasks script."""
    parser = argparse.ArgumentParser(description="Pull tasks from ClickUp and save IDs")
    parser.add_argument(
        "--output",
        default="config/clickup-tasks.json",
        help="Output file path (default: config/clickup-tasks.json)",
    )
    parser.add_argument(
        "--include-closed",
        action="store_true",
        help="Include closed/completed tasks",
    )
    parser.add_argument(
        "--mapping-only",
        action="store_true",
        help="Only output story ID to task ID mapping",
    )

    args = parser.parse_args()

    # Initialize ClickUp client
    try:
        client = get_client()
    except ValueError:
        sys.exit(1)

    # Fetch all tasks
    tasks = fetch_all_tasks(client, include_closed=args.include_closed)

    if args.mapping_only:
        # Output only the story ID mapping
        mapping = extract_task_id_mapping(tasks)

        # Save mapping to separate file
        mapping_file = Path(args.output).parent / "clickup-story-mapping.json"
        with mapping_file.open("w", encoding="utf-8") as f:
            json.dump(mapping, f, indent=2)
    else:
        # Save all task data
        save_tasks(tasks, args.output)

        # Also save mapping
        mapping = extract_task_id_mapping(tasks)
        mapping_file = Path(args.output).parent / "clickup-story-mapping.json"
        with mapping_file.open("w", encoding="utf-8") as f:
            json.dump(mapping, f, indent=2)

    status_counts = {}
    for task in tasks:
        status = task["status"]
        status_counts[status] = status_counts.get(status, 0) + 1

    for _status, _count in sorted(status_counts.items()):
        pass


if __name__ == "__main__":
    main()
