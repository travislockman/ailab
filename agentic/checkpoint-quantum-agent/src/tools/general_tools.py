"""General tools for policy operations, session management, and system information."""

from typing import Any, Dict, List, Optional, Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

from ..api.checkpoint_client import CheckPointClient
from ..api.models import PublishRequest, InstallPolicyRequest
from ..utils.logger import get_logger


class PublishChangesInput(BaseModel):
    """Input for publishing changes."""
    targets: Optional[List[str]] = Field(default=None, description="Target gateways (optional)")


class DiscardChangesInput(BaseModel):
    """Input for discarding changes."""
    confirm: bool = Field(default=False, description="Confirmation to discard changes")


class InstallPolicyInput(BaseModel):
    """Input for installing policy."""
    targets: List[str] = Field(..., description="Target gateways")
    policy_package: str = Field(..., description="Policy package name")
    access: bool = Field(default=True, description="Install access policy")
    threat_prevention: bool = Field(default=True, description="Install threat prevention")
    desktop_security: bool = Field(default=False, description="Install desktop security")
    qos: bool = Field(default=False, description="Install QoS policy")
    identity_awareness: bool = Field(default=False, description="Install identity awareness")


class ShowGatewaysInput(BaseModel):
    """Input for showing gateways."""
    status_filter: Optional[str] = Field(default=None, description="Filter by status (online, offline)")


class GetSessionStatusInput(BaseModel):
    """Input for getting session status."""
    detailed: bool = Field(default=False, description="Include detailed session information")


class PublishChangesTool(BaseTool):
    """Tool for publishing changes to Check Point manager."""
    
    name: str = "publish_changes"
    description: str = """
    Publish pending changes to Check Point Security Management.
    This commits all modifications to the management database.
    """
    args_schema: Type[BaseModel] = PublishChangesInput
    
    def __init__(self):
        super().__init__()
        # Store logger and client as class attributes to avoid Pydantic validation issues
        if not hasattr(self.__class__, '_logger'):
            self.__class__._logger = get_logger("publish_changes_tool")
        if not hasattr(self.__class__, '_client'):
            self.__class__._client = CheckPointClient()
    
    def _run(self, **kwargs) -> str:
        """Publish changes."""
        try:
            # Validate input
            input_data = PublishChangesInput(**kwargs)
            
            # Create publish request
            publish_request = PublishRequest(
                targets=input_data.targets,
                force=False
            )
            
            # Publish changes
            response = self._client.publish_changes(input_data.targets)
            
            if response["success"]:
                result = response["data"]
                return (
                    f"✅ Successfully published changes to Check Point manager\n"
                    f"Publish task ID: {result.get('task-id', 'N/A')}\n"
                    f"Targets: {', '.join(input_data.targets) if input_data.targets else 'All gateways'}"
                )
            else:
                return f"❌ Failed to publish changes: {response.get('message', 'Unknown error')}"
                
        except Exception as e:
            self._logger.error("Error in publish_changes", error=str(e))
            return f"❌ Error publishing changes: {str(e)}"


class DiscardChangesTool(BaseTool):
    """Tool for discarding pending changes."""
    
    name: str = "discard_changes"
    description: str = """
    Discard all pending changes in Check Point Security Management.
    This rolls back all uncommitted modifications.
    """
    args_schema: Type[BaseModel] = DiscardChangesInput
    
    def __init__(self):
        super().__init__()
        self._logger = get_logger("discard_changes_tool")
        self._client = CheckPointClient()
    
    def _run(self, **kwargs) -> str:
        """Discard changes."""
        try:
            # Validate input
            input_data = DiscardChangesInput(**kwargs)
            
            if not input_data.confirm:
                return (
                    "⚠️  Discard changes requires confirmation.\n"
                    "This will rollback all uncommitted modifications.\n"
                    "Use confirm=true to proceed."
                )
            
            # Discard changes
            response = self._client.discard_changes()
            
            if response["success"]:
                return "✅ Successfully discarded all pending changes"
            else:
                return f"❌ Failed to discard changes: {response.get('message', 'Unknown error')}"
                
        except Exception as e:
            self._logger.error("Error in discard_changes", error=str(e))
            return f"❌ Error discarding changes: {str(e)}"


