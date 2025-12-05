"""Tests for CrewAI agents."""

import pytest
from unittest.mock import Mock, patch

from src.agents.quantum_agent import QuantumAgent
from src.agents.log_analyzer_agent import LogAnalyzerAgent
from src.agents.policy_manager_agent import PolicyManagerAgent
from src.agents.object_manager_agent import ObjectManagerAgent
from src.agents.threat_prevention_agent import ThreatPreventionAgent


class TestQuantumAgent:
    """Test the main Quantum Agent."""
    
    @patch('src.agents.quantum_agent.ChatOpenAI')
    def test_quantum_agent_initialization(self, mock_llm):
        """Test Quantum Agent initialization."""
        agent = QuantumAgent()
        
        assert agent.agent is not None
        assert len(agent.tools) > 0
        assert agent.agent.role == "Check Point Quantum Security Manager"
    
    @patch('src.agents.quantum_agent.ChatOpenAI')
    def test_quantum_agent_info(self, mock_llm):
        """Test getting agent information."""
        agent = QuantumAgent()
        info = agent.get_agent_info()
        
        assert info["name"] == "Check Point Quantum Security Manager"
        assert "tools_count" in info
        assert "capabilities" in info


class TestLogAnalyzerAgent:
    """Test the Log Analyzer Agent."""
    
    @patch('src.agents.log_analyzer_agent.ChatOpenAI')
    def test_log_analyzer_initialization(self, mock_llm):
        """Test Log Analyzer Agent initialization."""
        agent = LogAnalyzerAgent()
        
        assert agent.agent is not None
        assert len(agent.tools) == 5  # 5 log analysis tools
        assert agent.agent.role == "Firewall Log Analysis Specialist"
    
    @patch('src.agents.log_analyzer_agent.ChatOpenAI')
    def test_log_analyzer_info(self, mock_llm):
        """Test getting agent information."""
        agent = LogAnalyzerAgent()
        info = agent.get_agent_info()
        
        assert info["name"] == "Firewall Log Analysis Specialist"
        assert info["tools_count"] == 5


class TestPolicyManagerAgent:
    """Test the Policy Manager Agent."""
    
    @patch('src.agents.policy_manager_agent.ChatOpenAI')
    def test_policy_manager_initialization(self, mock_llm):
        """Test Policy Manager Agent initialization."""
        agent = PolicyManagerAgent()
        
        assert agent.agent is not None
        assert len(agent.tools) == 7  # 7 policy management tools
        assert agent.agent.role == "Firewall Policy Administrator"
    
    @patch('src.agents.policy_manager_agent.ChatOpenAI')
    def test_policy_manager_info(self, mock_llm):
        """Test getting agent information."""
        agent = PolicyManagerAgent()
        info = agent.get_agent_info()
        
        assert info["name"] == "Firewall Policy Administrator"
        assert info["tools_count"] == 7


class TestObjectManagerAgent:
    """Test the Object Manager Agent."""
    
    @patch('src.agents.object_manager_agent.ChatOpenAI')
    def test_object_manager_initialization(self, mock_llm):
        """Test Object Manager Agent initialization."""
        agent = ObjectManagerAgent()
        
        assert agent.agent is not None
        assert len(agent.tools) == 7  # 7 object management tools
        assert agent.agent.role == "Network Object Administrator"
    
    @patch('src.agents.object_manager_agent.ChatOpenAI')
    def test_object_manager_info(self, mock_llm):
        """Test getting agent information."""
        agent = ObjectManagerAgent()
        info = agent.get_agent_info()
        
        assert info["name"] == "Network Object Administrator"
        assert info["tools_count"] == 7


class TestThreatPreventionAgent:
    """Test the Threat Prevention Agent."""
    
    @patch('src.agents.threat_prevention_agent.ChatOpenAI')
    def test_threat_prevention_initialization(self, mock_llm):
        """Test Threat Prevention Agent initialization."""
        agent = ThreatPreventionAgent()
        
        assert agent.agent is not None
        assert len(agent.tools) == 5  # 5 threat prevention tools
        assert agent.agent.role == "Threat Prevention Specialist"
    
    @patch('src.agents.threat_prevention_agent.ChatOpenAI')
    def test_threat_prevention_info(self, mock_llm):
        """Test getting agent information."""
        agent = ThreatPreventionAgent()
        info = agent.get_agent_info()
        
        assert info["name"] == "Threat Prevention Specialist"
        assert info["tools_count"] == 5

