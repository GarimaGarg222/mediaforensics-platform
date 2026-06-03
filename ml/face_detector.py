"""
Face detection using YOLOv8.
Detects faces in images and video frames, returns bounding boxes.
"""
import cv2
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class FaceDetector:
    def __init__(self, model_name: str = "yolov8n.pt", confidence: float = 0.5):
        self.confidence = confidence
        self.model = None
        self.model_name = model_name
        self._load_model()

    def _load_model(self):
        try:
            from ultralytics import YOLO
            self.model = YOLO(self.model_name)
            logger.info(f"[FaceDetector] Loaded YOLO model: {self.model_name}")
        except Exception as e:
            logger.error(f"[FaceDetector] Failed to load YOLO: {e}")
            self.model = None

    def detect(self, frame: np.ndarray) -> List[Dict]:
        """
        Detect faces in a single frame.
        Returns list of dicts with bbox, confidence.
        """
        if self.model is None:
            return []

        try:
            results = self.model(frame, verbose=False, conf=self.confidence)
            faces = []

            for result in results:
                for box in result.boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                    conf = float(box.conf[0])
                    faces.append({
                        "bbox": [x1, y1, x2, y2],
                        "confidence": round(conf, 3),
                        "width": x2 - x1,
                        "height": y2 - y1,
                    })

            return faces

        except Exception as e:
            logger.error(f"[FaceDetector] Detection error: {e}")
            return []

    def detect_largest_face(self, frame: np.ndarray) -> Optional[Dict]:
        """Return only the largest detected face (by area)."""
        faces = self.detect(frame)
        if not faces:
            return None
        return max(faces, key=lambda f: f["width"] * f["height"])

    def crop_face(self, frame: np.ndarray, face: Dict, padding: float = 0.2) -> np.ndarray:
        """Crop face region with optional padding."""
        x1, y1, x2, y2 = face["bbox"]
        h, w = frame.shape[:2]

        pad_x = int((x2 - x1) * padding)
        pad_y = int((y2 - y1) * padding)

        x1 = max(0, x1 - pad_x)
        y1 = max(0, y1 - pad_y)
        x2 = min(w, x2 + pad_x)
        y2 = min(h, y2 + pad_y)

        return frame[y1:y2, x1:x2]
