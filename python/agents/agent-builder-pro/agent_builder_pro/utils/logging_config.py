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

"""Centralized logging configuration for Agent Builder Pro."""

import logging
import sys
from typing import Optional


def setup_logging(
    level: str = "INFO",
    format_string: Optional[str] = None,
    include_timestamp: bool = True
) -> None:
    """
    Configure logging for the entire application.

    Args:
        level: Logging level ("DEBUG", "INFO", "WARNING", "ERROR")
        format_string: Custom format string (optional)
        include_timestamp: Whether to include timestamps in logs
    """
    if format_string is None:
        if include_timestamp:
            format_string = (
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
        else:
            format_string = "%(name)s - %(levelname)s - %(message)s"

    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format=format_string,
        stream=sys.stdout
    )

    # Set specific log levels for noisy libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("google").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module.

    Args:
        name: Name of the logger (typically __name__)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)
