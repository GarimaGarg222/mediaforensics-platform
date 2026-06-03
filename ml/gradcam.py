"""
Grad-CAM heatmap generation.
Produces forensic overlays showing WHICH regions the model flagged as manipulated.
"""
import numpy as np
import cv2
from PIL import Image
import logging
from typing import Optional, Tuple
import os

logger = logging.getLogger(__name__)


def generate_heatmap(
    model,
    frame: np.ndarray,
    device: str = "cpu",
    output_path: Optional[str] = None,
) -> Tuple[np.ndarray, Optional[str]]:
    """
    Generate Grad-CAM heatmap for a frame.
    Returns (heatmap_array, saved_path)
    """
    try:
        import torch
        from pytorch_grad_cam import GradCAM
        from pytorch_grad_cam.utils.image import show_cam_on_image
        from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget
        from torchvision import transforms

        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ])

        pil_img = Image.fromarray(frame.astype(np.uint8))
        tensor = transform(pil_img).unsqueeze(0)

        # Target last conv layer of EfficientNet-B4
        target_layers = [model.conv_head] if hasattr(model, "conv_head") else [list(model.children())[-3]]

        cam = GradCAM(model=model, target_layers=target_layers)

        # Target class 1 = fake
        targets = [ClassifierOutputTarget(1)]
        grayscale_cam = cam(input_tensor=tensor, targets=targets)[0]

        # Overlay on original image
        rgb_img = np.float32(cv2.resize(frame, (224, 224))) / 255.0
        visualization = show_cam_on_image(rgb_img, grayscale_cam, use_rgb=True)

        if output_path:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            cv2.imwrite(output_path, cv2.cvtColor(visualization, cv2.COLOR_RGB2BGR))
            logger.info(f"[GradCAM] Saved heatmap to {output_path}")
            return visualization, output_path

        return visualization, None

    except Exception as e:
        logger.warning(f"[GradCAM] Failed, using fallback heatmap: {e}")
        return _fallback_heatmap(frame, output_path)


def _fallback_heatmap(
    frame: np.ndarray,
    output_path: Optional[str] = None,
) -> Tuple[np.ndarray, Optional[str]]:
    """
    Fallback heatmap using image gradient analysis
    when Grad-CAM is unavailable.
    """
    resized = cv2.resize(frame, (224, 224))
    gray = cv2.cvtColor(resized, cv2.COLOR_RGB2GRAY)

    # Laplacian for edge/noise analysis
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    abs_lap = np.abs(laplacian)

    # Normalize to 0-255
    normalized = cv2.normalize(abs_lap, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

    # Apply colormap
    heatmap = cv2.applyColorMap(normalized, cv2.COLORMAP_JET)
    heatmap_rgb = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)

    # Blend with original
    alpha = 0.5
    overlay = cv2.addWeighted(resized, 1 - alpha, heatmap_rgb, alpha, 0)

    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        cv2.imwrite(output_path, cv2.cvtColor(overlay, cv2.COLOR_RGB2BGR))

    return overlay, output_path
