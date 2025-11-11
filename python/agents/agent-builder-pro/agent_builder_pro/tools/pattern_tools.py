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

"""Tools for ADK pattern analysis and recommendations."""

import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


def get_adk_patterns() -> Dict[str, Any]:
    """
    Returns comprehensive ADK pattern knowledge.

    This function always succeeds and provides information about
    available ADK agent patterns and when to use them.

    Returns:
        Dictionary containing pattern descriptions and use cases
    """
    return {
        "agent_types": {
            "LlmAgent": {
                "description": "Single-agent with direct LLM interaction",
                "best_for": [
                    "Simple conversational agents",
                    "Single-purpose tools",
                    "Direct question answering",
                    "When no orchestration needed"
                ],
                "complexity": "simple",
                "example_use_cases": [
                    "Customer service chatbot",
                    "Code explainer",
                    "Translation service"
                ]
            },
            "SequentialAgent": {
                "description": "Orchestrates multiple sub-agents in sequence",
                "best_for": [
                    "Multi-step workflows with dependencies",
                    "Data processing pipelines",
                    "Complex tasks requiring multiple stages",
                    "When output of one step feeds the next"
                ],
                "complexity": "moderate",
                "example_use_cases": [
                    "Research and report generation",
                    "Multi-stage data analysis",
                    "Code review then testing"
                ]
            },
            "ParallelAgent": {
                "description": "Executes multiple sub-agents concurrently",
                "best_for": [
                    "Independent tasks that can run simultaneously",
                    "Gathering diverse information",
                    "Performance optimization",
                    "When sub-tasks don't depend on each other"
                ],
                "complexity": "moderate",
                "example_use_cases": [
                    "Multi-source research",
                    "Parallel data validation",
                    "Simultaneous code analysis"
                ]
            },
            "LoopAgent": {
                "description": "Iterates sub-agents until condition met",
                "best_for": [
                    "Refinement workflows",
                    "Optimization tasks",
                    "Quality improvement loops",
                    "When iterations needed to reach goal"
                ],
                "complexity": "complex",
                "example_use_cases": [
                    "Iterative code improvement",
                    "Progressive image enhancement",
                    "Optimization algorithms"
                ]
            },
            "CustomBaseAgent": {
                "description": "Custom logic extending BaseAgent",
                "best_for": [
                    "Unique orchestration patterns",
                    "Complex decision trees",
                    "Dynamic agent selection",
                    "When built-in patterns don't fit"
                ],
                "complexity": "complex",
                "example_use_cases": [
                    "Adaptive workflow routing",
                    "Conditional agent execution",
                    "Custom state management"
                ]
            }
        },
        "model_recommendations": {
            "gemini-2.5-flash": {
                "best_for": "Simple tasks, high speed, cost optimization",
                "use_when": "straightforward queries, basic conversions, simple tool use"
            },
            "gemini-2.5-pro": {
                "best_for": "Complex reasoning, multi-step planning, detailed analysis",
                "use_when": "complex orchestration, deep analysis, sophisticated reasoning"
            }
        },
        "session_management": {
            "in_memory": {
                "description": "Transient session state (default)",
                "best_for": "Stateless agents, single conversations"
            },
            "firestore": {
                "description": "Persistent session state in Firestore",
                "best_for": "Multi-turn conversations, state persistence",
                "requires": "Firestore setup"
            }
        }
    }


