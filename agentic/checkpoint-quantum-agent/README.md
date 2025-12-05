# Check Point Quantum Blue Team Agent

A production-ready autonomous agent that interfaces with Check Point R82 Security Management via both MCP server and REST API for comprehensive blue team defensive operations.

## 🛡️ Overview

The Check Point Quantum Blue Team Agent is an intelligent security automation platform that enables natural language interaction with Check Point firewalls. It combines CrewAI multi-agent orchestration with Check Point's Management API to provide comprehensive security operations capabilities.

### Key Features

- **Natural Language Interface**: Process security commands in plain English
- **Multi-Agent Architecture**: Specialized agents for different security domains
- **Dual Integration**: Both MCP server and direct API support
- **Comprehensive Logging**: Structured logging with observability
- **Kubernetes Ready**: Full container orchestration support
- **Production Grade**: Error handling, retries, and resilience

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Natural Language Interface                │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                 Quantum Crew Orchestration                  │
├─────────────────┬─────────────────┬─────────────────────────┤
│  Quantum Agent  │ Log Analyzer    │ Policy Manager          │
│  (Orchestrator) │ (Log Analysis)  │ (Access Rules)          │
├─────────────────┼─────────────────┼─────────────────────────┤
│ Object Manager  │ Threat Prevention│ MCP Integration        │
│ (Network Objs)  │ (IPS Exceptions) │ (Alternative API)      │
└─────────────────┴─────────────────┴─────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│              Check Point R82 Management API                 │
│              (Smart-1 Cloud / On-Premises)                 │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Check Point R82 Management Server access
- OpenAI API key
- Docker (for containerized deployment)
- Kubernetes cluster (for orchestrated deployment)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd checkpoint-quantum-agent
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp env.example .env
   # Edit .env with your Check Point and OpenAI credentials
   ```

4. **Run the agent**
   ```bash
   python -m src.main --interactive
   ```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with the following variables:

```bash
# Check Point API Configuration
CHECKPOINT_MGMT_SERVER=https://your-smart1-cloud.checkpoint.com
CHECKPOINT_USERNAME=your_api_user
CHECKPOINT_PASSWORD=your_api_password
CHECKPOINT_DOMAIN=SMC User

# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here

# Agent Configuration
AGENT_NAME=quantum-blue-team-agent
LOG_LEVEL=INFO
LOG_FORMAT=json

# MCP Server Configuration
MCP_SERVER_ENABLED=true
MCP_SERVER_PATH=/path/to/mcp-server

# Kubernetes Configuration
K8S_NAMESPACE=blue-team
```

### Configuration Files

- `config/config.yaml`: Main agent configuration
- `config/prompts.yaml`: Agent prompts and system messages

## 🎯 Usage Examples

### Natural Language Commands

The agent understands natural language commands for all security operations:

#### Log Analysis
```bash
"Show me all blocked connections from 192.168.1.100 in the last hour"
"Analyze threat logs for the last 24 hours"
"What are the top sources of blocked traffic today?"
"Search logs for IP address 10.0.0.50"
```

#### Policy Management
```bash
"Create a rule to allow HTTPS from internal network to any"
"Show me the current access policy rules"
"Delete the rule named 'Temp-Allow-RDP'"
"Create a new policy layer called 'DMZ-Rules'"
```

#### Object Management
```bash
"Add 10.0.0.50 as a host object named WebServer01"
"Create a network object for 172.16.0.0/24 named Branch-Office"
"Show all host objects"
"Delete the host object named OldServer"
```

#### Threat Prevention
```bash
"Create an IPS exception for signature 12345 on host DMZ-Server"
"Show me all threat exceptions"
"Analyze threat protection effectiveness"
"Block all traffic from 203.0.113.45"
```

#### System Operations
```bash
"Publish all pending changes"
"Show me the security gateways"
"Install policy to all gateways"
"Check session status"
```

### Command Line Interface

```bash
# Interactive mode
python -m src.main --interactive

# Single command
python -m src.main --command "Show me recent blocked connections"

# Health check
python -m src.main --health

