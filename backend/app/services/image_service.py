"""Upload validation and normalization.

Gemini bills per image token and selfies from phones are large, so every upload
is re-encoded to a bounded JPEG. The declared content type is never trusted:
the bytes are decoded with Pillow and rejected when they are not a real image
or when they are larger than the configured limit.
"""

from __future__ import annotations

import hashlib
import io
from dataclasses import dataclass

from PIL import Image, ImageOps, ImageStat, UnidentifiedImageError

from app.core.config import Settings
from app.core.exceptions import InvalidImageError


def read_upload(upload, config):
    raw = upload.file.read(config.max_upload_mb * 1024 * 1024 + 1)
    return raw


@dataclass(frozen=True)
class PreparedImage:
    data: bytes
    mime_type: str
    width: int
    height: int
    brightness: int
    sha256: str


def prepare_image(raw: bytes, config: Settings) -> PreparedImage:
    if not raw:
        raise InvalidImageError("El archivo de imagen está vacío.")

    max_bytes = config.max_upload_mb * 1024 * 1024
    if len(raw) > max_bytes:
        raise InvalidImageError(f"La imagen supera el límite de {config.max_upload_mb} MB.")

    try:
        with Image.open(io.BytesIO(raw)) as probe:
            if (
                probe.format not in {"JPEG", "PNG", "WEBP"}
                or probe.width * probe.height > 40_000_000
            ):
                raise InvalidImageError("Formato o dimensiones de imagen no permitidos.")
            probe.verify()
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as exc:
        raise InvalidImageError(
            "El archivo no es una imagen válida (se esperaba JPEG, PNG o WebP)."
        ) from exc

    with Image.open(io.BytesIO(raw)) as image:
        image = ImageOps.exif_transpose(image)

        if image.mode in {"RGBA", "LA", "P"}:
            background = Image.new("RGB", image.size, (255, 255, 255))
            background.paste(image.convert("RGBA"), mask=image.convert("RGBA").split()[-1])
            image = background
        elif image.mode != "RGB":
            image = image.convert("RGB")

        image.thumbnail((config.image_max_side, config.image_max_side), Image.Resampling.LANCZOS)

        brightness = int(ImageStat.Stat(image.convert("L")).mean[0])

        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=88, optimize=True, progressive=True)
        data = buffer.getvalue()
        width, height = image.size

    return PreparedImage(
        data=data,
        mime_type="image/jpeg",
        width=width,
        height=height,
        brightness=max(0, min(100, round(brightness / 2.55))),
        sha256=hashlib.sha256(data).hexdigest(),
    )


def low_light_warning(image: PreparedImage) -> str | None:
    """Server-side sanity check mirroring the client light calibrator."""
    if image.brightness < 35:
        return (
            "La imagen es muy oscura (brillo "
            f"{image.brightness}/100). Repite la captura con luz frontal natural."
        )
    return None
