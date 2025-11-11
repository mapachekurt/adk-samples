# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Validators for agent specifications and configurations."""

import logging
from typing import Dict, List, Any

from .error_handling import ValidationError, safe_get

logger = logging.getLogger(__name__)


def validate_requirements(requirements: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Validate requirements specification from the requirements gatherer.

    Args:
        requirements: Requirements dictionary to validate

    Returns:
        Dictionary with 'errors' and 'warnings' lists
    """
    errors = []
    warnings = []

    # Required fields
    if not requirements.get("purpose"):
        errors.append("Missing 'purpose' field")

    if not requirements.get("use_case"):
        errors.append("Missing 'use_case' field")

    # Validate complexity
    complexity = requirements.get("complexity", "")
    valid_complexity = ["simple", "moderate", "complex"]
    if complexity not in valid_complexity:
        warnings.append(
            f"Invalid complexity '{complexity}', expected one of {valid_complexity}"
        )

    # Validate boolean fields
    bool_fields = [
        "needs_sub_agents",
        "needs_parallel_execution",
        "needs_iteration",
        "needs_custom_logic"
    ]
    for field in bool_fields:
        value = requirements.get(field)
        if value is not None and not isinstance(value, bool):
            warnings.append(f"Field '{field}' should be boolean, got {type(value).__name__}")

    # Validate lists
    list_fields = ["suggested_mcps", "custom_tool_requirements"]
    for field in list_fields:
        value = requirements.get(field, [])
        if not isinstance(value, list):
            errors.append(f"Field '{field}' should be a list, got {type(value).__name__}")

    return {"errors": errors, "warnings": warnings}


def validate_architecture(architecture: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Validate architecture design specification.

    Args:
        architecture: Architecture dictionary to validate

    Returns:
        Dictionary with 'errors' and 'warnings' lists
    """
    errors = []
    warnings = []

    # Required fields
    if not architecture.get("agent_type"):
        errors.append("Missing 'agent_type' field")

    # Validate agent type
    agent_type = architecture.get("agent_type", "")
    valid_types = [
        "LlmAgent",
        "SequentialAgent",
        "ParallelAgent",
        "LoopAgent",
        "CustomBaseAgent"
    ]
    if agent_type not in valid_types:
        warnings.append(
            f"Unusual agent type '{agent_type}', expected one of {valid_types}"
        )

    # Validate model suggestion
    model = architecture.get("model_suggestion", "")
    if model and not model.startswith("gemini"):
        warnings.append(f"Non-Gemini model suggested: {model}")

    # Check for rationale
    if not architecture.get("rationale"):
        warnings.append("Missing rationale for architecture choice")

    return {"errors": errors, "warnings": warnings}


def validate_tool_spec(tool_spec: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Validate tool specification.

    Args:
        tool_spec: Tool specification dictionary to validate

    Returns:
        Dictionary with 'errors' and 'warnings' lists
    """
    errors = []
    warnings = []

    # Validate list fields
    mcp_tools = tool_spec.get("mcp_tools", [])
    if not isinstance(mcp_tools, list):
        errors.append("'mcp_tools' should be a list")

    google_tools = tool_spec.get("google_tools", [])
    if not isinstance(google_tools, list):
        errors.append("'google_tools' should be a list")

    custom_functions = tool_spec.get("custom_functions", [])
    if not isinstance(custom_functions, list):
        errors.append("'custom_functions' should be a list")
    else:
        # Validate custom function structure
        for i, func in enumerate(custom_functions):
            if not isinstance(func, dict):
                errors.append(f"custom_functions[{i}] should be a dictionary")
                continue

            if not func.get("name"):
                errors.append(f"custom_functions[{i}] missing 'name'")

            if not func.get("description"):
                warnings.append(f"custom_functions[{i}] missing 'description'")

            params = func.get("params", [])
            if not isinstance(params, list):
                errors.append(f"custom_functions[{i}]['params'] should be a list")

    # Check if at least one tool type is specified
    has_tools = bool(mcp_tools or google_tools or custom_functions)
    if not has_tools:
        warnings.append("No tools specified - agent may have limited capabilities")

    return {"errors": errors, "warnings": warnings}


def validate_project_files(project_files: Dict[str, str]) -> Dict[str, List[str]]:
    """
    Validate generated project files.

    Args:
        project_files: Dictionary mapping filename to content

    Returns:
        Dictionary with 'errors' and 'warnings' lists
    """
    errors = []
    warnings = []

    # Required files
    required_files = [
        "agent_py",
        "requirements_txt",
        "readme_md"
    ]

    for file_key in required_files:
        if not project_files.get(file_key):
            errors.append(f"Missing required file: {file_key}")
        elif not isinstance(project_files[file_key], str):
            errors.append(f"File {file_key} content should be a string")
        elif len(project_files[file_key].strip()) == 0:
            errors.append(f"File {file_key} is empty")

    # Check for optional but recommended files
    optional_files = ["tools_py", "env_example", "deploy_py", "tests_py"]
    for file_key in optional_files:
        if not project_files.get(file_key):
            warnings.append(f"Optional file not generated: {file_key}")

    return {"errors": errors, "warnings": warnings}
