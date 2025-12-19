# Security Configuration Guide

## Environment Variables for Sensitive Data

### Overview
All sensitive configuration data (database credentials, API keys) should be stored in environment variables rather than hardcoded in source files.

### Local Development

#### 1. Setup Environment File
```bash
# Copy the example file
cp .env.example .env

# Edit with your actual credentials
nano .env
```

#### 2. Required Environment Variables
```bash
# Teradata Database Connection
TERADATA_DATABASE_URI=teradata://username:password@host:port/database

# Optional: AWS Configuration (for local testing)
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-east-1

# Optional: Model Configuration
CLAUDE_MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0
```

### Amazon AgentCore Production Deployment

#### Option 1: Environment Variables in AgentCore Config
```yaml
# .bedrock_agentcore.yaml
agents:
  agent:
    environment:
      TERADATA_DATABASE_URI: "teradata://username:password@host:port/database"
```

#### Option 2: AWS Secrets Manager (Recommended)
1. **Store credentials in AWS Secrets Manager:**
```bash
aws secretsmanager create-secret \
    --name "teradata-banking-db" \
    --description "Teradata database credentials for banking agents" \
    --secret-string '{"username":"your_user","password":"your_pass","host":"your_host","port":"1025","database":"your_db"}'
```

2. **Update agent code to use Secrets Manager:**
```python
import boto3
import json
import os

def get_database_uri():
    """Get database URI from AWS Secrets Manager or environment variable"""
    
    # Try environment variable first (for local development)
    if os.getenv("TERADATA_DATABASE_URI"):
        return os.getenv("TERADATA_DATABASE_URI")
    
    # Use AWS Secrets Manager for production
    secret_name = "teradata-banking-db"
    region_name = "us-east-1"
    
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )
    
    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        secret = json.loads(get_secret_value_response['SecretString'])
        
        return f"teradata://{secret['username']}:{secret['password']}@{secret['host']}:{secret['port']}/{secret['database']}"
    except Exception as e:
        raise Exception(f"Failed to retrieve database credentials: {str(e)}")

# Updated teradata_config
teradata_config = {
    "command": "uvx",
    "args": ["teradata-mcp-server"],
    "env": {
        "DATABASE_URI": get_database_uri()
    }
}
```

#### Option 3: AWS Systems Manager Parameter Store
1. **Store credentials in Parameter Store:**
```bash
aws ssm put-parameter \
    --name "/banking-agents/teradata/database-uri" \
    --value "teradata://username:password@host:port/database" \
    --type "SecureString" \
    --description "Teradata database URI for banking agents"
```

2. **Update agent code to use Parameter Store:**
```python
import boto3
import os

def get_database_uri():
    """Get database URI from Parameter Store or environment variable"""
    
    # Try environment variable first (for local development)
    if os.getenv("TERADATA_DATABASE_URI"):
        return os.getenv("TERADATA_DATABASE_URI")
    
    # Use Parameter Store for production
    ssm = boto3.client('ssm', region_name='us-east-1')
    
    try:
        response = ssm.get_parameter(
            Name='/banking-agents/teradata/database-uri',
            WithDecryption=True
        )
        return response['Parameter']['Value']
    except Exception as e:
        raise Exception(f"Failed to retrieve database URI from Parameter Store: {str(e)}")
```

### Security Best Practices

#### 1. Never Commit Sensitive Data
- Add `.env` to `.gitignore`
- Use `.env.example` for documentation
- Never hardcode credentials in source code

#### 2. Use Least Privilege Access
```yaml
# IAM policy for AgentCore execution role
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "secretsmanager:GetSecretValue"
            ],
            "Resource": "arn:aws:secretsmanager:us-east-1:*:secret:teradata-banking-db*"
        }
    ]
}
```

#### 3. Rotate Credentials Regularly
- Set up automatic rotation in AWS Secrets Manager
- Update database passwords quarterly
- Monitor access logs for unusual activity

#### 4. Network Security
```yaml
# .bedrock_agentcore.yaml - Use private networking
network_configuration:
  network_mode: PRIVATE
  vpc_configuration:
    vpc_id: vpc-xxxxxxxxx
    subnet_ids:
      - subnet-xxxxxxxxx
      - subnet-yyyyyyyyy
    security_group_ids:
      - sg-xxxxxxxxx
```

#### 5. Encryption
- Enable encryption in transit for database connections
- Use TLS 1.2+ for all communications
- Enable CloudTrail for audit logging

### Environment-Specific Configuration

#### Development
```bash
# .env (local development)
TERADATA_DATABASE_URI=teradata://dev_user:dev_pass@dev-host:1025/dev_db
CLAUDE_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0  # Cheaper for testing
```

#### Staging
```bash
# Use AWS Secrets Manager
SECRET_NAME=teradata-banking-db-staging
CLAUDE_MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0
```

#### Production
```bash
# Use AWS Secrets Manager with rotation
SECRET_NAME=teradata-banking-db-prod
CLAUDE_MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0
```

### Troubleshooting

#### Common Issues
1. **Environment variable not found**
   - Check `.env` file exists and is properly formatted
   - Verify environment variable names match exactly

2. **AWS Secrets Manager access denied**
   - Check IAM permissions for AgentCore execution role
   - Verify secret name and region are correct

3. **Database connection fails**
   - Test connection string manually
   - Check network connectivity and security groups
   - Verify database credentials are correct

#### Testing Configuration
```bash
# Test environment variables locally
python -c "import os; print(os.getenv('TERADATA_DATABASE_URI', 'Not found'))"

# Test AWS Secrets Manager access
aws secretsmanager get-secret-value --secret-id teradata-banking-db
```

### Compliance Considerations

#### GDPR & Data Protection
- Encrypt all customer data in transit and at rest
- Implement data retention policies
- Maintain audit logs for data access

#### Financial Regulations
- Follow PCI DSS for payment data
- Implement Basel III compliance monitoring
- Maintain SOX compliance for financial reporting

#### Banking Security Standards
- Use multi-factor authentication
- Implement network segmentation
- Regular security assessments and penetration testing