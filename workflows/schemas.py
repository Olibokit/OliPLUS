from pydantic import BaseModel, Field
from typing import List, Union, Literal

# 📤 Étapes individuelles du workflow
class SendEmailParams(BaseModel):
    to: str
    subject: str
    body: str

class WaitParams(BaseModel):
    duration_seconds: int

class AssignSegmentParams(BaseModel):
    segment_id: str

class StepSchema(BaseModel):
    type: Literal["send_email", "wait", "assign_segment"]
    params: Union[SendEmailParams, WaitParams, AssignSegmentParams] = Field(..., description="Paramètres selon le type d'étape")

# 🧠 Structure principale du workflow
class WorkflowSchema(BaseModel):
    name: str = Field(..., description="Nom du workflow")
    trigger_event: str = Field(..., description="Événement déclencheur du workflow")
    steps: List[StepSchema] = Field(..., description="Liste ordonnée d'étapes à exécuter")
