"""
Main ML inference pipeline.
Orchestrates: frame extraction → face detection → classification → ELA → heatmap → aggregation
"""
import os
import logging
from pathlib import Path
from typing import Dict, Any
from datetime import datetime, timezone

from .frame_extractor import FrameExtractor
from .face_detector import FaceDetector
from .classifier import DeepfakeClassifier
from .ela import run_ela_on_array, run_ela
from .gradcam import generate_heatmap
from .aggregator import (
    aggregate_frame_scores,
    compute_authenticity_score,
    count_flagged_frames,
)

logger = logging.getLogger(__name__)

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
DEVICE     = os.getenv("DEVICE", "cpu")
MODEL_PATH = os.getenv("MODEL_PATH", None)


class MediaForensicsPipeline:
    def __init__(self):
        logger.info("[Pipeline] Initializing ML components...")
        self.extractor  = FrameExtractor(sample_rate=10, max_frames=50)
        self.detector   = FaceDetector(confidence=0.4)
        self.classifier = DeepfakeClassifier(model_path=MODEL_PATH, device=DEVICE)
        logger.info("[Pipeline] Ready ✓")

    def analyze(self, job_id: str, file_path: str) -> Dict[str, Any]:
        """
        Full analysis pipeline for one media file.
        Returns complete result dict ready to save to MongoDB.
        """
        logger.info(f"[Pipeline] Starting analysis for job {job_id}: {file_path}")

        try:
            # ── Step 1: Extract frames ─────────────────────
            frames, media_meta = self.extractor.load_media(file_path)
            logger.info(f"[Pipeline] Extracted {len(frames)} frames")

            # ── Step 2 & 3: Face detection + Classification ─
            frame_fake_probs = []
            ela_scores       = []
            face_detected    = []
            frame_results    = []

            for i, frame in enumerate(frames):
                # Face detection
                face = self.detector.detect_largest_face(frame)
                has_face = face is not None
                face_detected.append(has_face)

                # Use face crop if available, else full frame
                region = self.detector.crop_face(frame, face) if has_face else frame

                # Deepfake classification
                fake_prob, real_prob = self.classifier.predict_frame(region)
                frame_fake_probs.append(fake_prob)

                # ELA
                _, ela_score = run_ela_on_array(frame)
                ela_scores.append(ela_score)

                is_flagged = fake_prob > 0.5
                frame_idx  = media_meta.get("frame_indices", [i])[i] if i < len(media_meta.get("frame_indices", [])) else i

                frame_results.append({
                    "frame_index":    frame_idx,
                    "timestamp_sec":  round(frame_idx / max(media_meta.get("fps") or 30, 1), 2),
                    "is_manipulated": is_flagged,
                    "confidence":     round(fake_prob, 3),
                    "face_detected":  has_face,
                })

                logger.debug(f"[Pipeline] Frame {i}: fake={fake_prob:.3f} face={has_face}")

            # ── Step 4: Generate heatmap for most suspicious frame ──
            heatmap_url = None
            if frames and frame_fake_probs:
                worst_idx = int(max(range(len(frame_fake_probs)), key=lambda i: frame_fake_probs[i]))
                heatmap_path = os.path.join(UPLOAD_DIR, f"{job_id}_heatmap.png")

                if self.classifier.model is not None:
                    _, saved = generate_heatmap(
                        self.classifier.model,
                        frames[worst_idx],
                        device=DEVICE,
                        output_path=heatmap_path,
                    )
                else:
                    from .gradcam import _fallback_heatmap
                    _, saved = _fallback_heatmap(frames[worst_idx], heatmap_path)

                if saved:
                    heatmap_url = f"/uploads/{job_id}_heatmap.png"

            # ── Step 5: Aggregate scores ───────────────────
            signals = aggregate_frame_scores(frame_fake_probs, ela_scores, face_detected)
            auth_score, confidence, verdict = compute_authenticity_score(signals)
            frames_flagged = count_flagged_frames(frame_fake_probs)

            result = {
                "authenticity_score": auth_score,
                "verdict":            verdict,
                "confidence":         confidence,
                "signals":            signals,
                "frames_analyzed":    len(frames),
                "frames_flagged":     frames_flagged,
                "heatmap_url":        heatmap_url,
                "frame_results":      frame_results,
            }

            logger.info(
                f"[Pipeline] Done — verdict: {verdict} | "
                f"score: {auth_score} | flagged: {frames_flagged}/{len(frames)}"
            )
            return result

        except Exception as e:
            logger.error(f"[Pipeline] Analysis failed for {job_id}: {e}", exc_info=True)
            raise


# Singleton instance (loaded once per worker process)
_pipeline: MediaForensicsPipeline = None


def get_pipeline() -> MediaForensicsPipeline:
    global _pipeline
    if _pipeline is None:
        _pipeline = MediaForensicsPipeline()
    return _pipeline
