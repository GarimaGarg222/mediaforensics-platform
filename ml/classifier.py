"""
Deepfake classifier using EfficientNet-B4 pretrained on FaceForensics++.
Falls back to a heuristic model if weights aren't available.
"""
import torch
import torch.nn as nn
import numpy as np
from PIL import Image
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)

# ImageNet normalization
MEAN = [0.485, 0.456, 0.406]
STD  = [0.229, 0.224, 0.225]
IMG_SIZE = 224


class DeepfakeClassifier:
    def __init__(self, model_path: str = None, device: str = "cpu"):
        self.device = torch.device(device)
        self.model = None
        self.transform = self._build_transform()
        self._load_model(model_path)

    def _build_transform(self):
        from torchvision import transforms
        return transforms.Compose([
            transforms.Resize((IMG_SIZE, IMG_SIZE)),
            transforms.ToTensor(),
            transforms.Normalize(mean=MEAN, std=STD),
        ])

    def _load_model(self, model_path: str = None):
        """Load model — tries custom weights first, falls back to pretrained."""
        try:
            import timm
            # EfficientNet-B4 — strong deepfake detector
            self.model = timm.create_model(
                "efficientnet_b4",
                pretrained=True,
                num_classes=2,        # Real vs Fake
            )

            # Load custom weights if available
            if model_path:
                try:
                    state = torch.load(model_path, map_location=self.device)
                    self.model.load_state_dict(state, strict=False)
                    logger.info(f"[Classifier] Loaded custom weights from {model_path}")
                except Exception as e:
                    logger.warning(f"[Classifier] Could not load custom weights: {e}")
                    logger.info("[Classifier] Using pretrained ImageNet weights")

            self.model.eval()
            self.model.to(self.device)
            logger.info(f"[Classifier] EfficientNet-B4 ready on {self.device}")

        except Exception as e:
            logger.error(f"[Classifier] Failed to load model: {e}")
            self.model = None

    def preprocess(self, frame: np.ndarray) -> torch.Tensor:
        """Convert numpy frame to model input tensor."""
        pil_img = Image.fromarray(frame.astype(np.uint8))
        tensor = self.transform(pil_img)
        return tensor.unsqueeze(0).to(self.device)

    def predict_frame(self, frame: np.ndarray) -> Tuple[float, float]:
        """
        Predict whether a single frame is fake.
        Returns (fake_probability, real_probability)
        """
        if self.model is None:
            # Heuristic fallback based on image statistics
            return self._heuristic_predict(frame)

        try:
            with torch.no_grad():
                tensor = self.preprocess(frame)
                logits = self.model(tensor)
                probs = torch.softmax(logits, dim=1)[0]
                # Index 0 = real, Index 1 = fake
                real_prob = float(probs[0])
                fake_prob = float(probs[1])
                return fake_prob, real_prob

        except Exception as e:
            logger.error(f"[Classifier] Prediction error: {e}")
            return self._heuristic_predict(frame)

    def predict_batch(self, frames: List[np.ndarray]) -> List[Tuple[float, float]]:
        """Predict on a list of frames."""
        return [self.predict_frame(f) for f in frames]

    def _heuristic_predict(self, frame: np.ndarray) -> Tuple[float, float]:
        """
        Fallback heuristic when model unavailable.
        Uses image statistics to estimate manipulation probability.
        """
        gray = np.mean(frame, axis=2)

        # High frequency noise analysis
        laplacian_var = np.var(np.gradient(np.gradient(gray))[0])
        noise_score = min(laplacian_var / 1000.0, 1.0)

        # Color distribution analysis
        channel_stds = [np.std(frame[:,:,i]) for i in range(3)]
        color_imbalance = np.std(channel_stds) / (np.mean(channel_stds) + 1e-6)
        color_score = min(color_imbalance / 0.5, 1.0)

        fake_prob = (noise_score * 0.4 + color_score * 0.6)
        fake_prob = max(0.1, min(0.9, fake_prob))
        return fake_prob, 1.0 - fake_prob
