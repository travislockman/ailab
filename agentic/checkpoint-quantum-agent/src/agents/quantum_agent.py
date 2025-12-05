"""Main Check Point Quantum Agent for orchestrating security operations."""

from typing import List, Optional
from crewai import Agent
from langchain_openai import ChatOpenAI

from ..utils.config import config
from ..utils.logger import get_logger
from ..tools.log_query_tools import (
    QueryFirewallLogsTool, GetRecentBlocksTool, AnalyzeThreatLogsTool,
    SearchLogsByIPTool, GetLogStatisticsTool
)
from ..tools.policy_tools import (
    CreateAccessRuleTool, ModifyAccessRuleTool, DeleteAccessRuleTool,
    ShowPolicyRulesTool, ReorderRulesTool, CreatePolicyLayerTool, CreatePolicySectionTool
)
from ..tools.object_tools import (
    CreateHostObjectTool, CreateNetworkObjectTool, CreateGroupObjectTool,
    CreateServiceObjectTool, DeleteObjectTool, ModifyObjectTool, ShowObjectsTool
)
from ..tools.threat_tools import (
    CreateThreatExceptionTool, DeleteThreatExceptionTool, ModifyThreatExceptionTool,
    ShowThreatExceptionsTool, AnalyzeThreatProtectionsTool
)
from ..tools.general_tools import (
    PublishChangesTool, DiscardChangesTool, InstallPolicyTool,
    ShowGatewaysTool, GetSessionStatusTool, HealthCheckTool
)
from ..tools.mcp_tools import (
    MCPCreateAccessRuleTool, MCPCreateHostObjectTool, MCPQueryLogsTool,
    MCPShowObjectsTool, MCPPublishChangesTool, MCPCreateThreatExceptionTool, MCPStatusTool
)


class QuantumAgent:
    """Main Check Point Quantum Security Manager Agent."""
    
    def __init__(self):
        self.logger = get_logger("quantum_agent")
        self.config = config.get_agent_config()
        self.openai_config = config.get_openai_config()
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=self.openai_config["model"],
            temperature=self.openai_config["temperature"],
            api_key=self.openai_config["api_key"]
        )
        
        # Initialize all tools
        self.tools = self._initialize_tools()
        
        # Create the agent
        self.agent = self._create_agent()
    
    def _initialize_tools(self) -> List:
        """Initialize all available tools."""
        tools = [
            # Log query tools
            QueryFirewallLogsTool(),
            GetRecentBlocksTool(),
            AnalyzeThreatLogsTool(),
            SearchLogsByIPTool(),
            GetLogStatisticsTool(),
            
            # Policy management tools
            CreateAccessRuleTool(),
            ModifyAccessRuleTool(),
            DeleteAccessRuleTool(),
            ShowPolicyRulesTool(),
            ReorderRulesTool(),
            CreatePolicyLayerTool(),
            CreatePolicySectionTool(),
            
            # Object management tools
            CreateHostObjectTool(),
            CreateNetworkObjectTool(),
            CreateGroupObjectTool(),
            CreateServiceObjectTool(),
            DeleteObjectTool(),
            ModifyObjectTool(),
            ShowObjectsTool(),
            
            # Threat prevention tools
            CreateThreatExceptionTool(),
            DeleteThreatExceptionTool(),
            ModifyThreatExceptionTool(),
            ShowThreatExceptionsTool(),
            AnalyzeThreatProtectionsTool(),
            
            # General tools
            PublishChangesTool(),
            DiscardChangesTool(),
            InstallPolicyTool(),
            ShowGatewaysTool(),
            GetSessionStatusTool(),
            HealthCheckTool(),
            
            # MCP tools
            MCPCreateAccessRuleTool(),
            MCPCreateHostObjectTool(),
            MCPQueryLogsTool(),
            MCPShowObjectsTool(),
            MCPPublishChangesTool(),
            MCPCreateThreatExceptionTool(),
            MCPStatusTool(),
        ]
        
        self.logger.info(f"Initialized {len(tools)} tools for Quantum Agent")
        return tools
    
    def _create_agent(self) -> Agent:
        """Create the main Quantum Agent."""
        return Agent(
            role="Check Point Quantum Security Manager",
            goal="Interpret natural language commands and orchestrate Check Point security operations to defend against threats",
            backstory="""You are an expert blue team operator with deep knowledge of Check Point Quantum Security Management.
            You understand firewall policies, threat prevention, log analysis, and network security operations.
            You can interpret natural language commands and translate them into precise Check Point API operations.
            You always prioritize security and validate actions before execution.
            
            Your capabilities include:
            - Analyzing firewall logs and identifying security threats
            - Creating and managing firewall access rules and policy layers
            - Managing network objects (hosts, networks, groups, services)
            - Configuring threat prevention policies and IPS exceptions
            - Publishing changes and installing policies to gateways
            - Monitoring system health and gateway status
            
            You can work with both direct Check Point API calls and MCP server integration.
            Always provide clear, actionable responses and confirm destructive operations.""",
            tools=self.tools,
            llm=self.llm,
            verbose=self.config["verbose"],
            memory=self.config["memory"],
            max_iterations=self.config["max_iterations"],
            allow_delegation=True
        )
    
    def process_command(self, command: str) -> str:
        """Process a natural language command."""
        try:
            self.logger.info("Processing user command", command=command)
            
            # Create a task for the agent
            task = f"""
            Process the following user command for Check Point security management:
            
            Command: {command}
            
            Instructions:
            1. Analyze the command to understand the user's intent
            2. Determine which tools and operations are needed
            3. Execute the required operations
            4. Provide a clear summary of what was accomplished
            5. If this is a destructive operation, confirm the action before proceeding
            
            Provide a comprehensive response that includes:
            - What action was taken
            - Any results or data retrieved
            - Confirmation of successful operations
            - Any warnings or recommendations
            """
            
            # Execute the task
            result = self.agent.execute_task(task)
            
            self.logger.info("Command processed successfully")
            return result
            
        except Exception as e:
            self.logger.error("Error processing command", error=str(e))
            return f"❌ Error processing command: {str(e)}"
    
    def get_agent_info(self) -> dict:
        """Get information about the agent."""
        return {
            "name": "Check Point Quantum Security Manager",
            "role": "Blue Team Security Operations",
            "tools_count": len(self.tools),
            "capabilities": [
                "Firewall log analysis and threat detection",
                "Access rule and policy management",
                "Network object administration",
                "Threat prevention configuration",
                "Policy publishing and installation",
                "System health monitoring",
                "MCP server integration"
            ],
            "llm_model": self.openai_config["model"],
            "verbose": self.config["verbose"],
            "memory_enabled": self.config["memory"]
        }

