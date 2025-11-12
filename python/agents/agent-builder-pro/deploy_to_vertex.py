#!/usr/bin/env python3
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

"""
Production-ready deployment script for Agent Builder Pro to Vertex AI Agent Engine Runtime.

This script performs comprehensive checks before deployment:
- GCP authentication validation
- Environment variable verification
- GCS staging bucket creation/validation
- Required APIs enablement check
- Agent import verification
- Deployment with retry logic

Usage:
    python deploy_to_vertex.py [--project PROJECT_ID] [--location LOCATION] [--bucket BUCKET_NAME]
"""

import argparse
import json
import logging
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class DeploymentError(Exception):
    """Custom exception for deployment failures."""
    pass


class VertexAIDeployer:
    """Handles deployment of Agent Builder Pro to Vertex AI."""

    def __init__(
        self,
        project_id: Optional[str] = None,
        location: Optional[str] = None,
        staging_bucket: Optional[str] = None
    ):
        """
        Initialize the deployer.

        Args:
            project_id: GCP project ID (defaults to GOOGLE_CLOUD_PROJECT env var)
            location: GCP location (defaults to GOOGLE_CLOUD_LOCATION or us-central1)
            staging_bucket: GCS bucket name (auto-generated if not provided)
        """
        self.project_id = project_id or os.getenv('GOOGLE_CLOUD_PROJECT')
        self.location = location or os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1')
        self.staging_bucket = staging_bucket

        if not self.staging_bucket:
            # Auto-generate bucket name
            self.staging_bucket = f"gs://agent-builder-staging-claude-code-{self.project_id}"

        # Ensure bucket name has gs:// prefix
        if not self.staging_bucket.startswith('gs://'):
            self.staging_bucket = f"gs://{self.staging_bucket}"

        self.required_apis = [
            'aiplatform.googleapis.com',
            'storage.googleapis.com',
            'compute.googleapis.com'
        ]

    def run_command(self, cmd: list, check: bool = True) -> Tuple[int, str, str]:
        """
        Run a shell command and return output.

        Args:
            cmd: Command as list of strings
            check: Whether to raise exception on non-zero exit code

        Returns:
            Tuple of (return_code, stdout, stderr)
        """
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=check
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.CalledProcessError as e:
            if check:
                raise
            return e.returncode, e.stdout or '', e.stderr or ''

    def check_gcloud_auth(self) -> bool:
        """
        Check if gcloud authentication is configured.

        Returns:
            True if authenticated, False otherwise
        """
        logger.info("Checking gcloud authentication...")

        # Check application default credentials
        returncode, stdout, stderr = self.run_command(
            ['gcloud', 'auth', 'application-default', 'print-access-token'],
            check=False
        )

        if returncode == 0:
            logger.info("✓ Application default credentials configured")
            return True

        logger.warning("✗ Application default credentials not found")
        logger.info("\nPlease run: gcloud auth application-default login")
        return False

    def verify_environment_variables(self) -> bool:
        """
        Verify required environment variables are set.

        Returns:
            True if all required variables are set, False otherwise
        """
        logger.info("Verifying environment variables...")

        if not self.project_id:
            logger.error("✗ GOOGLE_CLOUD_PROJECT not set")
            logger.info("  Set it with: export GOOGLE_CLOUD_PROJECT=your-project-id")
            return False

        logger.info(f"✓ Project ID: {self.project_id}")
        logger.info(f"✓ Location: {self.location}")
        logger.info(f"✓ Staging bucket: {self.staging_bucket}")

        return True

    def check_api_enabled(self, api: str) -> bool:
        """
        Check if a specific API is enabled.

        Args:
            api: API name (e.g., 'aiplatform.googleapis.com')

        Returns:
            True if enabled, False otherwise
        """
        returncode, stdout, stderr = self.run_command(
            ['gcloud', 'services', 'list', '--enabled',
             '--filter', f'name:{api}',
             '--format', 'value(name)',
             '--project', self.project_id],
            check=False
        )

        return returncode == 0 and api in stdout

    def enable_required_apis(self) -> bool:
        """
        Check and enable required APIs.

        Returns:
            True if all APIs are enabled, False otherwise
        """
        logger.info("Checking required APIs...")

        missing_apis = []
        for api in self.required_apis:
            if self.check_api_enabled(api):
                logger.info(f"✓ {api} is enabled")
            else:
                logger.warning(f"✗ {api} is not enabled")
                missing_apis.append(api)

        if missing_apis:
            logger.info("\nEnabling missing APIs...")
            for api in missing_apis:
                logger.info(f"  Enabling {api}...")
                returncode, stdout, stderr = self.run_command(
                    ['gcloud', 'services', 'enable', api, '--project', self.project_id],
                    check=False
                )

                if returncode == 0:
                    logger.info(f"  ✓ {api} enabled")
                else:
                    logger.error(f"  ✗ Failed to enable {api}: {stderr}")
                    return False

        return True

    def create_staging_bucket(self) -> bool:
        """
        Create or verify GCS staging bucket exists.

        Returns:
            True if bucket exists or was created, False otherwise
        """
        logger.info("Checking staging bucket...")

        bucket_name = self.staging_bucket.replace('gs://', '')

        # Check if bucket exists
        returncode, stdout, stderr = self.run_command(
            ['gsutil', 'ls', '-b', self.staging_bucket],
            check=False
        )

        if returncode == 0:
            logger.info(f"✓ Bucket {self.staging_bucket} exists")
            return True

        # Create bucket
        logger.info(f"Creating staging bucket {self.staging_bucket}...")

        returncode, stdout, stderr = self.run_command(
            ['gsutil', 'mb', '-p', self.project_id, '-l', self.location, self.staging_bucket],
            check=False
        )

        if returncode == 0:
            logger.info(f"✓ Bucket {self.staging_bucket} created")
            return True
        else:
            logger.error(f"✗ Failed to create bucket: {stderr}")
            return False

    def verify_agent_import(self) -> bool:
        """
        Verify the agent can be imported.

        Returns:
            True if agent imports successfully, False otherwise
        """
        logger.info("Verifying agent import...")

        try:
            # Add current directory to Python path
            sys.path.insert(0, str(Path(__file__).parent))

            from agent_builder_pro.agent import root_agent

            if root_agent is None:
                logger.error("✗ root_agent is None")
                return False

            logger.info(f"✓ Agent imported: {root_agent.name}")
            logger.info(f"  Type: {type(root_agent).__name__}")

            # Count sub-agents if available
            if hasattr(root_agent, 'sub_agents'):
                logger.info(f"  Sub-agents: {len(root_agent.sub_agents)}")

            return True

        except ImportError as e:
            logger.error(f"✗ Failed to import agent: {e}")
            logger.info("  Make sure you're running from the agent-builder-pro directory")
            return False
        except Exception as e:
            logger.error(f"✗ Error importing agent: {e}")
            return False

    def deploy_agent(self, max_retries: int = 3) -> Optional[str]:
        """
        Deploy the agent to Vertex AI with retry logic.

        Args:
            max_retries: Maximum number of retry attempts

        Returns:
            Resource name if successful, None otherwise
        """
        logger.info("Deploying agent to Vertex AI...")

        try:
            import vertexai
            from vertexai import agent_engines
            from agent_builder_pro.agent import root_agent

            # Initialize Vertex AI client
            client = vertexai.Client(
                project=self.project_id,
                location=self.location
            )

            # Create AdkApp wrapper
            logger.info("Creating AdkApp wrapper...")
            app = agent_engines.AdkApp(root_agent=root_agent)

            # Deployment configuration
            config = {
                "requirements": [
                    "google-cloud-aiplatform[agent_engines,adk]>=1.112",
                    "google-adk>=0.3.0",
                    "google-genai>=1.0.0",
                    "pydantic>=2.0.0"
                ],
                "staging_bucket": self.staging_bucket,
                "display_name": "Agent Builder Pro",
                "description": (
                    "Meta-agent system for creating custom Google ADK agents. "
                    "Guides users through requirements gathering, architecture design, "
                    "tool specification, code generation, and deployment."
                ),
                "min_instances": 0,
                "max_instances": 1,
                "machine_type": "n1-standard-4",
            }

            # Retry loop
            for attempt in range(1, max_retries + 1):
                logger.info(f"Deployment attempt {attempt}/{max_retries}...")

                try:
                    remote_agent = client.agent_engines.create(
                        agent=app,
                        config=config
                    )

                    resource_name = remote_agent.api_resource.name
                    logger.info("=" * 70)
                    logger.info("✓ DEPLOYMENT SUCCESSFUL!")
                    logger.info("=" * 70)
                    logger.info(f"Resource Name: {resource_name}")
                    logger.info(f"Display Name: {config['display_name']}")
                    logger.info(f"Location: {self.location}")
                    logger.info(f"Staging Bucket: {self.staging_bucket}")
                    logger.info("=" * 70)

                    return resource_name

                except Exception as e:
                    error_msg = str(e).lower()

                    # Check for retryable errors
                    retryable_keywords = [
                        'quota', 'rate limit', 'rate_limit', 'ratelimit',
                        'timeout', 'deadline', 'unavailable', '503', '429'
                    ]

                    is_retryable = any(keyword in error_msg for keyword in retryable_keywords)

                    if is_retryable and attempt < max_retries:
                        wait_time = 2 ** attempt  # Exponential backoff
                        logger.warning(
                            f"Retryable error encountered: {e}\n"
                            f"Retrying in {wait_time} seconds..."
                        )
                        time.sleep(wait_time)
                        continue

                    # Non-retryable error or max retries exceeded
                    logger.error(f"✗ Deployment failed: {e}")
                    return None

        except ImportError as e:
            logger.error(f"✗ Missing dependencies: {e}")
            logger.info("Install with: pip install -r requirements.txt")
            return None
        except Exception as e:
            logger.error(f"✗ Deployment error: {e}", exc_info=True)
            return None

        return None

    def run_full_deployment(self) -> bool:
        """
        Run the complete deployment pipeline.

        Returns:
            True if deployment succeeds, False otherwise
        """
        logger.info("=" * 70)
        logger.info("AGENT BUILDER PRO - VERTEX AI DEPLOYMENT")
        logger.info("=" * 70)
        logger.info("")

        # Step 1: Check authentication
        if not self.check_gcloud_auth():
            return False

        # Step 2: Verify environment variables
        if not self.verify_environment_variables():
            return False

        # Step 3: Enable required APIs
        if not self.enable_required_apis():
            return False

        # Step 4: Create staging bucket
        if not self.create_staging_bucket():
            return False

        # Step 5: Verify agent import
        if not self.verify_agent_import():
            return False

        # Step 6: Deploy agent
        resource_name = self.deploy_agent()

        if resource_name:
            logger.info("\n✓ All deployment steps completed successfully!")
            return True
        else:
            logger.error("\n✗ Deployment failed")
            return False


