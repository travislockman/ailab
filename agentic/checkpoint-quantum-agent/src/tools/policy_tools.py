"""Policy management tools for firewall access rules and policy layers."""

from typing import Any, Dict, List, Optional, Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

from ..api.checkpoint_client import CheckPointClient
from ..api.models import AccessRule, PolicyLayer
from ..utils.logger import get_logger


class CreateAccessRuleInput(BaseModel):
    """Input for creating an access rule."""
    name: str = Field(..., description="Rule name")
    source: str = Field(..., description="Source object/network")
    destination: str = Field(..., description="Destination object/network")
    service: str = Field(..., description="Service object")
    action: str = Field(..., description="Rule action (accept, drop, reject)")
    track: str = Field(default="log", description="Track action (log, alert, none)")
    layer: str = Field(..., description="Policy layer name")
    position: Optional[int] = Field(default=None, description="Rule position (1-based)")
    comments: Optional[str] = Field(default=None, description="Rule comments")


class ModifyAccessRuleInput(BaseModel):
    """Input for modifying an access rule."""
    rule_uid: str = Field(..., description="Rule UID to modify")
    name: Optional[str] = Field(default=None, description="New rule name")
    source: Optional[str] = Field(default=None, description="New source")
    destination: Optional[str] = Field(default=None, description="New destination")
    service: Optional[str] = Field(default=None, description="New service")
    action: Optional[str] = Field(default=None, description="New action")
    track: Optional[str] = Field(default=None, description="New track action")
    comments: Optional[str] = Field(default=None, description="New comments")


class DeleteAccessRuleInput(BaseModel):
    """Input for deleting an access rule."""
    rule_uid: str = Field(..., description="Rule UID to delete")


class ShowPolicyRulesInput(BaseModel):
    """Input for showing policy rules."""
    layer: str = Field(..., description="Policy layer name")
    limit: int = Field(default=500, description="Maximum number of rules to show")


class ReorderRulesInput(BaseModel):
    """Input for reordering rules."""
    layer: str = Field(..., description="Policy layer name")
    rule_uid: str = Field(..., description="Rule UID to move")
    new_position: int = Field(..., description="New position (1-based)")


class CreatePolicyLayerInput(BaseModel):
    """Input for creating a policy layer."""
    name: str = Field(..., description="Layer name")
    comments: Optional[str] = Field(default=None, description="Layer comments")
    shared: bool = Field(default=False, description="Whether layer is shared")


class CreatePolicySectionInput(BaseModel):
    """Input for creating a policy section."""
    name: str = Field(..., description="Section name")
    layer: str = Field(..., description="Policy layer name")
    position: Optional[int] = Field(default=None, description="Section position")


class CreateAccessRuleTool(BaseTool):
    """Tool for creating new access rules."""
    
    name: str = "create_access_rule"
    description: str = """
    Create a new access rule in Check Point firewall policy.
    Supports creating rules with specific source, destination, service, and action.
    Can position rules at specific locations in the policy layer.
    """
    args_schema: Type[BaseModel] = CreateAccessRuleInput
    
    def __init__(self):
        super().__init__()
        self._logger = get_logger("create_access_rule_tool")
        self._client = CheckPointClient()
    
    def _run(self, **kwargs) -> str:
        """Create an access rule."""
        try:
            # Validate input
            input_data = CreateAccessRuleInput(**kwargs)
            
            # Create access rule object
            rule = AccessRule(
                name=input_data.name,
                source=input_data.source,
                destination=input_data.destination,
                service=input_data.service,
                action=input_data.action,
                track=input_data.track,
                layer=input_data.layer,
                position=input_data.position,
                comments=input_data.comments
            )
            
            # Create the rule
            response = self._client.create_access_rule(rule)
            
            if response["success"]:
                rule_data = response["data"]
                return (
                    f"✅ Successfully created access rule '{input_data.name}'\n"
                    f"Rule UID: {rule_data.get('uid', 'N/A')}\n"
                    f"Layer: {input_data.layer}\n"
                    f"Source: {input_data.source}\n"
                    f"Destination: {input_data.destination}\n"
                    f"Service: {input_data.service}\n"
                    f"Action: {input_data.action}\n"
                    f"Track: {input_data.track}"
                )
            else:
                return f"❌ Failed to create access rule: {response.get('message', 'Unknown error')}"
                
        except Exception as e:
            self._logger.error("Error in create_access_rule", error=str(e))
            return f"❌ Error creating access rule: {str(e)}"


