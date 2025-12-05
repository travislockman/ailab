"""Threat prevention tools for managing IPS exceptions and threat protection."""

from typing import Any, Dict, List, Optional, Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

from ..api.checkpoint_client import CheckPointClient
from ..api.models import ThreatException
from ..utils.logger import get_logger


class CreateThreatExceptionInput(BaseModel):
    """Input for creating a threat exception."""
    name: str = Field(..., description="Exception name")
    layer: str = Field(..., description="Threat layer name")
    rule: str = Field(..., description="Threat rule name or UID")
    exception_type: str = Field(..., description="Exception type (exclude, ignore, etc.)")
    target: str = Field(..., description="Target object name or UID")
    comments: Optional[str] = Field(default=None, description="Exception comments")
    enabled: bool = Field(default=True, description="Whether exception is enabled")


class DeleteThreatExceptionInput(BaseModel):
    """Input for deleting a threat exception."""
    exception_uid: str = Field(..., description="Exception UID to delete")


class ModifyThreatExceptionInput(BaseModel):
    """Input for modifying a threat exception."""
    exception_uid: str = Field(..., description="Exception UID to modify")
    name: Optional[str] = Field(default=None, description="New exception name")
    exception_type: Optional[str] = Field(default=None, description="New exception type")
    target: Optional[str] = Field(default=None, description="New target")
    comments: Optional[str] = Field(default=None, description="New comments")
    enabled: Optional[bool] = Field(default=None, description="New enabled status")


class ShowThreatExceptionsInput(BaseModel):
    """Input for showing threat exceptions."""
    layer: Optional[str] = Field(default=None, description="Filter by threat layer")
    limit: int = Field(default=500, description="Maximum number of exceptions to show")


class AnalyzeThreatProtectionsInput(BaseModel):
    """Input for analyzing threat protections."""
    time_range: str = Field(default="last-24-hours", description="Time range for analysis")
    layer: Optional[str] = Field(default=None, description="Filter by threat layer")
    limit: int = Field(default=200, description="Maximum number of results")


class CreateThreatExceptionTool(BaseTool):
    """Tool for creating threat prevention exceptions."""
    
    name: str = "create_threat_exception"
    description: str = """
    Create a new threat prevention exception in Check Point firewall.
    Exceptions can exclude, ignore, or modify threat protection behavior for specific targets.
    """
    args_schema: Type[BaseModel] = CreateThreatExceptionInput
    
    def __init__(self):
        super().__init__()
        self._logger = get_logger("create_threat_exception_tool")
        self._client = CheckPointClient()
    
    def _run(self, **kwargs) -> str:
        """Create a threat exception."""
        try:
            # Validate input
            input_data = CreateThreatExceptionInput(**kwargs)
            
            # Create threat exception object
            exception = ThreatException(
                name=input_data.name,
                layer=input_data.layer,
                rule=input_data.rule,
                exception_type=input_data.exception_type,
                target=input_data.target,
                comments=input_data.comments,
                enabled=input_data.enabled
            )
            
            # Create the exception
            response = self._client.create_threat_exception(exception)
            
            if response["success"]:
                exception_data = response["data"]
                return (
                    f"✅ Successfully created threat exception '{input_data.name}'\n"
                    f"Exception UID: {exception_data.get('uid', 'N/A')}\n"
                    f"Layer: {input_data.layer}\n"
                    f"Rule: {input_data.rule}\n"
                    f"Type: {input_data.exception_type}\n"
                    f"Target: {input_data.target}\n"
                    f"Enabled: {input_data.enabled}\n"
                    f"Comments: {input_data.comments or 'None'}"
                )
            else:
                return f"❌ Failed to create threat exception: {response.get('message', 'Unknown error')}"
                
        except Exception as e:
            self._logger.error("Error in create_threat_exception", error=str(e))
            return f"❌ Error creating threat exception: {str(e)}"


class DeleteThreatExceptionTool(BaseTool):
    """Tool for deleting threat exceptions."""
    
    name: str = "delete_threat_exception"
    description: str = """
    Delete a threat prevention exception from Check Point firewall.
    Removes the exception permanently from the threat layer.
    """
    args_schema: Type[BaseModel] = DeleteThreatExceptionInput
    
    def __init__(self):
        super().__init__()
        self._logger = get_logger("delete_threat_exception_tool")
        self._client = CheckPointClient()
    
    def _run(self, **kwargs) -> str:
        """Delete a threat exception."""
        try:
            # Validate input
            input_data = DeleteThreatExceptionInput(**kwargs)
            
            # Delete the exception
            response = self._client.delete_threat_exception(input_data.exception_uid)
            
            if response["success"]:
                return f"✅ Successfully deleted threat exception (UID: {input_data.exception_uid})"
            else:
                return f"❌ Failed to delete threat exception: {response.get('message', 'Unknown error')}"
                
        except Exception as e:
            self._logger.error("Error in delete_threat_exception", error=str(e))
            return f"❌ Error deleting threat exception: {str(e)}"


