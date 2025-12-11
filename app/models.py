from pydantic import BaseModel
from typing import Any, Dict, Optional

class CreateGraphRequest(BaseModel):
    graph: Dict

class CreateGraphResponse(BaseModel):
    graph_id: str

class RunGraphRequest(BaseModel):
    graph_id: str
    initial_state: Optional[Dict[str, Any]] = {}

class RunGraphResponse(BaseModel):
    run_id: str

class RunStateResponse(BaseModel):
    run_id: str
    graph_id: str
    state: Dict[str, Any]
    log: list
    status: str
    started_at: float
    finished_at: Optional[float]
#