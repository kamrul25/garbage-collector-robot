"""ESP32-CAM MJPEG stream reader."""
import cv2
import numpy as np

from backend.config import settings


class CameraStream:
    """Wraps cv2.VideoCapture for the ESP32-CAM MJPEG stream."""

    def __init__(self, url: str | None = None):
        self.url = url or settings.camera.stream_url
        self._cap: cv2.VideoCapture | None = None

    def open(self):
        self._cap = cv2.VideoCapture(self.url, cv2.CAP_FFMPEG)
        self._cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    def close(self):
        if self._cap:
            self._cap.release()
            self._cap = None

    def read(self) -> np.ndarray | None:
        if self._cap is None or not self._cap.isOpened():
            self.open()
        if self._cap is None:
            return None
        ret, frame = self._cap.read()
        if not ret:
            self.close()
        return frame if ret else None

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, *args):
        self.close()   