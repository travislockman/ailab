"""MCP server integration tools for Check Point operations."""

import asyncio
from typing import Any, Dict, List, Optional, Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

from ..mcp.mcp_integration import mcp_integration
from ..utils.logger import get_logger


class MCPCreateAccessRuleInput(BaseModel):
    """Input for MCP create access rule."""
    name: str = Field(..., description="Rule name")
    source: str = Field(..., description="Source object/network")
    destination: str = Field(..., description="Destination object/network")
    service: str = Field(..., description="Service object")
    action: str = Field(..., description="Rule action")
    track: str = Field(default="log", description="Track action")
    layer: str = Field(..., description="Policy layer name")


class MCPCreateHostObjectInput(BaseModel):
    """Input for MCP create host object."""
    name: str = Field(..., description="Host object name")
    ip_address: str = Field(..., description="IPv4 address")
    comments: Optional[str] = Field(default=None, description="Comments")


class MCPQueryLogsInput(BaseModel):
    """Input for MCP query logs."""
    query: str = Field(..., description="Log query string")
    limit: int = Field(default=100, description="Maximum number of results")
    time_range: Optional[str] = Field(default=None, description="Time range filter")


class MCPShowObjectsInput(BaseModel):
    """Input for MCP show objects."""
    object_type: Optional[str] = Field(default=None, description="Object type filter")


class MCPPublishChangesInput(BaseModel):
    """Input for MCP publish changes."""
    targets: Optional[List[str]] = Field(default=None, description="Target gateways")


class MCPCreateThreatExceptionInput(BaseModel):
    """Input for MCP create threat exception."""
    name: str = Field(..., description="Exception name")
    layer: str = Field(..., description="Threat layer name")
    rule: str = Field(..., description="Threat rule name")
    exception_type: str = Field(..., description="Exception type")
    target: str = Field(..., description="Target object name")


class MCPCreateAccessRuleTool(BaseTool):
    """MCP tool for creating access rules."""
    
    name: str = "mcp_create_access_rule"
    description: str = """
    Create a new access rule using Check Point MCP server.
    This is an alternative to direct API calls, using the MCP server for rule creation.
    """
    args_schema: Type[BaseModel] = MCPCreateAccessRuleInput
    
    def __init__(self):
        super().__init__()
        self._logger = get_logger("mcp_create_access_rule_tool")
    
    def _run(self, **kwargs) -> str:
        """Create access rule via MCP."""
        try:
            # Validate input
            input_data = MCPCreateAccessRuleInput(**kwargs)
            
            # Check if MCP is available
            if not mcp_integration.is_available():
                return "❌ MCP server is not available. Falling back to direct API calls."
            
            # Prepare rule data
            rule_data = {
                "name": input_data.name,
                "source": input_data.source,
                "destination": input_data.destination,
                "service": input_data.service,
                "action": input_data.action,
                "track": input_data.track,
                "layer": input_data.layer
            }
            
            # Run async MCP call
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                response = loop.run_until_complete(
                    mcp_integration.mcp_create_access_rule(rule_data)
                )
            finally:
                loop.close()
            
            if response["success"]:
                return (
                    f"✅ Successfully created access rule via MCP\n"
                    f"Rule: {input_data.name}\n"
                    f"Layer: {input_data.layer}\n"
                    f"Source: {input_data.source}\n"
                    f"Destination: {input_data.destination}\n"
                    f"Service: {input_data.service}\n"
                    f"Action: {input_data.action}"
                )
            else:
                return f"❌ Failed to create access rule via MCP: {response.get('message', 'Unknown error')}"
                
        except Exception as e:
            self._logger.error("Error in mcp_create_access_rule", error=str(e))
            return f"❌ Error creating access rule via MCP: {str(e)}"


class MCPCreateHostObjectTool(BaseTool):
    """MCP tool for creating host objects."""
    
    name: str = "mcp_create_host_object"
    description: str = """
    Create a new host object using Check Point MCP server.
    This is an alternative to direct API calls, using the MCP server for object creation.
    """
    args_schema: Type[BaseModel] = MCPCreateHostObjectInput
    
    def __init__(self):
        super().__init__()
        self._logger = get_logger("mcp_create_host_object_tool")
    
    def _run(self, **kwargs) -> str:
        """Create host object via MCP."""
        try:
            # Validate input
            input_data = MCPCreateHostObjectInput(**kwargs)
            
            # Check if MCP is available
            if not mcp_integration.is_available():
                return "❌ MCP server is not available. Falling back to direct API calls."
            
            # Prepare host data
            host_data = {
                "name": input_data.name,
                "ipv4-address": input_data.ip_address
            }
            
            if input_data.comments:
                host_data["comments"] = input_data.comments
            
            # Run async MCP call
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                response = loop.run_until_complete(
                    mcp_integration.mcp_create_host_object(host_data)
                )
            finally:
                loop.close()
            
            if response["success"]:
                return (
                    f"✅ Successfully created host object via MCP\n"
                    f"Host: {input_data.name}\n"
                    f"IP Address: {input_data.ip_address}\n"
                    f"Comments: {input_data.comments or 'None'}"
                )
            else:
                return f"❌ Failed to create host object via MCP: {response.get('message', 'Unknown error')}"
                
        except Exception as e:
            self._logger.error("Error in mcp_create_host_object", error=str(e))
            return f"❌ Error creating host object via MCP: {str(e)}"


