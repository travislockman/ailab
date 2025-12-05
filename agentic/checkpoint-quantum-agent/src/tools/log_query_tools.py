"""Log query tools for firewall log analysis."""

from typing import Any, Dict, List, Optional, Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

from ..api.checkpoint_client import CheckPointClient
from ..api.models import LogQuery, LogEntry
from ..utils.logger import get_logger


class QueryFirewallLogsInput(BaseModel):
    """Input for querying firewall logs."""
    query: str = Field(..., description="Log query string")
    limit: int = Field(default=100, description="Maximum number of results")
    time_range: Optional[str] = Field(default=None, description="Time range filter (e.g., 'last-1-hour')")
    source_ip: Optional[str] = Field(default=None, description="Filter by source IP")
    destination_ip: Optional[str] = Field(default=None, description="Filter by destination IP")
    service: Optional[str] = Field(default=None, description="Filter by service")
    action: Optional[str] = Field(default=None, description="Filter by action")


class GetRecentBlocksInput(BaseModel):
    """Input for getting recent blocked connections."""
    limit: int = Field(default=50, description="Maximum number of results")
    time_range: str = Field(default="last-1-hour", description="Time range for recent blocks")


class AnalyzeThreatLogsInput(BaseModel):
    """Input for analyzing threat logs."""
    time_range: str = Field(default="last-24-hours", description="Time range for analysis")
    severity: Optional[str] = Field(default=None, description="Filter by severity level")
    limit: int = Field(default=200, description="Maximum number of results")


class SearchLogsByIPInput(BaseModel):
    """Input for searching logs by IP address."""
    ip_address: str = Field(..., description="IP address to search for")
    time_range: str = Field(default="last-24-hours", description="Time range for search")
    limit: int = Field(default=100, description="Maximum number of results")


class GetLogStatisticsInput(BaseModel):
    """Input for getting log statistics."""
    time_range: str = Field(default="last-24-hours", description="Time range for statistics")
    group_by: str = Field(default="action", description="Group statistics by field (action, source, destination, service)")


class QueryFirewallLogsTool(BaseTool):
    """Tool for querying firewall logs with various filters."""
    
    name: str = "query_firewall_logs"
    description: str = """
    Query Check Point firewall logs with flexible filtering options.
    Supports filtering by time range, source/destination IPs, service, and action.
    Returns structured log entries with detailed information.
    """
    args_schema: Type[BaseModel] = QueryFirewallLogsInput
    
    def __init__(self):
        super().__init__()
        # Store logger and client as class attributes to avoid Pydantic validation issues
        if not hasattr(self.__class__, '_logger'):
            self.__class__._logger = get_logger("query_firewall_logs_tool")
        if not hasattr(self.__class__, '_client'):
            self.__class__._client = CheckPointClient()
    
    def _run(self, **kwargs) -> str:
        """Execute the log query."""
        try:
            # Validate input
            input_data = QueryFirewallLogsInput(**kwargs)
            
            # Create log query
            log_query = LogQuery(
                query=input_data.query,
                limit=input_data.limit,
                time_range=input_data.time_range,
                source_ip=input_data.source_ip,
                destination_ip=input_data.destination_ip,
                service=input_data.service,
                action=input_data.action
            )
            
            # Execute query
            response = self._client.query_logs(log_query)
            
            if response["success"]:
                logs = response["data"].get("objects", [])
                
                if not logs:
                    return "No logs found matching the query criteria."
                
                # Format results
                result_lines = [f"Found {len(logs)} log entries:"]
                for i, log in enumerate(logs[:10], 1):  # Show first 10
                    result_lines.append(
                        f"{i}. {log.get('time', 'N/A')} | "
                        f"{log.get('src', 'N/A')} -> {log.get('dst', 'N/A')} | "
                        f"Service: {log.get('service', 'N/A')} | "
                        f"Action: {log.get('action', 'N/A')} | "
                        f"Rule: {log.get('rule', 'N/A')}"
                    )
                
                if len(logs) > 10:
                    result_lines.append(f"... and {len(logs) - 10} more entries")
                
                return "\n".join(result_lines)
            else:
                return f"Failed to query logs: {response.get('message', 'Unknown error')}"
                
        except Exception as e:
            self._logger.error("Error in query_firewall_logs", error=str(e))
            return f"Error querying logs: {str(e)}"


