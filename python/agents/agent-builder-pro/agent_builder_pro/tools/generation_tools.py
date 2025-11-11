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

"""Code generation tools for creating ADK agent projects."""

import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


def generate_agent_code(
    agent_name: str,
    agent_type: str,
    model: str,
    description: str,
    tools: List[str],
    sub_agents: List[str] = None
) -> str:
    """
    Generates the main agent.py file.

    Args:
        agent_name: Name of the agent
        agent_type: Type of agent (LlmAgent, SequentialAgent, etc.)
        model: Gemini model to use
        description: Agent description
        tools: List of tool names
        sub_agents: List of sub-agent names (for orchestrating agents)

    Returns:
        Generated Python code as a string
    """
    tool_imports = "\n".join([f"from .tools import {tool}" for tool in tools]) if tools else ""
    tool_list = ", ".join(tools) if tools else ""

    if agent_type == "LlmAgent":
        code = f'''# Copyright 2025 Google LLC
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

"""{description}"""

import logging
from google.adk.agents import LlmAgent
from google.genai import types

{tool_imports}
from . import prompts

logger = logging.getLogger(__name__)

MODEL = "{model}"

{agent_name}_agent = LlmAgent(
    name="{agent_name}",
    model=MODEL,
    description="{description}",
    instruction=prompts.AGENT_INSTRUCTION,
    tools=[{tool_list}],
    generate_content_config=types.GenerateContentConfig(temperature=0.1),
)

# For ADK tools compatibility
root_agent = {agent_name}_agent
'''

    elif agent_type == "SequentialAgent":
        sub_agent_imports = "\n".join([
            f"from .sub_agents.{sa} import {sa}_agent"
            for sa in (sub_agents or [])
        ])
        sub_agent_list = ", ".join([f"{sa}_agent" for sa in (sub_agents or [])])

        code = f'''# Copyright 2025 Google LLC
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

"""{description}"""

import logging
from google.adk.agents import SequentialAgent

{sub_agent_imports}

logger = logging.getLogger(__name__)

{agent_name}_agent = SequentialAgent(
    name="{agent_name}",
    sub_agents=[{sub_agent_list}],
    description="{description}",
)

# For ADK tools compatibility
root_agent = {agent_name}_agent
'''

    else:
        # Generic template for other types
        code = f'''# Copyright 2025 Google LLC
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

"""{description}"""

import logging
from google.adk import agents

logger = logging.getLogger(__name__)

# TODO: Implement {agent_type} agent
# Refer to ADK documentation for {agent_type} implementation

root_agent = None  # Replace with your agent implementation
'''

    return code


def generate_tools_code(custom_functions: List[Dict[str, Any]]) -> str:
    """
    Generates tools.py with custom tool functions.

    Args:
        custom_functions: List of function specifications

    Returns:
        Generated Python code
    """
    if not custom_functions:
        return '''# Copyright 2025 Google LLC
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

"""Custom tools for the agent."""

import logging

logger = logging.getLogger(__name__)

# Add your custom tool functions here
'''

    functions_code = []
    for func in custom_functions:
        name = func.get("name", "custom_tool")
        description = func.get("description", "Custom tool function")
        params = func.get("params", [])

        param_list = ", ".join([f"{p['name']}: {p.get('type', 'str')}" for p in params])
        param_docs = "\n    ".join([
            f"{p['name']} ({p.get('type', 'str')}): {p.get('description', 'Parameter')}"
            for p in params
        ])

        func_code = f'''
def {name}({param_list}) -> dict:
    """
    {description}

    Args:
        {param_docs}

    Returns:
        dict: Result dictionary with status and data

    Example:
        >>> {name}({', '.join([p['name'] + '="value"' for p in params])})
        {{'status': 'success', 'data': {{}}}}
    """
    logger.info(f"Executing {name}")

    try:
        # TODO: Implement tool logic here
        result = {{"status": "success", "message": "Tool executed successfully"}}
        return result

    except Exception as e:
        logger.error(f"Error in {name}: {{e}}", exc_info=True)
        return {{"status": "error", "error": str(e)}}
'''
        functions_code.append(func_code)

    return f'''# Copyright 2025 Google LLC
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

"""Custom tools for the agent."""

import logging

logger = logging.getLogger(__name__)

{"".join(functions_code)}
'''


