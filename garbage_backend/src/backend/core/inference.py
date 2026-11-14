"""YOLOv8 inference wrapper."""
import numpy as np
from ultralytics import YOLO

from backend.config import settings


class Detector:
    """Loads the model once, exposes a detect() method."""

    def __init__(self):
        self.model = YOLO(settings.model.path)
        self.conf = settings.model.confidence
        self.target_classes = set(settings.model.target_classes)

    def detect(self, frame: np.ndarray) -> dict | None:
        """
        Returns the best (largest) target detection or None.
        Keys: class, cx, cy, w, h, conf, area
        """
        results = self.model.predict(frame, conf=self.conf, verbose=False)
        best = None
        for result in results:
            for box in result.boxes:
                cls_name = result.names[int(box.cls[0])]
                if cls_name not in self.target_classes:
                    continue
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
                w, h = x2 - x1, y2 - y1
                area = w * h
                if best is None or area > best["area"]:
                    best = {
                        "class": cls_name,
                        "cx": cx, "cy": cy,
                        "w": w, "h": h,
                        "conf": float(box.conf[0]),
                        "area": area,
                    }
        return best

    def annotate(self, frame: np.ndarray) -> np.ndarray:
        """Return frame with YOLO boxes drawn (for /stream endpoint)."""
        results = self.model.predict(frame, conf=self.conf, verbose=False)
        return results[0].plot()   