def analyze_complexity(requirements: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyzes requirements complexity and suggests appropriate agent type.

    Args:
        requirements: Requirements specification dictionary

    Returns:
        Dictionary containing:
            - complexity_score: 1-10 complexity rating
            - suggested_agent_types: List of recommended agent types
            - reasoning: Explanation of the recommendation
    """
    score = 0
    reasoning = []

    # Check for sub-agent needs
    if requirements.get("needs_sub_agents", False):
        score += 3
        reasoning.append("Multiple sub-agents required")

    # Check for parallel execution
    if requirements.get("needs_parallel_execution", False):
        score += 2
        reasoning.append("Parallel execution needed")

    # Check for iteration
    if requirements.get("needs_iteration", False):
        score += 3
        reasoning.append("Iterative processing required")

    # Check for custom logic
    if requirements.get("needs_custom_logic", False):
        score += 2
        reasoning.append("Custom orchestration logic needed")

    # Check tool complexity
    mcp_count = len(requirements.get("suggested_mcps", []))
    custom_tool_count = len(requirements.get("custom_tool_requirements", []))

    if mcp_count + custom_tool_count > 5:
        score += 2
        reasoning.append(f"Many tools required ({mcp_count + custom_tool_count})")
    elif mcp_count + custom_tool_count > 0:
        score += 1

    # Determine suggested agent types based on score and requirements
    suggested_types = []

    if score <= 3:
        suggested_types = ["LlmAgent"]
        complexity = "simple"
    elif requirements.get("needs_parallel_execution"):
        suggested_types = ["ParallelAgent", "SequentialAgent"]
        complexity = "moderate"
    elif requirements.get("needs_iteration"):
        suggested_types = ["LoopAgent"]
        complexity = "complex"
    elif requirements.get("needs_custom_logic"):
        suggested_types = ["CustomBaseAgent", "SequentialAgent"]
        complexity = "complex"
    elif requirements.get("needs_sub_agents"):
        suggested_types = ["SequentialAgent", "ParallelAgent"]
        complexity = "moderate"
    else:
        suggested_types = ["LlmAgent", "SequentialAgent"]
        complexity = "moderate"

    return {
        "complexity_score": min(score, 10),
        "complexity_level": complexity,
        "suggested_agent_types": suggested_types,
        "reasoning": reasoning,
        "primary_recommendation": suggested_types[0]
    }


def suggest_pattern(
    agent_type: str,
    requirements: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Suggests implementation patterns for the chosen agent type.

    Args:
        agent_type: The chosen agent type
        requirements: Requirements specification

    Returns:
        Dictionary with implementation suggestions
    """
    patterns = get_adk_patterns()
    agent_info = patterns["agent_types"].get(agent_type, {})

    suggestions = {
        "agent_type": agent_type,
        "description": agent_info.get("description", ""),
        "implementation_tips": [],
        "potential_challenges": [],
        "recommended_model": "gemini-2.5-pro"
    }

    # Add specific suggestions based on agent type
    if agent_type == "LlmAgent":
        suggestions["implementation_tips"] = [
            "Keep prompt instructions clear and concise",
            "Use structured outputs for consistent responses",
            "Test tool integration thoroughly"
        ]
        suggestions["potential_challenges"] = [
            "May need refinement if task is too complex",
            "Limited to single-turn reasoning"
        ]
        if requirements.get("complexity") == "simple":
            suggestions["recommended_model"] = "gemini-2.5-flash"

    elif agent_type == "SequentialAgent":
        suggestions["implementation_tips"] = [
            "Design clear output_key for each sub-agent",
            "Use session.state to pass data between agents",
            "Keep sub-agent responsibilities well-defined",
            "Consider error handling at each stage"
        ]
        suggestions["potential_challenges"] = [
            "Debugging can be complex with multiple stages",
            "One failing stage blocks subsequent stages"
        ]

    elif agent_type == "ParallelAgent":
        suggestions["implementation_tips"] = [
            "Ensure sub-agents are truly independent",
            "Design result aggregation strategy",
            "Handle partial failures gracefully"
        ]
        suggestions["potential_challenges"] = [
            "Higher token cost (multiple parallel calls)",
            "Need to aggregate diverse outputs"
        ]

    elif agent_type == "LoopAgent":
        suggestions["implementation_tips"] = [
            "Define clear termination conditions",
            "Set maximum iteration limit",
            "Track improvement metrics",
            "Log each iteration for debugging"
        ]
        suggestions["potential_challenges"] = [
            "Risk of infinite loops",
            "Higher cost due to iterations",
            "Complex termination logic"
        ]

    elif agent_type == "CustomBaseAgent":
        suggestions["implementation_tips"] = [
            "Extend BaseAgent class properly",
            "Implement run() method with your logic",
            "Handle state management carefully",
            "Document custom behavior thoroughly"
        ]
        suggestions["potential_challenges"] = [
            "Most complex to implement",
            "Requires deep ADK understanding",
            "More maintenance burden"
        ]

    return suggestions


def calculate_cost_estimate(
    agent_type: str,
    model: str,
    requirements: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Estimates token usage and cost for the agent design.

    Args:
        agent_type: The agent type
        model: The Gemini model to use
        requirements: Requirements specification

    Returns:
        Dictionary with cost estimates
    """
    # Base token estimates per request
    base_tokens = {
        "gemini-2.5-flash": {"input": 1000, "output": 500},
        "gemini-2.5-pro": {"input": 2000, "output": 1000}
    }

    model_tokens = base_tokens.get(model, base_tokens["gemini-2.5-pro"])

    # Multipliers based on agent type
    multipliers = {
        "LlmAgent": 1,
        "SequentialAgent": 3,  # Assumes 3 sub-agents
        "ParallelAgent": 3,    # Parallel calls
        "LoopAgent": 5,        # Multiple iterations
        "CustomBaseAgent": 4   # Complex orchestration
    }

    multiplier = multipliers.get(agent_type, 1)

    # Add tool usage overhead
    tool_count = len(requirements.get("suggested_mcps", [])) + \
                 len(requirements.get("custom_tool_requirements", []))
    tool_overhead = tool_count * 200  # 200 tokens per tool call

    estimated_input = (model_tokens["input"] * multiplier) + tool_overhead
    estimated_output = model_tokens["output"] * multiplier

    return {
        "estimated_input_tokens": estimated_input,
        "estimated_output_tokens": estimated_output,
        "estimated_total_tokens": estimated_input + estimated_output,
        "cost_level": "low" if estimated_input + estimated_output < 5000 else
                      "medium" if estimated_input + estimated_output < 15000 else "high",
        "note": "Estimates are per conversation turn and may vary significantly"
    }
