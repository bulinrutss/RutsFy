"""Carrega chaves da YouTube Data API (ordem = prioridade)."""

from __future__ import annotations

import hashlib
import re

from app.config import Settings, settings

_KEY_LINE = re.compile(r"^AIza[0-9A-Za-z_-]+$")


def key_fingerprint(api_key: str) -> str:
    return hashlib.sha256(api_key.encode("utf-8")).hexdigest()[:16]


def _parse_keys_blob(blob: str) -> list[str]:
    out: list[str] = []
    for part in re.split(r"[\n,;]+", blob):
        token = part.strip().strip('"').strip("'")
        if token and _KEY_LINE.fullmatch(token):
            out.append(token)
    return out


def resolve_youtube_api_keys(cfg: Settings | None = None) -> list[str]:
    """Ordem: YOUTUBE_API_KEY (principal), depois cada entrada em YOUTUBE_API_KEYS."""
    cfg = cfg or settings
    ordered: list[str] = []

    primary = (cfg.youtube_api_key or "").strip()
    if primary and _KEY_LINE.fullmatch(primary):
        ordered.append(primary)

    ordered.extend(_parse_keys_blob(cfg.youtube_api_keys or ""))

    seen: set[str] = set()
    unique: list[str] = []
    for k in ordered:
        if k not in seen:
            seen.add(k)
            unique.append(k)
    return unique