class ModifyThreatExceptionTool(BaseTool):
    """Tool for modifying threat exceptions."""
    
    name: str = "modify_threat_exception"
    description: str = """
    Modify an existing threat prevention exception in Check Point firewall.
    Can update exception properties like type, target, and enabled status.
    """
    args_schema: Type[BaseModel] = ModifyThreatExceptionInput
    
    def __init__(self):
        super().__init__()
        self._logger = get_logger("modify_threat_exception_tool")
        self._client = CheckPointClient()
    
    def _run(self, **kwargs) -> str:
        """Modify a threat exception."""
        try:
            # Validate input
            input_data = ModifyThreatExceptionInput(**kwargs)
            
            # Prepare modification data
            modify_data = {"uid": input_data.exception_uid}
            if input_data.name is not None:
                modify_data["name"] = input_data.name
            if input_data.exception_type is not None:
                modify_data["exception-type"] = input_data.exception_type
            if input_data.target is not None:
                modify_data["target"] = input_data.target
            if input_data.comments is not None:
                modify_data["comments"] = input_data.comments
            if input_data.enabled is not None:
                modify_data["enabled"] = input_data.enabled
            
            # Modify the exception
            response = self._client._retry_request(
                "POST", "/set-threat-exception", data=modify_data
            )
            
            if response["success"]:
                updated_fields = [k for k in modify_data.keys() if k != "uid"]
                return (
                    f"✅ Successfully modified threat exception\n"
                    f"Exception UID: {input_data.exception_uid}\n"
                    f"Updated fields: {', '.join(updated_fields)}"
                )
            else:
                return f"❌ Failed to modify threat exception: {response.get('message', 'Unknown error')}"
                
        except Exception as e:
            self._logger.error("Error in modify_threat_exception", error=str(e))
            return f"❌ Error modifying threat exception: {str(e)}"


class ShowThreatExceptionsTool(BaseTool):
    """Tool for displaying threat exceptions."""
    
    name: str = "show_threat_exceptions"
    description: str = """
    Display threat prevention exceptions from Check Point firewall.
    Can show all exceptions or filter by specific threat layer.
    """
    args_schema: Type[BaseModel] = ShowThreatExceptionsInput
    
    def __init__(self):
        super().__init__()
        self._logger = get_logger("show_threat_exceptions_tool")
        self._client = CheckPointClient()
    
    def _run(self, **kwargs) -> str:
        """Show threat exceptions."""
        try:
            # Validate input
            input_data = ShowThreatExceptionsInput(**kwargs)
            
            # Prepare query data
            query_data = {"limit": input_data.limit}
            if input_data.layer:
                query_data["layer"] = input_data.layer
            
            # Get threat exceptions
            response = self._client._retry_request(
                "POST", "/show-threat-rule-exception-rulebase", data=query_data
            )
            
            if response["success"]:
                exceptions = response["data"].get("objects", [])
                
                if not exceptions:
                    filter_text = f" in layer '{input_data.layer}'" if input_data.layer else ""
                    return f"No threat exceptions found{filter_text}."
                
                # Format results
                result_lines = [f"Threat Prevention Exceptions ({len(exceptions)} found):"]
                result_lines.append("")
                
                for i, exception in enumerate(exceptions, 1):
                    result_lines.append(
                        f"{i}. {exception.get('name', 'Unnamed')} (UID: {exception.get('uid', 'N/A')})"
                    )
                    result_lines.append(f"   Layer: {exception.get('layer', 'N/A')}")
                    result_lines.append(f"   Rule: {exception.get('rule', 'N/A')}")
                    result_lines.append(f"   Type: {exception.get('exception-type', 'N/A')}")
                    result_lines.append(f"   Target: {exception.get('target', 'N/A')}")
                    result_lines.append(f"   Enabled: {exception.get('enabled', 'N/A')}")
                    if exception.get('comments'):
                        result_lines.append(f"   Comments: {exception.get('comments')}")
                    result_lines.append("")
                
                return "\n".join(result_lines)
            else:
                return f"❌ Failed to show threat exceptions: {response.get('message', 'Unknown error')}"
                
        except Exception as e:
            self._logger.error("Error in show_threat_exceptions", error=str(e))
            return f"❌ Error showing threat exceptions: {str(e)}"


