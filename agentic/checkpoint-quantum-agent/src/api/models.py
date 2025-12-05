"""Data models for Check Point API operations."""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from datetime import datetime


class CheckPointResponse(BaseModel):
    """Base response model for Check Point API."""
    success: bool
    data: Optional[Any] = None
    message: Optional[str] = None
    status_code: Optional[int] = None


class AccessRule(BaseModel):
    """Access rule model."""
    uid: str
    name: str
    source: List[str]
    destination: List[str]
    service: List[str]
    action: str
    position: int
    enabled: bool = True
    comments: Optional[str] = None


class HostObject(BaseModel):
    """Host object model."""
    uid: str
    name: str
    ipv4_address: str
    ipv6_address: Optional[str] = None
    comments: Optional[str] = None
    color: str = "black"
    groups: List[str] = Field(default_factory=list)


class NetworkObject(BaseModel):
    """Network object model."""
    uid: str
    name: str
    subnet: str
    mask_length: int
    comments: Optional[str] = None
    color: str = "black"
    groups: List[str] = Field(default_factory=list)


class GroupObject(BaseModel):
    """Group object model."""
    uid: str
    name: str
    members: List[str] = Field(default_factory=list)
    comments: Optional[str] = None
    color: str = "black"


class ServiceObject(BaseModel):
    """Service object model."""
    uid: str
    name: str
    port: Optional[int] = None
    protocol: str
    comments: Optional[str] = None
    color: str = "black"


class ThreatException(BaseModel):
    """Threat exception model."""
    uid: str
    name: str
    protection: str
    action: str
    track: str
    comments: Optional[str] = None
    enabled: bool = True


class LogQuery(BaseModel):
    """Log query model."""
    query: str
    limit: int = 100
    time_range: Optional[str] = None
    source_ip: Optional[str] = None
    destination_ip: Optional[str] = None
    service: Optional[str] = None
    action: Optional[str] = None


class LogEntry(BaseModel):
    """Log entry model."""
    timestamp: datetime
    src: str
    dst: str
    service: str
    action: str
    rule: Optional[str] = None
    message: Optional[str] = None
    severity: Optional[str] = None


class PolicyLayer(BaseModel):
    """Policy layer model."""
    uid: str
    name: str
    comments: Optional[str] = None
    color: str = "black"


class Gateway(BaseModel):
    """Gateway model."""
    uid: str
    name: str
    ipv4_address: str
    ipv6_address: Optional[str] = None
    version: Optional[str] = None
    platform: Optional[str] = None
    status: str = "unknown"


class Task(BaseModel):
    """Task model."""
    task_id: str
    status: str
    progress: int = 0
    message: Optional[str] = None


class PublishRequest(BaseModel):
    """Publish request model."""
    targets: Optional[List[str]] = None
    force: bool = False


class InstallPolicyRequest(BaseModel):
    """Install policy request model."""
    targets: List[str]
    policy_package: str
    access: bool = True
    threat_prevention: bool = True
    desktop_security: bool = False
    qos: bool = False
    identity_awareness: bool = False


# Input models for tools
class AccessRuleInput(BaseModel):
    """Input model for access rule operations."""
    name: str
    source: List[str]
    destination: List[str]
    service: List[str]
    action: str
    position: Optional[int] = None
    enabled: bool = True
    comments: Optional[str] = None


class HostObjectInput(BaseModel):
    """Input model for host object operations."""
    name: str
    ipv4_address: str
    ipv6_address: Optional[str] = None
    comments: Optional[str] = None
    color: str = "black"
    groups: List[str] = Field(default_factory=list)


class NetworkObjectInput(BaseModel):
    """Input model for network object operations."""
    name: str
    subnet: str
    mask_length: int
    comments: Optional[str] = None
    color: str = "black"
    groups: List[str] = Field(default_factory=list)


class GroupObjectInput(BaseModel):
    """Input model for group object operations."""
    name: str
    members: List[str] = Field(default_factory=list)
    comments: Optional[str] = None
    color: str = "black"


class ServiceObjectInput(BaseModel):
    """Input model for service object operations."""
    name: str
    port: Optional[int] = None
    protocol: str
    comments: Optional[str] = None
    color: str = "black"


class ThreatExceptionInput(BaseModel):
    """Input model for threat exception operations."""
    name: str
    protection: str
    action: str
    track: str
    comments: Optional[str] = None
    enabled: bool = True


# Pydantic models for tool schemas
class AccessRuleModel(BaseModel):
    """Pydantic model for access rule tool schema."""
    name: str = Field(..., description="Name of the access rule")
    source: List[str] = Field(..., description="Source objects (hosts, networks, groups)")
    destination: List[str] = Field(..., description="Destination objects (hosts, networks, groups)")
    service: List[str] = Field(..., description="Service objects")
    action: str = Field(..., description="Action (Accept, Drop, Reject)")
    position: Optional[int] = Field(None, description="Position in the rule base")
    enabled: bool = Field(True, description="Whether the rule is enabled")
    comments: Optional[str] = Field(None, description="Comments for the rule")


class HostObjectModel(BaseModel):
    """Pydantic model for host object tool schema."""
    name: str = Field(..., description="Name of the host object")
    ipv4_address: str = Field(..., description="IPv4 address of the host")
    ipv6_address: Optional[str] = Field(None, description="IPv6 address of the host")
    comments: Optional[str] = Field(None, description="Comments for the host object")
    color: str = Field("black", description="Color of the host object")
    groups: List[str] = Field(default_factory=list, description="Groups the host belongs to")



