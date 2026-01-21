#!/bin/bash
# setup_agentcore.sh
# Run this inside /home/ubuntu/workshop/tdmcpagentcore
# Creates all required files for AgentCore deployment

set -e

WORKSHOP_DIR=$(pwd)

echo "🔧 Setting up AgentCore in: $WORKSHOP_DIR"
echo ""

# Check we're in the right directory
if [[ ! "$WORKSHOP_DIR" == *"tdmcpagentcore"* ]]; then
    echo "⚠️  Warning: Expected to be in tdmcpagentcore directory"
    echo "   Current: $WORKSHOP_DIR"
    read -p "   Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Get AWS account ID from IAM role
echo "📡 Getting AWS account info..."
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION="us-east-1"
echo "   Account ID: $ACCOUNT_ID"
echo "   Region: $REGION"
echo ""

# 1. Create .env file
echo "📝 Creating .env file..."
cat > .env << 'ENV_END'
# Teradata Workshop Configuration
# Update TERADATA_DATABASE_URI with your cluster endpoint

TERADATA_DATABASE_URI=teradata://dbc:TeradataTest2024@34.229.185.194:1025/dbc
AWS_DEFAULT_REGION=us-east-1
ENV_END
echo "   ✅ .env created"

# 2. Create requirements_linux.txt
echo "📝 Creating requirements_linux.txt..."
cat > requirements_linux.txt << 'REQ_END'
strands-agents>=1.19.0
mcp>=1.22.0
boto3
bedrock-agentcore>=1.1.1
python-dotenv
streamlit
REQ_END
echo "   ✅ requirements_linux.txt created"

# 3. Create Dockerfile
echo "📝 Creating Dockerfile..."
cat > Dockerfile << 'DOCKER_END'
# Teradata Workshop - AgentCore Container
FROM --platform=linux/arm64 ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements_linux.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install aws-opentelemetry-distro==0.12.2

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV AWS_REGION=us-east-1

# Expose port
EXPOSE 8080

# Run the application
CMD ["opentelemetry-instrument", "python", "agent.py"]
DOCKER_END
echo "   ✅ Dockerfile created"

# 4. Create .bedrock_agentcore.yaml
echo "📝 Creating .bedrock_agentcore.yaml..."
cat > .bedrock_agentcore.yaml << YAML_END
default_agent: agent
agents:
  agent:
    name: teradata-workshop-agent
    entrypoint: ${WORKSHOP_DIR}/agent.py
    deployment_type: container
    runtime_type: null
    platform: linux/arm64
    container_runtime: none
    source_path: ${WORKSHOP_DIR}
    aws:
      execution_role_auto_create: true
      account: '${ACCOUNT_ID}'
      region: ${REGION}
      ecr_auto_create: true
      s3_auto_create: true
      network_configuration:
        network_mode: PUBLIC
        network_mode_config: null
      protocol_configuration:
        server_protocol: HTTP
      observability:
        enabled: true
      lifecycle_configuration:
        idle_runtime_session_timeout: null
        max_lifetime: null
    memory:
      mode: NO_MEMORY
      memory_id: null
      memory_arn: null
      memory_name: null
      event_expiry_days: 30
      first_invoke_memory_check_done: false
      was_created_by_toolkit: false
    identity:
      credential_providers: []
      workload: null
    aws_jwt:
      enabled: false
      audiences: []
      signing_algorithm: ES384
      issuer_url: null
      duration_seconds: 300
    authorizer_configuration: null
    request_header_configuration: null
    oauth_configuration: null
    api_key_env_var_name: null
    api_key_credential_provider_name: null
    is_generated_by_agentcore_create: false
YAML_END
echo "   ✅ .bedrock_agentcore.yaml created"

# 5. Update agent.py to use load_dotenv if not already
if ! grep -q "load_dotenv" agent.py 2>/dev/null; then
    echo "📝 Adding load_dotenv to agent.py..."
    # Create backup
    cp agent.py agent.py.bak
    # Add import at top
    sed -i '1i from dotenv import load_dotenv\nload_dotenv()\n' agent.py
    echo "   ✅ agent.py updated (backup: agent.py.bak)"
else
    echo "   ℹ️  agent.py already has load_dotenv"
fi

echo ""
echo "=============================================="
echo "✅ Setup complete!"
echo "=============================================="
echo ""
echo "Files created:"
echo "  - .env (Teradata connection)"
echo "  - .bedrock_agentcore.yaml (AgentCore config)"
echo "  - Dockerfile (container build)"
echo "  - requirements_linux.txt (dependencies)"
echo ""
echo "Next steps:"
echo "  1. Verify .env has correct TERADATA_DATABASE_URI"
echo "  2. Run: agentcore deploy"
echo "  3. Test: agentcore invoke --prompt 'What tables are available?'"
echo ""