def generate_requirements(
    agent_type: str,
    needs_deployment: bool = True,
    additional_packages: List[str] = None
) -> str:
    """
    Generates requirements.txt file.

    Args:
        agent_type: Type of agent
        needs_deployment: Whether to include deployment packages
        additional_packages: Additional package requirements

    Returns:
        Requirements.txt content
    """
    base_requirements = [
        "google-adk>=0.3.0",
        "google-genai>=1.0.0",
    ]

    if needs_deployment:
        base_requirements.extend([
            "google-cloud-aiplatform[agent_engines,adk]>=1.112",
            "vertexai>=1.0.0"
        ])

    # Add development dependencies
    base_requirements.extend([
        "pytest>=7.4.0",
        "pylint>=3.0.0",
        "python-dotenv>=1.0.0"
    ])

    if additional_packages:
        base_requirements.extend(additional_packages)

    return "\n".join(sorted(set(base_requirements))) + "\n"


def generate_env_template(
    project_id_required: bool = True,
    custom_vars: List[str] = None
) -> str:
    """
    Generates .env.example template.

    Args:
        project_id_required: Whether GCP project ID is required
        custom_vars: Additional environment variables

    Returns:
        .env.example content
    """
    lines = ["# Environment variables for the agent\n"]

    if project_id_required:
        lines.extend([
            "# Google Cloud Project ID",
            "GOOGLE_CLOUD_PROJECT=your-project-id",
            "",
            "# Google Cloud Location (default: us-central1)",
            "GOOGLE_CLOUD_LOCATION=us-central1",
            "",
            "# Staging bucket for deployment",
            "STAGING_BUCKET=gs://your-staging-bucket",
            ""
        ])

    if custom_vars:
        lines.append("# Custom configuration")
        for var in custom_vars:
            lines.append(f"{var}=")
        lines.append("")

    lines.extend([
        "# Optional: Logging level (DEBUG, INFO, WARNING, ERROR)",
        "LOG_LEVEL=INFO"
    ])

    return "\n".join(lines) + "\n"


def generate_readme(
    agent_name: str,
    description: str,
    agent_type: str,
    features: List[str],
    setup_instructions: List[str]
) -> str:
    """
    Generates comprehensive README.md.

    Args:
        agent_name: Name of the agent
        description: Agent description
        agent_type: Type of agent
        features: List of features
        setup_instructions: Custom setup instructions

    Returns:
        README.md content
    """
    features_list = "\n".join([f"- {feature}" for feature in features])
    setup_list = "\n".join([f"{i+1}. {step}" for i, step in enumerate(setup_instructions)])

    return f'''# {agent_name}

{description}

## Overview

This agent is built using Google's Agent Development Kit (ADK) and uses the **{agent_type}** pattern.

## Features

{features_list}

## Prerequisites

- Python 3.10 or higher
- Google Cloud Platform account
- Vertex AI API enabled
- ADK installed (`pip install google-adk`)

## Setup

{setup_list}

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Edit `.env` and set your values:
- `GOOGLE_CLOUD_PROJECT`: Your GCP project ID
- `GOOGLE_CLOUD_LOCATION`: GCP region (default: us-central1)
- `STAGING_BUCKET`: GCS bucket for deployment artifacts

## Usage

### Local Development

Run the agent locally using ADK web interface:

```bash
adk web
```

This starts a local server where you can interact with the agent.

### Deployment

Deploy to Vertex AI Agent Engine Runtime:

```bash
python deployment/deploy.py
```

The deployment script includes:
- Automatic retry logic for transient failures
- Exponential backoff for rate limits
- Comprehensive error handling

## Architecture

This agent uses the **{agent_type}** pattern:

{get_architecture_description(agent_type)}

## Testing

Run the test suite:

```bash
pytest tests/
```

## Troubleshooting

### MCP Servers Not Found

If MCP servers are not detected:
1. Check MCP configuration locations
2. Verify JSON syntax in config files
3. Agent will continue without MCPs - manually add if needed

### Deployment Failures

If deployment fails:
1. Check GCP credentials: `gcloud auth list`
2. Verify Vertex AI API is enabled
3. Check GCS bucket permissions
4. Review deployment logs for specific errors

The deployment script automatically retries on transient failures.

## License

Copyright 2025 Google LLC

Licensed under the Apache License, Version 2.0.
See LICENSE file for details.

## Disclaimer

This agent is generated for demonstration purposes and may require
customization for production use.
'''


