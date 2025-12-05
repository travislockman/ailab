"""Configuration management for the Check Point Quantum Agent."""

import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv


class Config:
    """Configuration manager for the Check Point Quantum Agent."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration from file and environment variables."""
        # Load environment variables
        load_dotenv()
        
        # Load YAML configuration
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config" / "config.yaml"
        
        with open(config_path, 'r') as f:
            self._config = yaml.safe_load(f)
        
        # Override with environment variables
        self._load_env_overrides()
    
    def _load_env_overrides(self) -> None:
        """Override configuration with environment variables."""
        env_mappings = {
            'CHECKPOINT_SERVER': 'api.server',
            'CHECKPOINT_API_KEY': 'api.api_key',
            'CHECKPOINT_CLOUD_INFRA_TOKEN': 'api.cloud_infra_token',
            'CHECKPOINT_USERNAME': 'api.username',
            'CHECKPOINT_PASSWORD': 'api.password',
            'CHECKPOINT_DOMAIN': 'api.domain',
            'CHECKPOINT_AUTH_METHOD': 'api.auth_method',
            'OPENAI_API_KEY': 'openai.api_key',
            'AGENT_NAME': 'agent.name',
            'LOG_LEVEL': 'logging.level',
            'LOG_FORMAT': 'logging.format',
            'MCP_SERVER_ENABLED': 'mcp.enabled',
            'MCP_SERVER_PATH': 'mcp.server_path',
            'K8S_NAMESPACE': 'kubernetes.namespace',
            'API_TIMEOUT': 'api.timeout',
            'API_RETRY_ATTEMPTS': 'api.retry_attempts',
            'API_RETRY_DELAY': 'api.retry_delay',
            'AUTO_PUBLISH': 'api.auto_publish',
            'TLS_VERIFY': 'security.tls_verify',
            'CERT_PATH': 'security.cert_path',
        }
        
        for env_var, config_path in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                self._set_nested_value(config_path, value)
    
    def _set_nested_value(self, path: str, value: Any) -> None:
        """Set a nested configuration value using dot notation."""
        keys = path.split('.')
        current = self._config
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # Convert string values to appropriate types
        if isinstance(value, str):
            if value.lower() in ('true', 'false'):
                value = value.lower() == 'true'
            elif value.isdigit():
                value = int(value)
            elif value.replace('.', '').isdigit():
                value = float(value)
        
        current[keys[-1]] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation."""
        keys = key.split('.')
        current = self._config
        
        try:
            for key in keys:
                current = current[key]
            return current
        except (KeyError, TypeError):
            return default
    
    def get_checkpoint_config(self) -> Dict[str, Any]:
        """Get Check Point API configuration."""
        return {
            'server': self.get('api.server'),
            'api_key': self.get('api.api_key'),
            'cloud_infra_token': self.get('api.cloud_infra_token'),
            'username': self.get('api.username'),
            'password': self.get('api.password'),
            'domain': self.get('api.domain', 'SMC User'),
            'auth_method': self.get('api.auth_method', 'smart1_cloud'),
            'timeout': self.get('api.timeout', 30),
            'retry_attempts': self.get('api.retry_attempts', 3),
            'retry_delay': self.get('api.retry_delay', 2),
            'auto_publish': self.get('api.auto_publish', False),
        }
    
    def get_openai_config(self) -> Dict[str, Any]:
        """Get OpenAI configuration."""
        return {
            'api_key': self.get('openai.api_key'),
            'model': self.get('openai.model', 'gpt-4-turbo-preview'),
            'temperature': self.get('openai.temperature', 0.1),
        }
    
    def get_agent_config(self) -> Dict[str, Any]:
        """Get agent configuration."""
        return {
            'name': self.get('agent.name', 'Check Point Quantum Agent'),
            'max_iterations': self.get('agent.max_iterations', 10),
            'verbose': self.get('agent.verbose', True),
            'memory': self.get('agent.memory', True),
        }
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration."""
        return {
            'level': self.get('logging.level', 'INFO'),
            'format': self.get('logging.format', 'json'),
            'file': self.get('logging.file'),
            'console': self.get('logging.console', True),
        }
    
    def get_mcp_config(self) -> Dict[str, Any]:
        """Get MCP server configuration."""
        return {
            'enabled': self.get('mcp.enabled', True),
            'server_path': self.get('mcp.server_path'),
            'timeout': self.get('mcp.timeout', 30),
        }
    
    def get_security_config(self) -> Dict[str, Any]:
        """Get security configuration."""
        return {
            'tls_verify': self.get('security.tls_verify', True),
            'cert_path': self.get('security.cert_path'),
        }


# Global configuration instance
config = Config()

