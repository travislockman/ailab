"""Input validation utilities for the Check Point Quantum Agent."""

import re
import ipaddress
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, validator, Field


class IPAddressValidator:
    """Validator for IP addresses and networks."""
    
    @staticmethod
    def validate_ip(ip: str) -> bool:
        """Validate if string is a valid IP address."""
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_network(network: str) -> bool:
        """Validate if string is a valid network CIDR."""
        try:
            ipaddress.ip_network(network, strict=False)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_ip_or_network(value: str) -> bool:
        """Validate if string is either an IP address or network."""
        return (IPAddressValidator.validate_ip(value) or 
                IPAddressValidator.validate_network(value))


class PortValidator:
    """Validator for port numbers and ranges."""
    
    @staticmethod
    def validate_port(port: Union[int, str]) -> bool:
        """Validate if value is a valid port number."""
        try:
            port_num = int(port)
            return 1 <= port_num <= 65535
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_port_range(port_range: str) -> bool:
        """Validate if string is a valid port range (e.g., '80-443')."""
        try:
            if '-' in port_range:
                start, end = port_range.split('-', 1)
                return (PortValidator.validate_port(start) and 
                       PortValidator.validate_port(end) and 
                       int(start) <= int(end))
            else:
                return PortValidator.validate_port(port_range)
        except (ValueError, AttributeError):
            return False


class ObjectNameValidator:
    """Validator for Check Point object names."""
    
    @staticmethod
    def validate_name(name: str) -> bool:
        """Validate Check Point object name format."""
        if not name or len(name) > 63:
            return False
        
        # Check for valid characters (alphanumeric, hyphens, underscores)
        pattern = r'^[a-zA-Z0-9_-]+$'
        return bool(re.match(pattern, name))


class RuleActionValidator:
    """Validator for firewall rule actions."""
    
    VALID_ACTIONS = {
        'accept', 'drop', 'reject', 'inspect', 'apply-layer',
        'allow', 'deny', 'block'
    }
    
    @staticmethod
    def validate_action(action: str) -> bool:
        """Validate firewall rule action."""
        return action.lower() in RuleActionValidator.VALID_ACTIONS


class TrackActionValidator:
    """Validator for firewall rule track actions."""
    
    VALID_TRACK_ACTIONS = {
        'none', 'log', 'alert', 'mail', 'snmp', 'user-alert',
        'popup', 'user-alert-1', 'user-alert-2'
    }
    
    @staticmethod
    def validate_track(track: str) -> bool:
        """Validate firewall rule track action."""
        return track.lower() in TrackActionValidator.VALID_TRACK_ACTIONS


# Pydantic models for validation
class IPAddressModel(BaseModel):
    """Model for IP address validation."""
    ip: str = Field(..., description="IP address")
    
    @validator('ip')
    def validate_ip(cls, v):
        if not IPAddressValidator.validate_ip(v):
            raise ValueError(f"Invalid IP address: {v}")
        return v


class NetworkModel(BaseModel):
    """Model for network CIDR validation."""
    network: str = Field(..., description="Network CIDR")
    
    @validator('network')
    def validate_network(cls, v):
        if not IPAddressValidator.validate_network(v):
            raise ValueError(f"Invalid network CIDR: {v}")
        return v


class PortModel(BaseModel):
    """Model for port validation."""
    port: Union[int, str] = Field(..., description="Port number")
    
    @validator('port')
    def validate_port(cls, v):
        if not PortValidator.validate_port(v):
            raise ValueError(f"Invalid port: {v}")
        return int(v)


class PortRangeModel(BaseModel):
    """Model for port range validation."""
    port_range: str = Field(..., description="Port range (e.g., '80-443')")
    
    @validator('port_range')
    def validate_port_range(cls, v):
        if not PortValidator.validate_port_range(v):
            raise ValueError(f"Invalid port range: {v}")
        return v


class ObjectNameModel(BaseModel):
    """Model for Check Point object name validation."""
    name: str = Field(..., description="Object name")
    
    @validator('name')
    def validate_name(cls, v):
        if not ObjectNameValidator.validate_name(v):
            raise ValueError(f"Invalid object name: {v}")
        return v


class RuleActionModel(BaseModel):
    """Model for firewall rule action validation."""
    action: str = Field(..., description="Rule action")
    
    @validator('action')
    def validate_action(cls, v):
        if not RuleActionValidator.validate_action(v):
            raise ValueError(f"Invalid rule action: {v}")
        return v.lower()


