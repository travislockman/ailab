"""Session manager for Check Point API authentication."""

import time
import requests
from typing import Optional, Dict, Any
from dataclasses import dataclass

from ..utils.logger import get_logger


@dataclass
class Session:
    """Check Point API session data."""
    sid: str
    url: str
    domain: str
    server: str
    port: int
    session_timeout: int
    last_activity: float


class SessionManager:
    """Manages Check Point API authentication sessions."""
    
    def __init__(self, api_client):
        """Initialize session manager."""
        self.api_client = api_client
        self.logger = get_logger("session_manager")
        self._session: Optional[Session] = None
        self._last_activity: float = 0
        self._session_timeout: int = 3600  # 1 hour default
        self.is_authenticated: bool = False
    
    def login(self, username: str = None, password: str = None, domain: str = None, 
              api_key: str = None, cloud_infra_token: str = None) -> bool:
        """Login to Check Point API using the configured authentication method."""
        try:
            auth_method = self.api_client.config.get("auth_method", "smart1_cloud")
            
            if auth_method == "smart1_cloud":
                return self._login_smart1_cloud(api_key, cloud_infra_token)
            elif auth_method == "on_premise":
                return self._login_on_premise(username, password, domain)
            else:
                self.logger.error(f"Unknown authentication method: {auth_method}")
                return False
                
        except Exception as e:
            self.logger.error(f"Login failed: {str(e)}")
            return False
    
    def _login_smart1_cloud(self, api_key: str, cloud_infra_token: str = None) -> bool:
        """Login using Smart-1 Cloud API key authentication."""
        try:
            self.logger.info("Attempting Smart-1 Cloud authentication")
            
            if not api_key:
                self.logger.error("API key is required for Smart-1 Cloud authentication")
                return False
            
            # Smart-1 Cloud authentication requires calling /login with api-key in the body
            # This returns a session ID (sid) which is then used for all subsequent requests
            
            login_payload = {
                'api-key': api_key,
                'session-timeout': 3600
            }
            
            # Add cloud infra token if provided
            headers = {}
            if cloud_infra_token and cloud_infra_token != 'your_cloud_infra_token_here':
                headers['X-chkp-cloud-infra-token'] = cloud_infra_token
            
            # Make login request
            response = self.api_client.session.post(
                f"{self.api_client.base_url}/login",
                json=login_payload,
                headers=headers if headers else None,
                timeout=self.api_client.config.get("timeout", 30),
                verify=False  # Smart-1 Cloud may use self-signed certs
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract session ID from response
                sid = data.get('sid')
                if not sid:
                    self.logger.error("No session ID in login response")
                    return False
                
                # Create session object with the returned session ID
                self._session = Session(
                    sid=sid,
                    url=data.get('url', self.api_client.base_url),
                    domain=data.get('domain', 'Smart-1 Cloud'),
                    server=data.get('api-server-name', 'Smart-1 Cloud'),
                    port=data.get('port', 443),
                    session_timeout=data.get('session-timeout', 3600),
                    last_activity=time.time()
                )
                
                self._last_activity = time.time()
                self._session_timeout = self._session.session_timeout
                self.is_authenticated = True
                
                self.logger.info("Smart-1 Cloud authentication successful", 
                               sid=sid[:10] + "...",
                               domain=self._session.domain)
                return True
            else:
                self.logger.error(f"Smart-1 Cloud authentication failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Smart-1 Cloud authentication error: {str(e)}")
            return False
    
    def _login_on_premise(self, username: str, password: str, domain: str) -> bool:
        """Login using traditional on-premise authentication."""
        try:
            self.logger.info("Attempting on-premise authentication")
            
            login_data = {
                "user": username,
                "password": password,
                "domain": domain
            }
            
            response = self.api_client.session.post(
                f"{self.api_client.base_url}/web_api/login",
                json=login_data,
                timeout=self.api_client.config.get("timeout", 30)
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Create session object
                self._session = Session(
                    sid=data.get("sid", ""),
                    url=data.get("url", self.api_client.base_url),
                    domain=data.get("domain", domain),
                    server=data.get("server", ""),
                    port=data.get("port", 443),
                    session_timeout=data.get("session-timeout", 3600),
                    last_activity=time.time()
                )
                
                self._last_activity = time.time()
                self._session_timeout = self._session.session_timeout
                self.is_authenticated = True
                
                self.logger.info("On-premise authentication successful")
                return True
            else:
                self.logger.error(f"On-premise authentication failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"On-premise authentication error: {str(e)}")
            return False
    
    def logout(self) -> bool:
        """Logout from Check Point API."""
        try:
            if not self._session:
                self.logger.warning("No active session to logout")
                return True
            
            # Make logout request
            response = self.api_client.session.post(
                f"{self.api_client.base_url}/web_api/logout",
                headers=self.get_session_headers(),
                timeout=self.api_client.config.get("timeout", 30)
            )
            
            if response.status_code == 200:
                self.logger.info("Logout successful")
            else:
                self.logger.warning(f"Logout request failed: {response.status_code}")
            
            # Clear session data
            self._session = None
            self.is_authenticated = False
            self._last_activity = 0
            
            return True
            
        except Exception as e:
            self.logger.error(f"Logout error: {str(e)}")
            return False
    
    def get_session_headers(self) -> Dict[str, str]:
        """Get session headers for API requests."""
        if not self._session:
            raise RuntimeError("Not authenticated - no active session")
        
        return {"X-chkp-sid": self._session.sid}
    
    def _is_session_valid(self) -> bool:
        """Check if current session is still valid."""
        if not self._session:
            return False
        
        current_time = time.time()
        time_since_activity = current_time - self._last_activity
        
        return time_since_activity < self._session_timeout
    
    def ensure_authenticated(self) -> bool:
        """Ensure we have a valid authenticated session."""
        if self._is_session_valid():
            return True
        
        # Session expired or doesn't exist, try to re-authenticate
        self.logger.info("Session expired or invalid, re-authenticating")
        
        # Get authentication parameters based on method
        auth_method = self.api_client.config.get("auth_method", "smart1_cloud")
        
        if auth_method == "smart1_cloud":
            api_key = self.api_client.config.get("api_key")
            cloud_infra_token = self.api_client.config.get("cloud_infra_token")
            return self._login_smart1_cloud(api_key, cloud_infra_token)
        elif auth_method == "on_premise":
            username = self.api_client.config.get("username")
            password = self.api_client.config.get("password")
            domain = self.api_client.config.get("domain")
            return self._login_on_premise(username, password, domain)
        else:
            self.logger.error(f"Unknown authentication method: {auth_method}")
            return False
    
    @property
    def session(self) -> Optional[Session]:
        """Get current session object."""
        return self._session
    
    def update_activity(self) -> None:
        """Update last activity timestamp."""
        self._last_activity = time.time()
