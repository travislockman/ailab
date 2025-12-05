"""Policy Manager Agent for firewall policy and access rule management."""

from typing import List
from crewai import Agent
from langchain_openai import ChatOpenAI

from ..utils.config import config
from ..utils.logger import get_logger
from ..tools.policy_tools import (
    CreateAccessRuleTool, ModifyAccessRuleTool, DeleteAccessRuleTool,
    ShowPolicyRulesTool, ReorderRulesTool, CreatePolicyLayerTool, CreatePolicySectionTool
)


class PolicyManagerAgent:
    """Specialized agent for firewall policy and access rule management."""
    
    def __init__(self):
        self.logger = get_logger("policy_manager_agent")
        self.config = config.get_agent_config()
        self.openai_config = config.get_openai_config()
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=self.openai_config["model"],
            temperature=self.openai_config["temperature"],
            api_key=self.openai_config["api_key"]
        )
        
        # Initialize policy management tools
        self.tools = self._initialize_tools()
        
        # Create the agent
        self.agent = self._create_agent()
    
    def _initialize_tools(self) -> List:
        """Initialize policy management tools."""
        tools = [
            CreateAccessRuleTool(),
            ModifyAccessRuleTool(),
            DeleteAccessRuleTool(),
            ShowPolicyRulesTool(),
            ReorderRulesTool(),
            CreatePolicyLayerTool(),
            CreatePolicySectionTool(),
        ]
        
        self.logger.info(f"Initialized {len(tools)} policy management tools")
        return tools
    
    def _create_agent(self) -> Agent:
        """Create the Policy Manager Agent."""
        return Agent(
            role="Firewall Policy Administrator",
            goal="Create, modify, and manage firewall access rules and policy layers",
            backstory="""You are a firewall policy expert who understands network security principles.
            You can create precise access rules, organize policy layers, and ensure proper rule ordering.
            You always consider security implications and validate rule configurations.
            
            Your expertise includes:
            - Creating and modifying firewall access rules
            - Managing policy layers and sections
            - Organizing rules for optimal security and performance
            - Understanding rule precedence and ordering
            - Validating rule configurations for security best practices
            - Managing rule lifecycle (create, modify, delete)
            
            You ensure that all policy changes maintain security posture and follow best practices.""",
            tools=self.tools,
            llm=self.llm,
            verbose=self.config["verbose"],
            memory=self.config["memory"],
            max_iterations=self.config["max_iterations"],
            allow_delegation=False
        )
    
    def manage_policy(self, request: str) -> str:
        """Manage firewall policy based on a request."""
        try:
            self.logger.info("Managing policy", request=request)
            
            task = f"""
            Manage Check Point firewall policy based on the following request:
            
            Request: {request}
            
            Instructions:
            1. Analyze the policy management request
            2. Determine the appropriate policy operations needed
            3. Create, modify, or organize access rules as required
            4. Ensure proper rule ordering and security best practices
            5. Validate all policy changes for security implications
            
            Provide a comprehensive response including:
            - Summary of policy changes made
            - Rule details and configurations
            - Security considerations and validations
            - Recommendations for policy optimization
            """
            
            result = self.agent.execute_task(task)
            
            self.logger.info("Policy management completed successfully")
            return result
            
        except Exception as e:
            self.logger.error("Error in policy management", error=str(e))
            return f"❌ Error managing policy: {str(e)}"
    
    def get_agent_info(self) -> dict:
        """Get information about the agent."""
        return {
            "name": "Firewall Policy Administrator",
            "role": "Policy and Access Rule Management",
            "tools_count": len(self.tools),
            "capabilities": [
                "Access rule creation and modification",
                "Policy layer and section management",
                "Rule ordering and precedence",
                "Policy validation and optimization",
                "Security best practices enforcement",
                "Rule lifecycle management"
            ],
            "llm_model": self.openai_config["model"],
            "verbose": self.config["verbose"],
            "memory_enabled": self.config["memory"]
        }

