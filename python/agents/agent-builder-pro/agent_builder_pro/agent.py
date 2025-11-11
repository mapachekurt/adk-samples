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

"""Agent Builder Pro - Root Orchestrator Agent.

This is a meta-agent system that helps users create custom ADK agents through
an interactive, guided process. It uses a SequentialAgent to orchestrate 5
specialized sub-agents:

1. Requirements Gatherer - Interviews user to understand their needs
2. Architecture Designer - Designs optimal agent structure
3. Tool Specification - Identifies required tools and integrations
4. Code Generator - Generates complete ADK project
5. Validation & Deployment - Validates and deploys to Vertex AI

The system is fault-tolerant, handling missing MCP servers gracefully and
including retry logic for deployment operations.
"""

import logging
from google.adk.agents import SequentialAgent

from .sub_agents import (
    requirements_gatherer_agent,
    architecture_designer_agent,
    tool_specification_agent,
    code_generator_agent,
    validation_deployment_agent,
)
from .utils.logging_config import setup_logging

# Setup logging
setup_logging(level="INFO")
logger = logging.getLogger(__name__)

# System instruction for the meta-agent
SYSTEM_INSTRUCTION = """You are Agent Builder Pro, an expert system for creating production-ready
Google ADK agents. You guide users through a comprehensive process to design, generate, and deploy
custom AI agents.

Key principles:
- Be conversational and adaptive, not rigid
- Ask clarifying questions when needed
- Provide clear explanations of technical choices
- Handle errors gracefully and provide helpful feedback
- Never fail silently - always inform the user of issues

Your process:
1. Gather requirements through natural conversation
2. Design the optimal architecture with user input
3. Specify all required tools and integrations
4. Generate complete, production-ready code
5. Validate and optionally deploy to Vertex AI

You have 5 specialized sub-agents that will execute in sequence. Each sub-agent
passes its output to the next via session state, creating a comprehensive
agent building pipeline.
"""

# Create the root SequentialAgent
agent_builder_pro = SequentialAgent(
    name="agent_builder_pro",
    sub_agents=[
        requirements_gatherer_agent,
        architecture_designer_agent,
        tool_specification_agent,
        code_generator_agent,
        validation_deployment_agent,
    ],
    description=(
        "Meta-agent system that creates production-ready Google ADK agents. "
        "Guides users through requirements gathering, architecture design, "
        "tool specification, code generation, and deployment."
    ),
)

# For ADK tools compatibility, the root agent must be named `root_agent`
root_agent = agent_builder_pro

logger.info("Agent Builder Pro initialized successfully")
