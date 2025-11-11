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

"""Tests for Agent Builder Pro agents and tools."""

import pytest
from agent_builder_pro.agent import root_agent
from agent_builder_pro.tools.mcp_tools import read_existing_mcps, check_user_context
from agent_builder_pro.tools.pattern_tools import get_adk_patterns, analyze_complexity
from agent_builder_pro.utils.error_handling import validate_and_default, graceful_failure


def test_root_agent_import():
    """Test that the root agent can be imported."""
    assert root_agent is not None
    assert root_agent.name == "agent_builder_pro"


def test_root_agent_has_sub_agents():
    """Test that the root agent has all 5 sub-agents."""
    assert hasattr(root_agent, "sub_agents")
    assert len(root_agent.sub_agents) == 5


def test_read_existing_mcps_never_fails():
    """Test that read_existing_mcps never crashes, even with no MCPs."""
    result = read_existing_mcps()
    assert isinstance(result, dict)
    assert "available" in result
    assert "unavailable" in result
    assert "search_locations" in result
    assert "errors" in result
    assert isinstance(result["available"], list)


def test_check_user_context_never_fails():
    """Test that check_user_context never crashes."""
    result = check_user_context()
    assert isinstance(result, dict)
    assert "has_context" in result
    assert "patterns" in result
    assert "suggestions" in result
    assert isinstance(result["has_context"], bool)


def test_get_adk_patterns_always_succeeds():
    """Test that get_adk_patterns always returns valid data."""
    result = get_adk_patterns()
    assert isinstance(result, dict)
    assert "agent_types" in result
    assert "LlmAgent" in result["agent_types"]
    assert "SequentialAgent" in result["agent_types"]
    assert "model_recommendations" in result


def test_analyze_complexity():
    """Test complexity analysis with sample requirements."""
    requirements = {
        "needs_sub_agents": True,
        "needs_parallel_execution": False,
        "needs_iteration": False,
        "needs_custom_logic": False,
        "suggested_mcps": ["github"],
        "custom_tool_requirements": ["fetch_data"]
    }

    result = analyze_complexity(requirements)
    assert isinstance(result, dict)
    assert "complexity_score" in result
    assert "suggested_agent_types" in result
    assert isinstance(result["complexity_score"], int)
    assert result["complexity_score"] >= 0


def test_validate_and_default():
    """Test the validate_and_default utility."""
    # Test with valid value
    result = validate_and_default("test", str, "default", "field")
    assert result == "test"

    # Test with None
    result = validate_and_default(None, str, "default", "field")
    assert result == "default"

    # Test with wrong type
    result = validate_and_default(123, str, "default", "field")
    assert result == "default"


def test_graceful_failure_decorator():
    """Test the graceful_failure decorator."""
    @graceful_failure(default_return={"error": "failed"})
    def failing_function():
        raise ValueError("Test error")

    result = failing_function()
    assert result == {"error": "failed"}


def test_sub_agents_have_tools():
    """Test that sub-agents have appropriate tools."""
    from agent_builder_pro.sub_agents import (
        requirements_gatherer_agent,
        architecture_designer_agent,
        tool_specification_agent,
        code_generator_agent,
        validation_deployment_agent,
    )

    # Requirements gatherer should have MCP and context tools
    assert len(requirements_gatherer_agent.tools) >= 3

    # Architecture designer should have complexity analysis tools
    assert len(architecture_designer_agent.tools) >= 2

    # Tool specification should have listing tools
    assert len(tool_specification_agent.tools) >= 2

    # Code generator should have generation tools
    assert len(code_generator_agent.tools) >= 6

    # Validation should have validation and deployment tools
    assert len(validation_deployment_agent.tools) >= 5


def test_sub_agents_have_output_keys():
    """Test that sub-agents define output keys for state management."""
    from agent_builder_pro.sub_agents import (
        requirements_gatherer_agent,
        architecture_designer_agent,
        tool_specification_agent,
        code_generator_agent,
        validation_deployment_agent,
    )

    assert requirements_gatherer_agent.output_key == "requirements_spec"
    assert architecture_designer_agent.output_key == "architecture_design"
    assert tool_specification_agent.output_key == "tool_specs"
    assert code_generator_agent.output_key == "project_files"
    assert validation_deployment_agent.output_key == "deployment_result"


def test_generation_tools():
    """Test code generation tools."""
    from agent_builder_pro.tools.generation_tools import (
        generate_agent_code,
        generate_tools_code,
        generate_requirements,
    )

    # Test agent code generation
    code = generate_agent_code(
        agent_name="test_agent",
        agent_type="LlmAgent",
        model="gemini-2.5-pro",
        description="Test agent",
        tools=["tool1", "tool2"]
    )
    assert "test_agent" in code
    assert "LlmAgent" in code
    assert "gemini-2.5-pro" in code

    # Test tools code generation
    tools_code = generate_tools_code([
        {"name": "test_tool", "description": "Test", "params": []}
    ])
    assert "def test_tool" in tools_code

    # Test requirements generation
    requirements = generate_requirements("LlmAgent")
    assert "google-adk" in requirements
    assert "google-genai" in requirements


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
