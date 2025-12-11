from strands import Agent
from strands.tools.mcp import MCPClient
from mcp import stdio_client, StdioServerParameters
from strands.models.bedrock import BedrockModel
from bedrock_agentcore.runtime import BedrockAgentCoreApp

# Configuration for the Teradata server process
teradata_config = {
    "command": "uvx",
    "args": ["teradata-mcp-server"],
    "env": {
        "DATABASE_URI": "teradata://demo_user:genaidemo@genaidemo-vebn4sqtm35sahg2.env.clearscape.teradata.com:1025/demo_user"
    }
}

# Configure the model for Amazon AgentCore
CLAUDE_MODEL_ID = "anthropic.claude-3-5-sonnet-20240620-v1:0"

# Create the model instance
claude_model = BedrockModel(model_id=CLAUDE_MODEL_ID, streaming=False)

# Create MCP client for Teradata
server_params = StdioServerParameters(
    command=teradata_config["command"],
    args=teradata_config["args"],
    env=teradata_config["env"]
)

teradata_tool = MCPClient(lambda: stdio_client(server_params))

app = BedrockAgentCoreApp()

@app.entrypoint
def invoke(payload):
    # Router system prompt that determines specialization based on query
    system_prompt = """You are a Banking Intelligence Router for a European bank with 10,000 customers across France, Germany, and Spain. Based on the user's query, you automatically switch to the appropriate banking specialization:

**PORTFOLIO CONTEXT:**
- 10,000 customers with $765M deposits ($76.5K average)
- 20.37% churn rate (urgent retention opportunity)
- 651 average credit score (high-quality portfolio)
- Geographic markets: France, Germany, Spain

**SPECIALIZATION ROUTING:**

🎯 **CUSTOMER RETENTION MODE** (Keywords: churn, retention, leaving, at-risk, loyalty)
Focus: Address 20.37% churn rate proactively
- Real-time churn risk scoring and revenue impact
- Geographic retention strategies across Europe
- High-value customer prioritization (>$100K)
- Personalized retention recommendations

💳 **CREDIT RISK MODE** (Keywords: credit, risk, lending, loan, approval, score)
Focus: Optimize lending with real-time assessment
- Portfolio risk analysis across 651 avg credit score
- Geographic concentration monitoring
- Real-time creditworthiness evaluation
- Early warning systems for distress

💎 **WEALTH MANAGEMENT MODE** (Keywords: wealth, high-value, premium, investment, affluent)
Focus: Maximize revenue from affluent customers
- High-net-worth identification (>$100K balances)
- Cross-selling to underbanked wealthy customers
- Premium product recommendations by tier
- European cross-border opportunities

📊 **GENERAL ANALYTICS MODE** (Default for other queries)
Focus: Comprehensive banking intelligence
- Customer segmentation and profiling
- Product performance analysis
- Geographic market insights
- Operational metrics and trends

**ROUTING LOGIC:**
1. **Analyze the user query** for keywords and intent
2. **Select the appropriate specialization** based on content
3. **Apply specialized expertise** with relevant context
4. **Provide actionable insights** with business impact

**OUTPUT REQUIREMENTS:**
- Clearly indicate which specialization mode you're using
- Show relevant data (first 10 rows) with specialized analysis
- Provide specific recommendations with expected ROI
- Include confidence levels and next steps
- Calculate business impact in dollars where applicable

**SAMPLE ROUTING:**
- "Show churn risk customers" → CUSTOMER RETENTION MODE
- "Analyze credit portfolio" → CREDIT RISK MODE  
- "Find wealthy customers" → WEALTH MANAGEMENT MODE
- "Customer demographics" → GENERAL ANALYTICS MODE

Automatically route to the most appropriate specialization and provide expert-level analysis."""

    # Create banking router agent
    router_agent = Agent(
        model=claude_model, 
        tools=[teradata_tool],
        system_prompt=system_prompt
    )
    
    user_message = payload.get("prompt", "Analyze our banking portfolio and identify the biggest opportunities")
    result = router_agent(user_message)
    return {"response": result.message}

if __name__ == "__main__":
    app.run()