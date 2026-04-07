

from openenv.core.env_server.types import Action, Observation
from pydantic import Field, validator
from pydantic import BaseModel


class MyAction(BaseModel):
    dispatches: list[float]
    @validator('dispatches')
    def cap_total_supply(cls, v):
        # Cap each hospital at 20 max
        v = [min(d, 20.0) for d in v]
        # Cap total across all hospitals at 30
        total = sum(v)
        if total > 30.0:
            scale = 30.0 / total
            v = [d * scale for d in v]
        return v


class MyObservation(BaseModel):
    hospital_levels: list[float]
    patient_counts: list[int]  
    pending_delivery: list[float]
    message: str
    done: bool
    reward: float
    metadata: dict = Field(default_factory=dict)
