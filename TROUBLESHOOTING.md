# AgentCore Troubleshooting Guide

## RuntimeClientError: "An error occurred when starting the runtime"

This error typically occurs during agent startup. Here's how to diagnose and fix it:

### 🔍 **Step 1: Check CloudWatch Logs**

```bash
# Get your agent details
agentcore status

# Check CloudWatch logs in AWS Console:
# 1. Go to CloudWatch > Log groups
# 2. Look for: /aws/bedrock-agentcore/agent-[your-agent-id]
# 3. Check the latest log stream for error details
```

### 🛠️ **Step 2: Common Fixes**

#### **Fix 1: Syntax Error (FIXED)**
The issue was a malformed string in the database URI:
```python
# ❌ WRONG (extra quote)
"DATABASE_URI": os.getenv("TERADATA_DATABASE_URI", ""teradata://...")

# ✅ CORRECT
"DATABASE_URI": os.getenv("TERADATA_DATABASE_URI", "teradata://...")
```

#### **Fix 2: Test with Simple Agent**
Deploy the simplified agent first:

```bash
# Update .bedrock_agentcore.yaml to use simple agent
# Change entrypoint to: C:/work/tdmcpagentcore/agent_simple.py

agentcore deploy
```

#### **Fix 3: Check Dependencies**
Ensure all required packages are in requirements.txt:
```txt
bedrock-agentcore>=1.1.1
strands-agents>=1.19.0
mcp>=1.22.0
teradata-mcp-server>=0.1.0
```

#### **Fix 4: Environment Variables**
Verify environment variables are properly configured:

```yaml
# .bedrock_agentcore.yaml
agents:
  agent:
    environment:
      TERADATA_DATABASE_URI: "teradata://demo_user:genaidemo@genaidemo-vebn4sqtm35sahg2.env.clearscape.teradata.com:1025/demo_user"
```

### 🧪 **Step 3: Test Locally First**

```bash
# Test locally before cloud deployment
agentcore deploy --local

# If local works, then deploy to cloud
agentcore deploy
```

### 📋 **Step 4: Deployment Checklist**

- [ ] ✅ Fixed syntax error in agent.py
- [ ] ✅ Environment variables configured in .bedrock_agentcore.yaml
- [ ] ✅ All dependencies in requirements.txt
- [ ] ✅ Test with agent_simple.py first
- [ ] ✅ Check CloudWatch logs for specific errors

### 🔧 **Step 5: Alternative Deployment**

If issues persist, try deploying with command-line environment variables:

```bash
agentcore deploy --env TERADATA_DATABASE_URI="teradata://demo_user:genaidemo@genaidemo-vebn4sqtm35sahg2.env.clearscape.teradata.com:1025/demo_user"
```

### 📊 **Step 6: Verify Deployment**

```bash
# Check deployment status
agentcore status

# Test with simple query
agentcore invoke --prompt "What databases are available?"
```

### 🚨 **Common Error Patterns**

1. **Import Errors**: Missing dependencies in requirements.txt
2. **Syntax Errors**: Python syntax issues (like the extra quote)
3. **Environment Issues**: Missing or malformed environment variables
4. **MCP Server Issues**: teradata-mcp-server not available in container
5. **Model Access**: Insufficient permissions for Claude model

### 💡 **Quick Recovery Steps**

1. **Deploy Simple Agent**: Use `agent_simple.py` to test basic functionality
2. **Check Logs**: Always check CloudWatch logs for specific error messages
3. **Test Locally**: Use `--local` flag to test before cloud deployment
4. **Incremental Fixes**: Fix one issue at a time and redeploy

### 📞 **Getting Help**

If the issue persists:
1. Check CloudWatch logs for specific error messages
2. Test with the simple agent first
3. Verify all environment variables are set correctly
4. Ensure UV and teradata-mcp-server are available in the container environment