# Status check
python -m src.main --status
```

## 🤖 Agent Architecture

### Specialized Agents

1. **Quantum Agent (Orchestrator)**
   - Role: Main security manager
   - Capabilities: Command interpretation, agent coordination
   - Tools: All available tools

2. **Log Analyzer Agent**
   - Role: Firewall log analysis specialist
   - Capabilities: Log querying, threat detection, pattern analysis
   - Tools: 5 log analysis tools

3. **Policy Manager Agent**
   - Role: Firewall policy administrator
   - Capabilities: Access rule management, policy organization
   - Tools: 7 policy management tools

4. **Object Manager Agent**
   - Role: Network object administrator
   - Capabilities: Host/network/group/service management
   - Tools: 7 object management tools

5. **Threat Prevention Agent**
   - Role: Threat prevention specialist
   - Capabilities: IPS exceptions, threat profile management
   - Tools: 5 threat prevention tools

### Available Tools (25+)

#### Log Query Tools
- `query_firewall_logs` - Advanced log querying with filters
- `get_recent_blocks` - Recent blocked connections
- `analyze_threat_logs` - Threat log analysis
- `search_logs_by_ip` - IP-based log searching
- `get_log_statistics` - Statistical log analysis

#### Policy Tools
- `create_access_rule` - Create firewall rules
- `modify_access_rule` - Modify existing rules
- `delete_access_rule` - Delete rules
- `show_policy_rules` - Display rulebase
- `reorder_rules` - Change rule positions
- `create_policy_layer` - Create policy layers
- `create_policy_section` - Create policy sections

#### Object Tools
- `create_host_object` - Create host objects
- `create_network_object` - Create network objects
- `create_group_object` - Create group objects
- `create_service_object` - Create service objects
- `delete_object` - Delete any object
- `modify_object` - Modify object properties
- `show_objects` - List objects with filters

#### Threat Prevention Tools
- `create_threat_exception` - Create IPS exceptions
- `delete_threat_exception` - Delete exceptions
- `modify_threat_exception` - Modify exceptions
- `show_threat_exceptions` - List exceptions
- `analyze_threat_protections` - Analyze protection effectiveness

#### General Tools
- `publish_changes` - Publish pending changes
- `discard_changes` - Rollback changes
- `install_policy` - Install policy to gateways
- `show_gateways` - List security gateways
- `get_session_status` - Check API session
- `health_check` - System health check

#### MCP Tools
- `mcp_create_access_rule` - MCP-based rule creation
- `mcp_create_host_object` - MCP-based object creation
- `mcp_query_logs` - MCP-based log querying
- `mcp_show_objects` - MCP-based object listing
- `mcp_publish_changes` - MCP-based publishing
- `mcp_create_threat_exception` - MCP-based threat management
- `mcp_status` - MCP server status

## 🐳 Docker Deployment

### Build the Image

```bash
docker build -t checkpoint-quantum-agent:latest .
```

### Run the Container

```bash
docker run -d \
  --name quantum-agent \
  -p 8080:8080 \
  -e CHECKPOINT_MGMT_SERVER=https://your-server.checkpoint.com \
  -e CHECKPOINT_USERNAME=your_user \
  -e CHECKPOINT_PASSWORD=your_password \
  -e OPENAI_API_KEY=your_api_key \
  checkpoint-quantum-agent:latest
```

### Docker Compose

```yaml
version: '3.8'
services:
  quantum-agent:
    build: .
    ports:
      - "8080:8080"
    environment:
      - CHECKPOINT_MGMT_SERVER=https://your-server.checkpoint.com
      - CHECKPOINT_USERNAME=your_user
      - CHECKPOINT_PASSWORD=your_password
      - OPENAI_API_KEY=your_api_key
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
```

## ☸️ Kubernetes Deployment

### Prerequisites

- Kubernetes cluster
- kubectl configured
- Check Point and OpenAI credentials

### Deploy to Kubernetes

1. **Create namespace**
   ```bash
   kubectl create namespace blue-team
   ```

2. **Create secrets**
   ```bash
   # Copy and edit the secrets file
   cp k8s/secrets.yaml.example k8s/secrets.yaml
   # Edit with your actual credentials
   kubectl apply -f k8s/secrets.yaml
   ```

3. **Deploy the application**
   ```bash
   kubectl apply -f k8s/configmap.yaml
   kubectl apply -f k8s/deployment.yaml
   kubectl apply -f k8s/service.yaml
   ```

4. **Verify deployment**
   ```bash
   kubectl get pods -n blue-team
   kubectl get services -n blue-team
   ```

### Access the Agent

```bash
# Port forward for local access
kubectl port-forward -n blue-team svc/checkpoint-quantum-agent 8080:8080

