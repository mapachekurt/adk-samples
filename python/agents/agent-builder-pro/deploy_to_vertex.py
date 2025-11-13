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

"""Deploys the Agent Builder Pro agent to Vertex AI Agent Engine Runtime.

This script provides a robust, production-ready deployment mechanism with
comprehensive error handling and automatic retries for transient issues.

Key Features:
- Loads configuration from environment variables (.env file)
- Authenticates with Google Cloud using Application Default Credentials (ADC)
- Implements exponential backoff retry logic for API calls
- Provides clear, actionable error messages for common deployment failures
- Configures all necessary parameters for the Vertex AI Agent Engine

Usage:
    python deploy_to_vertex.py
"""

import logging
import os
import sys
import time

from dotenv import load_dotenv
from google.api_core import exceptions as api_exceptions
from google.cloud import aiplatform
import tenacity

# --- Configuration ---

# Load environment variables from .env file
# Ensure you have a .env file with:
# GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
# GOOGLE_CLOUD_LOCATION="your-gcp-region"  # e.g., us-central1
# STAGING_BUCKET="gs://your-gcs-bucket-for-staging"
load_dotenv()

# --- Logging Setup ---

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


# --- Retry Logic with Tenacity ---

# Define retry strategy for transient GCP errors
# This will retry on common network/API issues with exponential backoff
retry_strategy = tenacity.retry(
    wait=tenacity.wait_exponential(multiplier=2, min=2, max=60),
    stop=tenacity.stop_after_attempt(5),
    retry=tenacity.retry_if_exception_type(
        (
            api_exceptions.ServiceUnavailable,
            api_exceptions.ResourceExhausted,
            api_exceptions.InternalServerError,
            api_exceptions.DeadlineExceeded,
        )
    ),
    before_sleep=lambda retry_state: logger.info(
        f"Retrying API call due to transient error: {retry_state.outcome.exception()}. "
        f"Attempt #{retry_state.attempt_number}, waiting {retry_state.next_action.sleep}s..."
    ),
)


# --- Core Deployment Function ---


@retry_strategy
def deploy_agent_to_vertex(
    project_id: str, location: str, staging_bucket: str, agent_id: str
) -> None:
    """Deploys the ADK agent to Vertex AI Agent Engine.

    Args:
        project_id: The Google Cloud project ID.
        location: The GCP region for deployment.
        staging_bucket: The GCS bucket for staging deployment artifacts.
        agent_id: The ID for the deployed agent.

    Raises:
        ValueError: If required configuration is missing.
        google.auth.exceptions.DefaultCredentialsError: If authentication fails.
        api_exceptions.GoogleAPICallError: For non-transient API errors.
    """
    logger.info("--- Starting Agent Deployment to Vertex AI ---")
    logger.info(f"  Project: {project_id}")
    logger.info(f"  Location: {location}")
    logger.info(f"  Staging Bucket: {staging_bucket}")
    logger.info(f"  Agent ID: {agent_id}")

    try:
        # Initialize Vertex AI SDK
        aiplatform.init(
            project=project_id, location=location, staging_bucket=staging_bucket
        )

        # Deploy the agent
        # The SDK will automatically discover the `root_agent` in `agent.py`
        # It packages the code, builds a container, and deploys it.
        logger.info("Starting deployment process. This may take several minutes...")
        deployed_agent = aiplatform.Agent.deploy(
            agent="agent_builder_pro.agent.root_agent",  # Path to the agent object
            agent_id=agent_id,
            display_name="Agent Builder Pro",
        )

        logger.info("--- Deployment Submitted Successfully ---")
        logger.info(f"Agent Name: {deployed_agent.name}")
        logger.info(f"Deployed Agent URI: {deployed_agent.uri}")
        logger.info("It may take a few more minutes for the agent to become fully active.")

    except api_exceptions.PermissionDenied as e:
        logger.error(
            "Permission denied. Check IAM permissions for the Vertex AI API and GCS bucket.",
            exc_info=True,
        )
        raise e
    except api_exceptions.NotFound as e:
        logger.error(
            "A required resource was not found (e.g., project, location, or bucket).",
            exc_info=True,
        )
        raise e
    except Exception as e:
        logger.error(f"An unexpected error occurred during deployment: {e}", exc_info=True)
        raise e


# --- Main Execution Block ---

if __name__ == "__main__":
    logger.info("--- Agent Builder Pro Deployment Script ---")

    # Get configuration from environment variables
    gcp_project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    gcp_location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    gcs_staging_bucket = os.getenv("STAGING_BUCKET")
    deployment_agent_id = "agent-builder-pro-v1"

    # Validate configuration
    missing_vars = []
    if not gcp_project_id:
        missing_vars.append("GOOGLE_CLOUD_PROJECT")
    if not gcs_staging_bucket:
        missing_vars.append("STAGING_BUCKET")

    if missing_vars:
        error_msg = f"Error: Missing required environment variables: {', '.join(missing_vars)}"
        logger.error(error_msg)
        logger.error("Please create a .env file or set them in your environment.")
        sys.exit(1)  # Exit with a non-zero status code

    # Pre-deployment checks
    logger.info("Running pre-deployment checks...")
    if not gcs_staging_bucket.startswith("gs://"):
        logger.error("STAGING_BUCKET must start with 'gs://'")
        sys.exit(1)

    try:
        deploy_agent_to_vertex(
            project_id=gcp_project_id,
            location=gcp_location,
            staging_bucket=gcs_staging_bucket,
            agent_id=deployment_agent_id,
        )
        logger.info("--- Script finished successfully! ---")

    except (ValueError, api_exceptions.GoogleAPICallError) as e:
        logger.error(f"Deployment failed after retries. Please check the logs.", exc_info=False)
        sys.exit(1)
    except Exception as e:
        logger.error(f"An unexpected critical error occurred.", exc_info=False)
        sys.exit(1)
