"""ClickUp API client for project management integration.

This module provides a Python client for interacting with ClickUp's API,
including operations for tasks, lists, folders, and status management.

Classes:
    ClickUpClient: Main client for ClickUp API operations.

Functions:
    get_client: Factory function to create configured ClickUp client.
"""

import json
import os
import re
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

import requests


def _resolve_env_vars(value: Any) -> Any:
    """Resolve environment variable placeholders in config values.

    Supports ${VAR_NAME} syntax for environment variable substitution.
    Recursively processes dictionaries and lists.

    Args:
        value: The value to process (string, dict, list, or other).

    Returns:
        The value with environment variables resolved.

    Example:
        >>> os.environ["CLICKUP_WORKSPACE_ID"] = "12345"
        >>> _resolve_env_vars("${CLICKUP_WORKSPACE_ID}")
        '12345'
    """
    if isinstance(value, str):
        pattern = r"\$\{([^}]+)\}"
        matches = re.findall(pattern, value)
        for var_name in matches:
            env_value = os.environ.get(var_name, "")
            value = value.replace(f"${{{var_name}}}", env_value)
        return value
    elif isinstance(value, dict):
        return {k: _resolve_env_vars(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [_resolve_env_vars(item) for item in value]
    return value


class ClickUpClient:
    """Client for interacting with ClickUp API v2.

    This client handles authentication, request formatting, and provides
    methods for common ClickUp operations including task creation, updates,
    and status management.

    Attributes:
        api_key: ClickUp API key for authentication.
        base_url: Base URL for ClickUp API (defaults to v2).
        workspace_id: ClickUp workspace ID.
        space_id: ClickUp space ID.
        config: Configuration dictionary loaded from config file.
    """

    BASE_URL = "https://api.clickup.com/api/v2/"

    def __init__(self, api_key: str, config_path: str | None = None):
        """Initialize ClickUp client.

        Args:
            api_key: ClickUp API key for authentication.
            config_path: Optional path to config JSON file. Defaults to
                config/clickup-config.json.
        """
        self.api_key = api_key
        self.base_url = self.BASE_URL
        self.session = requests.Session()
        self.session.headers.update({"Authorization": self.api_key})

        if config_path is None:
            config_path = Path(__file__).parent / "../../config/clickup-config.json"
        else:
            config_path = Path(config_path)

        with config_path.open(encoding="utf-8") as f:
            raw_config = json.load(f)

        # Resolve environment variable placeholders in config
        self.config = _resolve_env_vars(raw_config)

        self.workspace_id = self.config["workspace"]["workspace_id"]
        self.space_id = self.config["workspace"]["space_id"]

    def _request(self, method: str, endpoint: str, **kwargs) -> dict[str, Any]:
        """Make HTTP request to ClickUp API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE).
            endpoint: API endpoint path.
            **kwargs: Additional arguments passed to requests.

        Returns:
            JSON response as dictionary.

        Raises:
            requests.HTTPError: If API request fails.
        """
        url = urljoin(self.base_url, endpoint)
        response = self.session.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json() if response.content else {}

    def get_folder(self, folder_id: str) -> dict[str, Any]:
        """Retrieve folder details by ID.

        Args:
            folder_id: ClickUp folder ID.

        Returns:
            Folder data including lists, statuses, and metadata.
        """
        return self._request("GET", f"folder/{folder_id}")

    def get_lists_in_folder(self, folder_id: str) -> list[dict[str, Any]]:
        """Retrieve all lists within a folder.

        Args:
            folder_id: ClickUp folder ID.

        Returns:
            List of list objects with their details.
        """
        response = self._request("GET", f"folder/{folder_id}/list")
        return response.get("lists", [])

    def get_list(self, list_id: str) -> dict[str, Any]:
        """Retrieve list details by ID.

        Args:
            list_id: ClickUp list ID.

        Returns:
            List data including tasks, statuses, and metadata.
        """
        return self._request("GET", f"list/{list_id}")

    def create_list(
        self,
        folder_id: str,
        name: str,
        content: str | None = None,
        due_date: int | None = None,
        priority: int | None = None,
        status: str | None = None,
    ) -> dict[str, Any]:
        """Create a new list in a folder.

        Args:
            folder_id: ClickUp folder ID.
            name: List name.
            content: Optional list description.
            due_date: Optional due date timestamp.
            priority: Optional priority (1=urgent, 2=high, 3=normal, 4=low).
            status: Optional list status.

        Returns:
            Created list data including ID.
        """
        data = {"name": name}

        if content is not None:
            data["content"] = content
        if due_date is not None:
            data["due_date"] = due_date
        if priority is not None:
            data["priority"] = priority
        if status is not None:
            data["status"] = status

        return self._request("POST", f"folder/{folder_id}/list", json=data)

    def get_tasks_in_list(
        self,
        list_id: str,
        include_closed: bool = False,
        page: int = 0,
    ) -> list[dict[str, Any]]:
        """Retrieve tasks from a specific list.

        Args:
            list_id: ClickUp list ID.
            include_closed: Whether to include closed tasks. Defaults to False.
            page: Page number for pagination. Defaults to 0.

        Returns:
            List of task objects.
        """
        params = {
            "archived": "false",
            "page": page,
            "include_closed": str(include_closed).lower(),
        }
        response = self._request("GET", f"list/{list_id}/task", params=params)
        return response.get("tasks", [])

    def get_task(self, task_id: str) -> dict[str, Any]:
        """Retrieve task details by ID.

        Args:
            task_id: ClickUp task ID.

        Returns:
            Task data including status, assignees, custom fields, and metadata.
        """
        return self._request("GET", f"task/{task_id}")

    def create_task(
        self,
        list_id: str,
        name: str,
        description: str | None = None,
        status: str | None = None,
        priority: int | None = None,
        assignees: list[int] | None = None,
        tags: list[str] | None = None,
        custom_fields: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Create a new task in ClickUp.

        Args:
            list_id: ClickUp list ID where task will be created.
            name: Task name/title.
            description: Optional task description (markdown supported).
            status: Optional status name.
            priority: Optional priority (1=urgent, 2=high, 3=normal, 4=low).
            assignees: Optional list of user IDs to assign.
            tags: Optional list of tag names.
            custom_fields: Optional custom field values.

        Returns:
            Created task data including ID and URL.
        """
        data = {
            "name": name,
            "description": description or "",
            "assignees": assignees or [],
            "tags": tags or [],
            "status": status,
            "priority": priority,
        }

        if custom_fields:
            data["custom_fields"] = custom_fields

        # Remove None values
        data = {k: v for k, v in data.items() if v is not None}

        return self._request("POST", f"list/{list_id}/task", json=data)

    def update_task(
        self,
        task_id: str,
        name: str | None = None,
        description: str | None = None,
        status: str | None = None,
        priority: int | None = None,
        assignees: list[int] | None = None,
    ) -> dict[str, Any]:
        """Update an existing task.

        Args:
            task_id: ClickUp task ID.
            name: Optional new task name.
            description: Optional new description.
            status: Optional new status name.
            priority: Optional new priority.
            assignees: Optional new list of assignees (replaces existing).

        Returns:
            Updated task data.
        """
        data = {}
        if name is not None:
            data["name"] = name
        if description is not None:
            data["description"] = description
        if status is not None:
            data["status"] = status
        if priority is not None:
            data["priority"] = priority
        if assignees is not None:
            data["assignees"] = {"add": assignees, "rem": []}

        return self._request("PUT", f"task/{task_id}", json=data)

    def update_task_status(self, task_id: str, status: str) -> dict[str, Any]:
        """Update task status.

        Args:
            task_id: ClickUp task ID.
            status: New status name (must match workspace statuses).

        Returns:
            Updated task data.
        """
        return self.update_task(task_id, status=status)

    def move_task_to_list(self, task_id: str, list_id: str) -> dict[str, Any]:
        """Move a task to a different list.

        Args:
            task_id: ClickUp task ID.
            list_id: Target list ID.

        Returns:
            Updated task data.
        """
        data = {"list_id": list_id}
        return self._request("PUT", f"task/{task_id}", json=data)

    def add_task_to_list(self, task_id: str, list_id: str) -> dict[str, Any]:
        """Add a task to an additional list (link without moving).

        This creates a reference to the task in the target list while keeping
        the task in its original list. The task will appear in both lists.

        Args:
            task_id: ClickUp task ID.
            list_id: Target list ID to link the task to.

        Returns:
            Response data from the API.
        """
        return self._request("POST", f"list/{list_id}/task/{task_id}")

    def remove_task_from_list(self, task_id: str, list_id: str) -> dict[str, Any]:
        """Remove a task from an additional list (unlink).

        This removes the task reference from the specified list. If this is
        the task's only list, the operation will fail.

        Args:
            task_id: ClickUp task ID.
            list_id: List ID to remove the task from.

        Returns:
            Response data from the API.
        """
        return self._request("DELETE", f"list/{list_id}/task/{task_id}")

    def add_task_comment(self, task_id: str, comment_text: str) -> dict[str, Any]:
        """Add a comment to a task.

        Args:
            task_id: ClickUp task ID.
            comment_text: Comment text (markdown supported).

        Returns:
            Created comment data.
        """
        data = {"comment_text": comment_text}
        return self._request("POST", f"task/{task_id}/comment", json=data)

    def set_custom_field(self, task_id: str, field_id: str, value: Any) -> dict[str, Any]:
        """Set a custom field value on a task.

        Args:
            task_id: ClickUp task ID.
            field_id: Custom field ID (UUID format).
            value: Value to set (type depends on field type).

        Returns:
            Updated task data.
        """
        return self._request("POST", f"task/{task_id}/field/{field_id}", json={"value": value})

    def get_list_custom_fields(self, list_id: str) -> list[dict[str, Any]]:
        """Get custom fields for a list.

        Args:
            list_id: ClickUp list ID.

        Returns:
            List of custom field definitions.
        """
        list_data = self.get_list(list_id)
        return list_data.get("fields", [])

    def create_subtask(
        self,
        parent_task_id: str,
        name: str,
        description: str | None = None,
        status: str | None = None,
        assignees: list[int] | None = None,
    ) -> dict[str, Any]:
        """Create a subtask under a parent task.

        Args:
            parent_task_id: Parent task ID.
            name: Subtask name.
            description: Optional subtask description.
            status: Optional status name.
            assignees: Optional list of user IDs to assign.

        Returns:
            Created subtask data.
        """
        # Get parent task to find its list
        parent_task = self.get_task(parent_task_id)
        list_id = parent_task["list"]["id"]

        # Create task as subtask
        data = {
            "name": name,
            "description": description or "",
            "parent": parent_task_id,
            "assignees": assignees or [],
            "status": status,
        }

        # Remove None values
        data = {k: v for k, v in data.items() if v is not None}

        return self._request("POST", f"list/{list_id}/task", json=data)

    def find_custom_field_by_name(self, list_id: str, field_name: str) -> dict[str, Any] | None:
        """Find a custom field by name in a list.

        Args:
            list_id: ClickUp list ID.
            field_name: Name of the custom field to find.

        Returns:
            Custom field definition if found, None otherwise.
        """
        fields = self.get_list_custom_fields(list_id)
        for field in fields:
            if field.get("name", "").lower() == field_name.lower():
                return field
        return None

    def get_space_statuses(self) -> list[dict[str, Any]]:
        """Retrieve all statuses for the workspace space.

        Returns:
            List of status objects with IDs, names, types, and colors.
        """
        space = self._request("GET", f"space/{self.space_id}")
        return space.get("statuses", [])

    def search_tasks(
        self,
        query: str,
        list_ids: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Search for tasks by text query.

        Args:
            query: Search query string.
            list_ids: Optional list of list IDs to search within.

        Returns:
            List of matching tasks.
        """
        # If list_ids provided, search within specific lists
        if list_ids:
            all_tasks = []
            for list_id in list_ids:
                tasks = self.get_tasks_in_list(list_id, include_closed=True)
                # Filter by query in task name
                matching = [t for t in tasks if query.lower() in t.get("name", "").lower()]
                all_tasks.extend(matching)
            return all_tasks

        # Otherwise use team-level search (without list_ids filter)
        endpoint = f"team/{self.workspace_id}/task"
        params = {"query": query}
        response = self._request("GET", endpoint, params=params)
        return response.get("tasks", [])


def get_client(api_key: str | None = None) -> ClickUpClient:
    """Factory function to create a configured ClickUp client.

    Args:
        api_key: Optional API key. If not provided, reads from
            CLICKUP_API_TOKEN environment variable.

    Returns:
        Configured ClickUpClient instance.

    Raises:
        ValueError: If API key is not provided and not in environment.
    """
    if api_key is None:
        api_key = os.environ.get("CLICKUP_API_TOKEN")

    if not api_key:
        raise ValueError(
            "ClickUp API key must be provided or set in CLICKUP_API_TOKEN environment variable"
        )

    return ClickUpClient(api_key)
