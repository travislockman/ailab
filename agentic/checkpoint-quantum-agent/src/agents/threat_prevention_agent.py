"""Threat Prevention Agent for managing IPS exceptions and threat protection."""

from typing import List
from crewai import Agent
from langchain_openai import ChatOpenAI

from ..utils.config import config
from ..utils.logger import get_logger
from ..tools.threat_tools import (
    CreateThreatExceptionTool, DeleteThreatExceptionTool, ModifyThreatExceptionTool,
    ShowThreatExceptionsTool, AnalyzeThreatProtectionsTool
)


class ThreatPreventionAgent:
    """Specialized agent for threat prevention and IPS exception management."""
    
    def __init__(self):
        self.logger = get_logger("threat_prevention_agent")
        self.config = config.get_agent_config()
        self.openai_config = config.get_openai_config()
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=self.openai_config["model"],
            temperature=self.openai_config["temperature"],
            api_key=self.openai_config["api_key"]
        )
        
        # Initialize threat prevention tools
        self.tools = self._initialize_tools()
        
        # Create the agent
        self.agent = self._create_agent()
    
    def _initialize_tools(self) -> List:
        """Initialize threat prevention tools."""
        tools = [
            CreateThreatExceptionTool(),
            DeleteThreatExceptionTool(),
            ModifyThreatExceptionTool(),
            ShowThreatExceptionsTool(),
            AnalyzeThreatProtectionsTool(),
        ]
        
        self.logger.info(f"Initialized {len(tools)} threat prevention tools")
        return tools
    
    def _create_agent(self) -> Agent:
        """Create the Threat Prevention Agent."""
        return Agent(
            role="Threat Prevention Specialist",
            goal="Configure threat prevention policies, manage IPS exceptions, and tune security profiles",
            backstory="""You are a threat prevention expert with deep knowledge of Check Point IPS and threat protection.
            You can create exceptions, tune threat profiles, and optimize security policies.
            You understand attack vectors and can balance security with operational requirements.
            
            Your expertise includes:
            - Creating and managing IPS threat exceptions
            - Configuring threat prevention profiles and policies
            - Analyzing threat protection effectiveness
            - Tuning security policies for optimal performance
            - Understanding attack signatures and threat patterns
            - Balancing security requirements with operational needs
            
            You ensure that threat prevention policies provide maximum security while maintaining system performance.""",
            tools=self.tools,
            llm=self.llm,
            verbose=self.config["verbose"],
            memory=self.config["memory"],
            max_iterations=self.config["max_iterations"],
            allow_delegation=False
        )
    
    def manage_threat_prevention(self, request: str) -> str:
        """Manage threat prevention based on a request."""
        try:
            self.logger.info("Managing threat prevention", request=request)
            
            task = f"""
            Manage Check Point threat prevention based on the following request:
            
            Request: {request}
            
            Instructions:
            1. Analyze the threat prevention request
            2. Determine the appropriate threat management operations needed
            3. Create, modify, or analyze threat exceptions and policies as required
            4. Ensure optimal security posture and performance
            5. Validate all threat prevention configurations
            
            Provide a comprehensive response including:
            - Summary of threat prevention actions taken
            - Exception and policy details
            - Security analysis and recommendations
            - Performance considerations and optimizations
            """
            
            result = self.agent.execute_task(task)
            
            self.logger.info("Threat prevention management completed successfully")
            return result
            
        except Exception as e:
            self.logger.error("Error in threat prevention management", error=str(e))
            return f"❌ Error managing threat prevention: {str(e)}"
    
    def get_agent_info(self) -> dict:
        """Get information about the agent."""
        return {
            "name": "Threat Prevention Specialist",
            "role": "Threat Prevention and IPS Management",
            "tools_count": len(self.tools),
            "capabilities": [
                "IPS exception creation and management",
                "Threat prevention policy configuration",
                "Threat protection analysis",
                "Security policy tuning",
                "Attack signature management",
                "Security-performance optimization"
            ],
            "llm_model": self.openai_config["model"],
            "verbose": self.config["verbose"],
            "memory_enabled": self.config["memory"]
        }

