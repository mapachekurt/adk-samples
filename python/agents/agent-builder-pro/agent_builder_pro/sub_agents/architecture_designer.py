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

"""Architecture Designer Sub-Agent."""

import logging
from google.adk.agents import LlmAgent
from google.genai import types

from ..templates.prompts import ARCHITECTURE_DESIGNER_PROMPT
from ..tools.pattern_tools import analyze_complexity, suggest_pattern, calculate_cost_estimate

logger = logging.getLogger(__name__)

architecture_designer_agent = LlmAgent(
    name="architecture_designer",
    model="gemini-2.5-pro",
    description=(
        "Analyzes requirements and designs optimal agent architecture. "
        "Suggests agent type, model, and provides cost estimates."
    ),
    instruction=ARCHITECTURE_DESIGNER_PROMPT,
    output_key="architecture_design",
    tools=[
        analyze_complexity,
        suggest_pattern,
        calculate_cost_estimate,
    ],
    generate_content_config=types.GenerateContentConfig(temperature=0.3),
)