class ModifyAccessRuleTool(BaseTool):
    """Tool for modifying existing access rules."""
    
    name: str = "modify_access_rule"
    description: str = """
    Modify an existing access rule in Check Point firewall policy.
    Can update rule properties like source, destination, service, action, and comments.
    """
    args_schema: Type[BaseModel] = ModifyAccessRuleInput
    
    def __init__(self):
        super().__init__()
        self._logger = get_logger("modify_access_rule_tool")
        self._client = CheckPointClient()
    
    def _run(self, **kwargs) -> str:
        """Modify an access rule."""
        try:
            # Validate input
            input_data = ModifyAccessRuleInput(**kwargs)
            
            # Create access rule object with only changed fields
            rule_data = {}
            if input_data.name is not None:
                rule_data["name"] = input_data.name
            if input_data.source is not None:
                rule_data["source"] = input_data.source
            if input_data.destination is not None:
                rule_data["destination"] = input_data.destination
            if input_data.service is not None:
                rule_data["service"] = input_data.service
            if input_data.action is not None:
                rule_data["action"] = input_data.action
            if input_data.track is not None:
                rule_data["track"] = input_data.track
            if input_data.comments is not None:
                rule_data["comments"] = input_data.comments
            
            rule = AccessRule(**rule_data)
            
            # Modify the rule
            response = self._client.modify_access_rule(input_data.rule_uid, rule)
            
            if response["success"]:
                return (
                    f"✅ Successfully modified access rule\n"
                    f"Rule UID: {input_data.rule_uid}\n"
                    f"Updated fields: {', '.join(rule_data.keys())}"
                )
            else:
                return f"❌ Failed to modify access rule: {response.get('message', 'Unknown error')}"
                
        except Exception as e:
            self._logger.error("Error in modify_access_rule", error=str(e))
            return f"❌ Error modifying access rule: {str(e)}"


class DeleteAccessRuleTool(BaseTool):
    """Tool for deleting access rules."""
    
    name: str = "delete_access_rule"
    description: str = """
    Delete an access rule from Check Point firewall policy.
    Removes the rule permanently from the policy layer.
    """
    args_schema: Type[BaseModel] = DeleteAccessRuleInput
    
    def __init__(self):
        super().__init__()
        self._logger = get_logger("delete_access_rule_tool")
        self._client = CheckPointClient()
    
    def _run(self, **kwargs) -> str:
        """Delete an access rule."""
        try:
            # Validate input
            input_data = DeleteAccessRuleInput(**kwargs)
            
            # Delete the rule
            response = self._client.delete_access_rule(input_data.rule_uid)
            
            if response["success"]:
                return f"✅ Successfully deleted access rule (UID: {input_data.rule_uid})"
            else:
                return f"❌ Failed to delete access rule: {response.get('message', 'Unknown error')}"
                
        except Exception as e:
            self._logger.error("Error in delete_access_rule", error=str(e))
            return f"❌ Error deleting access rule: {str(e)}"


class ShowPolicyRulesTool(BaseTool):
    """Tool for displaying policy rules."""
    
    name: str = "show_policy_rules"
    description: str = """
    Display access rules from a specific policy layer.
    Shows rule details including source, destination, service, action, and position.
    """
    args_schema: Type[BaseModel] = ShowPolicyRulesInput
    
    def __init__(self):
        super().__init__()
        self._logger = get_logger("show_policy_rules_tool")
        self._client = CheckPointClient()
    
    def _run(self, **kwargs) -> str:
        """Show policy rules."""
        try:
            # Validate input
            input_data = ShowPolicyRulesInput(**kwargs)
            
            # Get policy rules
            response = self._client.show_access_rulebase(input_data.layer, input_data.limit)
            
            if response["success"]:
                rules = response["data"].get("objects", [])
                
                if not rules:
                    return f"No rules found in layer '{input_data.layer}'."
                
                # Format results
                result_lines = [f"Access Rules in Layer '{input_data.layer}' ({len(rules)} rules):"]
                result_lines.append("")
                
                for i, rule in enumerate(rules, 1):
                    result_lines.append(
                        f"{i}. {rule.get('name', 'Unnamed')} (UID: {rule.get('uid', 'N/A')})"
                    )
                    result_lines.append(f"   Source: {rule.get('source', 'N/A')}")
                    result_lines.append(f"   Destination: {rule.get('destination', 'N/A')}")
                    result_lines.append(f"   Service: {rule.get('service', 'N/A')}")
                    result_lines.append(f"   Action: {rule.get('action', 'N/A')}")
                    result_lines.append(f"   Track: {rule.get('track', 'N/A')}")
                    if rule.get('comments'):
                        result_lines.append(f"   Comments: {rule.get('comments')}")
                    result_lines.append("")
                
                return "\n".join(result_lines)
            else:
                return f"❌ Failed to show policy rules: {response.get('message', 'Unknown error')}"
                
        except Exception as e:
            self._logger.error("Error in show_policy_rules", error=str(e))
            return f"❌ Error showing policy rules: {str(e)}"


