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

"""Code Generator Sub-Agent."""

import logging
from google.adk.agents import LlmAgent
from google.genai import types

from ..templates.prompts import CODE_GENERATOR_PROMPT
from ..tools.generation_tools import (
    generate_agent_code,
    generate_tools_code,
    generate_requirements,
    generate_env_template,
    generate_readme,
    generate_deployment_script,
    generate_tests
)

logger = logging.getLogger(__name__)

code_generator_agent = LlmAgent(
    name="code_generator",
    model="gemini-2.5-pro",
    description=(
        "Generates complete ADK project with all files including agent code, "
        "tools, tests, deployment scripts, and documentation."
    ),
    instruction=CODE_GENERATOR_PROMPT,
    output_key="project_files",
    tools=[
        generate_agent_code,
        generate_tools_code,
        generate_requirements,
        generate_env_template,
        generate_readme,
        generate_deployment_script,
        generate_tests,
    ],
    generate_content_config=types.GenerateContentConfig(temperature=0.1),
)
