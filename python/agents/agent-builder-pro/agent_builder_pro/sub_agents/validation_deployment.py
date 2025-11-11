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

"""Validation and Deployment Sub-Agent."""

import logging
import ast
from typing import Dict, Any
from google.adk.agents import LlmAgent
from google.genai import types

from ..templates.prompts import VALIDATION_DEPLOYMENT_PROMPT
from ..tools.deployment_tools import deploy_to_vertex, verify_deployment, validate_deployment_config

logger = logging.getLogger(__name__)


def lint_python(code: str) -> Dict[str, Any]:
    """
    Basic Python linting check.

    Args:
        code: Python code to lint

    Returns:
        Dictionary with issues found
    """
    issues = []

    # Check for common issues
    if "import *" in code:
        issues.append("Warning: Wildcard imports found (import *)")

    if "# TODO" in code or "# FIXME" in code:
        issues.append("Info: TODOs or FIXMEs found in code")

    # Check for missing docstrings
    lines = code.split("\n")
    func_lines = [i for i, line in enumerate(lines) if line.strip().startswith("def ")]
    for func_line in func_lines:
        # Check if next non-empty line is a docstring
        for next_line in lines[func_line + 1:func_line + 5]:
            stripped = next_line.strip()
            if stripped and not stripped.startswith('"""') and not stripped.startswith("'''"):
                issues.append(f"Warning: Function at line {func_line + 1} may be missing docstring")
                break
            if stripped.startswith('"""') or stripped.startswith("'''"):
                break

    return {
        "passed": len([i for i in issues if i.startswith("Error")]) == 0,
        "issues": issues,
        "issue_count": len(issues)
    }


def syntax_check(code: str) -> Dict[str, Any]:
    """
    Check Python syntax validity.

    Args:
        code: Python code to check

    Returns:
        Dictionary with syntax check results
    """
    try:
        ast.parse(code)
        return {
            "valid": True,
            "error": None
        }
    except SyntaxError as e:
        return {
            "valid": False,
            "error": f"Syntax error at line {e.lineno}: {e.msg}"
        }
    except Exception as e:
        return {
            "valid": False,
            "error": f"Parse error: {str(e)}"
        }


def run_unit_tests(test_code: str) -> Dict[str, Any]:
    """
    Simulates running unit tests.

    Args:
        test_code: Test code to run

    Returns:
        Dictionary with test results
    """
    # For now, just validate the test code syntax
    syntax_result = syntax_check(test_code)

    if not syntax_result["valid"]:
        return {
            "passed": False,
            "error": f"Test code has syntax errors: {syntax_result['error']}"
        }

    # Count number of test functions
    test_count = test_code.count("def test_")

    return {
        "passed": True,
        "test_count": test_count,
        "message": f"Found {test_count} test function(s). Ready to run with pytest."
    }


validation_deployment_agent = LlmAgent(
    name="validation_deployment",
    model="gemini-2.5-pro",
    description=(
        "Validates generated code for syntax, linting, and best practices. "
        "Deploys to Vertex AI with retry logic if requested."
    ),
    instruction=VALIDATION_DEPLOYMENT_PROMPT,
    output_key="deployment_result",
    tools=[
        lint_python,
        syntax_check,
        run_unit_tests,
        deploy_to_vertex,
        verify_deployment,
        validate_deployment_config,
    ],
    generate_content_config=types.GenerateContentConfig(temperature=0.1),
)