class ReorderRulesTool(BaseTool):
    """Tool for reordering rules in policy layers."""
    
    name: str = "reorder_rules"
    description: str = """
    Change the position of a rule within a policy layer.
    Rules are processed in order, so position affects rule precedence.
    """
    args_schema: Type[BaseModel] = ReorderRulesInput
    
    def __init__(self):
        super().__init__()
        self._logger = get_logger("reorder_rules_tool")
        self._client = CheckPointClient()
    
    def _run(self, **kwargs) -> str:
        """Reorder rules."""
        try:
            # Validate input
            input_data = ReorderRulesInput(**kwargs)
            
            # Create rule object with new position
            rule = AccessRule(
                name="",  # Will be updated by UID
                source="",  # Will be updated by UID
                destination="",  # Will be updated by UID
                service="",  # Will be updated by UID
                action="",  # Will be updated by UID
                layer=input_data.layer,
                position=input_data.new_position
            )
            
            # Reorder the rule
            response = self._client.modify_access_rule(input_data.rule_uid, rule)
            
            if response["success"]:
                return (
                    f"✅ Successfully reordered rule\n"
                    f"Rule UID: {input_data.rule_uid}\n"
                    f"New position: {input_data.new_position}\n"
                    f"Layer: {input_data.layer}"
                )
            else:
                return f"❌ Failed to reorder rule: {response.get('message', 'Unknown error')}"
                
        except Exception as e:
            self._logger.error("Error in reorder_rules", error=str(e))
            return f"❌ Error reordering rules: {str(e)}"


class CreatePolicyLayerTool(BaseTool):
    """Tool for creating new policy layers."""
    
    name: str = "create_policy_layer"
    description: str = """
    Create a new policy layer in Check Point firewall.
    Policy layers organize access rules and can be shared across gateways.
    """
    args_schema: Type[BaseModel] = CreatePolicyLayerInput
    
    def __init__(self):
        super().__init__()
        self._logger = get_logger("create_policy_layer_tool")
        self._client = CheckPointClient()
    
    def _run(self, **kwargs) -> str:
        """Create a policy layer."""
        try:
            # Validate input
            input_data = CreatePolicyLayerInput(**kwargs)
            
            # Create policy layer object
            layer = PolicyLayer(
                name=input_data.name,
                comments=input_data.comments,
                shared=input_data.shared
            )
            
            # Create the layer
            response = self._client._retry_request(
                "POST", "/add-access-layer", data=layer.dict()
            )
            
            if response["success"]:
                layer_data = response["data"]
                return (
                    f"✅ Successfully created policy layer '{input_data.name}'\n"
                    f"Layer UID: {layer_data.get('uid', 'N/A')}\n"
                    f"Shared: {input_data.shared}\n"
                    f"Comments: {input_data.comments or 'None'}"
                )
            else:
                return f"❌ Failed to create policy layer: {response.get('message', 'Unknown error')}"
                
        except Exception as e:
            self._logger.error("Error in create_policy_layer", error=str(e))
            return f"❌ Error creating policy layer: {str(e)}"


class CreatePolicySectionTool(BaseTool):
    """Tool for creating policy sections."""
    
    name: str = "create_policy_section"
    description: str = """
    Create a new section within a policy layer to organize rules.
    Sections help group related rules together for better management.
    """
    args_schema: Type[BaseModel] = CreatePolicySectionInput
    
    def __init__(self):
        super().__init__()
        self._logger = get_logger("create_policy_section_tool")
        self._client = CheckPointClient()
    
    def _run(self, **kwargs) -> str:
        """Create a policy section."""
        try:
            # Validate input
            input_data = CreatePolicySectionInput(**kwargs)
            
            # Create section data
            section_data = {
                "name": input_data.name,
                "layer": input_data.layer
            }
            
            if input_data.position:
                section_data["position"] = input_data.position
            
            # Create the section
            response = self._client._retry_request(
                "POST", "/add-access-section", data=section_data
            )
            
            if response["success"]:
                section_info = response["data"]
                return (
                    f"✅ Successfully created policy section '{input_data.name}'\n"
                    f"Layer: {input_data.layer}\n"
                    f"Position: {input_data.position or 'Default'}\n"
                    f"Section UID: {section_info.get('uid', 'N/A')}"
                )
            else:
                return f"❌ Failed to create policy section: {response.get('message', 'Unknown error')}"
                
        except Exception as e:
            self._logger.error("Error in create_policy_section", error=str(e))
            return f"❌ Error creating policy section: {str(e)}"