class InstallPolicyTool(BaseTool):
    """Tool for installing policy to gateways."""
    
    name: str = "install_policy"
    description: str = """
    Install policy to Check Point security gateways.
    Pushes access rules, threat prevention, and other security policies to gateways.
    """
    args_schema: Type[BaseModel] = InstallPolicyInput
    
    def __init__(self):
        super().__init__()
        self._logger = get_logger("install_policy_tool")
        self._client = CheckPointClient()
    
    def _run(self, **kwargs) -> str:
        """Install policy."""
        try:
            # Validate input
            input_data = InstallPolicyInput(**kwargs)
            
            # Create install policy request
            install_request = InstallPolicyRequest(
                targets=input_data.targets,
                policy_package=input_data.policy_package,
                access=input_data.access,
                threat_prevention=input_data.threat_prevention,
                desktop_security=input_data.desktop_security,
                qos=input_data.qos,
                identity_awareness=input_data.identity_awareness
            )
            
            # Install policy
            response = self._client.install_policy(install_request)
            
            if response["success"]:
                result = response["data"]
                return (
                    f"✅ Successfully initiated policy installation\n"
                    f"Installation task ID: {result.get('task-id', 'N/A')}\n"
                    f"Targets: {', '.join(input_data.targets)}\n"
                    f"Policy package: {input_data.policy_package}\n"
                    f"Components: Access={input_data.access}, "
                    f"Threat Prevention={input_data.threat_prevention}, "
                    f"Desktop Security={input_data.desktop_security}, "
                    f"QoS={input_data.qos}, "
                    f"Identity Awareness={input_data.identity_awareness}"
                )
            else:
                return f"❌ Failed to install policy: {response.get('message', 'Unknown error')}"
                
        except Exception as e:
            self._logger.error("Error in install_policy", error=str(e))
            return f"❌ Error installing policy: {str(e)}"


class ShowGatewaysTool(BaseTool):
    """Tool for displaying security gateways."""
    
    name: str = "show_gateways"
    description: str = """
    Display Check Point security gateways and their status.
    Shows gateway information including IP addresses, versions, and operational status.
    """
    args_schema: Type[BaseModel] = ShowGatewaysInput
    
    def __init__(self):
        super().__init__()
        self._logger = get_logger("show_gateways_tool")
        self._client = CheckPointClient()
    
    def _run(self, **kwargs) -> str:
        """Show gateways."""
        try:
            # Validate input
            input_data = ShowGatewaysInput(**kwargs)
            
            # Get gateways
            response = self._client.show_gateways()
            
            if response["success"]:
                gateways = response["data"].get("objects", [])
                
                if not gateways:
                    return "No security gateways found."
                
                # Filter by status if specified
                if input_data.status_filter:
                    gateways = [gw for gw in gateways 
                              if gw.get("status", "").lower() == input_data.status_filter.lower()]
                
                if not gateways:
                    return f"No gateways found with status '{input_data.status_filter}'."
                
                # Format results
                result_lines = [f"Security Gateways ({len(gateways)} found):"]
                result_lines.append("")
                
                for i, gateway in enumerate(gateways, 1):
                    result_lines.append(
                        f"{i}. {gateway.get('name', 'Unnamed')} (UID: {gateway.get('uid', 'N/A')})"
                    )
                    result_lines.append(f"   IP Address: {gateway.get('ipv4-address', 'N/A')}")
                    result_lines.append(f"   Version: {gateway.get('version', 'N/A')}")
                    result_lines.append(f"   Status: {gateway.get('status', 'N/A')}")
                    result_lines.append(f"   Platform: {gateway.get('platform', 'N/A')}")
                    if gateway.get('comments'):
                        result_lines.append(f"   Comments: {gateway.get('comments')}")
                    result_lines.append("")
                
                # Add summary
                status_counts = {}
                for gateway in gateways:
                    status = gateway.get("status", "Unknown")
                    status_counts[status] = status_counts.get(status, 0) + 1
                
                result_lines.append("Status Summary:")
                for status, count in status_counts.items():
                    result_lines.append(f"  {status}: {count}")
                
                return "\n".join(result_lines)
            else:
                return f"❌ Failed to show gateways: {response.get('message', 'Unknown error')}"
                
        except Exception as e:
            self._logger.error("Error in show_gateways", error=str(e))
            return f"❌ Error showing gateways: {str(e)}"