def main():
    """Main entry point for the deployment script."""
    parser = argparse.ArgumentParser(
        description='Deploy Agent Builder Pro to Vertex AI Agent Engine Runtime'
    )
    parser.add_argument(
        '--project',
        help='GCP project ID (default: GOOGLE_CLOUD_PROJECT env var)'
    )
    parser.add_argument(
        '--location',
        default='us-central1',
        help='GCP location (default: us-central1)'
    )
    parser.add_argument(
        '--bucket',
        help='GCS staging bucket name (default: auto-generated)'
    )
    parser.add_argument(
        '--max-retries',
        type=int,
        default=3,
        help='Maximum deployment retry attempts (default: 3)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Run checks without deploying'
    )

    args = parser.parse_args()

    # Create deployer instance
    deployer = VertexAIDeployer(
        project_id=args.project,
        location=args.location,
        staging_bucket=args.bucket
    )

    try:
        if args.dry_run:
            logger.info("DRY RUN MODE - No deployment will occur")
            # Run checks only
            checks_passed = (
                deployer.check_gcloud_auth() and
                deployer.verify_environment_variables() and
                deployer.enable_required_apis() and
                deployer.verify_agent_import()
            )
            if checks_passed:
                logger.info("✓ All pre-deployment checks passed")
                return 0
            else:
                logger.error("✗ Some pre-deployment checks failed")
                return 1
        else:
            # Run full deployment
            success = deployer.run_full_deployment()
            return 0 if success else 1

    except KeyboardInterrupt:
        logger.info("\nDeployment cancelled by user")
        return 130
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
