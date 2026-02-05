from pydantic import BaseModel
from typing import List, Optional, Any


class StepSchema(BaseModel):
    model: str
    prompt: str
    criteria_type: str
    criteria_value: Optional[Any] = None   # ✅ FIX
    max_retries: int


class WorkflowCreateSchema(BaseModel):
    name: str
    steps: List[StepSchema]
