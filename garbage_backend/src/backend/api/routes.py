"""FastAPI routes."""
import asyncio

import cv2
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from backend.core.camera import CameraStream
from backend.core.inference import Detector
from backend.models.schemas import SensorPayload, StateResponse

router = APIRouter()

def _get_robot(request):
    return request.app.state.robot

# ─── Endpoints ───────────────────────────────────────────────

@router.get("/state", response_model=StateResponse)
async def get_state(request):
    robot = _get_robot(request)
    import time
    return StateResponse(
        state=robot.state.value,
        target=robot.target_class,
        last_command=robot.last_command,
        distance_cm=robot.last_distance,
        frames=robot.frame_count,
        uptime_s=round(time.time() - robot.start_time, 1),
    )

@router.post("/sensor")
async def receive_sensor(payload: SensorPayload, request):
    """DevKit POSTs distance here every 200 ms."""
    robot = _get_robot(request)
    robot.last_distance = payload.d
    return {"ok": True}

@router.post("/reset")
async def reset(request):
    robot = _get_robot(request)
    robot.reset()
    return {"ok": True, "state": "SEEK"}

@router.get("/stream")
async def annotated_stream(request):
    """MJPEG stream with YOLO detection overlay."""
    detector = Detector()

    async def generate():
        cam = CameraStream()
        while True:
            frame = cam.read()
            if frame is None:
                break
            annotated = detector.annotate(frame)
            _, buf = cv2.imencode(".jpg", annotated)
            yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + buf.tobytes() + b"\r\n"
            await asyncio.sleep(0.1)
        cam.close()

    return StreamingResponse(
        generate(),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )

@router.get("/health")
async def health():
    return {"status": "ok"}   