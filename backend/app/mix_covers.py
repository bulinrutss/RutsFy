"""Capas salvas por mix (Explorar) — pool grande, preview de 4 aleatórias."""

from __future__ import annotations

import json
import random
from pathlib import Path
from threading import Lock
from typing import Any

from app.downloader import downloads_root

_LOCK = Lock()
MAX_STORED = 56
PREVIEW_COUNT = 4


def _covers_path() -> Path:
    return downloads_root() / "mix_covers.json"


def _normalize_thumb(url: str) -> str:
    u = url.strip()
    if not u:
        return ""
    return u.replace("/mqdefault", "/hqdefault").replace("/sddefault", "/hqdefault")


def _load_all() -> dict[str, list[str]]:
    path = _covers_path()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, json.JSONDecodeError):
        return {}
    mixes = data.get("mixes") if isinstance(data, dict) else None
    if not isinstance(mixes, dict):
        return {}
    out: dict[str, list[str]] = {}
    for mix_id, urls in mixes.items():
        if not isinstance(mix_id, str) or not isinstance(urls, list):
            continue
        clean = [_normalize_thumb(u) for u in urls if isinstance(u, str)]
        out[mix_id] = [u for u in clean if u]
    return out


def _save_all(mixes: dict[str, list[str]]) -> None:
    path = _covers_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"mixes": mixes}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def list_stored(mix_id: str) -> list[str]:
    with _LOCK:
        return list(_load_all().get(mix_id) or [])


def add_mix_covers(mix_id: str, thumbnail_urls: list[str]) -> list[str]:
    """Acrescenta URLs únicas; mantém no máximo MAX_STORED (mais recentes primeiro)."""
    incoming = [_normalize_thumb(u) for u in thumbnail_urls if isinstance(u, str)]
    incoming = [u for u in incoming if u]
    if not incoming:
        with _LOCK:
            return list(_load_all().get(mix_id) or [])

    with _LOCK:
        all_mixes = _load_all()
        pool = list(all_mixes.get(mix_id) or [])
        seen = set(pool)
        for url in incoming:
            if url in seen:
                continue
            pool.insert(0, url)
            seen.add(url)
        pool = pool[:MAX_STORED]
        all_mixes[mix_id] = pool
        _save_all(all_mixes)
        return pool


def preview_covers_for_mix(mix_id: str, count: int = PREVIEW_COUNT) -> list[str]:
    """Até `count` URLs; se o pool for menor, repete aleatoriamente para encher o mosaico."""
    with _LOCK:
        pool = list(_load_all().get(mix_id) or [])
    if not pool:
        return []
    if len(pool) >= count:
        return random.sample(pool, count)
    return [random.choice(pool) for _ in range(count)]


def enrich_mix_dict(mix: dict[str, Any]) -> dict[str, Any]:
    mix_id = mix.get("id")
    if isinstance(mix_id, str) and mix_id:
        mix = {**mix, "coverPreview": preview_covers_for_mix(mix_id)}
    else:
        mix = {**mix, "coverPreview": []}
    return mix