class GetRecentBlocksTool(BaseTool):
    """Tool for getting recent blocked connections."""
    
    name: str = "get_recent_blocks"
    description: str = """
    Get recently blocked connections from firewall logs.
    Shows blocked traffic with source, destination, and reason for blocking.
    """
    args_schema: Type[BaseModel] = GetRecentBlocksInput
    
    def __init__(self):
        super().__init__()
        self._logger = get_logger("get_recent_blocks_tool")
        self._client = CheckPointClient()
    
    def _run(self, **kwargs) -> str:
        """Get recent blocked connections."""
        try:
            # Validate input
            input_data = GetRecentBlocksInput(**kwargs)
            
            # Create query for blocked connections
            log_query = LogQuery(
                query="action:drop OR action:reject",
                limit=input_data.limit,
                time_range=input_data.time_range
            )
            
            # Execute query
            response = self._client.query_logs(log_query)
            
            if response["success"]:
                logs = response["data"].get("objects", [])
                
                if not logs:
                    return f"No blocked connections found in the {input_data.time_range}."
                
                # Format results
                result_lines = [f"Recent blocked connections ({len(logs)} found):"]
                for i, log in enumerate(logs, 1):
                    result_lines.append(
                        f"{i}. {log.get('time', 'N/A')} | "
                        f"BLOCKED: {log.get('src', 'N/A')} -> {log.get('dst', 'N/A')} | "
                        f"Service: {log.get('service', 'N/A')} | "
                        f"Action: {log.get('action', 'N/A')} | "
                        f"Rule: {log.get('rule', 'N/A')}"
                    )
                
                return "\n".join(result_lines)
            else:
                return f"Failed to get recent blocks: {response.get('message', 'Unknown error')}"
                
        except Exception as e:
            self._logger.error("Error in get_recent_blocks", error=str(e))
            return f"Error getting recent blocks: {str(e)}"


class AnalyzeThreatLogsTool(BaseTool):
    """Tool for analyzing threat logs and identifying security events."""
    
    name: str = "analyze_threat_logs"
    description: str = """
    Analyze threat prevention logs to identify security events and attacks.
    Provides insights into detected threats, attack patterns, and security incidents.
    """
    args_schema: Type[BaseModel] = AnalyzeThreatLogsInput
    
    def __init__(self):
        super().__init__()
        self._logger = get_logger("analyze_threat_logs_tool")
        self._client = CheckPointClient()
    
    def _run(self, **kwargs) -> str:
        """Analyze threat logs."""
        try:
            # Validate input
            input_data = AnalyzeThreatLogsInput(**kwargs)
            
            # Create query for threat logs
            query = "product:Threat Prevention"
            if input_data.severity:
                query += f" AND severity:{input_data.severity}"
            
            log_query = LogQuery(
                query=query,
                limit=input_data.limit,
                time_range=input_data.time_range
            )
            
            # Execute query
            response = self._client.query_logs(log_query)
            
            if response["success"]:
                logs = response["data"].get("objects", [])
                
                if not logs:
                    return f"No threat logs found in the {input_data.time_range}."
                
                # Analyze logs
                threat_summary = {}
                high_severity_count = 0
                
                for log in logs:
                    threat_name = log.get('threat_name', 'Unknown Threat')
                    severity = log.get('severity', 'Unknown')
                    source = log.get('src', 'Unknown')
                    
                    if threat_name not in threat_summary:
                        threat_summary[threat_name] = {
                            'count': 0,
                            'severity': severity,
                            'sources': set()
                        }
                    
                    threat_summary[threat_name]['count'] += 1
                    threat_summary[threat_name]['sources'].add(source)
                    
                    if severity in ['High', 'Critical']:
                        high_severity_count += 1
                
                # Format analysis results
                result_lines = [
                    f"Threat Analysis Summary ({input_data.time_range}):",
                    f"Total threat events: {len(logs)}",
                    f"High/Critical severity events: {high_severity_count}",
                    f"Unique threat types: {len(threat_summary)}",
                    "",
                    "Top Threats:"
                ]
                
                # Sort by count
                sorted_threats = sorted(threat_summary.items(), key=lambda x: x[1]['count'], reverse=True)
                
                for i, (threat_name, data) in enumerate(sorted_threats[:10], 1):
                    result_lines.append(
                        f"{i}. {threat_name} - {data['count']} events "
                        f"(Severity: {data['severity']}, Sources: {len(data['sources'])})"
                    )
                
                return "\n".join(result_lines)
            else:
                return f"Failed to analyze threat logs: {response.get('message', 'Unknown error')}"
                
        except Exception as e:
            self._logger.error("Error in analyze_threat_logs", error=str(e))
            return f"Error analyzing threat logs: {str(e)}"