class AnalyzeThreatProtectionsTool(BaseTool):
    """Tool for analyzing active threat protections."""
    
    name: str = "analyze_threat_protections"
    description: str = """
    Analyze active threat protection policies and their effectiveness.
    Provides insights into threat detection, prevention actions, and security posture.
    """
    args_schema: Type[BaseModel] = AnalyzeThreatProtectionsInput
    
    def __init__(self):
        super().__init__()
        self._logger = get_logger("analyze_threat_protections_tool")
        self._client = CheckPointClient()
    
    def _run(self, **kwargs) -> str:
        """Analyze threat protections."""
        try:
            # Validate input
            input_data = AnalyzeThreatProtectionsInput(**kwargs)
            
            # Query threat logs for analysis
            from ..api.models import LogQuery
            log_query = LogQuery(
                query="product:Threat Prevention",
                limit=input_data.limit,
                time_range=input_data.time_range
            )
            
            if input_data.layer:
                log_query.query += f" AND layer:{input_data.layer}"
            
            # Get threat logs
            response = self._client.query_logs(log_query)
            
            if response["success"]:
                logs = response["data"].get("objects", [])
                
                if not logs:
                    return f"No threat protection activity found in the {input_data.time_range}."
                
                # Analyze threat protection effectiveness
                protection_stats = {
                    "total_events": len(logs),
                    "prevented_attacks": 0,
                    "detected_threats": 0,
                    "by_severity": {},
                    "by_action": {},
                    "top_threats": {},
                    "top_sources": {}
                }
                
                for log in logs:
                    # Count prevented attacks
                    action = log.get("action", "").lower()
                    if action in ["prevent", "block", "drop"]:
                        protection_stats["prevented_attacks"] += 1
                    
                    # Count detected threats
                    if log.get("threat_name"):
                        protection_stats["detected_threats"] += 1
                    
                    # Count by severity
                    severity = log.get("severity", "Unknown")
                    protection_stats["by_severity"][severity] = protection_stats["by_severity"].get(severity, 0) + 1
                    
                    # Count by action
                    protection_stats["by_action"][action] = protection_stats["by_action"].get(action, 0) + 1
                    
                    # Top threats
                    threat_name = log.get("threat_name", "Unknown")
                    protection_stats["top_threats"][threat_name] = protection_stats["top_threats"].get(threat_name, 0) + 1
                    
                    # Top sources
                    source = log.get("src", "Unknown")
                    protection_stats["top_sources"][source] = protection_stats["top_sources"].get(source, 0) + 1
                
                # Format analysis results
                result_lines = [
                    f"Threat Protection Analysis ({input_data.time_range}):",
                    f"Total security events: {protection_stats['total_events']}",
                    f"Prevented attacks: {protection_stats['prevented_attacks']}",
                    f"Detected threats: {protection_stats['detected_threats']}",
                    "",
                    "Events by Severity:"
                ]
                
                for severity, count in sorted(protection_stats["by_severity"].items(), key=lambda x: x[1], reverse=True):
                    percentage = (count / protection_stats["total_events"]) * 100
                    result_lines.append(f"  {severity}: {count} ({percentage:.1f}%)")
                
                result_lines.extend([
                    "",
                    "Events by Action:"
                ])
                
                for action, count in sorted(protection_stats["by_action"].items(), key=lambda x: x[1], reverse=True):
                    percentage = (count / protection_stats["total_events"]) * 100
                    result_lines.append(f"  {action}: {count} ({percentage:.1f}%)")
                
                result_lines.extend([
                    "",
                    "Top Threats:"
                ])
                
                for threat, count in sorted(protection_stats["top_threats"].items(), key=lambda x: x[1], reverse=True)[:10]:
                    result_lines.append(f"  {threat}: {count} events")
                
                result_lines.extend([
                    "",
                    "Top Source IPs:"
                ])
                
                for source, count in sorted(protection_stats["top_sources"].items(), key=lambda x: x[1], reverse=True)[:10]:
                    result_lines.append(f"  {source}: {count} events")
                
                # Calculate protection effectiveness
                if protection_stats["total_events"] > 0:
                    prevention_rate = (protection_stats["prevented_attacks"] / protection_stats["total_events"]) * 100
                    result_lines.extend([
                        "",
                        f"Protection Effectiveness: {prevention_rate:.1f}% of threats were prevented"
                    ])
                
                return "\n".join(result_lines)
            else:
                return f"❌ Failed to analyze threat protections: {response.get('message', 'Unknown error')}"
                
        except Exception as e:
            self._logger.error("Error in analyze_threat_protections", error=str(e))
            return f"❌ Error analyzing threat protections: {str(e)}"

