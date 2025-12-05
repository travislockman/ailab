"""CrewAI crew orchestration for Check Point Quantum Blue Team operations."""

from typing import List, Optional
from crewai import Crew, Process, Task
from langchain_openai import ChatOpenAI

from ..agents.quantum_agent import QuantumAgent
from ..agents.log_analyzer_agent import LogAnalyzerAgent
from ..agents.policy_manager_agent import PolicyManagerAgent
from ..agents.object_manager_agent import ObjectManagerAgent
from ..agents.threat_prevention_agent import ThreatPreventionAgent
from ..utils.config import config
from ..utils.logger import get_logger, ActionLogger


class QuantumCrew:
    """CrewAI crew for orchestrating Check Point Quantum Blue Team operations."""
    
    def __init__(self):
        self.logger = get_logger("quantum_crew")
        self.action_logger = ActionLogger("quantum_crew")
        self.config = config.get_agent_config()
        self.crew_config = config.get("crew", {})
        
        # Initialize agents
        self.quantum_agent = QuantumAgent()
        self.log_analyzer = LogAnalyzerAgent()
        self.policy_manager = PolicyManagerAgent()
        self.object_manager = ObjectManagerAgent()
        self.threat_prevention = ThreatPreventionAgent()
        
        # Create the crew
        self.crew = self._create_crew()
        
        self.logger.info("Quantum Crew initialized with 5 specialized agents")
    
    def _create_crew(self, tasks: Optional[List[Task]] = None) -> Crew:
        """Create the CrewAI crew with all agents."""
        agents = [
            self.quantum_agent.agent,
            self.log_analyzer.agent,
            self.policy_manager.agent,
            self.object_manager.agent,
            self.threat_prevention.agent
        ]
        
        return Crew(
            agents=agents,
            tasks=tasks or [],
            process=Process.sequential,
            memory=self.crew_config.get("memory", True),
            verbose=self.crew_config.get("verbose", True)
        )
    
    def process_command(self, command: str, context: Optional[str] = None) -> str:
        """Process a natural language command using the crew."""
        try:
            self.action_logger.log_user_command(command, {"context": context})
            
            # Create main task for the quantum agent
            main_task = Task(
                description="""
                Process the following user command for Check Point security management:
                
                Command: {command}
                Context: {context}
                
                Instructions:
                1. Analyze the command to understand the user's intent
                2. Determine which specialized agents and operations are needed
                3. Coordinate with appropriate agents to execute the required operations
                4. Provide a comprehensive summary of all actions taken
                5. Include any security recommendations or warnings
                
                If this involves log analysis, coordinate with the Log Analyzer Agent.
                If this involves policy management, coordinate with the Policy Manager Agent.
                If this involves object management, coordinate with the Object Manager Agent.
                If this involves threat prevention, coordinate with the Threat Prevention Agent.
                
                Provide a clear, actionable response that includes:
                - Summary of the command and intent
                - Actions taken by each involved agent
                - Results and data retrieved
                - Security implications and recommendations
                - Next steps or follow-up actions if needed
                """,
                agent=self.quantum_agent.agent,
                expected_output="A comprehensive response detailing all actions taken, results obtained, and recommendations provided."
            )
            
            # Create a crew with this specific task
            crew = self._create_crew(tasks=[main_task])
            
            # Execute the crew
            result = crew.kickoff(inputs={"command": command, "context": context or ""})
            
            self.action_logger.log_action_success("process_command", result=str(result)[:200] + "...")
            return str(result)
            
        except Exception as e:
            self.action_logger.log_action_error("process_command", str(e))
            self.logger.error("Error processing command", error=str(e))
            return f"❌ Error processing command: {str(e)}"
    
    def analyze_logs(self, query: str) -> str:
        """Analyze firewall logs using the Log Analyzer Agent."""
        try:
            self.action_logger.log_action_start("analyze_logs", query=query)
            
            task = Task(
                description=f"""
                Analyze Check Point firewall logs based on the following request:
                
                Query: {query}
                
                Instructions:
                1. Use appropriate log analysis tools to gather data
                2. Analyze the results for security insights and patterns
                3. Identify any threats, anomalies, or security events
                4. Provide actionable recommendations
                5. Generate a comprehensive security report
                """,
                agent=self.log_analyzer.agent,
                expected_output="A detailed log analysis report with security insights and recommendations."
            )
            
            result = self.crew.kickoff([task])
            
            self.action_logger.log_action_success("analyze_logs", result=str(result)[:200] + "...")
            return str(result)
            
        except Exception as e:
            self.action_logger.log_action_error("analyze_logs", str(e))
            self.logger.error("Error analyzing logs", error=str(e))
            return f"❌ Error analyzing logs: {str(e)}"
    
    def manage_policy(self, request: str) -> str:
        """Manage firewall policy using the Policy Manager Agent."""
        try:
            self.action_logger.log_action_start("manage_policy", request=request)
            
            task = Task(
                description=f"""
                Manage Check Point firewall policy based on the following request:
                
                Request: {request}
                
                Instructions:
                1. Analyze the policy management requirements
                2. Create, modify, or organize access rules as needed
                3. Ensure proper rule ordering and security best practices
                4. Validate all policy changes for security implications
                5. Provide recommendations for policy optimization
                """,
                agent=self.policy_manager.agent,
                expected_output="A comprehensive policy management report with all changes made and recommendations."
            )
            
            result = self.crew.kickoff([task])
            
            self.action_logger.log_action_success("manage_policy", result=str(result)[:200] + "...")
            return str(result)
            
        except Exception as e:
            self.action_logger.log_action_error("manage_policy", str(e))
            self.logger.error("Error managing policy", error=str(e))
            return f"❌ Error managing policy: {str(e)}"
    
    def manage_objects(self, request: str) -> str:
        """Manage network objects using the Object Manager Agent."""
        try:
            self.action_logger.log_action_start("manage_objects", request=request)
            
            task = Task(
                description=f"""
                Manage Check Point network objects based on the following request:
                
                Request: {request}
                
                Instructions:
                1. Analyze the object management requirements
                2. Create, modify, or organize network objects as needed
                3. Ensure proper object naming and organization
                4. Validate all object configurations
                5. Provide recommendations for object management
                """,
                agent=self.object_manager.agent,
                expected_output="A comprehensive object management report with all changes made and recommendations."
            )
            
            result = self.crew.kickoff([task])
            
            self.action_logger.log_action_success("manage_objects", result=str(result)[:200] + "...")
            return str(result)
            
        except Exception as e:
            self.action_logger.log_action_error("manage_objects", str(e))
            self.logger.error("Error managing objects", error=str(e))
            return f"❌ Error managing objects: {str(e)}"
    
    def manage_threat_prevention(self, request: str) -> str:
        """Manage threat prevention using the Threat Prevention Agent."""
        try:
            self.action_logger.log_action_start("manage_threat_prevention", request=request)
            
            task = Task(
                description=f"""
                Manage Check Point threat prevention based on the following request:
                
                Request: {request}
                
                Instructions:
                1. Analyze the threat prevention requirements
                2. Create, modify, or analyze threat exceptions and policies as needed
                3. Ensure optimal security posture and performance
                4. Validate all threat prevention configurations
                5. Provide recommendations for threat prevention optimization
                """,
                agent=self.threat_prevention.agent,
                expected_output="A comprehensive threat prevention report with all changes made and recommendations."
            )
            
            result = self.crew.kickoff([task])
            
            self.action_logger.log_action_success("manage_threat_prevention", result=str(result)[:200] + "...")
            return str(result)
            
        except Exception as e:
            self.action_logger.log_action_error("manage_threat_prevention", str(e))
            self.logger.error("Error managing threat prevention", error=str(e))
            return f"❌ Error managing threat prevention: {str(e)}"
    
    def get_crew_info(self) -> dict:
        """Get information about the crew and its agents."""
        return {
            "crew_name": "Check Point Quantum Blue Team Crew",
            "process": "Sequential",
            "agents": [
                self.quantum_agent.get_agent_info(),
                self.log_analyzer.get_agent_info(),
                self.policy_manager.get_agent_info(),
                self.object_manager.get_agent_info(),
                self.threat_prevention.get_agent_info()
            ],
            "total_agents": 5,
            "total_tools": sum([
                len(self.quantum_agent.tools),
                len(self.log_analyzer.tools),
                len(self.policy_manager.tools),
                len(self.object_manager.tools),
                len(self.threat_prevention.tools)
            ]),
            "capabilities": [
                "Natural language command processing",
                "Firewall log analysis and threat detection",
                "Access rule and policy management",
                "Network object administration",
                "Threat prevention configuration",
                "Multi-agent coordination and orchestration"
            ]
        }
    
    def health_check(self) -> str:
        """Perform a health check of the crew and all agents."""
        try:
            self.logger.info("Performing crew health check")
            
            health_info = {
                "crew_status": "✅ Operational",
                "agents": [],
                "total_agents": 5,
                "operational_agents": 0
            }
            
            # Check each agent
            agents = [
                ("Quantum Agent", self.quantum_agent),
                ("Log Analyzer", self.log_analyzer),
                ("Policy Manager", self.policy_manager),
                ("Object Manager", self.object_manager),
                ("Threat Prevention", self.threat_prevention)
            ]
            
            for agent_name, agent in agents:
                try:
                    agent_info = agent.get_agent_info()
                    health_info["agents"].append({
                        "name": agent_name,
                        "status": "✅ Operational",
                        "tools": agent_info["tools_count"],
                        "capabilities": len(agent_info["capabilities"])
                    })
                    health_info["operational_agents"] += 1
                except Exception as e:
                    health_info["agents"].append({
                        "name": agent_name,
                        "status": f"❌ Error: {str(e)}",
                        "tools": 0,
                        "capabilities": 0
                    })
            
            # Format health check results
            result_lines = [
                "Check Point Quantum Crew Health Check:",
                f"Crew Status: {health_info['crew_status']}",
                f"Operational Agents: {health_info['operational_agents']}/{health_info['total_agents']}",
                "",
                "Agent Status:"
            ]
            
            for agent in health_info["agents"]:
                result_lines.append(f"  {agent['name']}: {agent['status']}")
                if agent['status'].startswith("✅"):
                    result_lines.append(f"    Tools: {agent['tools']}, Capabilities: {agent['capabilities']}")
            
            return "\n".join(result_lines)
            
        except Exception as e:
            self.logger.error("Error in crew health check", error=str(e))
            return f"❌ Crew health check failed: {str(e)}"