class SearchLogsByIPTool(BaseTool):
    """Tool for searching logs by IP address."""
    
    name: str = "search_logs_by_ip"
    description: str = """
    Search firewall logs for all activity involving a specific IP address.
    Shows both inbound and outbound connections for the specified IP.
    """
    args_schema: Type[BaseModel] = SearchLogsByIPInput
    
    def __init__(self):
        super().__init__()
        self._logger = get_logger("search_logs_by_ip_tool")
        self._client = CheckPointClient()
    
    def _run(self, **kwargs) -> str:
        """Search logs by IP address."""
        try:
            # Validate input
            input_data = SearchLogsByIPInput(**kwargs)
            
            # Create query for IP address
            log_query = LogQuery(
                query=f"src:{input_data.ip_address} OR dst:{input_data.ip_address}",
                limit=input_data.limit,
                time_range=input_data.time_range
            )
            
            # Execute query
            response = self._client.query_logs(log_query)
            
            if response["success"]:
                logs = response["data"].get("objects", [])
                
                if not logs:
                    return f"No logs found for IP {input_data.ip_address} in the {input_data.time_range}."
                
                # Analyze activity
                inbound_count = 0
                outbound_count = 0
                blocked_count = 0
                
                result_lines = [f"Log activity for IP {input_data.ip_address} ({len(logs)} entries):"]
                
                for i, log in enumerate(logs[:20], 1):  # Show first 20
                    src = log.get('src', 'N/A')
                    dst = log.get('dst', 'N/A')
                    action = log.get('action', 'N/A')
                    
                    if src == input_data.ip_address:
                        outbound_count += 1
                        direction = "OUTBOUND"
                    else:
                        inbound_count += 1
                        direction = "INBOUND"
                    
                    if action in ['drop', 'reject']:
                        blocked_count += 1
                    
                    result_lines.append(
                        f"{i}. {log.get('time', 'N/A')} | "
                        f"{direction}: {src} -> {dst} | "
                        f"Service: {log.get('service', 'N/A')} | "
                        f"Action: {action} | "
                        f"Rule: {log.get('rule', 'N/A')}"
                    )
                
                if len(logs) > 20:
                    result_lines.append(f"... and {len(logs) - 20} more entries")
                
                # Add summary
                result_lines.extend([
                    "",
                    "Activity Summary:",
                    f"- Inbound connections: {inbound_count}",
                    f"- Outbound connections: {outbound_count}",
                    f"- Blocked connections: {blocked_count}"
                ])
                
                return "\n".join(result_lines)
            else:
                return f"Failed to search logs for IP: {response.get('message', 'Unknown error')}"
                
        except Exception as e:
            self._logger.error("Error in search_logs_by_ip", error=str(e))
            return f"Error searching logs by IP: {str(e)}"


class GetLogStatisticsTool(BaseTool):
    """Tool for generating log statistics and reports."""
    
    name: str = "get_log_statistics"
    description: str = """
    Generate statistical analysis of firewall logs.
    Provides insights into traffic patterns, top sources/destinations, and security trends.
    """
    args_schema: Type[BaseModel] = GetLogStatisticsInput
    
    def __init__(self):
        super().__init__()
        self._logger = get_logger("get_log_statistics_tool")
        self._client = CheckPointClient()
    
    def _run(self, **kwargs) -> str:
        """Generate log statistics."""
        try:
            # Validate input
            input_data = GetLogStatisticsInput(**kwargs)
            
            # Create query for all logs in time range
            log_query = LogQuery(
                query="*",
                limit=1000,  # Get more data for statistics
                time_range=input_data.time_range
            )
            
            # Execute query
            response = self._client.query_logs(log_query)
            
            if response["success"]:
                logs = response["data"].get("objects", [])
                
                if not logs:
                    return f"No logs found in the {input_data.time_range}."
                
                # Generate statistics based on group_by field
                stats = {}
                total_logs = len(logs)
                
                for log in logs:
                    key = log.get(input_data.group_by, 'Unknown')
                    if key not in stats:
                        stats[key] = 0
                    stats[key] += 1
                
                # Sort by count
                sorted_stats = sorted(stats.items(), key=lambda x: x[1], reverse=True)
                
                # Format results
                result_lines = [
                    f"Log Statistics ({input_data.time_range}):",
                    f"Total log entries: {total_logs}",
                    f"Grouped by: {input_data.group_by}",
                    "",
                    f"Top {input_data.group_by.title()}s:"
                ]
                
                for i, (key, count) in enumerate(sorted_stats[:15], 1):
                    percentage = (count / total_logs) * 100
                    result_lines.append(f"{i}. {key}: {count} ({percentage:.1f}%)")
                
                # Additional insights
                if input_data.group_by == "action":
                    blocked_count = sum(count for key, count in stats.items() 
                                      if key.lower() in ['drop', 'reject'])
                    allowed_count = sum(count for key, count in stats.items() 
                                      if key.lower() in ['accept', 'allow'])
                    
                    result_lines.extend([
                        "",
                        "Security Summary:",
                        f"- Blocked connections: {blocked_count} ({blocked_count/total_logs*100:.1f}%)",
                        f"- Allowed connections: {allowed_count} ({allowed_count/total_logs*100:.1f}%)"
                    ])
                
                return "\n".join(result_lines)
            else:
                return f"Failed to generate log statistics: {response.get('message', 'Unknown error')}"
                
        except Exception as e:
            self._logger.error("Error in get_log_statistics", error=str(e))
            return f"Error generating log statistics: {str(e)}"

