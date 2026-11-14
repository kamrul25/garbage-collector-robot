"""Decision state machine: maps detection + distance → command."""
from backend.config import settings
from backend.models.state import State


def decide(detection: dict | None, distance_cm: float | None) -> tuple[str, int]:
    """
    Returns (command, speed).
    Commands: F, B, L, R, S, PICK
    """
    dc = settings.decision
    frame_w = settings.camera.resolution[0]

    if detection is None:
        return ("F", dc.seek_speed)

    offset = (detection["cx"] / frame_w) - 0.5

    if abs(offset) > dc.center_tolerance:
        return ("L" if offset > 0 else "R", dc.turn_speed)

    if distance_cm is not None and distance_cm > dc.stop_distance_cm:
        return ("F", dc.approach_speed)

    return ("S", 0)

def next_state(detection: dict | None, distance_cm: float | None, current: State) -> State:
    dc = settings.decision

    if current == State.SEEK:
        return State.APPROACH if detection else State.SEEK

    if current == State.APPROACH:
        if detection is None:
            return State.SEEK
        if distance_cm is not None and distance_cm <= dc.stop_distance_cm:
            return State.STOP
        return State.APPROACH

    if current == State.STOP:
        return State.PICK

    if current == State.PICK:
        return State.DONE

    return current   