"""MCP server integration for Check Point operations."""

import subprocess
import json
import asyncio
from typing import Any, Dict, List, Optional, Union
from pathlib import Path

from ..utils.logger import get_logger, ActionLogger
from ..utils.config import config


class MCPIntegration:
    """Integration with Check Point MCP server."""
    
    def __init__(self):
        self.logger = get_logger("mcp_integration")
        self.action_logger = ActionLogger("mcp_integration")
        
        # Get MCP configuration
        self.mcp_config = config.get_mcp_config()
        self.enabled = self.mcp_config["enabled"]
        self.server_path = self.mcp_config.get("server_path")
        
        # MCP server process
        self._process: Optional[subprocess.Popen] = None
        self._connected = False
        
        if self.enabled and self.server_path:
            self.logger.info("MCP integration enabled", server_path=self.server_path)
        else:
            self.logger.info("MCP integration disabled")
    
    def is_available(self) -> bool:
        """Check if MCP server is available."""
        return self.enabled and self.server_path and Path(self.server_path).exists()
    
    async def start_server(self) -> bool:
        """Start the MCP server process."""
        if not self.is_available():
            self.logger.warning("MCP server not available")
            return False
        
        try:
            self.logger.info("Starting MCP server")
            
            # Start MCP server process
            self._process = subprocess.Popen(
                ["python", self.server_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for server to be ready
            await asyncio.sleep(2)
            
            if self._process.poll() is None:
                self._connected = True
                self.logger.info("MCP server started successfully")
                return True
            else:
                self.logger.error("MCP server failed to start")
                return False
                
        except Exception as e:
            self.logger.error("Failed to start MCP server", error=str(e))
            return False
    
    async def stop_server(self) -> bool:
        """Stop the MCP server process."""
        if self._process:
            try:
                self.logger.info("Stopping MCP server")
                self._process.terminate()
                self._process.wait(timeout=5)
                self._connected = False
                self.logger.info("MCP server stopped")
                return True
            except Exception as e:
                self.logger.error("Failed to stop MCP server", error=str(e))
                return False
        return True
    
    async def _send_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Send request to MCP server."""
        if not self._connected or not self._process:
            return {"success": False, "message": "MCP server not connected"}
        
        try:
            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": method,
                "params": params
            }
            
            # Send request
            self._process.stdin.write(json.dumps(request) + "\n")
            self._process.stdin.flush()
            
            # Read response
            response_line = self._process.stdout.readline()
            if response_line:
                response = json.loads(response_line.strip())
                return {
                    "success": True,
                    "data": response
                }
            else:
                return {"success": False, "message": "No response from MCP server"}
                
        except Exception as e:
            self.logger.error("MCP request failed", method=method, error=str(e))
            return {"success": False, "message": str(e)}
    
    # MCP Tool Wrappers
    async def mcp_create_access_rule(self, rule_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create access rule via MCP."""
        self.action_logger.log_action_start("mcp_create_access_rule", rule_name=rule_data.get("name"))
        
        if not self.is_available():
            return {"success": False, "message": "MCP server not available"}
        
        response = await self._send_request("create_access_rule", rule_data)
        
        if response["success"]:
            self.action_logger.log_action_success("mcp_create_access_rule", result=response["data"])
        else:
            self.action_logger.log_action_error("mcp_create_access_rule", response.get("message", "Unknown error"))
        
        return response
    
    async def mcp_create_host_object(self, host_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create host object via MCP."""
        self.action_logger.log_action_start("mcp_create_host_object", host_name=host_data.get("name"))
        
        if not self.is_available():
            return {"success": False, "message": "MCP server not available"}
        
        response = await self._send_request("create_host_object", host_data)
        
        if response["success"]:
            self.action_logger.log_action_success("mcp_create_host_object", result=response["data"])
        else:
            self.action_logger.log_action_error("mcp_create_host_object", response.get("message", "Unknown error"))
        
        return response
    
    async def mcp_query_logs(self, query_data: Dict[str, Any]) -> Dict[str, Any]:
        """Query logs via MCP."""
        self.action_logger.log_action_start("mcp_query_logs", query=query_data.get("query"))
        
        if not self.is_available():
            return {"success": False, "message": "MCP server not available"}
        
        response = await self._send_request("query_logs", query_data)
        
        if response["success"]:
            logs = response["data"].get("result", {}).get("objects", [])
            self.action_logger.log_action_success("mcp_query_logs", result_count=len(logs))
        else:
            self.action_logger.log_action_error("mcp_query_logs", response.get("message", "Unknown error"))
        
        return response
    
    async def mcp_show_objects(self, object_type: Optional[str] = None) -> Dict[str, Any]:
        """Show objects via MCP."""
        self.action_logger.log_action_start("mcp_show_objects", object_type=object_type)
        
        if not self.is_available():
            return {"success": False, "message": "MCP server not available"}
        
        params = {}
        if object_type:
            params["type"] = object_type
        
        response = await self._send_request("show_objects", params)
        
        if response["success"]:
            objects = response["data"].get("result", {}).get("objects", [])
            self.action_logger.log_action_success("mcp_show_objects", result_count=len(objects))
        else:
            self.action_logger.log_action_error("mcp_show_objects", response.get("message", "Unknown error"))
        
        return response
    
    async def mcp_publish_changes(self, targets: Optional[List[str]] = None) -> Dict[str, Any]:
        """Publish changes via MCP."""
        self.action_logger.log_action_start("mcp_publish_changes", targets=targets)
        
        if not self.is_available():
            return {"success": False, "message": "MCP server not available"}
        
        params = {}
        if targets:
            params["targets"] = targets
        
        response = await self._send_request("publish_changes", params)
        
        if response["success"]:
            self.action_logger.log_action_success("mcp_publish_changes", result=response["data"])
        else:
            self.action_logger.log_action_error("mcp_publish_changes", response.get("message", "Unknown error"))
        
        return response
    
    async def mcp_show_gateways(self) -> Dict[str, Any]:
        """Show gateways via MCP."""
        self.action_logger.log_action_start("mcp_show_gateways")
        
        if not self.is_available():
            return {"success": False, "message": "MCP server not available"}
        
        response = await self._send_request("show_gateways", {})
        
        if response["success"]:
            gateways = response["data"].get("result", {}).get("objects", [])
            self.action_logger.log_action_success("mcp_show_gateways", result_count=len(gateways))
        else:
            self.action_logger.log_action_error("mcp_show_gateways", response.get("message", "Unknown error"))
        
        return response
    
    async def mcp_create_threat_exception(self, exception_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create threat exception via MCP."""
        self.action_logger.log_action_start("mcp_create_threat_exception", exception_name=exception_data.get("name"))
        
        if not self.is_available():
            return {"success": False, "message": "MCP server not available"}
        
        response = await self._send_request("create_threat_exception", exception_data)
        
        if response["success"]:
            self.action_logger.log_action_success("mcp_create_threat_exception", result=response["data"])
        else:
            self.action_logger.log_action_error("mcp_create_threat_exception", response.get("message", "Unknown error"))
        
        return response
    
    async def mcp_show_policy_rules(self, layer: str) -> Dict[str, Any]:
        """Show policy rules via MCP."""
        self.action_logger.log_action_start("mcp_show_policy_rules", layer=layer)
        
        if not self.is_available():
            return {"success": False, "message": "MCP server not available"}
        
        response = await self._send_request("show_policy_rules", {"layer": layer})
        
        if response["success"]:
            rules = response["data"].get("result", {}).get("objects", [])
            self.action_logger.log_action_success("mcp_show_policy_rules", result_count=len(rules))
        else:
            self.action_logger.log_action_error("mcp_show_policy_rules", response.get("message", "Unknown error"))
        
        return response
    
    async def mcp_delete_object(self, object_uid: str) -> Dict[str, Any]:
        """Delete object via MCP."""
        self.action_logger.log_action_start("mcp_delete_object", object_uid=object_uid)
        
        if not self.is_available():
            return {"success": False, "message": "MCP server not available"}
        
        response = await self._send_request("delete_object", {"uid": object_uid})
        
        if response["success"]:
            self.action_logger.log_action_success("mcp_delete_object")
        else:
            self.action_logger.log_action_error("mcp_delete_object", response.get("message", "Unknown error"))
        
        return response
    
    async def mcp_install_policy(self, install_data: Dict[str, Any]) -> Dict[str, Any]:
        """Install policy via MCP."""
        self.action_logger.log_action_start("mcp_install_policy", targets=install_data.get("targets"))
        
        if not self.is_available():
            return {"success": False, "message": "MCP server not available"}
        
        response = await self._send_request("install_policy", install_data)
        
        if response["success"]:
            self.action_logger.log_action_success("mcp_install_policy", result=response["data"])
        else:
            self.action_logger.log_action_error("mcp_install_policy", response.get("message", "Unknown error"))
        
        return response
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get MCP server capabilities."""
        if not self.is_available():
            return {"available": False, "capabilities": []}
        
        # Standard Check Point MCP capabilities
        capabilities = [
            "create_access_rule",
            "modify_access_rule", 
            "delete_access_rule",
            "show_policy_rules",
            "create_host_object",
            "create_network_object",
            "create_group_object",
            "create_service_object",
            "delete_object",
            "show_objects",
            "query_logs",
            "create_threat_exception",
            "delete_threat_exception",
            "show_threat_exceptions",
            "publish_changes",
            "discard_changes",
            "install_policy",
            "show_gateways"
        ]
        
        return {
            "available": True,
            "capabilities": capabilities,
            "server_path": self.server_path
        }
    
    async def __aenter__(self):
        """Async context manager entry."""
        if self.is_available():
            await self.start_server()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.stop_server()


# Global MCP integration instance
mcp_integration = MCPIntegration()

