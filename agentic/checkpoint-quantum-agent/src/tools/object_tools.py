"""Object management tools for network objects, hosts, networks, groups, and services."""

from typing import Any, Dict, List, Optional, Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

from ..api.checkpoint_client import CheckPointClient
from ..api.models import HostObject, NetworkObject, GroupObject, ServiceObject
from ..utils.logger import get_logger


class CreateHostObjectInput(BaseModel):
    """Input for creating a host object."""
    name: str = Field(..., description="Host object name")
    ip_address: str = Field(..., description="IPv4 address")
    comments: Optional[str] = Field(default=None, description="Comments")
    color: str = Field(default="black", description="Object color")


class CreateNetworkObjectInput(BaseModel):
    """Input for creating a network object."""
    name: str = Field(..., description="Network object name")
    subnet: str = Field(..., description="Network subnet (e.g., 192.168.1.0)")
    mask_length: int = Field(..., description="Subnet mask length (e.g., 24)")
    comments: Optional[str] = Field(default=None, description="Comments")
    color: str = Field(default="black", description="Object color")


class CreateGroupObjectInput(BaseModel):
    """Input for creating a group object."""
    name: str = Field(..., description="Group object name")
    members: List[str] = Field(..., description="List of member object names")
    comments: Optional[str] = Field(default=None, description="Comments")
    color: str = Field(default="black", description="Object color")


class CreateServiceObjectInput(BaseModel):
    """Input for creating a service object."""
    name: str = Field(..., description="Service object name")
    port: int = Field(..., description="Port number")
    protocol: str = Field(..., description="Protocol (tcp or udp)")
    comments: Optional[str] = Field(default=None, description="Comments")
    color: str = Field(default="black", description="Object color")


class DeleteObjectInput(BaseModel):
    """Input for deleting an object."""
    object_uid: str = Field(..., description="Object UID to delete")


class ModifyObjectInput(BaseModel):
    """Input for modifying an object."""
    object_uid: str = Field(..., description="Object UID to modify")
    name: Optional[str] = Field(default=None, description="New object name")
    comments: Optional[str] = Field(default=None, description="New comments")
    color: Optional[str] = Field(default=None, description="New color")


class ShowObjectsInput(BaseModel):
    """Input for showing objects."""
    object_type: Optional[str] = Field(default=None, description="Object type filter (host, network, group, service)")
    limit: int = Field(default=500, description="Maximum number of objects to show")


class CreateHostObjectTool(BaseTool):
    """Tool for creating host objects."""
    
    name: str = "create_host_object"
    description: str = """
    Create a new host object in Check Point firewall.
    Host objects represent individual IP addresses and can be used in access rules.
    """
    args_schema: Type[BaseModel] = CreateHostObjectInput
    
    def __init__(self):
        super().__init__()
        self._logger = get_logger("create_host_object_tool")
        self._client = CheckPointClient()
    
    def _run(self, **kwargs) -> str:
        """Create a host object."""
        try:
            # Validate input
            input_data = CreateHostObjectInput(**kwargs)
            
            # Create host object
            host = HostObject(
                name=input_data.name,
                ipv4_address=input_data.ip_address,
                comments=input_data.comments,
                color=input_data.color
            )
            
            # Create the host
            response = self._client.create_host_object(host)
            
            if response["success"]:
                host_data = response["data"]
                return (
                    f"✅ Successfully created host object '{input_data.name}'\n"
                    f"Host UID: {host_data.get('uid', 'N/A')}\n"
                    f"IP Address: {input_data.ip_address}\n"
                    f"Comments: {input_data.comments or 'None'}"
                )
            else:
                return f"❌ Failed to create host object: {response.get('message', 'Unknown error')}"
                
        except Exception as e:
            self._logger.error("Error in create_host_object", error=str(e))
            return f"❌ Error creating host object: {str(e)}"


