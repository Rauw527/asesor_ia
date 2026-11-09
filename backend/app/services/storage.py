"""Pluggable media storage.

Phase 1 writes to the local filesystem and serves the files through FastAPI's
static mount. Swapping in S3/Firebase means implementing the same two methods.
"""

from __future__ import annotations

import re
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol

_ALLOWED_PATH = re.compile(r"^[A-Za-z0-9_./-]+$")


class StorageBackend(Protocol):
    def save(self, data: bytes, category: str) -> str: ...

    def url_for(self, relative_path: str) -> str: ...

    def read(self, relative_path: str) -> bytes: ...


class LocalStorage:
    def __init__(self, root: Path, url_prefix: str) -> None:
        self._root = Path(root)
        self._url_prefix = url_prefix.rstrip("/")
        self._root.mkdir(parents=True, exist_ok=True)

    def save(self, data: bytes, category: str) -> str:
        safe_category = re.sub(r"[^a-z0-9_-]", "", category.lower()) or "misc"
        folder = datetime.now(UTC).strftime("%Y-%m")
        relative = f"{safe_category}/{folder}/{uuid.uuid4().hex}.jpg"
        destination = self._root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
        return relative

    def url_for(self, relative_path: str) -> str:
        if not _ALLOWED_PATH.match(relative_path) or ".." in relative_path:
            raise ValueError("Ruta de media inválida.")
        return f"{self._url_prefix}/{relative_path.lstrip('/')}"

    def read(self, relative_path: str) -> bytes:
        if not _ALLOWED_PATH.match(relative_path) or ".." in relative_path:
            raise ValueError("Ruta de media inválida.")
        return (self._root / relative_path).read_bytes()