class MCPQueryLogsTool(BaseTool):
    """MCP tool for querying logs."""
    
    name: str = "mcp_query_logs"
    description: str = """
    Query firewall logs using Check Point MCP server.
    This is an alternative to direct API calls, using the MCP server for log queries.
    """
    args_schema: Type[BaseModel] = MCPQueryLogsInput
    
    def __init__(self):
        super().__init__()
        self._logger = get_logger("mcp_query_logs_tool")
    
    def _run(self, **kwargs) -> str:
        """Query logs via MCP."""
        try:
            # Validate input
            input_data = MCPQueryLogsInput(**kwargs)
            
            # Check if MCP is available
            if not mcp_integration.is_available():
                return "❌ MCP server is not available. Falling back to direct API calls."
            
            # Prepare query data
            query_data = {
                "query": input_data.query,
                "limit": input_data.limit
            }
            
            if input_data.time_range:
                query_data["time-range"] = input_data.time_range
            
            # Run async MCP call
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                response = loop.run_until_complete(
                    mcp_integration.mcp_query_logs(query_data)
                )
            finally:
                loop.close()
            
            if response["success"]:
                logs = response["data"].get("result", {}).get("objects", [])
                
                if not logs:
                    return "No logs found matching the query criteria via MCP."
                
                # Format results
                result_lines = [f"Found {len(logs)} log entries via MCP:"]
                for i, log in enumerate(logs[:10], 1):  # Show first 10
                    result_lines.append(
                        f"{i}. {log.get('time', 'N/A')} | "
                        f"{log.get('src', 'N/A')} -> {log.get('dst', 'N/A')} | "
                        f"Service: {log.get('service', 'N/A')} | "
                        f"Action: {log.get('action', 'N/A')}"
                    )
                
                if len(logs) > 10:
                    result_lines.append(f"... and {len(logs) - 10} more entries")
                
                return "\n".join(result_lines)
            else:
                return f"❌ Failed to query logs via MCP: {response.get('message', 'Unknown error')}"
                
        except Exception as e:
            self._logger.error("Error in mcp_query_logs", error=str(e))
            return f"❌ Error querying logs via MCP: {str(e)}"


class MCPShowObjectsTool(BaseTool):
    """MCP tool for showing objects."""
    
    name: str = "mcp_show_objects"
    description: str = """
    Show objects using Check Point MCP server.
    This is an alternative to direct API calls, using the MCP server for object queries.
    """
    args_schema: Type[BaseModel] = MCPShowObjectsInput
    
    def __init__(self):
        super().__init__()
        self._logger = get_logger("mcp_show_objects_tool")
    
    def _run(self, **kwargs) -> str:
        """Show objects via MCP."""
        try:
            # Validate input
            input_data = MCPShowObjectsInput(**kwargs)
            
            # Check if MCP is available
            if not mcp_integration.is_available():
                return "❌ MCP server is not available. Falling back to direct API calls."
            
            # Run async MCP call
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                response = loop.run_until_complete(
                    mcp_integration.mcp_show_objects(input_data.object_type)
                )
            finally:
                loop.close()
            
            if response["success"]:
                objects = response["data"].get("result", {}).get("objects", [])
                
                if not objects:
                    filter_text = f" of type '{input_data.object_type}'" if input_data.object_type else ""
                    return f"No objects found{filter_text} via MCP."
                
                # Format results
                result_lines = [f"Check Point Objects via MCP ({len(objects)} found):"]
                for i, obj in enumerate(objects[:20], 1):  # Show first 20
                    result_lines.append(
                        f"{i}. {obj.get('name', 'Unnamed')} (UID: {obj.get('uid', 'N/A')})"
                    )
                    if obj.get('ipv4-address'):
                        result_lines.append(f"   IP: {obj.get('ipv4-address')}")
                    elif obj.get('subnet') and obj.get('mask-length'):
                        result_lines.append(f"   Network: {obj.get('subnet')}/{obj.get('mask-length')}")
                    elif obj.get('port') and obj.get('protocol'):
                        result_lines.append(f"   Port: {obj.get('port')}/{obj.get('protocol').upper()}")
                
                if len(objects) > 20:
                    result_lines.append(f"... and {len(objects) - 20} more objects")
                
                return "\n".join(result_lines)
            else:
                return f"❌ Failed to show objects via MCP: {response.get('message', 'Unknown error')}"
                
        except Exception as e:
            self._logger.error("Error in mcp_show_objects", error=str(e))
            return f"❌ Error showing objects via MCP: {str(e)}"