class CreateNetworkObjectTool(BaseTool):
    """Tool for creating network objects."""
    
    name: str = "create_network_object"
    description: str = """
    Create a new network object in Check Point firewall.
    Network objects represent IP subnets and can be used in access rules.
    """
    args_schema: Type[BaseModel] = CreateNetworkObjectInput
    
    def __init__(self):
        super().__init__()
        self._logger = get_logger("create_network_object_tool")
        self._client = CheckPointClient()
    
    def _run(self, **kwargs) -> str:
        """Create a network object."""
        try:
            # Validate input
            input_data = CreateNetworkObjectInput(**kwargs)
            
            # Create network object
            network = NetworkObject(
                name=input_data.name,
                subnet=input_data.subnet,
                mask_length=input_data.mask_length,
                comments=input_data.comments,
                color=input_data.color
            )
            
            # Create the network
            response = self._client.create_network_object(network)
            
            if response["success"]:
                network_data = response["data"]
                return (
                    f"✅ Successfully created network object '{input_data.name}'\n"
                    f"Network UID: {network_data.get('uid', 'N/A')}\n"
                    f"Subnet: {input_data.subnet}/{input_data.mask_length}\n"
                    f"Comments: {input_data.comments or 'None'}"
                )
            else:
                return f"❌ Failed to create network object: {response.get('message', 'Unknown error')}"
                
        except Exception as e:
            self._logger.error("Error in create_network_object", error=str(e))
            return f"❌ Error creating network object: {str(e)}"


class CreateGroupObjectTool(BaseTool):
    """Tool for creating group objects."""
    
    name: str = "create_group_object"
    description: str = """
    Create a new group object in Check Point firewall.
    Group objects contain multiple member objects and can be used in access rules.
    """
    args_schema: Type[BaseModel] = CreateGroupObjectInput
    
    def __init__(self):
        super().__init__()
        self._logger = get_logger("create_group_object_tool")
        self._client = CheckPointClient()
    
    def _run(self, **kwargs) -> str:
        """Create a group object."""
        try:
            # Validate input
            input_data = CreateGroupObjectInput(**kwargs)
            
            # Create group object
            group = GroupObject(
                name=input_data.name,
                members=input_data.members,
                comments=input_data.comments,
                color=input_data.color
            )
            
            # Create the group
            response = self._client.create_group_object(group)
            
            if response["success"]:
                group_data = response["data"]
                return (
                    f"✅ Successfully created group object '{input_data.name}'\n"
                    f"Group UID: {group_data.get('uid', 'N/A')}\n"
                    f"Members: {', '.join(input_data.members)}\n"
                    f"Comments: {input_data.comments or 'None'}"
                )
            else:
                return f"❌ Failed to create group object: {response.get('message', 'Unknown error')}"
                
        except Exception as e:
            self._logger.error("Error in create_group_object", error=str(e))
            return f"❌ Error creating group object: {str(e)}"


class CreateServiceObjectTool(BaseTool):
    """Tool for creating service objects."""
    
    name: str = "create_service_object"
    description: str = """
    Create a new service object in Check Point firewall.
    Service objects represent TCP or UDP ports and can be used in access rules.
    """
    args_schema: Type[BaseModel] = CreateServiceObjectInput
    
    def __init__(self):
        super().__init__()
        self._logger = get_logger("create_service_object_tool")
        self._client = CheckPointClient()
    
    def _run(self, **kwargs) -> str:
        """Create a service object."""
        try:
            # Validate input
            input_data = CreateServiceObjectInput(**kwargs)
            
            # Create service object
            service = ServiceObject(
                name=input_data.name,
                port=input_data.port,
                protocol=input_data.protocol,
                comments=input_data.comments,
                color=input_data.color
            )
            
            # Create the service
            response = self._client.create_service_object(service)
            
            if response["success"]:
                service_data = response["data"]
                return (
                    f"✅ Successfully created service object '{input_data.name}'\n"
                    f"Service UID: {service_data.get('uid', 'N/A')}\n"
                    f"Port: {input_data.port}/{input_data.protocol.upper()}\n"
                    f"Comments: {input_data.comments or 'None'}"
                )
            else:
                return f"❌ Failed to create service object: {response.get('message', 'Unknown error')}"
                
        except Exception as e:
            self._logger.error("Error in create_service_object", error=str(e))
            return f"❌ Error creating service object: {str(e)}"


class DeleteObjectTool(BaseTool):
    """Tool for deleting objects."""
    
    name: str = "delete_object"
    description: str = """
    Delete any object from Check Point firewall by its UID.
    Can delete hosts, networks, groups, services, and other object types.
    """
    args_schema: Type[BaseModel] = DeleteObjectInput
    
    def __init__(self):
        super().__init__()
        self._logger = get_logger("delete_object_tool")
        self._client = CheckPointClient()
    
    def _run(self, **kwargs) -> str:
        """Delete an object."""
        try:
            # Validate input
            input_data = DeleteObjectInput(**kwargs)
            
            # Delete the object
            response = self._client.delete_object(input_data.object_uid)
            
            if response["success"]:
                return f"✅ Successfully deleted object (UID: {input_data.object_uid})"
            else:
                return f"❌ Failed to delete object: {response.get('message', 'Unknown error')}"
                
        except Exception as e:
            self._logger.error("Error in delete_object", error=str(e))
            return f"❌ Error deleting object: {str(e)}"