class GetSessionStatusTool(BaseTool):
    """Tool for checking API session status."""
    
    name: str = "get_session_status"
    description: str = """
    Check the current API session status with Check Point management server.
    Shows authentication status, server information, and session details.
    """
    args_schema: Type[BaseModel] = GetSessionStatusInput
    
    def __init__(self):
        super().__init__()
        self._logger = get_logger("get_session_status_tool")
        self._client = CheckPointClient()
    
    def _run(self, **kwargs) -> str:
        """Get session status."""
        try:
            # Validate input
            input_data = GetSessionStatusInput(**kwargs)
            
            # Get session status
            response = self._client.get_session_status()
            
            if response["success"]:
                session_data = response["data"]
                
                result_lines = [
                    "Check Point API Session Status:",
                    f"Authenticated: {'✅ Yes' if session_data.get('authenticated') else '❌ No'}",
                    f"Server: {session_data.get('server', 'N/A')}",
                    f"Domain: {session_data.get('domain', 'N/A')}"
                ]
                
                if input_data.detailed and session_data.get('session_id'):
                    result_lines.append(f"Session ID: {session_data.get('session_id')}")
                
                # Check if session is valid
                if not session_data.get('authenticated'):
                    result_lines.append("")
                    result_lines.append("⚠️  Session is not authenticated. Some operations may fail.")
                
                return "\n".join(result_lines)
            else:
                return f"❌ Failed to get session status: {response.get('message', 'Unknown error')}"
                
        except Exception as e:
            self._logger.error("Error in get_session_status", error=str(e))
            return f"❌ Error getting session status: {str(e)}"


class HealthCheckTool(BaseTool):
    """Tool for performing system health checks."""
    
    name: str = "health_check"
    description: str = """
    Perform a comprehensive health check of the Check Point system.
    Checks API connectivity, session status, and basic system information.
    """
    args_schema: Type[BaseModel] = BaseModel  # No input parameters needed
    
    def __init__(self):
        super().__init__()
        self._logger = get_logger("health_check_tool")
        self._client = CheckPointClient()
    
    def _run(self, **kwargs) -> str:
        """Perform health check."""
        try:
            result_lines = ["Check Point System Health Check:"]
            result_lines.append("")
            
            # Check 1: API connectivity
            result_lines.append("1. API Connectivity:")
            try:
                if self._client.ensure_authenticated():
                    result_lines.append("   ✅ API connection successful")
                else:
                    result_lines.append("   ❌ API connection failed")
            except Exception as e:
                result_lines.append(f"   ❌ API connection error: {str(e)}")
            
            # Check 2: Session status
            result_lines.append("")
            result_lines.append("2. Session Status:")
            try:
                session_response = self._client.get_session_status()
                if session_response["success"]:
                    session_data = session_response["data"]
                    if session_data.get("authenticated"):
                        result_lines.append("   ✅ Session is authenticated")
                        result_lines.append(f"   Server: {session_data.get('server', 'N/A')}")
                        result_lines.append(f"   Domain: {session_data.get('domain', 'N/A')}")
                    else:
                        result_lines.append("   ❌ Session is not authenticated")
                else:
                    result_lines.append(f"   ❌ Session check failed: {session_response.get('message')}")
            except Exception as e:
                result_lines.append(f"   ❌ Session check error: {str(e)}")
            
            # Check 3: Basic API operations
            result_lines.append("")
            result_lines.append("3. Basic API Operations:")
            try:
                # Try to get gateways (basic read operation)
                gateways_response = self._client.show_gateways()
                if gateways_response["success"]:
                    gateways = gateways_response["data"].get("objects", [])
                    result_lines.append(f"   ✅ Can read gateways ({len(gateways)} found)")
                else:
                    result_lines.append(f"   ❌ Cannot read gateways: {gateways_response.get('message')}")
            except Exception as e:
                result_lines.append(f"   ❌ Gateway check error: {str(e)}")
            
            # Check 4: System summary
            result_lines.append("")
            result_lines.append("4. System Summary:")
            try:
                # Get basic system info
                gateways_response = self._client.show_gateways()
                if gateways_response["success"]:
                    gateways = gateways_response["data"].get("objects", [])
                    online_gateways = [gw for gw in gateways if gw.get("status", "").lower() == "online"]
                    result_lines.append(f"   Total gateways: {len(gateways)}")
                    result_lines.append(f"   Online gateways: {len(online_gateways)}")
                else:
                    result_lines.append("   Unable to retrieve gateway information")
            except Exception as e:
                result_lines.append(f"   Error retrieving system info: {str(e)}")
            
            return "\n".join(result_lines)
            
        except Exception as e:
            self._logger.error("Error in health_check", error=str(e))
            return f"❌ Health check failed: {str(e)}"