def get_architecture_description(agent_type: str) -> str:
    """Helper to get architecture description."""
    descriptions = {
        "LlmAgent": "Single LLM agent that directly processes user requests and executes tools.",
        "SequentialAgent": "Orchestrates multiple sub-agents in sequence, where each agent's output feeds into the next.",
        "ParallelAgent": "Executes multiple sub-agents concurrently for independent tasks.",
        "LoopAgent": "Iteratively runs sub-agents until a termination condition is met.",
    }
    return descriptions.get(agent_type, "Custom agent implementation.")


def generate_deployment_script(
    agent_name: str,
    project_id_var: str = "GOOGLE_CLOUD_PROJECT",
    location_var: str = "GOOGLE_CLOUD_LOCATION"
) -> str:
    """
    Generates deployment script with retry logic.

    Args:
        agent_name: Name of the agent
        project_id_var: Environment variable for project ID
        location_var: Environment variable for location

    Returns:
        deploy.py content
    """
    return f'''# Copyright 2025 Google LLC
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

"""Deployment script with fault-tolerant retry logic."""

import os
import sys
import time
import logging
from pathlib import Path

import vertexai
from vertexai import agent_engines

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_env():
    """Load environment variables from .env file."""
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        logger.warning("python-dotenv not installed, using system environment variables")


def deploy_agent(max_retries: int = 3):
    """
    Deploy agent to Vertex AI with retry logic.

    Args:
        max_retries: Maximum number of deployment attempts
    """
    load_env()

    # Get configuration from environment
    project_id = os.getenv("{project_id_var}")
    location = os.getenv("{location_var}", "us-central1")
    staging_bucket = os.getenv("STAGING_BUCKET")

    if not project_id:
        logger.error("GOOGLE_CLOUD_PROJECT environment variable not set")
        sys.exit(1)

    if not staging_bucket:
        logger.error("STAGING_BUCKET environment variable not set")
        sys.exit(1)

    logger.info(f"Deploying {agent_name} to project {{project_id}} in {{location}}")

    # Import the agent
    try:
        from {agent_name}.agent import root_agent as app
    except ImportError as e:
        logger.error(f"Failed to import agent: {{e}}")
        sys.exit(1)

    # Initialize Vertex AI client
    client = vertexai.Client(
        project=project_id,
        location=location
    )

    # Deployment with retry logic
    for attempt in range(1, max_retries + 1):
        logger.info(f"Deployment attempt {{attempt}}/{{max_retries}}")

        try:
            remote_agent = client.agent_engines.create(
                agent=app,
                config={{
                    "requirements": [
                        "google-cloud-aiplatform[agent_engines,adk]>=1.112",
                        "google-adk>=0.3.0"
                    ],
                    "staging_bucket": staging_bucket,
                    "display_name": "{agent_name}",
                    "min_instances": 0,
                    "max_instances": 1,
                }}
            )

            logger.info("✓ Deployment successful!")
            logger.info(f"Resource ID: {{remote_agent.api_resource.name}}")
            logger.info(f"Endpoint: {{remote_agent.api_resource.display_name}}")

            return remote_agent

        except Exception as e:
            error_msg = str(e).lower()

            # Check for retryable errors
            is_retryable = any(keyword in error_msg for keyword in [
                "quota", "rate limit", "timeout", "unavailable", "deadline"
            ])

            if is_retryable and attempt < max_retries:
                wait_time = 2 ** attempt  # Exponential backoff: 2s, 4s, 8s
                logger.warning(
                    f"Deployment failed with retryable error: {{e}}\\n"
                    f"Retrying in {{wait_time}} seconds..."
                )
                time.sleep(wait_time)
                continue

            # Non-retryable error or max retries exceeded
            logger.error(f"Deployment failed after {{attempt}} attempts: {{e}}")
            sys.exit(1)


if __name__ == "__main__":
    deploy_agent()
'''


def generate_tests(agent_name: str, tools: List[str]) -> str:
    """
    Generates test file.

    Args:
        agent_name: Name of the agent
        tools: List of tool names to test

    Returns:
        test_agent.py content
    """
    tool_tests = "\n\n".join([
        f'''def test_{tool}():
    """Test {tool} function."""
    # TODO: Implement test
    pass'''
        for tool in tools
    ]) if tools else "# Add your tests here"

    return f'''# Copyright 2025 Google LLC
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

"""Tests for {agent_name} agent."""

import pytest


def test_agent_import():
    """Test that agent can be imported."""
    try:
        from {agent_name}.agent import root_agent
        assert root_agent is not None
    except ImportError as e:
        pytest.fail(f"Failed to import agent: {{e}}")


{tool_tests}
'''