class ModifyObjectTool(BaseTool):
    """Tool for modifying object properties."""
    
    name: str = "modify_object"
    description: str = """
    Modify properties of existing objects in Check Point firewall.
    Can update object name, comments, and color.
    """
    args_schema: Type[BaseModel] = ModifyObjectInput
    
    def __init__(self):
        super().__init__()
        self._logger = get_logger("modify_object_tool")
        self._client = CheckPointClient()
    
    def _run(self, **kwargs) -> str:
        """Modify an object."""
        try:
            # Validate input
            input_data = ModifyObjectInput(**kwargs)
            
            # Prepare modification data
            modify_data = {"uid": input_data.object_uid}
            if input_data.name is not None:
                modify_data["name"] = input_data.name
            if input_data.comments is not None:
                modify_data["comments"] = input_data.comments
            if input_data.color is not None:
                modify_data["color"] = input_data.color
            
            # Modify the object
            response = self._client._retry_request(
                "POST", "/set-generic-object", data=modify_data
            )
            
            if response["success"]:
                updated_fields = [k for k in modify_data.keys() if k != "uid"]
                return (
                    f"✅ Successfully modified object\n"
                    f"Object UID: {input_data.object_uid}\n"
                    f"Updated fields: {', '.join(updated_fields)}"
                )
            else:
                return f"❌ Failed to modify object: {response.get('message', 'Unknown error')}"
                
        except Exception as e:
            self._logger.error("Error in modify_object", error=str(e))
            return f"❌ Error modifying object: {str(e)}"


class ShowObjectsTool(BaseTool):
    """Tool for displaying objects."""
    
    name: str = "show_objects"
    description: str = """
    Display objects from Check Point firewall with optional filtering.
    Can show all objects or filter by type (host, network, group, service).
    """
    args_schema: Type[BaseModel] = ShowObjectsInput
    
    def __init__(self):
        super().__init__()
        self._logger = get_logger("show_objects_tool")
        self._client = CheckPointClient()
    
    def _run(self, **kwargs) -> str:
        """Show objects."""
        try:
            # Validate input
            input_data = ShowObjectsInput(**kwargs)
            
            # Get objects
            response = self._client.show_objects(input_data.object_type, input_data.limit)
            
            if response["success"]:
                objects = response["data"].get("objects", [])
                
                if not objects:
                    filter_text = f" of type '{input_data.object_type}'" if input_data.object_type else ""
                    return f"No objects found{filter_text}."
                
                # Group objects by type
                objects_by_type = {}
                for obj in objects:
                    obj_type = obj.get("type", "unknown")
                    if obj_type not in objects_by_type:
                        objects_by_type[obj_type] = []
                    objects_by_type[obj_type].append(obj)
                
                # Format results
                result_lines = [f"Check Point Objects ({len(objects)} total):"]
                result_lines.append("")
                
                for obj_type, type_objects in objects_by_type.items():
                    result_lines.append(f"{obj_type.upper()} OBJECTS ({len(type_objects)}):")
                    for obj in type_objects:
                        result_lines.append(f"  • {obj.get('name', 'Unnamed')} (UID: {obj.get('uid', 'N/A')})")
                        if obj.get('ipv4-address'):
                            result_lines.append(f"    IP: {obj.get('ipv4-address')}")
                        elif obj.get('subnet') and obj.get('mask-length'):
                            result_lines.append(f"    Network: {obj.get('subnet')}/{obj.get('mask-length')}")
                        elif obj.get('port') and obj.get('protocol'):
                            result_lines.append(f"    Port: {obj.get('port')}/{obj.get('protocol').upper()}")
                        elif obj.get('members'):
                            result_lines.append(f"    Members: {', '.join(obj.get('members', []))}")
                        if obj.get('comments'):
                            result_lines.append(f"    Comments: {obj.get('comments')}")
                    result_lines.append("")
                
                return "\n".join(result_lines)
            else:
                return f"❌ Failed to show objects: {response.get('message', 'Unknown error')}"
                
        except Exception as e:
            self._logger.error("Error in show_objects", error=str(e))
            return f"❌ Error showing objects: {str(e)}"

