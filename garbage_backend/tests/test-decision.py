"""Unit tests for the decision state machine (no hardware needed)."""
import pytest
from backend.core.decision import decide, next_state
from backend.models.state import State

# Fake detection: object centred in a 320-wide frame
FAKE_CENTRED = {"class": "bottle", "cx": 160, "cy": 120, "w": 60, "h": 80, "conf": 0.9, "area": 4800}
FAKE_LEFT    = {"class": "can",    "cx": 40,  "cy": 120, "w": 50, "h": 70, "conf": 0.8, "area": 3500}

class TestDecide:
    def test_no_detection_drives_forward(self):
        cmd, speed = decide(None, None)
        assert cmd == "F"

    def test_off_center_steers(self):
        cmd, _ = decide(FAKE_LEFT, 30)
        assert cmd == "L"

    def test_centered_far_approaches(self):
        cmd, _ = decide(FAKE_CENTRED, 40)
        assert cmd == "F"

    def test_centered_close_stops(self):
        cmd, _ = decide(FAKE_CENTRED, 10)
        assert cmd == "S"

class TestStateMachine:
    def test_seek_to_approach(self):
        assert next_state(FAKE_CENTRED, 30, State.SEEK) == State.APPROACH

    def test_approach_to_stop(self):
        assert next_state(FAKE_CENTRED, 10, State.APPROACH) == State.STOP

    def test_stop_to_pick(self):
        assert next_state(FAKE_CENTRED, 10, State.STOP) == State.PICK

    def test_pick_to_done(self):
        assert next_state(None, None, State.PICK) == State.DONE

    def test_approach_lost_target_back_to_seek(self):
        assert next_state(None, None, State.APPROACH) == State.SEEK   