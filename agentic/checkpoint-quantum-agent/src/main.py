"""Main entry point for the Check Point Quantum Blue Team Agent."""

import sys
import asyncio
from typing import Optional
import argparse

from .crew.quantum_crew import QuantumCrew
from .utils.config import config
from .utils.logger import get_logger, ActionLogger
from .api.checkpoint_client import CheckPointClient


class QuantumAgentApp:
    """Main application class for the Check Point Quantum Agent."""
    
    def __init__(self):
        self.logger = get_logger("quantum_agent_app")
        self.action_logger = ActionLogger("quantum_agent_app")
        self.crew = QuantumCrew()
        self.client = CheckPointClient()
        
        self.logger.info("Check Point Quantum Agent initialized")
    
    def initialize(self) -> bool:
        """Initialize the agent and verify connectivity."""
        try:
            self.logger.info("Initializing Check Point Quantum Agent")
            
            # Test Check Point API connectivity
            if not self.client.ensure_authenticated():
                self.logger.error("Failed to authenticate with Check Point management server")
                return False
            
            self.logger.info("Successfully authenticated with Check Point management server")
            
            # Perform health check
            health_result = self.crew.health_check()
            self.logger.info("Crew health check completed", result=health_result)
            
            return True
            
        except Exception as e:
            self.logger.error("Initialization failed", error=str(e))
            return False
    
    def process_command(self, command: str, context: Optional[str] = None) -> str:
        """Process a natural language command."""
        try:
            self.action_logger.log_user_command(command, {"context": context})
            
            # Process command through the crew
            result = self.crew.process_command(command, context)
            
            self.action_logger.log_action_success("process_command", result=result[:200] + "..." if len(result) > 200 else result)
            return result
            
        except Exception as e:
            self.action_logger.log_action_error("process_command", str(e))
            self.logger.error("Error processing command", error=str(e))
            return f"❌ Error processing command: {str(e)}"
    
    def interactive_mode(self):
        """Run the agent in interactive mode."""
        print("🛡️  Check Point Quantum Blue Team Agent")
        print("=" * 50)
        print("Type 'help' for available commands, 'quit' to exit")
        print("=" * 50)
        
        while True:
            try:
                command = input("\n🔵 Quantum Agent> ").strip()
                
                if not command:
                    continue
                
                if command.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if command.lower() == 'help':
                    self._show_help()
                    continue
                
                if command.lower() == 'status':
                    self._show_status()
                    continue
                
                if command.lower() == 'health':
                    self._show_health()
                    continue
                
                # Process the command
                print("\n🔄 Processing command...")
                result = self.process_command(command)
                print(f"\n📋 Result:\n{result}")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")
    
    def _show_help(self):
        """Show help information."""
        help_text = """
🛡️  Check Point Quantum Blue Team Agent - Help

Available Commands:
  help                    - Show this help message
  status                  - Show agent status and capabilities
  health                  - Perform system health check
  quit/exit/q             - Exit the application

Natural Language Commands:
  Log Analysis:
    - "Show me all blocked connections from 192.168.1.100 in the last hour"
    - "Analyze threat logs for the last 24 hours"
    - "What are the top sources of blocked traffic today?"
    - "Search logs for IP address 10.0.0.50"

  Policy Management:
    - "Create a rule to allow HTTPS from internal network to any"
    - "Show me the current access policy rules"
    - "Delete the rule named 'Temp-Allow-RDP'"
    - "Create a new policy layer called 'DMZ-Rules'"

  Object Management:
    - "Add 10.0.0.50 as a host object named WebServer01"
    - "Create a network object for 172.16.0.0/24 named Branch-Office"
    - "Show all host objects"
    - "Delete the host object named OldServer"

  Threat Prevention:
    - "Create an IPS exception for signature 12345 on host DMZ-Server"
    - "Show me all threat exceptions"
    - "Analyze threat protection effectiveness"
    - "Block all traffic from 203.0.113.45"

  System Operations:
    - "Publish all pending changes"
    - "Show me the security gateways"
    - "Install policy to all gateways"
    - "Check session status"

Examples:
  "Block all traffic from 192.168.100.50 and log it"
  "Show me recent blocked connections"
  "Create a rule to allow SSH from management network to servers"
  "What threats were detected today?"
        """
        print(help_text)
    
    def _show_status(self):
        """Show agent status."""
        try:
            crew_info = self.crew.get_crew_info()
            session_status = self.client.get_session_status()
            
            print("\n🛡️  Check Point Quantum Agent Status")
            print("=" * 40)
            print(f"Crew: {crew_info['crew_name']}")
            print(f"Agents: {crew_info['total_agents']}")
            print(f"Tools: {crew_info['total_tools']}")
            print(f"Process: {crew_info['process']}")
            
            if session_status["success"]:
                session_data = session_status["data"]
                print(f"\nCheck Point Connection:")
                print(f"  Server: {session_data.get('server', 'N/A')}")
                print(f"  Domain: {session_data.get('domain', 'N/A')}")
                print(f"  Authenticated: {'✅ Yes' if session_data.get('authenticated') else '❌ No'}")
            
            print(f"\nCapabilities:")
            for capability in crew_info["capabilities"]:
                print(f"  • {capability}")
                
        except Exception as e:
            print(f"❌ Error getting status: {str(e)}")
    
    def _show_health(self):
        """Show system health."""
        try:
            health_result = self.crew.health_check()
            print(f"\n🏥 System Health Check:\n{health_result}")
        except Exception as e:
            print(f"❌ Error performing health check: {str(e)}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Check Point Quantum Blue Team Agent")
    parser.add_argument("--command", "-c", help="Execute a single command and exit")
    parser.add_argument("--interactive", "-i", action="store_true", help="Run in interactive mode")
    parser.add_argument("--health", action="store_true", help="Perform health check and exit")
    parser.add_argument("--status", action="store_true", help="Show status and exit")
    
    args = parser.parse_args()
    
    # Initialize the application
    app = QuantumAgentApp()
    
    if not app.initialize():
        print("❌ Failed to initialize Check Point Quantum Agent")
        sys.exit(1)
    
    try:
        if args.health:
            app._show_health()
        elif args.status:
            app._show_status()
        elif args.command:
            result = app.process_command(args.command)
            print(result)
        elif args.interactive:
            app.interactive_mode()
        else:
            # Default to interactive mode
            app.interactive_mode()
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Application error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()

