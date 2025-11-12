# Deploying Agent Builder Pro to Vertex AI

This guide walks through deploying Agent Builder Pro to Vertex AI Agent Engine Runtime.

## Prerequisites

### 1. Google Cloud Platform Setup

- GCP project with billing enabled
- gcloud CLI installed and configured
- Required APIs enabled (handled automatically by deployment script):
  - Vertex AI API (`aiplatform.googleapis.com`)
  - Cloud Storage API (`storage.googleapis.com`)
  - Compute Engine API (`compute.googleapis.com`)

### 2. Local Environment

```bash
# Install dependencies
pip install -r requirements.txt

# Authenticate with GCP
gcloud auth application-default login

# Set your project
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_CLOUD_LOCATION="us-central1"  # Optional, defaults to us-central1
```

## Deployment Methods

### Method 1: Using the Deployment Script (Recommended)

The `deploy_to_vertex.py` script handles all deployment steps automatically:

```bash
# Basic deployment (uses environment variables)
python deploy_to_vertex.py

# Specify project and location
python deploy_to_vertex.py --project my-project-id --location us-central1

# Custom staging bucket
python deploy_to_vertex.py --bucket gs://my-custom-bucket

# Dry run (check without deploying)
python deploy_to_vertex.py --dry-run

# Help
python deploy_to_vertex.py --help
```

#### What the Script Does

1. ✓ **Authentication Check**: Verifies gcloud credentials
2. ✓ **Environment Validation**: Checks required variables
3. ✓ **API Enablement**: Enables required GCP APIs
4. ✓ **Bucket Creation**: Creates staging bucket if needed
5. ✓ **Agent Verification**: Imports and validates agent code
6. ✓ **Deployment**: Deploys to Vertex AI with retry logic

### Method 2: Manual Deployment

If you prefer manual control:

```python
import vertexai
from vertexai import agent_engines
from agent_builder_pro.agent import root_agent

# Initialize client
client = vertexai.Client(
    project="your-project-id",
    location="us-central1"
)

# Create app wrapper
app = agent_engines.AdkApp(root_agent=root_agent)

# Deploy
remote_agent = client.agent_engines.create(
    agent=app,
    config={
        "requirements": [
            "google-cloud-aiplatform[agent_engines,adk]>=1.112",
            "google-adk>=0.3.0"
        ],
        "staging_bucket": "gs://your-staging-bucket",
        "display_name": "Agent Builder Pro",
        "min_instances": 0,
        "max_instances": 1
    }
)

print(f"Deployed: {remote_agent.api_resource.name}")
```

## Configuration

### Environment Variables

Required:
- `GOOGLE_CLOUD_PROJECT`: Your GCP project ID

Optional:
- `GOOGLE_CLOUD_LOCATION`: GCP region (default: us-central1)
- `STAGING_BUCKET`: Custom staging bucket (auto-generated if not set)

### Staging Bucket

The deployment automatically creates a bucket with pattern:
```
gs://agent-builder-staging-claude-code-{project_id}
```

Or specify your own:
```bash
python deploy_to_vertex.py --bucket gs://my-custom-bucket
```

### Resource Configuration

Default settings in `deployment_config.yaml`:
- **Machine Type**: n1-standard-4
- **Min Instances**: 0 (scales to zero when idle)
- **Max Instances**: 1
- **Location**: us-central1

## Deployment Output

Successful deployment shows:

```
======================================================================
✓ DEPLOYMENT SUCCESSFUL!
======================================================================
Resource Name: projects/12345/locations/us-central1/reasoningEngines/98765
Display Name: Agent Builder Pro
Location: us-central1
Staging Bucket: gs://agent-builder-staging-claude-code-my-project
======================================================================
```

## Using the Deployed Agent

### Via Python SDK

```python
import vertexai
from vertexai import agent_engines

# Initialize client
client = vertexai.Client(project="your-project-id", location="us-central1")

# Get the deployed agent
resource_name = "projects/12345/locations/us-central1/reasoningEngines/98765"
remote_agent = client.agent_engines.get(resource_name)

# Query the agent
response = remote_agent.query(
    prompt="I want to build a customer service agent that handles product inquiries"
)

print(response)
```

### Via REST API

```bash
# Get access token
TOKEN=$(gcloud auth print-access-token)

# Query the agent
curl -X POST \
  "https://us-central1-aiplatform.googleapis.com/v1/projects/PROJECT_ID/locations/us-central1/reasoningEngines/ENGINE_ID:query" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "I want to build a data processing agent"
  }'
```

## Updating the Deployed Agent

To update the agent after code changes:

```bash
# 1. Make your code changes
# 2. Test locally
adk web

# 3. Redeploy
python deploy_to_vertex.py
```

Note: Each deployment creates a new version. Old versions can be deleted via Cloud Console.

## Monitoring and Logs

### View Logs

```bash
# Via gcloud
gcloud logging read "resource.type=aiplatform.googleapis.com/ReasoningEngine" \
  --project=your-project-id \
  --limit=50 \
  --format=json

# Via Cloud Console
# Navigate to: Vertex AI > Agent Engine > Your Agent > Logs
```

### Monitoring Metrics

Monitor in Cloud Console:
- Request count
- Response latency
- Error rate
- Instance count (should be 0 when idle due to scale-to-zero)

## Troubleshooting

### Authentication Errors

```bash
# Error: Could not automatically determine credentials
gcloud auth application-default login

# Verify authentication
gcloud auth application-default print-access-token
```

### API Not Enabled

```bash
# The script enables APIs automatically, but you can manually enable:
gcloud services enable aiplatform.googleapis.com --project=your-project-id
gcloud services enable storage.googleapis.com --project=your-project-id
```

### Permission Denied

You need these IAM roles:
```bash
# Grant roles (requires project owner/admin)
gcloud projects add-iam-policy-binding your-project-id \
  --member="user:your-email@example.com" \
  --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding your-project-id \
  --member="user:your-email@example.com" \
  --role="roles/storage.objectAdmin"
```

### Quota Exceeded

The deployment script automatically retries on quota errors with exponential backoff.

If persistent:
1. Check quotas: https://console.cloud.google.com/iam-admin/quotas
2. Request quota increase if needed
3. Try a different region

### Deployment Timeout

```bash
# Increase timeout with max retries
python deploy_to_vertex.py --max-retries 5
```

### Import Errors During Deployment

Ensure you're running from the correct directory:
```bash
cd python/agents/agent-builder-pro
python deploy_to_vertex.py
```

### Bucket Already Exists (Different Region)

```bash
# Use a different bucket name
python deploy_to_vertex.py --bucket gs://my-unique-bucket-name
```

## Cost Management

### Estimated Costs

With `min_instances: 0` (default):
- **Idle**: $0 (scales to zero)
- **Active**: ~$50-100/month with moderate usage
- **Per request**: Varies by model calls and processing time

### Cost Optimization Tips

1. **Scale to Zero**: Default configuration scales to zero when idle
2. **Monitor Usage**: Set up budget alerts in Cloud Console
3. **Choose Region**: Some regions have lower costs
4. **Use Flash Model**: For simpler sub-agents, use gemini-2.5-flash instead of pro

### Set Budget Alerts

```bash
# Create budget alert (example: $100/month)
gcloud billing budgets create \
  --billing-account=BILLING_ACCOUNT_ID \
  --display-name="Agent Builder Pro Budget" \
  --budget-amount=100 \
  --threshold-rule=percent=50 \
  --threshold-rule=percent=90 \
  --threshold-rule=percent=100
```

## Cleanup

### Delete the Deployed Agent

```bash
# Via gcloud
gcloud ai reasoning-engines delete REASONING_ENGINE_ID \
  --region=us-central1 \
  --project=your-project-id

# Via Python
import vertexai
client = vertexai.Client(project="your-project-id", location="us-central1")
client.agent_engines.delete("projects/.../reasoningEngines/...")
```

### Delete Staging Bucket

```bash
# Delete bucket and all contents
gsutil -m rm -r gs://agent-builder-staging-claude-code-your-project
```

## Production Considerations

### Security

- [ ] Never commit credentials or API keys
- [ ] Use service accounts for production
- [ ] Enable VPC Service Controls if needed
- [ ] Review IAM permissions regularly

### Reliability

- [ ] Set up monitoring and alerting
- [ ] Configure error budgets
- [ ] Test failover scenarios
- [ ] Document incident response procedures

### Performance

- [ ] Benchmark response times
- [ ] Optimize model selection (Flash vs Pro)
- [ ] Consider increasing max_instances for high traffic
- [ ] Cache frequent responses if applicable

### Compliance

- [ ] Review data residency requirements
- [ ] Ensure GDPR/privacy compliance
- [ ] Document data handling procedures
- [ ] Regular security audits

## Support

For issues with:
- **ADK**: See [ADK documentation](https://google.github.io/adk-docs/)
- **Vertex AI**: See [Vertex AI docs](https://cloud.google.com/vertex-ai/docs)
- **This Agent**: Open an issue in the repository

---

**Deployment Status Parallel Testing**: This deployment is part of a parallel experiment comparing Claude Code vs Jules deployment workflows.