# Access via NodePort (if configured)
curl http://your-cluster-ip:30080/health
```

## 📊 Monitoring and Observability

### Logging

The agent provides comprehensive structured logging:

- **JSON Format**: Machine-readable logs for analysis
- **Multiple Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Action Tracking**: All operations are logged with context
- **Performance Metrics**: Response times and success rates

### Health Checks

- **Liveness Probe**: `/health` endpoint for container health
- **Readiness Probe**: `/ready` endpoint for traffic routing
- **Agent Health**: Internal agent status monitoring

### Metrics

The agent tracks:
- Commands processed per minute
- API call latency and success rates
- Agent task completion times
- Error rates and types

## 🔧 Development

### Project Structure

```
checkpoint-quantum-agent/
├── src/
│   ├── agents/           # CrewAI agents
│   ├── api/             # Check Point API client
│   ├── crew/            # Crew orchestration
│   ├── mcp/             # MCP server integration
│   ├── tools/           # Agent tools
│   └── utils/           # Utilities and configuration
├── config/              # Configuration files
├── k8s/                 # Kubernetes manifests
├── tests/               # Test files
├── Dockerfile           # Container definition
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-mock

# Run tests
pytest tests/

# Run with coverage
pytest --cov=src tests/
```

### Code Quality

```bash
# Format code
black src/

# Lint code
flake8 src/

# Type checking
mypy src/
```

## 🔒 Security Considerations

### Credential Management

- **Environment Variables**: Never hardcode credentials
- **Kubernetes Secrets**: Use K8s secrets for production
- **API Key Rotation**: Support for credential rotation
- **TLS Verification**: All API communications use TLS

### Input Validation

- **Pydantic Models**: All inputs are validated
- **Sanitization**: Input sanitization to prevent injection
- **Error Handling**: Comprehensive error handling

### Audit Logging

- **Action Logging**: All operations are logged
- **User Commands**: Original commands are preserved
- **API Calls**: All API interactions are tracked
- **Security Events**: Security-relevant events are highlighted

## 🚨 Troubleshooting

### Common Issues

1. **Authentication Failures**
   - Verify Check Point credentials
   - Check network connectivity
   - Validate domain settings

2. **API Timeouts**
   - Increase timeout values in config
   - Check network latency
   - Verify Check Point server status

3. **MCP Server Issues**
   - Ensure MCP server is installed
   - Check MCP server path configuration
   - Verify MCP server permissions

4. **Memory Issues**
   - Increase container memory limits
   - Check for memory leaks in logs
   - Optimize query limits

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python -m src.main --interactive
```

### Log Analysis

```bash
# View structured logs
tail -f logs/quantum-agent.log | jq .

# Search for errors
grep "ERROR" logs/quantum-agent.log

# Monitor API calls
grep "API call" logs/quantum-agent.log
```

## 📈 Performance Optimization

### Configuration Tuning

- **API Timeouts**: Adjust based on network conditions
- **Retry Logic**: Configure retry attempts and delays
- **Concurrent Requests**: Limit concurrent API calls
- **Session Management**: Optimize session timeouts

### Resource Limits

- **Memory**: 2GB recommended for production
- **CPU**: 1 core recommended for production
- **Storage**: 10GB for logs and temporary files

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:

- **Issues**: Create GitHub issues for bugs and feature requests
- **Documentation**: Check this README and inline code documentation
- **Community**: Join our community discussions

## 🔮 Roadmap

### Planned Features

- **Web UI**: Browser-based interface for agent interaction
- **Slack Integration**: Direct Slack bot integration
- **Scheduled Tasks**: Automated periodic security tasks
- **Multi-Gateway Support**: Enhanced multi-gateway management
- **Backup/Restore**: Configuration backup and restore
- **Advanced Analytics**: Enhanced security analytics and reporting

### Version History

- **v1.0.0**: Initial release with core functionality
- **v1.1.0**: Enhanced MCP integration and performance improvements
- **v1.2.0**: Web UI and advanced analytics (planned)

---

**Check Point Quantum Blue Team Agent** - Defending your network with intelligent automation 🛡️

