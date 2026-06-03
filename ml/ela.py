"""
Error Level Analysis (ELA) — detects JPEG compression inconsistencies
that indicate image manipulation or splicing.
"""
import numpy as np
from PIL import Image, ImageChops, ImageEnhance
import io
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

ELA_QUALITY = 90        # JPEG recompression quality
ELA_AMPLIFY = 20        # Amplification factor for visualization


def run_ela(image_path: str) -> Tuple[np.ndarray, float]:
    """
    Run ELA on an image file.
    Returns (ela_array, manipulation_score 0-1)
    """
    try:
        original = Image.open(image_path).convert("RGB")

        # Resave at known quality
        buffer = io.BytesIO()
        original.save(buffer, format="JPEG", quality=ELA_QUALITY)
        buffer.seek(0)
        recompressed = Image.open(buffer).convert("RGB")

        # Compute difference
        diff = ImageChops.difference(original, recompressed)

        # Amplify for visibility
        enhancer = ImageEnhance.Brightness(diff)
        ela_image = enhancer.enhance(ELA_AMPLIFY)

        ela_array = np.array(ela_image)

        # Compute manipulation score from ELA intensity
        ela_mean = np.mean(ela_array)
        ela_max  = np.max(ela_array)
        ela_std  = np.std(ela_array)

        # High variance = inconsistent compression = likely manipulation
        score = min((ela_std / 50.0) * 0.6 + (ela_mean / 100.0) * 0.4, 1.0)

        logger.info(f"[ELA] Score: {score:.3f} | Mean: {ela_mean:.1f} | Std: {ela_std:.1f}")
        return ela_array, float(score)

    except Exception as e:
        logger.error(f"[ELA] Error: {e}")
        return np.zeros((224, 224, 3), dtype=np.uint8), 0.0


def run_ela_on_array(frame: np.ndarray) -> Tuple[np.ndarray, float]:
    """Run ELA on a numpy array (frame from video)."""
    try:
        pil_img = Image.fromarray(frame.astype(np.uint8))

        buffer1 = io.BytesIO()
        pil_img.save(buffer1, format="JPEG", quality=ELA_QUALITY)
        buffer1.seek(0)
        recompressed = Image.open(buffer1).convert("RGB")

        diff = ImageChops.difference(pil_img, recompressed)
        enhancer = ImageEnhance.Brightness(diff)
        ela_image = enhancer.enhance(ELA_AMPLIFY)
        ela_array = np.array(ela_image)

        ela_std = np.std(ela_array)
        ela_mean = np.mean(ela_array)
        score = min((ela_std / 50.0) * 0.6 + (ela_mean / 100.0) * 0.4, 1.0)

        return ela_array, float(score)

    except Exception as e:
        logger.error(f"[ELA] Array error: {e}")
        return frame, 0.0
