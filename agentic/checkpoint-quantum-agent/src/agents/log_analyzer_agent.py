"""Log Analyzer Agent for firewall log analysis and threat detection."""

from typing import List
from crewai import Agent
from langchain_openai import ChatOpenAI

from ..utils.config import config
from ..utils.logger import get_logger
from ..tools.log_query_tools import (
    QueryFirewallLogsTool, GetRecentBlocksTool, AnalyzeThreatLogsTool,
    SearchLogsByIPTool, GetLogStatisticsTool
)


class LogAnalyzerAgent:
    """Specialized agent for firewall log analysis and threat detection."""
    
    def __init__(self):
        self.logger = get_logger("log_analyzer_agent")
        self.config = config.get_agent_config()
        self.openai_config = config.get_openai_config()
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=self.openai_config["model"],
            temperature=self.openai_config["temperature"],
            api_key=self.openai_config["api_key"]
        )
        
        # Initialize log analysis tools
        self.tools = self._initialize_tools()
        
        # Create the agent
        self.agent = self._create_agent()
    
    def _initialize_tools(self) -> List:
        """Initialize log analysis tools."""
        tools = [
            QueryFirewallLogsTool(),
            GetRecentBlocksTool(),
            AnalyzeThreatLogsTool(),
            SearchLogsByIPTool(),
            GetLogStatisticsTool(),
        ]
        
        self.logger.info(f"Initialized {len(tools)} log analysis tools")
        return tools
    
    def _create_agent(self) -> Agent:
        """Create the Log Analyzer Agent."""
        return Agent(
            role="Firewall Log Analysis Specialist",
            goal="Analyze firewall logs, identify threats, and generate security reports",
            backstory="""You are a specialized log analyst with expertise in Check Point firewall logs.
            You can query logs with complex filters, identify attack patterns, and provide actionable insights.
            You understand log formats, threat signatures, and security event correlation.
            
            Your expertise includes:
            - Querying firewall logs with advanced filtering
            - Identifying blocked connections and security events
            - Analyzing threat prevention logs and attack patterns
            - Searching logs by IP addresses and time ranges
            - Generating statistical analysis and security reports
            - Correlating events to identify security incidents
            
            You provide detailed analysis and actionable recommendations for security operations.""",
            tools=self.tools,
            llm=self.llm,
            verbose=self.config["verbose"],
            memory=self.config["memory"],
            max_iterations=self.config["max_iterations"],
            allow_delegation=False
        )
    
    def analyze_logs(self, query: str) -> str:
        """Analyze firewall logs based on a query."""
        try:
            self.logger.info("Analyzing logs", query=query)
            
            task = f"""
            Analyze Check Point firewall logs based on the following request:
            
            Request: {query}
            
            Instructions:
            1. Determine the appropriate log analysis approach
            2. Use the most suitable tools to gather log data
            3. Analyze the results for security insights
            4. Identify any threats, anomalies, or patterns
            5. Provide actionable recommendations
            
            Provide a comprehensive analysis including:
            - Summary of findings
            - Security insights and patterns
            - Identified threats or anomalies
            - Recommendations for security actions
            """
            
            result = self.agent.execute_task(task)
            
            self.logger.info("Log analysis completed successfully")
            return result
            
        except Exception as e:
            self.logger.error("Error in log analysis", error=str(e))
            return f"❌ Error analyzing logs: {str(e)}"
    
    def get_agent_info(self) -> dict:
        """Get information about the agent."""
        return {
            "name": "Firewall Log Analysis Specialist",
            "role": "Log Analysis and Threat Detection",
            "tools_count": len(self.tools),
            "capabilities": [
                "Advanced log querying and filtering",
                "Threat pattern identification",
                "Security event correlation",
                "Statistical log analysis",
                "IP-based log searching",
                "Blocked connection analysis"
            ],
            "llm_model": self.openai_config["model"],
            "verbose": self.config["verbose"],
            "memory_enabled": self.config["memory"]
        }

