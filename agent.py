from strands import Agent
from strands.tools.mcp import MCPClient
from mcp import stdio_client, StdioServerParameters
from strands.models.bedrock import BedrockModel

from bedrock_agentcore.runtime import BedrockAgentCoreApp  #Bedrock agentcoreApp

# Configuration for the Teradata server process
teradata_config = {
    "command": "uvx",
    "args": ["teradata-mcp-server"],
    "env": {
        "DATABASE_URI": "teradata://demo_user:genaidemo@genaidemo-vebn4sqtm35sahg2.env.clearscape.teradata.com:1025/demo_user"
    }
}


# Configure the model for AgentCore
#LLAMA_MODEL_ID = "anthropic.claude-3-sonnet-20240229-v1:0" 
LLAMA_MODEL_ID = "anthropic.claude-3-5-sonnet-20240620-v1:0"


# Create the new model instance
llama_model = BedrockModel(model_id=LLAMA_MODEL_ID, streaming=False)

# 1. Define the StdioServerParameters using the configuration
server_params = StdioServerParameters(
    command=teradata_config["command"],
    args=teradata_config["args"],
    env=teradata_config["env"]
)

# 2. Create the MCP client tool using a lambda factory
# This passes the *config* to the stdio client, not the MCPClient itself.
teradata_tool = MCPClient(
    lambda: stdio_client(server_params)
    
)

app = BedrockAgentCoreApp()  #Bedrock AgentCoreApp

@app.entrypoint
def invoke(payload):
    # System prompt to show raw data but limit output to avoid token limits
    system_prompt = """You are a Teradata database assistant for a financial industry. When users ask for database information:

1. Show actual raw data from tool results, but limit to first 10 rows to avoid token limits
2. Display data in clear table format with column headers  
3. After showing data, mention total count if available
4. Be concise but show real data, not summaries

Example: Show first 10 database names with types, then say "Total: X databases found" """

    # Create a fresh agent for each request to avoid state issues
    agent = Agent(
        model=llama_model, 
        tools=[teradata_tool],
        system_prompt=system_prompt
    )
    user_message = payload.get("prompt", "What are the databases available?")
    result = agent(user_message)
    return {"response": result.message} # The output format expected by AgentCore

if __name__ == "__main__":
    app.run()