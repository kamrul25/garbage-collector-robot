"""Pydantic request/response schemas for the API."""
from pydantic import BaseModel


class SensorPayload(BaseModel):
    """DevKit POSTs this every 200 ms."""
    d: float  # distance in cm

class CommandPayload(BaseModel):
    """What the backend sends to the DevKit."""
    c: str    # F, B, L, R, S, PICK
    s: int = 0

class StateResponse(BaseModel):
    state: str
    target: str | None
    last_command: str | None
    distance_cm: float | None
    frames: int
    uptime_s: float   