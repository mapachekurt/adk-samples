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

"""Fault-tolerant MCP server discovery and context checking tools."""

import json
import logging
import os
from pathlib import Path
from typing import Dict, List

logger = logging.getLogger(__name__)


def read_existing_mcps() -> Dict[str, any]:
    """
    Discover existing MCP servers from configuration files.

    This function NEVER FAILS - it returns an empty list if no MCPs are found.
    Searches multiple common locations for MCP configuration files.

    Returns:
        Dictionary containing:
            - available: List of available MCP server names
            - unavailable: List of configured but unavailable servers
            - search_locations: List of paths searched
            - errors: List of any errors encountered (non-fatal)

    Example:
        >>> result = read_existing_mcps()
        >>> print(result["available"])
        ['github', 'linear', 'filesystem']
    """
    result = {
        "available": [],
        "unavailable": [],
        "search_locations": [],
        "errors": []
    }

    # Define search paths for MCP configuration
    search_paths = [
        Path.home() / ".config" / "claude" / "claude_desktop_config.json",
        Path.home() / ".claude" / "mcp_config.json",
        Path("./mcp_config.json"),
        Path("../mcp_config.json"),
        Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json",  # macOS
    ]

    for config_path in search_paths:
        result["search_locations"].append(str(config_path))

        try:
            if config_path.exists():
                logger.info(f"Found MCP config at {config_path}")

                with open(config_path, 'r') as f:
                    config = json.load(f)

                # Try different config structures
                mcps = config.get("mcpServers", {})
                if not mcps:
                    mcps = config.get("mcp_servers", {})
                if not mcps:
                    mcps = config.get("servers", {})

                if mcps:
                    result["available"] = list(mcps.keys())
                    logger.info(f"Found {len(result['available'])} MCP servers: {result['available']}")
                    return result

        except json.JSONDecodeError as e:
            error_msg = f"{config_path}: Invalid JSON - {str(e)}"
            result["errors"].append(error_msg)
            logger.warning(error_msg)

        except PermissionError as e:
            error_msg = f"{config_path}: Permission denied"
            result["errors"].append(error_msg)
            logger.warning(error_msg)

        except Exception as e:
            error_msg = f"{config_path}: {type(e).__name__} - {str(e)}"
            result["errors"].append(error_msg)
            logger.warning(error_msg)

    # No MCPs found - log it but don't fail
    logger.info("No MCP servers found in any search location - continuing without MCPs")
    return result


def check_user_context() -> Dict[str, any]:
    """
    Check the user's current context to suggest relevant integrations.

    Examines the current directory for patterns that might inform
    agent design (e.g., GitHub repo, Python project, etc.).

    Returns:
        Dictionary containing:
            - has_context: Whether useful context was found
            - patterns: List of detected patterns
            - suggestions: List of suggested integrations
            - errors: List of any errors encountered

    Example:
        >>> context = check_user_context()
        >>> if context["has_context"]:
        ...     print(context["suggestions"])
        ['Consider using GitHub MCP for repository access']
    """
    result = {
        "has_context": False,
        "patterns": [],
        "suggestions": [],
        "errors": []
    }

    try:
        cwd = Path.cwd()

        # Check for git repository
        if (cwd / ".git").exists():
            result["patterns"].append("git_repository")
            result["suggestions"].append(
                "Consider using GitHub/GitLab MCP for repository operations"
            )
            result["has_context"] = True

        # Check for Python project
        python_indicators = ["setup.py", "pyproject.toml", "requirements.txt", "Pipfile"]
        for indicator in python_indicators:
            if (cwd / indicator).exists():
                result["patterns"].append("python_project")
                result["suggestions"].append(
                    "Python project detected - code execution tools recommended"
                )
                result["has_context"] = True
                break

        # Check for package.json (Node.js)
        if (cwd / "package.json").exists():
            result["patterns"].append("nodejs_project")
            result["suggestions"].append(
                "Node.js project detected - npm/filesystem tools recommended"
            )
            result["has_context"] = True

        # Check for common cloud configs
        cloud_configs = {
            "gcp": [".gcloudignore", "app.yaml", "cloudbuild.yaml"],
            "aws": [".aws", "cloudformation.yaml", "serverless.yml"],
            "azure": ["azure-pipelines.yml", ".azure"]
        }

        for cloud, indicators in cloud_configs.items():
            for indicator in indicators:
                if (cwd / indicator).exists():
                    result["patterns"].append(f"{cloud}_project")
                    result["suggestions"].append(
                        f"{cloud.upper()} project detected - cloud integration tools recommended"
                    )
                    result["has_context"] = True
                    break

        # Check for documentation
        doc_files = ["README.md", "docs", "documentation"]
        for doc in doc_files:
            if (cwd / doc).exists():
                result["patterns"].append("has_documentation")
                break

    except Exception as e:
        error_msg = f"Error checking context: {type(e).__name__} - {str(e)}"
        result["errors"].append(error_msg)
        logger.warning(error_msg)

    return result


def list_available_google_tools() -> List[Dict[str, str]]:
    """
    Returns a list of available Google-provided tools for ADK.

    These are built-in tools that can be used without additional configuration.

    Returns:
        List of dictionaries describing available tools
    """
    return [
        {
            "name": "google_search",
            "description": "Search the web using Google Search",
            "use_case": "Finding current information, research, fact-checking"
        },
        {
            "name": "code_execution",
            "description": "Execute Python code in a sandboxed environment",
            "use_case": "Data analysis, calculations, code generation and testing"
        },
        {
            "name": "vertex_ai_search",
            "description": "Search enterprise data using Vertex AI Search",
            "use_case": "Enterprise RAG, document search, knowledge retrieval",
            "requires_setup": True
        }
    ]
