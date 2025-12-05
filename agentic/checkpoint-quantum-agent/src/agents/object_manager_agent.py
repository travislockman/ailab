"""Object Manager Agent for network object management."""

from typing import List
from crewai import Agent
from langchain_openai import ChatOpenAI

from ..utils.config import config
from ..utils.logger import get_logger
from ..tools.object_tools import (
    CreateHostObjectTool, CreateNetworkObjectTool, CreateGroupObjectTool,
    CreateServiceObjectTool, DeleteObjectTool, ModifyObjectTool, ShowObjectsTool
)


class ObjectManagerAgent:
    """Specialized agent for network object management."""
    
    def __init__(self):
        self.logger = get_logger("object_manager_agent")
        self.config = config.get_agent_config()
        self.openai_config = config.get_openai_config()
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=self.openai_config["model"],
            temperature=self.openai_config["temperature"],
            api_key=self.openai_config["api_key"]
        )
        
        # Initialize object management tools
        self.tools = self._initialize_tools()
        
        # Create the agent
        self.agent = self._create_agent()
    
    def _initialize_tools(self) -> List:
        """Initialize object management tools."""
        tools = [
            CreateHostObjectTool(),
            CreateNetworkObjectTool(),
            CreateGroupObjectTool(),
            CreateServiceObjectTool(),
            DeleteObjectTool(),
            ModifyObjectTool(),
            ShowObjectsTool(),
        ]
        
        self.logger.info(f"Initialized {len(tools)} object management tools")
        return tools
    
    def _create_agent(self) -> Agent:
        """Create the Object Manager Agent."""
        return Agent(
            role="Network Object Administrator",
            goal="Manage network objects including hosts, networks, groups, and services",
            backstory="""You are a network administrator with expertise in Check Point object management.
            You can create, modify, and organize network objects efficiently.
            You understand IP addressing, service definitions, and object hierarchies.
            
            Your expertise includes:
            - Creating and managing host objects with IP addresses
            - Defining network objects with subnets and CIDR notation
            - Organizing objects into logical groups
            - Creating service objects for TCP/UDP ports
            - Modifying object properties and relationships
            - Maintaining object naming conventions and documentation
            
            You ensure that all network objects are properly configured and organized for efficient policy management.""",
            tools=self.tools,
            llm=self.llm,
            verbose=self.config["verbose"],
            memory=self.config["memory"],
            max_iterations=self.config["max_iterations"],
            allow_delegation=False
        )
    
    def manage_objects(self, request: str) -> str:
        """Manage network objects based on a request."""
        try:
            self.logger.info("Managing objects", request=request)
            
            task = f"""
            Manage Check Point network objects based on the following request:
            
            Request: {request}
            
            Instructions:
            1. Analyze the object management request
            2. Determine the appropriate object operations needed
            3. Create, modify, or organize network objects as required
            4. Ensure proper object naming and organization
            5. Validate all object configurations
            
            Provide a comprehensive response including:
            - Summary of object operations performed
            - Object details and configurations
            - Organization and naming conventions used
            - Recommendations for object management
            """
            
            result = self.agent.execute_task(task)
            
            self.logger.info("Object management completed successfully")
            return result
            
        except Exception as e:
            self.logger.error("Error in object management", error=str(e))
            return f"❌ Error managing objects: {str(e)}"
    
    def get_agent_info(self) -> dict:
        """Get information about the agent."""
        return {
            "name": "Network Object Administrator",
            "role": "Network Object Management",
            "tools_count": len(self.tools),
            "capabilities": [
                "Host object creation and management",
                "Network object definition",
                "Group object organization",
                "Service object configuration",
                "Object property modification",
                "Object hierarchy management"
            ],
            "llm_model": self.openai_config["model"],
            "verbose": self.config["verbose"],
            "memory_enabled": self.config["memory"]
        }