class TrackActionModel(BaseModel):
    """Model for firewall rule track action validation."""
    track: str = Field(..., description="Track action")
    
    @validator('track')
    def validate_track(cls, v):
        if not TrackActionValidator.validate_track(v):
            raise ValueError(f"Invalid track action: {v}")
        return v.lower()


class AccessRuleModel(BaseModel):
    """Model for access rule validation."""
    name: str = Field(..., description="Rule name")
    source: str = Field(..., description="Source object/network")
    destination: str = Field(..., description="Destination object/network")
    service: str = Field(..., description="Service object")
    action: str = Field(..., description="Rule action")
    track: str = Field(default="log", description="Track action")
    layer: str = Field(..., description="Policy layer")
    position: Optional[int] = Field(default=None, description="Rule position")
    
    @validator('name')
    def validate_name(cls, v):
        if not ObjectNameValidator.validate_name(v):
            raise ValueError(f"Invalid rule name: {v}")
        return v
    
    @validator('action')
    def validate_action(cls, v):
        if not RuleActionValidator.validate_action(v):
            raise ValueError(f"Invalid rule action: {v}")
        return v.lower()
    
    @validator('track')
    def validate_track(cls, v):
        if not TrackActionValidator.validate_track(v):
            raise ValueError(f"Invalid track action: {v}")
        return v.lower()


class HostObjectModel(BaseModel):
    """Model for host object validation."""
    name: str = Field(..., description="Host name")
    ip_address: str = Field(..., description="IP address")
    comments: Optional[str] = Field(default=None, description="Comments")
    
    @validator('name')
    def validate_name(cls, v):
        if not ObjectNameValidator.validate_name(v):
            raise ValueError(f"Invalid host name: {v}")
        return v
    
    @validator('ip_address')
    def validate_ip_address(cls, v):
        if not IPAddressValidator.validate_ip(v):
            raise ValueError(f"Invalid IP address: {v}")
        return v


class NetworkObjectModel(BaseModel):
    """Model for network object validation."""
    name: str = Field(..., description="Network name")
    subnet: str = Field(..., description="Network subnet")
    mask_length: int = Field(..., description="Subnet mask length")
    comments: Optional[str] = Field(default=None, description="Comments")
    
    @validator('name')
    def validate_name(cls, v):
        if not ObjectNameValidator.validate_name(v):
            raise ValueError(f"Invalid network name: {v}")
        return v
    
    @validator('subnet')
    def validate_subnet(cls, v):
        if not IPAddressValidator.validate_ip(v):
            raise ValueError(f"Invalid subnet: {v}")
        return v
    
    @validator('mask_length')
    def validate_mask_length(cls, v):
        if not 0 <= v <= 32:
            raise ValueError(f"Invalid mask length: {v}")
        return v


class ServiceObjectModel(BaseModel):
    """Model for service object validation."""
    name: str = Field(..., description="Service name")
    port: Union[int, str] = Field(..., description="Port number")
    protocol: str = Field(..., description="Protocol (tcp/udp)")
    comments: Optional[str] = Field(default=None, description="Comments")
    
    @validator('name')
    def validate_name(cls, v):
        if not ObjectNameValidator.validate_name(v):
            raise ValueError(f"Invalid service name: {v}")
        return v
    
    @validator('port')
    def validate_port(cls, v):
        if not PortValidator.validate_port(v):
            raise ValueError(f"Invalid port: {v}")
        return int(v)
    
    @validator('protocol')
    def validate_protocol(cls, v):
        if v.lower() not in ['tcp', 'udp']:
            raise ValueError(f"Invalid protocol: {v}")
        return v.lower()


def validate_input(data: Dict[str, Any], model_class: BaseModel) -> Dict[str, Any]:
    """Validate input data using a Pydantic model."""
    try:
        validated_data = model_class(**data)
        return validated_data.dict()
    except Exception as e:
        raise ValueError(f"Validation error: {str(e)}")


def sanitize_input(value: str) -> str:
    """Sanitize input to prevent injection attacks."""
    if not isinstance(value, str):
        return str(value)
    
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\';\\]', '', value)
    
    # Limit length
    if len(sanitized) > 1000:
        sanitized = sanitized[:1000]
    
    return sanitized.strip()

