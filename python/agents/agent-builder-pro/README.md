# Agent Builder Pro

**A production-ready meta-agent system for creating custom Google ADK agents**

Agent Builder Pro is an intelligent assistant that guides you through the complete process of designing, generating, and deploying ADK-based AI agents. It uses a sophisticated multi-agent architecture to handle everything from requirements gathering to production deployment.

## 🌟 Features

- **Interactive Requirements Gathering**: Natural conversation-based approach to understand your agent needs
- **Intelligent Architecture Design**: Analyzes complexity and suggests optimal agent patterns (LlmAgent, SequentialAgent, ParallelAgent, LoopAgent, CustomBaseAgent)
- **MCP Server Discovery**: Automatically detects available MCP servers and suggests integrations
- **Context-Aware Suggestions**: Analyzes your project structure to recommend relevant tools
- **Complete Code Generation**: Generates production-ready code with error handling, logging, and documentation
- **Fault-Tolerant Design**: Gracefully handles missing MCPs and deployment failures
- **Automated Deployment**: Deploys to Vertex AI Agent Engine Runtime with retry logic
- **Cost Estimation**: Provides token usage and cost estimates for your agent design

## 🏗️ Architecture

Agent Builder Pro uses a **SequentialAgent** pattern with 5 specialized sub-agents:

```
┌─────────────────────────────────────────┐
│     Agent Builder Pro (Root)            │
│     SequentialAgent Orchestrator        │
└─────────────────────────────────────────┘
                  │
        ┌─────────┴─────────┐
        │   Sequential Flow  │
        └─────────┬─────────┘
                  │
    ┌─────────────┼─────────────┐
    │             │             │
    ▼             ▼             ▼
┌────────┐   ┌────────┐   ┌────────┐
│ Sub-   │   │ Sub-   │   │ Sub-   │
│ Agent  │──▶│ Agent  │──▶│ Agent  │
│   1    │   │   2    │   │   3    │
└────────┘   └────────┘   └────────┘
Requirements  Architecture  Tool
Gatherer      Designer      Specification
    │             │             │
    └─────────────┼─────────────┘
                  ▼
    ┌─────────────┼─────────────┐
    │             │             │
    ▼             ▼             ▼
┌────────┐   ┌────────────────┐
│ Sub-   │   │ Sub-Agent 5    │
│ Agent  │──▶│ Validation &   │
│   4    │   │ Deployment     │
└────────┘   └────────────────┘
Code
Generator
```

### Sub-Agent Details

1. **Requirements Gatherer** (LlmAgent)
   - Conducts adaptive conversation to understand user needs
   - Discovers available MCP servers
   - Analyzes project context
   - **Output**: requirements_spec

2. **Architecture Designer** (LlmAgent)
   - Analyzes complexity
   - Suggests optimal agent type
   - Provides cost estimates
   - **Output**: architecture_design

3. **Tool Specification** (LlmAgent)
   - Identifies MCP tools, Google tools, and custom functions
   - Specifies tool parameters and requirements
   - **Output**: tool_specs

4. **Code Generator** (LlmAgent)
   - Generates complete ADK project
   - Creates agent.py, tools.py, tests, deployment scripts
   - Includes error handling and documentation
   - **Output**: project_files

5. **Validation & Deployment** (LlmAgent)
   - Validates syntax and best practices
   - Runs linting checks
   - Deploys to Vertex AI with retry logic
   - **Output**: deployment_result

## 📋 Prerequisites

- Python 3.10 or higher
- Google Cloud Platform account
- Vertex AI API enabled
- ADK installed: `pip install google-adk`
- gcloud CLI configured: `gcloud auth application-default login`

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository (if not already cloned)
git clone https://github.com/google/adk-samples.git
cd adk-samples/python/agents/agent-builder-pro

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env and set your values
# - GOOGLE_CLOUD_PROJECT: Your GCP project ID
# - GOOGLE_CLOUD_LOCATION: GCP region (default: us-central1)
# - STAGING_BUCKET: GCS bucket for deployment artifacts
```

### 3. Run Locally

```bash
# Start the ADK web interface
adk web

# Open browser to http://localhost:8000
# Start chatting with Agent Builder Pro!
```

### 4. Example Conversation

```
You: I want to build a customer service agent that handles product inquiries
     and can check inventory

Agent Builder Pro: Great! Let me help you build that. I have a few questions:

                   1. Who will be using this agent - end customers,
                      support staff, or both?
                   2. What data sources does it need to access for inventory?

[Continues conversation...]

Agent Builder Pro: Based on our discussion, I recommend a SequentialAgent with:
                   - LlmAgent for customer interaction
                   - Sub-agent for inventory lookup
                   Would you like to proceed with this architecture?

[Generates code, validates, and optionally deploys...]

