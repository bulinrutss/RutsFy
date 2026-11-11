"""URLs públicas com prefixo opcional (proxy em /rutsfy/)."""

from __future__ import annotations

from app.config import settings


def public_path(path: str) -> str:
    if not path.startswith("/"):
        path = f"/{path}"
    base = settings.normalized_base_path()
    if not base:
        return path
    if path == base or path.startswith(f"{base}/"):
        return path
    return f"{base}{path}"
