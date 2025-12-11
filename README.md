# Teradata MCP AgentCore

A Teradata database assistant built with AWS Bedrock AgentCore and the Model Context Protocol (MCP). This agent provides intelligent database interactions for financial industry use cases, leveraging Anthropic's Claude 3.5 Sonnet model.

## Features

- **Teradata Database Integration**: Direct connection to Teradata databases via MCP server
- **AWS Bedrock AgentCore**: Serverless deployment on AWS infrastructure
- **Claude 3.5 Sonnet**: Advanced language model for intelligent database queries
- **Financial Industry Focus**: Optimized for financial data analysis and reporting
- **Raw Data Display**: Shows actual database results with smart formatting and limits

## Architecture

The application consists of:
- **Agent Core**: AWS Bedrock AgentCore runtime for serverless execution
- **MCP Client**: Model Context Protocol client for Teradata connectivity
- **Strands Framework**: Agent orchestration and tool management
- **Teradata MCP Server**: Database connectivity and query execution

## Prerequisites

- Python 3.12+
- AWS Account with Bedrock AgentCore access
- Teradata database access
- UV package manager (for MCP server)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd tdmcpagentcore
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install UV for MCP server management:
```bash
# Follow installation guide: https://docs.astral.sh/uv/getting-started/installation/
```

## Configuration

### Database Connection

Update the Teradata connection string in `agent.py`:
```python
teradata_config = {
    "command": "uvx",
    "args": ["teradata-mcp-server"],
    "env": {
        "DATABASE_URI": "teradata://username:password@host:port/database"
    }
}
```

### AWS Configuration

The agent is configured for AWS Bedrock AgentCore deployment. Update `.bedrock_agentcore.yaml` with your AWS settings:
- Execution role ARN
- AWS account ID and region
- ECR repository
- Network configuration

## Usage

### Local Development

Run the agent locally:
```bash
python agent.py
```

### AWS Deployment

Deploy to Bedrock AgentCore:
```bash
# Use Bedrock AgentCore CLI or SDK for deployment
```

### Example Queries

The agent can handle various database operations:
- "What databases are available?"
- "Show me the tables in the finance database"
- "Get the top 10 customers by revenue"
- "Analyze quarterly sales trends"

## Project Structure

```
tdmcpagentcore/
├── agent.py                 # Main agent implementation
├── main.py                  # Entry point
├── pyproject.toml          # Project configuration
├── requirements.txt        # Python dependencies
├── .bedrock_agentcore.yaml # AWS AgentCore configuration
├── .bedrock_agentcore/     # AgentCore deployment files
└── README.md              # This file
```

## Key Dependencies

- **bedrock-agentcore**: AWS Bedrock AgentCore SDK
- **strands-agents**: Agent framework and orchestration
- **mcp**: Model Context Protocol implementation
- **teradata-mcp-server**: Teradata database connectivity
- **botocore**: AWS SDK core functionality

## Features in Detail

### Smart Data Display
- Limits output to first 10 rows to avoid token limits
- Clear table formatting with column headers
- Total count display when available
- Concise but comprehensive data presentation

### Financial Industry Optimization
- Tailored system prompts for financial use cases
- Optimized for common financial data patterns
- Support for financial reporting and analysis queries

## Development

### Adding New Tools
Extend the agent by adding new MCP tools to the `tools` list in `agent.py`.

### Customizing Prompts
Modify the `system_prompt` in the `invoke` function to adjust agent behavior.

### Model Configuration
Change the model by updating `LLAMA_MODEL_ID` to use different Bedrock models.