Agent Builder Pro: ✓ Your agent has been generated successfully!
                   ✓ All validation checks passed
                   Would you like me to deploy it to Vertex AI?
```

## 🛠️ Fault Tolerance Features

### MCP Server Discovery
- Searches multiple common locations for MCP configuration
- Returns empty list if no MCPs found (never crashes)
- Provides clear error messages for invalid configs

### Deployment Retry Logic
- Automatic retry on transient failures (quota, rate limits, timeouts)
- Exponential backoff (2s, 4s, 8s)
- Maximum 3 attempts by default
- Clear error messages guide troubleshooting

### Defensive Validation
- Type checking for all inputs
- None handling with sensible defaults
- Comprehensive error logging
- Generated code includes error handling patterns

## 📁 Project Structure

```
agent-builder-pro/
├── agent_builder_pro/
│   ├── __init__.py
│   ├── agent.py                 # Root SequentialAgent
│   ├── sub_agents/              # 5 specialized sub-agents
│   │   ├── requirements_gatherer.py
│   │   ├── architecture_designer.py
│   │   ├── tool_specification.py
│   │   ├── code_generator.py
│   │   └── validation_deployment.py
│   ├── tools/                   # Tools for sub-agents
│   │   ├── mcp_tools.py        # MCP discovery (fault-tolerant)
│   │   ├── pattern_tools.py    # ADK pattern knowledge
│   │   ├── generation_tools.py # Code generation
│   │   └── deployment_tools.py # Vertex AI deployment
│   ├── utils/                   # Utilities
│   │   ├── error_handling.py   # @graceful_failure decorator
│   │   ├── logging_config.py   # Centralized logging
│   │   └── validators.py       # Input validation
│   └── templates/               # Code generation templates
│       └── prompts.py          # Sub-agent prompts
├── tests/
│   └── test_agents.py
├── requirements.txt
├── .env.example
└── README.md
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=agent_builder_pro --cov-report=html

# Run specific test file
pytest tests/test_agents.py
```

## 🔍 Troubleshooting

### No MCP Servers Found

This is **not an error** - Agent Builder Pro works without MCPs:
- The system will ask more questions to understand your needs
- You can manually specify tool requirements
- Generated agents won't include MCP integrations (can be added later)

**To add MCPs**: Create a config file at one of these locations:
- `~/.config/claude/claude_desktop_config.json`
- `~/.claude/mcp_config.json`
- `./mcp_config.json`

### Deployment Failures

**Error: Missing GOOGLE_CLOUD_PROJECT**
```bash
# Check your .env file
cat .env

# Or set environment variable
export GOOGLE_CLOUD_PROJECT=your-project-id
```

**Error: Quota exceeded**
- The deployment script will automatically retry
- Wait a few minutes and try again
- Check your GCP quotas: https://console.cloud.google.com/iam-admin/quotas

**Error: Permission denied on staging bucket**
```bash
# Grant your account Storage Object Admin role
gcloud storage buckets add-iam-policy-binding gs://your-bucket \
    --member="user:your-email@example.com" \
    --role="roles/storage.objectAdmin"
```

### Import Errors

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check Python version (requires 3.10+)
python --version
```

## 🎯 Example Use Cases

### Simple Customer Service Bot
- **Agent Type**: LlmAgent
- **Tools**: FAQ lookup, ticket creation
- **Model**: gemini-2.5-flash (cost-effective)

### Research Assistant with Multiple Sources
- **Agent Type**: ParallelAgent
- **Tools**: Web search, document retrieval, academic databases
- **Model**: gemini-2.5-pro (better reasoning)

### Data Processing Pipeline
- **Agent Type**: SequentialAgent
- **Sub-agents**: Data validation → Processing → Report generation
- **Model**: gemini-2.5-flash for each stage

### Iterative Code Improvement
- **Agent Type**: LoopAgent
- **Tools**: Code execution, linting, testing
- **Model**: gemini-2.5-pro (complex reasoning)

## 🤝 Contributing

Contributions are welcome! Please see the [main contributing guidelines](../../CONTRIBUTING.md).

## 📄 License

Copyright 2025 Google LLC

Licensed under the Apache License, Version 2.0. See [LICENSE](../../LICENSE) for details.

## ⚠️ Disclaimer

This agent is for demonstration purposes and may require customization for production use. Always review generated code before deploying to production environments.

## 🔗 Related Resources

- [ADK Documentation](https://google.github.io/adk-docs/)
- [ADK Python GitHub](https://github.com/google/adk-python)
- [Vertex AI Agent Engine](https://cloud.google.com/vertex-ai/docs/generative-ai/agent-engine)
- [Gemini Models](https://ai.google.dev/models/gemini)

---

**Built with ❤️ using Google ADK**
