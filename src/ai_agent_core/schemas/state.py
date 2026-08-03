from pydantic import BaseModel, Field
from typing import Optional, List

class AgentState(BaseModel):
    query: str
    session_id: str
    plan: Optional[str] = None
    reasoning_steps: Optional[List[str]] = Field(default_factory=list)
    # is_cot_valid: Optional[bool] = None
    # cot_retry_count: int = 0