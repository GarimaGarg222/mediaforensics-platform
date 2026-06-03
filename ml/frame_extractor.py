"""
Frame extraction from video files using OpenCV.
Samples frames at regular intervals for analysis.
"""
import cv2
import numpy as np
from typing import List, Tuple, Dict
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class FrameExtractor:
    def __init__(self, sample_rate: int = 10, max_frames: int = 100):
        """
        Args:
            sample_rate: Extract every Nth frame
            max_frames: Maximum number of frames to extract
        """
        self.sample_rate = sample_rate
        self.max_frames = max_frames

    def extract_from_video(self, video_path: str) -> Tuple[List[np.ndarray], Dict]:
        """
        Extract frames from a video file.
        Returns (frames, metadata)
        """
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            raise ValueError(f"Could not open video: {video_path}")

        # Get video metadata
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = total_frames / fps if fps > 0 else 0

        metadata = {
            "fps": round(fps, 2),
            "total_frames": total_frames,
            "width": width,
            "height": height,
            "duration_sec": round(duration, 2),
        }

        logger.info(f"[FrameExtractor] Video: {width}x{height} @ {fps}fps, {duration:.1f}s")

        frames = []
        frame_indices = []
        frame_idx = 0

        while cap.isOpened() and len(frames) < self.max_frames:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_idx % self.sample_rate == 0:
                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frames.append(frame_rgb)
                frame_indices.append(frame_idx)

            frame_idx += 1

        cap.release()
        metadata["frames_extracted"] = len(frames)
        metadata["frame_indices"] = frame_indices

        logger.info(f"[FrameExtractor] Extracted {len(frames)} frames")
        return frames, metadata

    def load_image(self, image_path: str) -> Tuple[np.ndarray, Dict]:
        """
        Load a single image file.
        Returns (frame, metadata)
        """
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not load image: {image_path}")

        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h, w = img_rgb.shape[:2]

        metadata = {
            "width": w,
            "height": h,
            "duration_sec": None,
            "fps": None,
            "frames_extracted": 1,
            "frame_indices": [0],
        }

        return img_rgb, metadata

    def load_media(self, file_path: str) -> Tuple[List[np.ndarray], Dict]:
        """
        Auto-detect media type and load accordingly.
        Returns (frames_list, metadata)
        """
        ext = Path(file_path).suffix.lower()
        video_exts = {".mp4", ".mov", ".avi", ".mkv", ".webm"}

        if ext in video_exts:
            return self.extract_from_video(file_path)
        else:
            frame, meta = self.load_image(file_path)
            return [frame], meta
