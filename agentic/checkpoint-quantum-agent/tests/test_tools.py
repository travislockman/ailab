"""Tests for agent tools."""

import pytest
from unittest.mock import Mock, patch

from src.tools.log_query_tools import QueryFirewallLogsTool
from src.tools.policy_tools import CreateAccessRuleTool
from src.tools.object_tools import CreateHostObjectTool
from src.tools.threat_tools import CreateThreatExceptionTool
from src.tools.general_tools import PublishChangesTool


class TestLogQueryTools:
    """Test log query tools."""
    
    @patch('src.tools.log_query_tools.CheckPointClient')
    def test_query_firewall_logs_tool(self, mock_client):
        """Test QueryFirewallLogsTool."""
        # Mock the client response
        mock_client.return_value.query_logs.return_value = {
            "success": True,
            "data": {
                "objects": [
                    {
                        "time": "2024-01-01T10:00:00Z",
                        "src": "192.168.1.100",
                        "dst": "8.8.8.8",
                        "service": "https",
                        "action": "accept",
                        "rule": "Allow-HTTPS"
                    }
                ]
            }
        }
        
        tool = QueryFirewallLogsTool()
        result = tool._run(
            query="action:accept",
            limit=10,
            time_range="last-1-hour"
        )
        
        assert "Found 1 log entries" in result
        assert "192.168.1.100" in result
    
    @patch('src.tools.log_query_tools.CheckPointClient')
    def test_get_recent_blocks_tool(self, mock_client):
        """Test GetRecentBlocksTool."""
        # Mock the client response
        mock_client.return_value.query_logs.return_value = {
            "success": True,
            "data": {
                "objects": [
                    {
                        "time": "2024-01-01T10:00:00Z",
                        "src": "192.168.1.100",
                        "dst": "8.8.8.8",
                        "service": "https",
                        "action": "drop",
                        "rule": "Block-Suspicious"
                    }
                ]
            }
        }
        
        tool = GetRecentBlocksTool()
        result = tool._run(
            limit=10,
            time_range="last-1-hour"
        )
        
        assert "Recent blocked connections" in result
        assert "BLOCKED" in result


class TestPolicyTools:
    """Test policy management tools."""
    
    @patch('src.tools.policy_tools.CheckPointClient')
    def test_create_access_rule_tool(self, mock_client):
        """Test CreateAccessRuleTool."""
        # Mock the client response
        mock_client.return_value.create_access_rule.return_value = {
            "success": True,
            "data": {
                "uid": "test-rule-uid"
            }
        }
        
        tool = CreateAccessRuleTool()
        result = tool._run(
            name="Test Rule",
            source="Internal-Network",
            destination="Any",
            service="HTTPS",
            action="accept",
            layer="Network"
        )
        
        assert "Successfully created access rule" in result
        assert "Test Rule" in result
    
    @patch('src.tools.policy_tools.CheckPointClient')
    def test_show_policy_rules_tool(self, mock_client):
        """Test ShowPolicyRulesTool."""
        # Mock the client response
        mock_client.return_value.show_access_rulebase.return_value = {
            "success": True,
            "data": {
                "objects": [
                    {
                        "name": "Test Rule",
                        "uid": "test-rule-uid",
                        "source": "Internal-Network",
                        "destination": "Any",
                        "service": "HTTPS",
                        "action": "accept",
                        "track": "log"
                    }
                ]
            }
        }
        
        tool = ShowPolicyRulesTool()
        result = tool._run(
            layer="Network",
            limit=100
        )
        
        assert "Access Rules in Layer" in result
        assert "Test Rule" in result


class TestObjectTools:
    """Test object management tools."""
    
    @patch('src.tools.object_tools.CheckPointClient')
    def test_create_host_object_tool(self, mock_client):
        """Test CreateHostObjectTool."""
        # Mock the client response
        mock_client.return_value.create_host_object.return_value = {
            "success": True,
            "data": {
                "uid": "test-host-uid"
            }
        }
        
        tool = CreateHostObjectTool()
        result = tool._run(
            name="TestHost",
            ip_address="192.168.1.100",
            comments="Test host object"
        )
        
        assert "Successfully created host object" in result
        assert "TestHost" in result
        assert "192.168.1.100" in result
    
    @patch('src.tools.object_tools.CheckPointClient')
    def test_show_objects_tool(self, mock_client):
        """Test ShowObjectsTool."""
        # Mock the client response
        mock_client.return_value.show_objects.return_value = {
            "success": True,
            "data": {
                "objects": [
                    {
                        "name": "TestHost",
                        "uid": "test-host-uid",
                        "type": "host",
                        "ipv4-address": "192.168.1.100"
                    }
                ]
            }
        }
        
        tool = ShowObjectsTool()
        result = tool._run(
            object_type="host",
            limit=100
        )
        
        assert "Check Point Objects" in result
        assert "TestHost" in result


class TestThreatTools:
    """Test threat prevention tools."""
    
    @patch('src.tools.threat_tools.CheckPointClient')
    def test_create_threat_exception_tool(self, mock_client):
        """Test CreateThreatExceptionTool."""
        # Mock the client response
        mock_client.return_value.create_threat_exception.return_value = {
            "success": True,
            "data": {
                "uid": "test-exception-uid"
            }
        }
        
        tool = CreateThreatExceptionTool()
        result = tool._run(
            name="Test Exception",
            layer="Threat Prevention",
            rule="Test Rule",
            exception_type="exclude",
            target="TestHost"
        )
        
        assert "Successfully created threat exception" in result
        assert "Test Exception" in result
    
    @patch('src.tools.threat_tools.CheckPointClient')
    def test_show_threat_exceptions_tool(self, mock_client):
        """Test ShowThreatExceptionsTool."""
        # Mock the client response
        mock_client.return_value._retry_request.return_value = {
            "success": True,
            "data": {
                "objects": [
                    {
                        "name": "Test Exception",
                        "uid": "test-exception-uid",
                        "layer": "Threat Prevention",
                        "rule": "Test Rule",
                        "exception-type": "exclude",
                        "target": "TestHost"
                    }
                ]
            }
        }
        
        tool = ShowThreatExceptionsTool()
        result = tool._run(
            limit=100
        )
        
        assert "Threat Prevention Exceptions" in result
        assert "Test Exception" in result


class TestGeneralTools:
    """Test general tools."""
    
    @patch('src.tools.general_tools.CheckPointClient')
    def test_publish_changes_tool(self, mock_client):
        """Test PublishChangesTool."""
        # Mock the client response
        mock_client.return_value.publish_changes.return_value = {
            "success": True,
            "data": {
                "task-id": "test-task-id"
            }
        }
        
        tool = PublishChangesTool()
        result = tool._run(
            targets=["gateway1", "gateway2"]
        )
        
        assert "Successfully published changes" in result
        assert "test-task-id" in result
    
    @patch('src.tools.general_tools.CheckPointClient')
    def test_show_gateways_tool(self, mock_client):
        """Test ShowGatewaysTool."""
        # Mock the client response
        mock_client.return_value.show_gateways.return_value = {
            "success": True,
            "data": {
                "objects": [
                    {
                        "name": "TestGateway",
                        "uid": "test-gateway-uid",
                        "ipv4-address": "192.168.1.1",
                        "version": "R82",
                        "status": "online",
                        "platform": "Check Point"
                    }
                ]
            }
        }
        
        tool = ShowGatewaysTool()
        result = tool._run()
        
        assert "Security Gateways" in result
        assert "TestGateway" in result
        assert "online" in result

