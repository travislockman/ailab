"""Tests for Check Point API client."""

import pytest
from unittest.mock import Mock, patch, MagicMock

from src.api.checkpoint_client import CheckPointClient
from src.api.models import AccessRule, HostObject, LogQuery
from src.api.session_manager import SessionManager


class TestCheckPointClient:
    """Test Check Point API client."""
    
    @patch('src.api.checkpoint_client.requests.Session')
    def test_client_initialization(self, mock_session):
        """Test client initialization."""
        with patch('src.api.checkpoint_client.config') as mock_config:
            mock_config.get_checkpoint_config.return_value = {
                "server": "https://test.checkpoint.com",
                "username": "test_user",
                "password": "test_password",
                "domain": "SMC User",
                "timeout": 30,
                "retry_attempts": 3,
                "retry_delay": 2,
                "auto_publish": False
            }
            mock_config.get_security_config.return_value = {
                "tls_verify": True,
                "cert_path": None
            }
            
            client = CheckPointClient()
            
            assert client.base_url == "https://test.checkpoint.com"
            assert client.session_manager is not None
    
    @patch('src.api.checkpoint_client.requests.Session')
    def test_login(self, mock_session):
        """Test login functionality."""
        with patch('src.api.checkpoint_client.config') as mock_config:
            mock_config.get_checkpoint_config.return_value = {
                "server": "https://test.checkpoint.com",
                "username": "test_user",
                "password": "test_password",
                "domain": "SMC User",
                "timeout": 30,
                "retry_attempts": 3,
                "retry_delay": 2,
                "auto_publish": False
            }
            mock_config.get_security_config.return_value = {
                "tls_verify": True,
                "cert_path": None
            }
            
            # Mock successful login response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "sid": "test-session-id",
                "url": "https://test.checkpoint.com",
                "domain": "SMC User",
                "server": "test-server",
                "port": 443,
                "session-timeout": 600
            }
            mock_session.return_value.request.return_value = mock_response
            
            client = CheckPointClient()
            result = client.login()
            
            assert result is True
            assert client.session_manager.session is not None
            assert client.session_manager.session.sid == "test-session-id"
    
    @patch('src.api.checkpoint_client.requests.Session')
    def test_create_access_rule(self, mock_session):
        """Test creating access rule."""
        with patch('src.api.checkpoint_client.config') as mock_config:
            mock_config.get_checkpoint_config.return_value = {
                "server": "https://test.checkpoint.com",
                "username": "test_user",
                "password": "test_password",
                "domain": "SMC User",
                "timeout": 30,
                "retry_attempts": 3,
                "retry_delay": 2,
                "auto_publish": False
            }
            mock_config.get_security_config.return_value = {
                "tls_verify": True,
                "cert_path": None
            }
            
            # Mock successful API response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "uid": "test-rule-uid"
            }
            mock_session.return_value.request.return_value = mock_response
            
            client = CheckPointClient()
            
            # Mock authenticated session
            client.session_manager._session = Mock()
            client.session_manager._session.sid = "test-session-id"
            client.session_manager.is_authenticated = True
            
            rule = AccessRule(
                name="Test Rule",
                source="Internal-Network",
                destination="Any",
                service="HTTPS",
                action="accept",
                layer="Network"
            )
            
            result = client.create_access_rule(rule)
            
            assert result["success"] is True
            assert result["data"]["uid"] == "test-rule-uid"
    
    @patch('src.api.checkpoint_client.requests.Session')
    def test_create_host_object(self, mock_session):
        """Test creating host object."""
        with patch('src.api.checkpoint_client.config') as mock_config:
            mock_config.get_checkpoint_config.return_value = {
                "server": "https://test.checkpoint.com",
                "username": "test_user",
                "password": "test_password",
                "domain": "SMC User",
                "timeout": 30,
                "retry_attempts": 3,
                "retry_delay": 2,
                "auto_publish": False
            }
            mock_config.get_security_config.return_value = {
                "tls_verify": True,
                "cert_path": None
            }
            
            # Mock successful API response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "uid": "test-host-uid"
            }
            mock_session.return_value.request.return_value = mock_response
            
            client = CheckPointClient()
            
            # Mock authenticated session
            client.session_manager._session = Mock()
            client.session_manager._session.sid = "test-session-id"
            client.session_manager.is_authenticated = True
            
            host = HostObject(
                name="TestHost",
                ipv4_address="192.168.1.100"
            )
            
            result = client.create_host_object(host)
            
            assert result["success"] is True
            assert result["data"]["uid"] == "test-host-uid"
    
    @patch('src.api.checkpoint_client.requests.Session')
    def test_query_logs(self, mock_session):
        """Test querying logs."""
        with patch('src.api.checkpoint_client.config') as mock_config:
            mock_config.get_checkpoint_config.return_value = {
                "server": "https://test.checkpoint.com",
                "username": "test_user",
                "password": "test_password",
                "domain": "SMC User",
                "timeout": 30,
                "retry_attempts": 3,
                "retry_delay": 2,
                "auto_publish": False
            }
            mock_config.get_security_config.return_value = {
                "tls_verify": True,
                "cert_path": None
            }
            
            # Mock successful API response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
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
            mock_session.return_value.request.return_value = mock_response
            
            client = CheckPointClient()
            
            # Mock authenticated session
            client.session_manager._session = Mock()
            client.session_manager._session.sid = "test-session-id"
            client.session_manager.is_authenticated = True
            
            log_query = LogQuery(
                query="action:accept",
                limit=10
            )
            
            result = client.query_logs(log_query)
            
            assert result["success"] is True
            assert len(result["data"]["objects"]) == 1
            assert result["data"]["objects"][0]["src"] == "192.168.1.100"


class TestSessionManager:
    """Test session manager."""
    
    def test_session_manager_initialization(self):
        """Test session manager initialization."""
        mock_client = Mock()
        session_manager = SessionManager(mock_client)
        
        assert session_manager.api_client == mock_client
        assert session_manager._session is None
        assert session_manager.is_authenticated is False
    
    def test_is_session_valid(self):
        """Test session validation."""
        mock_client = Mock()
        session_manager = SessionManager(mock_client)
        
        # No session
        assert session_manager._is_session_valid() is False
        
        # Valid session
        session_manager._session = Mock()
        session_manager._last_activity = 1000  # Mock timestamp
        session_manager._session_timeout = 600
        
        with patch('time.time', return_value=1500):  # 500 seconds later
            assert session_manager._is_session_valid() is True
        
        # Expired session
        with patch('time.time', return_value=2000):  # 1000 seconds later
            assert session_manager._is_session_valid() is False
    
    def test_get_session_headers(self):
        """Test getting session headers."""
        mock_client = Mock()
        session_manager = SessionManager(mock_client)
        
        # No session
        with pytest.raises(RuntimeError, match="Not authenticated"):
            session_manager.get_session_headers()
        
        # Valid session
        session_manager._session = Mock()
        session_manager._session.sid = "test-session-id"
        
        headers = session_manager.get_session_headers()
        assert headers == {"X-chkp-sid": "test-session-id"}

