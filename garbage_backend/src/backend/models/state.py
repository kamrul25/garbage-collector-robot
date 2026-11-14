"""Robot state machine definitions."""
import time
from dataclasses import dataclass, field
from enum import Enum


class State(Enum):
    SEEK     = "SEEK"
    APPROACH = "APPROACH"
    STOP     = "STOP"
    PICK     = "PICK"
    DONE     = "DONE"
    ERROR    = "ERROR"

@dataclass
class RobotState:
    state: State = State.SEEK
    target_class: str | None = None
    last_command: str | None = None
    last_distance: float | None = None
    frame_count: int = 0
    start_time: float = field(default_factory=time.time)

    def reset(self):
        self.state = State.SEEK
        self.target_class = None
        self.last_command = None
        self.frame_count = 0
        self.start_time = time.time()   