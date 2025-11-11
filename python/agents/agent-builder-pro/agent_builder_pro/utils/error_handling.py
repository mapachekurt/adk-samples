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

"""Error handling utilities for fault-tolerant agent operations."""

import logging
from functools import wraps
from typing import Any, Callable, Optional, Type, Union

logger = logging.getLogger(__name__)


def graceful_failure(
    default_return: Any = None,
    log_level: str = "warning",
    suppress_errors: tuple = (Exception,)
) -> Callable:
    """
    Decorator that catches exceptions and returns a default value.

    This ensures that tool failures never crash the agent, allowing it to
    continue operation and provide feedback to the user.

    Args:
        default_return: Value to return if the function fails
        log_level: Logging level for the error ("debug", "info", "warning", "error")
        suppress_errors: Tuple of exception types to suppress

    Returns:
        Decorated function that never raises exceptions

    Example:
        @graceful_failure(default_return={}, log_level="warning")
        def read_config():
            with open("config.json") as f:
                return json.load(f)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except suppress_errors as e:
                log_func = getattr(logger, log_level, logger.warning)
                log_func(
                    f"{func.__name__} failed with {type(e).__name__}: {str(e)}",
                    exc_info=log_level == "error"
                )
                return default_return
        return wrapper
    return decorator


def validate_and_default(
    value: Any,
    expected_type: Union[Type, tuple],
    default: Any,
    field_name: str = "value"
) -> Any:
    """
    Validates a value's type and returns default if invalid.

    This provides defensive validation for all inputs, ensuring that
    None values and type mismatches are handled gracefully.

    Args:
        value: Value to validate
        expected_type: Expected type(s) - can be a single type or tuple of types
        default: Default value to return if validation fails
        field_name: Name of the field for logging

    Returns:
        The validated value or default

    Example:
        complexity = validate_and_default(
            requirements.get("complexity"),
            str,
            "simple",
            "complexity"
        )
    """
    if value is None:
        logger.debug(f"{field_name} is None, using default: {default}")
        return default

    if not isinstance(value, expected_type):
        logger.warning(
            f"{field_name} has invalid type {type(value).__name__}, "
            f"expected {expected_type}, using default: {default}"
        )
        return default

    return value


def safe_get(dictionary: dict, key: str, default: Any = None, expected_type: Optional[Type] = None) -> Any:
    """
    Safely get a value from a dictionary with type validation.

    Combines dictionary access with type validation in a single call.

    Args:
        dictionary: Dictionary to access
        key: Key to retrieve
        default: Default value if key not found or type mismatch
        expected_type: Expected type for validation (optional)

    Returns:
        The value or default

    Example:
        complexity = safe_get(requirements, "complexity", "simple", str)
    """
    value = dictionary.get(key, default)

    if expected_type is not None:
        return validate_and_default(value, expected_type, default, key)

    return value if value is not None else default


class AgentBuilderError(Exception):
    """Base exception for Agent Builder Pro errors."""
    pass


class ValidationError(AgentBuilderError):
    """Raised when validation fails."""
    pass


class DeploymentError(AgentBuilderError):
    """Raised when deployment fails after all retries."""
    pass


class ToolError(AgentBuilderError):
    """Raised when a tool operation fails."""
    pass
