"""Two-tier cache used by the INCI scanner.

Layer 1 (``inci:ocr:<sha256>``) avoids paying twice for the same label photo.
Layer 2 (``inci:verdict:<sha256>``) avoids recomputing the same verdict.

Redis is optional: when ``REDIS_URL`` is unset or unreachable the process falls
back to a bounded in-memory TTL cache, which is enough for a single-node demo.
"""

from __future__ import annotations

import json
import logging
import threading
import time
from collections import OrderedDict
from typing import Any, Protocol, runtime_checkable

from app.core.config import Settings

logger = logging.getLogger(__name__)


@runtime_checkable
class CacheBackend(Protocol):
    def get_json(self, key: str) -> Any | None: ...

    def set_json(self, key: str, value: Any, ttl_seconds: int | None = None) -> None: ...

    def delete(self, key: str) -> None: ...


class InMemoryTTLCache:
    """Thread-safe LRU + TTL cache (the API runs sync endpoints in a threadpool)."""

    def __init__(self, max_entries: int = 512) -> None:
        self._max_entries = max_entries
        self._store: OrderedDict[str, tuple[float, Any]] = OrderedDict()
        self._lock = threading.Lock()

    def get_json(self, key: str) -> Any | None:
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            expires_at, value = entry
            if expires_at and expires_at < time.monotonic():
                self._store.pop(key, None)
                return None
            self._store.move_to_end(key)
            return value

    def set_json(self, key: str, value: Any, ttl_seconds: int | None = None) -> None:
        expires_at = time.monotonic() + ttl_seconds if ttl_seconds else 0.0
        with self._lock:
            self._store[key] = (expires_at, value)
            self._store.move_to_end(key)
            while len(self._store) > self._max_entries:
                self._store.popitem(last=False)

    def delete(self, key: str) -> None:
        with self._lock:
            self._store.pop(key, None)

    def clear(self) -> None:
        with self._lock:
            self._store.clear()


class RedisCache:
    """Redis-backed cache; values are JSON encoded."""

    def __init__(self, client: Any) -> None:
        self._client = client

    def get_json(self, key: str) -> Any | None:
        raw = self._client.get(key)
        if raw is None:
            return None
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            logger.warning("Discarding corrupt cache entry for key %s", key)
            self._client.delete(key)
            return None

    def set_json(self, key: str, value: Any, ttl_seconds: int | None = None) -> None:
        payload = json.dumps(value, ensure_ascii=False)
        if ttl_seconds:
            self._client.setex(key, ttl_seconds, payload)
        else:
            self._client.set(key, payload)

    def delete(self, key: str) -> None:
        self._client.delete(key)


def build_cache(config: Settings) -> CacheBackend:
    if not config.redis_url:
        return InMemoryTTLCache()

    try:
        import redis

        client = redis.Redis.from_url(
            config.redis_url, socket_connect_timeout=1.5, socket_timeout=1.5
        )
        client.ping()
    except Exception as exc:  # pragma: no cover - depends on local infra
        logger.warning("Redis unavailable (%s); using the in-memory INCI cache instead", exc)
        return InMemoryTTLCache()

    logger.info("INCI cache backed by Redis")
    return RedisCache(client)
