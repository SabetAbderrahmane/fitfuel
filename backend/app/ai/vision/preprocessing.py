from __future__ import annotations

from io import BytesIO
from pathlib import Path

from PIL import Image


def load_pil_image_from_bytes(image_bytes: bytes) -> Image.Image:
    """
    Load an image from raw bytes and normalize it to RGB.
    """
    image = Image.open(BytesIO(image_bytes))
    return image.convert("RGB")


def load_pil_image_from_path(image_path: str | Path) -> Image.Image:
    """
    Load an image from a file path and normalize it to RGB.
    """
    image = Image.open(image_path)
    return image.convert("RGB")