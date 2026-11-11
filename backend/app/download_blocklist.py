"""Faixas bloqueadas para download (ex.: arquivo acima do limite de MB)."""

from __future__ import annotations

import json
import threading
import time
from pathlib import Path
from typing import Any

_LOCK = threading.Lock()


def _path() -> Path:
    from app.downloader import downloads_root

    return downloads_root() / "download_blocklist.json"


def _load() -> dict[str, Any]:
    path = _path()
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _save(data: dict[str, Any]) -> None:
    path = _path()
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def is_blocklisted(video_id: str | None) -> bool:
    if not video_id:
        return False
    with _LOCK:
        return video_id in _load()


def entry(video_id: str) -> dict[str, Any] | None:
    with _LOCK:
        raw = _load().get(video_id)
    return dict(raw) if isinstance(raw, dict) else None


def list_video_ids() -> list[str]:
    with _LOCK:
        return sorted(_load().keys())


def add_to_blocklist(
    video_id: str,
    *,
    reason: str,
    size_bytes: int | None = None,
    title: str | None = None,
) -> None:
    if not video_id:
        return
    now = time.time()
    with _LOCK:
        data = _load()
        data[video_id] = {
            "reason": (reason or "blocked")[:500],
            "sizeBytes": size_bytes,
            "title": (title or "")[:300] or None,
            "blockedAt": now,
        }
        _save(data)


def assert_not_blocklisted(video_id: str) -> None:
    from app.downloader import DownloadError

    if not is_blocklisted(video_id):
        return
    ent = entry(video_id) or {}
    reason = str(ent.get("reason") or "")
    if reason == "too_large":
        from app.size_policy import download_too_large_message

        raise DownloadError(download_too_large_message())
    if reason == "too_long":
        from app.duration_policy import DOWNLOAD_TOO_LONG_MESSAGE

        raise DownloadError(DOWNLOAD_TOO_LONG_MESSAGE)
    raise DownloadError("Esta faixa está bloqueada para download no servidor.")