class MCPPublishChangesTool(BaseTool):
    """MCP tool for publishing changes."""
    
    name: str = "mcp_publish_changes"
    description: str = """
    Publish changes using Check Point MCP server.
    This is an alternative to direct API calls, using the MCP server for publishing.
    """
    args_schema: Type[BaseModel] = MCPPublishChangesInput
    
    def __init__(self):
        super().__init__()
        self._logger = get_logger("mcp_publish_changes_tool")
    
    def _run(self, **kwargs) -> str:
        """Publish changes via MCP."""
        try:
            # Validate input
            input_data = MCPPublishChangesInput(**kwargs)
            
            # Check if MCP is available
            if not mcp_integration.is_available():
                return "❌ MCP server is not available. Falling back to direct API calls."
            
            # Run async MCP call
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                response = loop.run_until_complete(
                    mcp_integration.mcp_publish_changes(input_data.targets)
                )
            finally:
                loop.close()
            
            if response["success"]:
                return (
                    f"✅ Successfully published changes via MCP\n"
                    f"Targets: {', '.join(input_data.targets) if input_data.targets else 'All gateways'}"
                )
            else:
                return f"❌ Failed to publish changes via MCP: {response.get('message', 'Unknown error')}"
                
        except Exception as e:
            self._logger.error("Error in mcp_publish_changes", error=str(e))
            return f"❌ Error publishing changes via MCP: {str(e)}"


class MCPCreateThreatExceptionTool(BaseTool):
    """MCP tool for creating threat exceptions."""
    
    name: str = "mcp_create_threat_exception"
    description: str = """
    Create a threat exception using Check Point MCP server.
    This is an alternative to direct API calls, using the MCP server for threat management.
    """
    args_schema: Type[BaseModel] = MCPCreateThreatExceptionInput
    
    def __init__(self):
        super().__init__()
        self._logger = get_logger("mcp_create_threat_exception_tool")
    
    def _run(self, **kwargs) -> str:
        """Create threat exception via MCP."""
        try:
            # Validate input
            input_data = MCPCreateThreatExceptionInput(**kwargs)
            
            # Check if MCP is available
            if not mcp_integration.is_available():
                return "❌ MCP server is not available. Falling back to direct API calls."
            
            # Prepare exception data
            exception_data = {
                "name": input_data.name,
                "layer": input_data.layer,
                "rule": input_data.rule,
                "exception-type": input_data.exception_type,
                "target": input_data.target
            }
            
            # Run async MCP call
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                response = loop.run_until_complete(
                    mcp_integration.mcp_create_threat_exception(exception_data)
                )
            finally:
                loop.close()
            
            if response["success"]:
                return (
                    f"✅ Successfully created threat exception via MCP\n"
                    f"Exception: {input_data.name}\n"
                    f"Layer: {input_data.layer}\n"
                    f"Rule: {input_data.rule}\n"
                    f"Type: {input_data.exception_type}\n"
                    f"Target: {input_data.target}"
                )
            else:
                return f"❌ Failed to create threat exception via MCP: {response.get('message', 'Unknown error')}"
                
        except Exception as e:
            self._logger.error("Error in mcp_create_threat_exception", error=str(e))
            return f"❌ Error creating threat exception via MCP: {str(e)}"


class MCPStatusTool(BaseTool):
    """Tool for checking MCP server status."""
    
    name: str = "mcp_status"
    description: str = """
    Check the status and capabilities of the Check Point MCP server.
    Shows whether MCP is available and what operations it supports.
    """
    args_schema: Type[BaseModel] = BaseModel  # No input parameters needed
    
    def __init__(self):
        super().__init__()
        self._logger = get_logger("mcp_status_tool")
    
    def _run(self, **kwargs) -> str:
        """Check MCP status."""
        try:
            capabilities = mcp_integration.get_capabilities()
            
            result_lines = ["Check Point MCP Server Status:"]
            result_lines.append("")
            
            if capabilities["available"]:
                result_lines.append("✅ MCP server is available")
                result_lines.append(f"Server path: {capabilities['server_path']}")
                result_lines.append("")
                result_lines.append("Supported operations:")
                
                for capability in capabilities["capabilities"]:
                    result_lines.append(f"  • {capability}")
                
                result_lines.append("")
                result_lines.append("MCP server provides an alternative interface for Check Point operations.")
            else:
                result_lines.append("❌ MCP server is not available")
                result_lines.append("")
                result_lines.append("Falling back to direct API calls for all operations.")
            
            return "\n".join(result_lines)
            
        except Exception as e:
            self._logger.error("Error in mcp_status", error=str(e))
            return f"❌ Error checking MCP status: {str(e)}"

