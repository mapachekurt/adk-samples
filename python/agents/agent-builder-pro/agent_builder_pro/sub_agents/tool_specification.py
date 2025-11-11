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

"""Tool Specification Sub-Agent."""

import logging
from google.adk.agents import LlmAgent
from google.genai import types

from ..templates.prompts import TOOL_SPECIFICATION_PROMPT
from ..tools.mcp_tools import read_existing_mcps, list_available_google_tools

logger = logging.getLogger(__name__)

tool_specification_agent = LlmAgent(
    name="tool_specification",
    model="gemini-2.5-pro",
    description=(
        "Identifies and specifies all required tools including MCP servers, "
        "Google built-in tools, and custom functions."
    ),
    instruction=TOOL_SPECIFICATION_PROMPT,
    output_key="tool_specs",
    tools=[
        read_existing_mcps,
        list_available_google_tools,
    ],
    generate_content_config=types.GenerateContentConfig(temperature=0.2),
)
