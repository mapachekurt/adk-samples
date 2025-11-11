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

"""Requirements Gatherer Sub-Agent."""

import logging
from google.adk.agents import LlmAgent
from google.genai import types

from ..templates.prompts import REQUIREMENTS_GATHERER_PROMPT
from ..tools.mcp_tools import read_existing_mcps, check_user_context
from ..tools.pattern_tools import get_adk_patterns

logger = logging.getLogger(__name__)

requirements_gatherer_agent = LlmAgent(
    name="requirements_gatherer",
    model="gemini-2.5-pro",
    description=(
        "Gathers agent requirements through adaptive conversation. "
        "Discovers available MCP servers and user context to inform suggestions."
    ),
    instruction=REQUIREMENTS_GATHERER_PROMPT,
    output_key="requirements_spec",
    tools=[
        read_existing_mcps,
        check_user_context,
        get_adk_patterns,
    ],
    generate_content_config=types.GenerateContentConfig(temperature=0.7),
)
