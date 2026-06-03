"""
Aggregates all detection signals into a final authenticity score and verdict.
"""
from typing import List, Dict, Tuple
import numpy as np
import logging

logger = logging.getLogger(__name__)

# Verdict thresholds (authenticity score 0-100)
AUTHENTIC_THRESHOLD  = 70   # >= 70 = authentic
SUSPICIOUS_THRESHOLD = 40   # 40-69 = suspicious
                             # < 40  = fake


def aggregate_frame_scores(
    frame_fake_probs: List[float],
    ela_scores: List[float],
    face_detected: List[bool],
) -> Dict:
    """
    Combine per-frame scores into overall detection signals.
    Returns dict of signal scores (0-1 each).
    """
    if not frame_fake_probs:
        return _empty_signals()

    fake_probs = np.array(frame_fake_probs)
    ela = np.array(ela_scores) if ela_scores else np.zeros(len(fake_probs))

    # Face swap — high average fake probability
    face_swap_score = float(np.mean(fake_probs))

    # GAN artifacts — high max fake probability in any frame
    gan_score = float(np.percentile(fake_probs, 90))

    # Temporal inconsistency — variance across frames (video only)
    temporal_score = float(np.std(fake_probs)) * 2 if len(fake_probs) > 1 else 0.0
    temporal_score = min(temporal_score, 1.0)

    # Blink anomaly proxy — frames with no face when face expected
    total_with_face = sum(face_detected)
    blink_score = 0.0
    if total_with_face > 0 and len(face_detected) > 3:
        no_face_ratio = 1 - (total_with_face / len(face_detected))
        blink_score = min(no_face_ratio * 2, 1.0)

    # JPEG/ELA artifacts
    jpeg_score = float(np.mean(ela)) if len(ela) > 0 else 0.0

    return {
        "face_swap": round(face_swap_score, 3),
        "gan_artifacts": round(gan_score, 3),
        "temporal_inconsistency": round(temporal_score, 3),
        "blink_anomaly": round(blink_score, 3),
        "jpeg_artifacts": round(jpeg_score, 3),
    }


def compute_authenticity_score(signals: Dict) -> Tuple[float, float, str]:
    """
    Weighted combination of signals → authenticity score (0-100).
    Returns (authenticity_score, confidence, verdict)
    """
    weights = {
        "face_swap":               0.35,
        "gan_artifacts":           0.25,
        "temporal_inconsistency":  0.20,
        "blink_anomaly":           0.10,
        "jpeg_artifacts":          0.10,
    }

    # Weighted manipulation probability
    manip_prob = sum(
        signals.get(k, 0.0) * w
        for k, w in weights.items()
    )
    manip_prob = max(0.0, min(1.0, manip_prob))

    # Authenticity = inverse of manipulation
    authenticity_score = round((1.0 - manip_prob) * 100, 1)

    # Confidence based on signal consistency
    signal_values = list(signals.values())
    confidence = round(1.0 - np.std(signal_values), 3)
    confidence = max(0.5, min(0.99, confidence))

    # Verdict
    if authenticity_score >= AUTHENTIC_THRESHOLD:
        verdict = "authentic"
    elif authenticity_score >= SUSPICIOUS_THRESHOLD:
        verdict = "suspicious"
    else:
        verdict = "fake"

    logger.info(
        f"[Aggregator] Score: {authenticity_score} | "
        f"Verdict: {verdict} | Confidence: {confidence}"
    )
    return authenticity_score, confidence, verdict


def count_flagged_frames(fake_probs: List[float], threshold: float = 0.5) -> int:
    return sum(1 for p in fake_probs if p > threshold)


def _empty_signals() -> Dict:
    return {
        "face_swap": 0.0,
        "gan_artifacts": 0.0,
        "temporal_inconsistency": 0.0,
        "blink_anomaly": 0.0,
        "jpeg_artifacts": 0.0,
    }
