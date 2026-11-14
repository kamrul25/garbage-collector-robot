"""Background control loop: camera → detect → decide → send command."""
import asyncio
import logging

import httpx
from fastapi import FastAPI

from backend.config import settings
from backend.core.camera import CameraStream
from backend.core.decision import decide, next_state
from backend.core.inference import Detector
from backend.models.state import State

log = logging.getLogger("controller")

# Module-level singletons (set on startup)
_detector: Detector | None = None
_robot_state = None  # set in main.py via app.state

def _get_robot_state(app: FastAPI):
    return app.state.robot

async def _send_command(cmd: str, speed: int):
    url = settings.devkit.cmd_url
    try:
        async with httpx.AsyncClient(timeout=2) as client:
            await client.post(url, json={"c": cmd, "s": speed})
    except Exception as e:
        log.warning("DevKit unreachable: %s", e)

async def _control_loop(app: FastAPI):
    global _detector
    _detector = Detector()
    robot = _get_robot_state(app)
    camera = CameraStream()
    interval = 1.0 / settings.server.fps_limit

    log.info("Control loop started (target %d fps)", settings.server.fps_limit)

    while True:
        frame = camera.read()
        if frame is None:
            log.warning("Frame lost, retrying…")
            await asyncio.sleep(1)
            continue

        robot.frame_count += 1
        detection = _detector.detect(frame)
        distance = robot.last_distance

        cmd, speed = decide(detection, distance)
        robot.state = next_state(detection, distance, robot.state)

        # Trigger PICK command when entering PICK state
        if robot.state == State.PICK and cmd != "PICK":
            cmd, speed = "PICK", 0

        robot.last_command = f"{cmd}:{speed}"
        robot.target_class = detection["class"] if detection else None

        await _send_command(cmd, speed)
        await asyncio.sleep(interval)

def start_control_loop(app: FastAPI):
    """Called on FastAPI startup."""
    from backend.models.state import RobotState
    app.state.robot = RobotState()
    app.state.control_task = asyncio.create_task(_control_loop(app))

def stop_control_loop(app: FastAPI):
    """Called on FastAPI shutdown."""
    if hasattr(app.state, "control_task"):
        app.state.control_task.cancel()   