from typing import List, Optional, Dict, Literal
from pydantic import BaseModel, Field
from uuid import UUID, uuid4

class AutomationStep(BaseModel):
    type: Literal["email", "webhook", "script", "delay", "log"]
    params: Dict[str, str] = Field(default_factory=dict)
    description: Optional[str] = None
    enabled: bool = True

class AutomationWorkflow(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    description: Optional[str] = None
    trigger_event: str
    steps: List[AutomationStep]
    status: Literal["draft", "active", "archived"] = "draft"
    tags: Optional[List[str]] = None
    created_by: Optional[str] = None
    last_updated: Optional[str] = None
