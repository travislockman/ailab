"""Check Point R82 Management API client."""

import time
import requests
from typing import Any, Dict, List, Optional, Union
from urllib3.exceptions import InsecureRequestWarning
import urllib3

from .models import (
    CheckPointResponse, AccessRule, HostObject, NetworkObject, 
    GroupObject, ServiceObject, ThreatException, LogQuery, LogEntry,
    PolicyLayer, Gateway, Task, PublishRequest, InstallPolicyRequest
)
from .session_manager import SessionManager
from ..utils.logger import get_logger, ActionLogger
from ..utils.config import config
from ..utils.validators import validate_input, AccessRuleModel, HostObjectModel


class CheckPointClient:
    """Check Point R82 Management API client."""
    
    def __init__(self):
        self.logger = get_logger("checkpoint_client")
        self.action_logger = ActionLogger("checkpoint_client")
        
        # Get configuration
        self.config = config.get_checkpoint_config()
        self.security_config = config.get_security_config()
        
        # Setup session manager
        self.session_manager = SessionManager(self)
        
        # Setup requests session
        self.session = requests.Session()
        self.session.verify = self.security_config["tls_verify"]
        
        if not self.security_config["tls_verify"]:
            urllib3.disable_warnings(InsecureRequestWarning)
        
        # Set default headers
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
        
        # Base URL
        self.base_url = self.config["server"]
        if not self.base_url.startswith("http"):
            self.base_url = f"https://{self.base_url}"
        
        self.logger.info("Check Point client initialized", base_url=self.base_url)
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                     headers: Optional[Dict] = None, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make HTTP request to Check Point API."""
        # Smart-1 Cloud URLs already include /web_api in the base URL
        # On-premise setups need /web_api added
        if "/web_api" in self.base_url:
            url = f"{self.base_url}{endpoint}"
        else:
            url = f"{self.base_url}/web_api{endpoint}"
        
        # Add session headers if available
        request_headers = {}
        if self.session_manager.session:
            request_headers.update(self.session_manager.get_session_headers())
        
        if headers:
            request_headers.update(headers)
        
        start_time = time.time()
        
        try:
            self.logger.debug(
                "Making API request",
                method=method,
                url=url,
                endpoint=endpoint
            )
            
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                headers=request_headers,
                params=params,
                timeout=self.config["timeout"]
            )
            
            response_time = time.time() - start_time
            
            # Log API call
            self.action_logger.log_api_call(
                method=method,
                endpoint=endpoint,
                status_code=response.status_code,
                response_time=response_time
            )
            
            # Update session activity
            self.session_manager.update_activity()
            
            # Parse response
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    return {
                        "success": True,
                        "data": response_data,
                        "status_code": response.status_code
                    }
                except ValueError:
                    return {
                        "success": True,
                        "data": response.text,
                        "status_code": response.status_code
                    }
            else:
                error_message = f"HTTP {response.status_code}"
                try:
                    error_data = response.json()
                    if "message" in error_data:
                        error_message = error_data["message"]
                except ValueError:
                    error_message = response.text or error_message
                
                return {
                    "success": False,
                    "message": error_message,
                    "status_code": response.status_code
                }
                
        except requests.exceptions.Timeout:
            self.logger.error("API request timeout", endpoint=endpoint)
            return {
                "success": False,
                "message": "Request timeout",
                "status_code": 408
            }
        except requests.exceptions.ConnectionError:
            self.logger.error("API connection error", endpoint=endpoint)
            return {
                "success": False,
                "message": "Connection error",
                "status_code": 503
            }
        except Exception as e:
            self.logger.error("API request exception", endpoint=endpoint, error=str(e))
            return {
                "success": False,
                "message": str(e),
                "status_code": 500
            }
    
    def _retry_request(self, method: str, endpoint: str, data: Optional[Dict] = None,
                      headers: Optional[Dict] = None, params: Optional[Dict] = None,
                      max_retries: Optional[int] = None) -> Dict[str, Any]:
        """Make request with retry logic."""
        if max_retries is None:
            max_retries = self.config["retry_attempts"]
        
        for attempt in range(max_retries + 1):
            response = self._make_request(method, endpoint, data, headers, params)
            
            if response["success"]:
                return response
            
            # Don't retry on authentication errors
            if response.get("status_code") in [401, 403]:
                self.logger.warning("Authentication error, not retrying")
                break
            
            # Don't retry on client errors (4xx except 408, 429)
            if 400 <= response.get("status_code", 0) < 500:
                if response.get("status_code") not in [408, 429]:
                    break
            
            if attempt < max_retries:
                delay = self.config["retry_delay"] * (2 ** attempt)
                self.logger.warning(
                    "Request failed, retrying",
                    attempt=attempt + 1,
                    max_retries=max_retries,
                    delay=delay,
                    error=response.get("message")
                )
                time.sleep(delay)
            else:
                self.logger.error(
                    "Request failed after all retries",
                    max_retries=max_retries,
                    error=response.get("message")
                )
        
        return response
    
    # Authentication methods
    def login(self) -> bool:
        """Login to Check Point management server."""
        auth_method = self.config.get("auth_method", "smart1_cloud")
        
        if auth_method == "smart1_cloud":
            return self.session_manager.login(
                api_key=self.config.get("api_key"),
                cloud_infra_token=self.config.get("cloud_infra_token")
            )
        elif auth_method == "on_premise":
            return self.session_manager.login(
                username=self.config.get("username"),
                password=self.config.get("password"),
                domain=self.config.get("domain")
            )
        else:
            self.logger.error(f"Unknown authentication method: {auth_method}")
            return False
    
    def logout(self) -> bool:
        """Logout from Check Point management server."""
        return self.session_manager.logout()
    
    def ensure_authenticated(self) -> bool:
        """Ensure authenticated session."""
        return self.session_manager.ensure_authenticated()
    
    # Policy management methods
    def create_access_rule(self, rule: AccessRule) -> Dict[str, Any]:
        """Create a new access rule."""
        self.action_logger.log_action_start("create_access_rule", rule_name=rule.name)
        
        if not self.ensure_authenticated():
            return {"success": False, "message": "Authentication failed"}
        
        # Validate rule data
        try:
            validated_rule = validate_input(rule.dict(), AccessRuleModel)
        except ValueError as e:
            return {"success": False, "message": str(e)}
        
        data = {
            "name": validated_rule["name"],
            "source": validated_rule["source"],
            "destination": validated_rule["destination"],
            "service": validated_rule["service"],
            "action": validated_rule["action"],
            "track": validated_rule["track"],
            "layer": validated_rule["layer"]
        }
        
        if validated_rule.get("position"):
            data["position"] = validated_rule["position"]
        
        if validated_rule.get("comments"):
            data["comments"] = validated_rule["comments"]
        
        response = self._retry_request("POST", "/add-access-rule", data=data)
        
        if response["success"]:
            self.action_logger.log_action_success("create_access_rule", result=response["data"])
        else:
            self.action_logger.log_action_error("create_access_rule", response.get("message", "Unknown error"))
        
        return response
    
    def modify_access_rule(self, rule_uid: str, rule: AccessRule) -> Dict[str, Any]:
        """Modify an existing access rule."""
        self.action_logger.log_action_start("modify_access_rule", rule_uid=rule_uid)
        
        if not self.ensure_authenticated():
            return {"success": False, "message": "Authentication failed"}
        
        data = rule.dict(exclude_unset=True)
        data["uid"] = rule_uid
        
        response = self._retry_request("POST", "/set-access-rule", data=data)
        
        if response["success"]:
            self.action_logger.log_action_success("modify_access_rule", result=response["data"])
        else:
            self.action_logger.log_action_error("modify_access_rule", response.get("message", "Unknown error"))
        
        return response
    
    def delete_access_rule(self, rule_uid: str) -> Dict[str, Any]:
        """Delete an access rule."""
        self.action_logger.log_action_start("delete_access_rule", rule_uid=rule_uid)
        
        if not self.ensure_authenticated():
            return {"success": False, "message": "Authentication failed"}
        
        data = {"uid": rule_uid}
        response = self._retry_request("POST", "/delete-access-rule", data=data)
        
        if response["success"]:
            self.action_logger.log_action_success("delete_access_rule")
        else:
            self.action_logger.log_action_error("delete_access_rule", response.get("message", "Unknown error"))
        
        return response
    
    def show_access_rulebase(self, layer: str, limit: int = 500) -> Dict[str, Any]:
        """Show access rulebase."""
        self.action_logger.log_action_start("show_access_rulebase", layer=layer)
        
        if not self.ensure_authenticated():
            return {"success": False, "message": "Authentication failed"}
        
        data = {"name": layer, "limit": limit}
        response = self._retry_request("POST", "/show-access-rulebase", data=data)
        
        if response["success"]:
            self.action_logger.log_action_success("show_access_rulebase", result_count=len(response["data"].get("objects", [])))
        else:
            self.action_logger.log_action_error("show_access_rulebase", response.get("message", "Unknown error"))
        
        return response
    
    # Object management methods
    def create_host_object(self, host: HostObject) -> Dict[str, Any]:
        """Create a host object."""
        self.action_logger.log_action_start("create_host_object", host_name=host.name)
        
        if not self.ensure_authenticated():
            return {"success": False, "message": "Authentication failed"}
        
        # Validate host data
        try:
            validated_host = validate_input(host.dict(), HostObjectModel)
        except ValueError as e:
            return {"success": False, "message": str(e)}
        
        data = {
            "name": validated_host["name"],
            "ipv4-address": validated_host["ip_address"]
        }
        
        if validated_host.get("comments"):
            data["comments"] = validated_host["comments"]
        
        response = self._retry_request("POST", "/add-host", data=data)
        
        if response["success"]:
            self.action_logger.log_action_success("create_host_object", result=response["data"])
        else:
            self.action_logger.log_action_error("create_host_object", response.get("message", "Unknown error"))
        
        return response
    
    def create_network_object(self, network: NetworkObject) -> Dict[str, Any]:
        """Create a network object."""
        self.action_logger.log_action_start("create_network_object", network_name=network.name)
        
        if not self.ensure_authenticated():
            return {"success": False, "message": "Authentication failed"}
        
        data = {
            "name": network.name,
            "subnet": network.subnet,
            "mask-length": network.mask_length
        }
        
        if network.comments:
            data["comments"] = network.comments
        
        response = self._retry_request("POST", "/add-network", data=data)
        
        if response["success"]:
            self.action_logger.log_action_success("create_network_object", result=response["data"])
        else:
            self.action_logger.log_action_error("create_network_object", response.get("message", "Unknown error"))
        
        return response
    
    def create_group_object(self, group: GroupObject) -> Dict[str, Any]:
        """Create a group object."""
        self.action_logger.log_action_start("create_group_object", group_name=group.name)
        
        if not self.ensure_authenticated():
            return {"success": False, "message": "Authentication failed"}
        
        data = {
            "name": group.name,
            "members": group.members
        }
        
        if group.comments:
            data["comments"] = group.comments
        
        response = self._retry_request("POST", "/add-group", data=data)
        
        if response["success"]:
            self.action_logger.log_action_success("create_group_object", result=response["data"])
        else:
            self.action_logger.log_action_error("create_group_object", response.get("message", "Unknown error"))
        
        return response
    
    def create_service_object(self, service: ServiceObject) -> Dict[str, Any]:
        """Create a service object."""
        self.action_logger.log_action_start("create_service_object", service_name=service.name)
        
        if not self.ensure_authenticated():
            return {"success": False, "message": "Authentication failed"}
        
        data = {
            "name": service.name,
            "port": service.port,
            "protocol": service.protocol
        }
        
        if service.comments:
            data["comments"] = service.comments
        
        response = self._retry_request("POST", f"/add-service-{service.protocol}", data=data)
        
        if response["success"]:
            self.action_logger.log_action_success("create_service_object", result=response["data"])
        else:
            self.action_logger.log_action_error("create_service_object", response.get("message", "Unknown error"))
        
        return response
    
    def delete_object(self, object_uid: str) -> Dict[str, Any]:
        """Delete any object by UID."""
        self.action_logger.log_action_start("delete_object", object_uid=object_uid)
        
        if not self.ensure_authenticated():
            return {"success": False, "message": "Authentication failed"}
        
        data = {"uid": object_uid}
        response = self._retry_request("POST", "/delete-generic-object", data=data)
        
        if response["success"]:
            self.action_logger.log_action_success("delete_object")
        else:
            self.action_logger.log_action_error("delete_object", response.get("message", "Unknown error"))
        
        return response
    
    def show_objects(self, object_type: Optional[str] = None, limit: int = 500) -> Dict[str, Any]:
        """Show objects with optional filtering."""
        self.action_logger.log_action_start("show_objects", object_type=object_type)
        
        if not self.ensure_authenticated():
            return {"success": False, "message": "Authentication failed"}
        
        data = {"limit": limit}
        if object_type:
            data["type"] = object_type
        
        response = self._retry_request("POST", "/show-objects", data=data)
        
        if response["success"]:
            objects = response["data"].get("objects", [])
            self.action_logger.log_action_success("show_objects", result_count=len(objects))
        else:
            self.action_logger.log_action_error("show_objects", response.get("message", "Unknown error"))
        
        return response
    
    # Log query methods
    def query_logs(self, query: LogQuery) -> Dict[str, Any]:
        """Query firewall logs."""
        self.action_logger.log_action_start("query_logs", query=query.query)
        
        if not self.ensure_authenticated():
            return {"success": False, "message": "Authentication failed"}
        
        data = {
            "query": query.query,
            "limit": query.limit,
            "offset": query.offset
        }
        
        if query.time_range:
            data["time-range"] = query.time_range
        if query.source_ip:
            data["source-ip"] = query.source_ip
        if query.destination_ip:
            data["destination-ip"] = query.destination_ip
        if query.service:
            data["service"] = query.service
        if query.action:
            data["action"] = query.action
        
        response = self._retry_request("POST", "/show-logs", data=data)
        
        if response["success"]:
            logs = response["data"].get("objects", [])
            self.action_logger.log_action_success("query_logs", result_count=len(logs))
        else:
            self.action_logger.log_action_error("query_logs", response.get("message", "Unknown error"))
        
        return response
    
    # Threat prevention methods
    def create_threat_exception(self, exception: ThreatException) -> Dict[str, Any]:
        """Create a threat exception."""
        self.action_logger.log_action_start("create_threat_exception", exception_name=exception.name)
        
        if not self.ensure_authenticated():
            return {"success": False, "message": "Authentication failed"}
        
        data = {
            "name": exception.name,
            "layer": exception.layer,
            "rule": exception.rule,
            "exception-type": exception.exception_type,
            "target": exception.target
        }
        
        if exception.comments:
            data["comments"] = exception.comments
        
        response = self._retry_request("POST", "/add-threat-exception", data=data)
        
        if response["success"]:
            self.action_logger.log_action_success("create_threat_exception", result=response["data"])
        else:
            self.action_logger.log_action_error("create_threat_exception", response.get("message", "Unknown error"))
        
        return response
    
    def delete_threat_exception(self, exception_uid: str) -> Dict[str, Any]:
        """Delete a threat exception."""
        self.action_logger.log_action_start("delete_threat_exception", exception_uid=exception_uid)
        
        if not self.ensure_authenticated():
            return {"success": False, "message": "Authentication failed"}
        
        data = {"uid": exception_uid}
        response = self._retry_request("POST", "/delete-threat-exception", data=data)
        
        if response["success"]:
            self.action_logger.log_action_success("delete_threat_exception")
        else:
            self.action_logger.log_action_error("delete_threat_exception", response.get("message", "Unknown error"))
        
        return response
    
    # Policy operations
    def publish_changes(self, targets: Optional[List[str]] = None) -> Dict[str, Any]:
        """Publish changes to Check Point manager."""
        self.action_logger.log_action_start("publish_changes", targets=targets)
        
        if not self.ensure_authenticated():
            return {"success": False, "message": "Authentication failed"}
        
        data = {}
        if targets:
            data["targets"] = targets
        
        response = self._retry_request("POST", "/publish", data=data)
        
        if response["success"]:
            self.action_logger.log_action_success("publish_changes", result=response["data"])
        else:
            self.action_logger.log_action_error("publish_changes", response.get("message", "Unknown error"))
        
        return response
    
    def discard_changes(self) -> Dict[str, Any]:
        """Discard pending changes."""
        self.action_logger.log_action_start("discard_changes")
        
        if not self.ensure_authenticated():
            return {"success": False, "message": "Authentication failed"}
        
        response = self._retry_request("POST", "/discard", data={})
        
        if response["success"]:
            self.action_logger.log_action_success("discard_changes")
        else:
            self.action_logger.log_action_error("discard_changes", response.get("message", "Unknown error"))
        
        return response
    
    def install_policy(self, install_request: InstallPolicyRequest) -> Dict[str, Any]:
        """Install policy to gateways."""
        self.action_logger.log_action_start("install_policy", targets=install_request.targets)
        
        if not self.ensure_authenticated():
            return {"success": False, "message": "Authentication failed"}
        
        data = install_request.dict()
        response = self._retry_request("POST", "/install-policy", data=data)
        
        if response["success"]:
            self.action_logger.log_action_success("install_policy", result=response["data"])
        else:
            self.action_logger.log_action_error("install_policy", response.get("message", "Unknown error"))
        
        return response
    
    def show_gateways(self) -> Dict[str, Any]:
        """Show security gateways."""
        self.action_logger.log_action_start("show_gateways")
        
        if not self.ensure_authenticated():
            return {"success": False, "message": "Authentication failed"}
        
        response = self._retry_request("POST", "/show-gateways-and-servers", data={})
        
        if response["success"]:
            gateways = response["data"].get("objects", [])
            self.action_logger.log_action_success("show_gateways", result_count=len(gateways))
        else:
            self.action_logger.log_action_error("show_gateways", response.get("message", "Unknown error"))
        
        return response
    
    def get_session_status(self) -> Dict[str, Any]:
        """Get current session status."""
        if not self.session_manager.session:
            return {"success": False, "message": "No active session"}
        
        return {
            "success": True,
            "data": {
                "authenticated": self.session_manager.is_authenticated,
                "server": self.session_manager.session.server,
                "domain": self.session_manager.session.domain,
                "session_id": self.session_manager.session.sid
            }
        }

