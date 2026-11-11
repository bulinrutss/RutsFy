"""Cache em disco das respostas da API YouTube (economiza cota).

Buscas (texto, mix, por data): TTL 30 dias; detalhes de vídeo 60 dias.
"""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from threading import Lock
from typing import Any

from app.downloader import downloads_root

_LOCK = Lock()

# Segundos (TTL longo = menos cota YouTube; mixes/texto revalidam a cada 30 dias)
TTL_SEARCH_TEXT = 30 * 86400
TTL_SEARCH_MIX = 30 * 86400
TTL_SEARCH_FRESH = 30 * 86400
TTL_VIDEO = 60 * 86400
TTL_PLAYLIST = 30 * 86400


def _root() -> Path:
    p = downloads_root() / "youtube_api_cache"
    p.mkdir(parents=True, exist_ok=True)
    return p


def _read_file(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict):
        return None
    expires = data.get("expiresAt")
    if isinstance(expires, (int, float)) and time.time() > expires:
        try:
            path.unlink(missing_ok=True)
        except OSError:
            pass
        return None
    payload = data.get("payload")
    return payload if payload is not None else None


def _write_file(path: Path, payload: Any, ttl_seconds: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    now = time.time()
    body = {
        "cachedAt": now,
        "expiresAt": now + max(60, ttl_seconds),
        "payload": payload,
    }
    path.write_text(json.dumps(body, ensure_ascii=False), encoding="utf-8")


def search_ttl_seconds(
    *,
    mix_id: str | None,
    published_after: str | None,
    published_before: str | None,
    order: str | None,
) -> int:
    if published_after or published_before or (order or "").lower() == "date":
        return TTL_SEARCH_FRESH
    if mix_id:
        return TTL_SEARCH_MIX
    return TTL_SEARCH_TEXT


def search_cache_key(
    *,
    q: str,
    max_results: int,
    page_token: str | None,
    published_after: str | None,
    published_before: str | None,
    order: str | None,
    mix_id: str | None = None,
) -> str:
    blob = json.dumps(
        {
            "q": q,
            "mixId": mix_id or "",
            "maxResults": max_results,
            "pageToken": page_token or "",
            "publishedAfter": published_after or "",
            "publishedBefore": published_before or "",
            "order": order or "",
        },
        sort_keys=True,
        ensure_ascii=True,
    )
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:48]


def get_search_cached(key: str) -> dict[str, Any] | None:
    with _LOCK:
        raw = _read_file(_root() / "search" / f"{key}.json")
    return raw if isinstance(raw, dict) else None


def put_search_cached(key: str, payload: dict[str, Any], ttl_seconds: int) -> None:
    with _LOCK:
        _write_file(_root() / "search" / f"{key}.json", payload, ttl_seconds)


def get_videos_cached(video_ids: list[str]) -> tuple[list[dict[str, Any]], list[str]]:
    """Retorna (itens em ordem parcial, ids faltando)."""
    found: list[dict[str, Any]] = []
    missing: list[str] = []
    with _LOCK:
        for vid in video_ids:
            if not vid:
                continue
            item = _read_file(_root() / "videos" / f"{vid}.json")
            if isinstance(item, dict):
                found.append(item)
            else:
                missing.append(vid)
    return found, missing


def put_videos_cached(items: list[dict[str, Any]]) -> None:
    with _LOCK:
        for item in items:
            vid = item.get("id") if isinstance(item, dict) else None
            if isinstance(vid, str) and vid:
                _write_file(_root() / "videos" / f"{vid}.json", item, TTL_VIDEO)


def merge_videos_response(
    video_ids: list[str],
    cached_items: list[dict[str, Any]],
    fetched_items: list[dict[str, Any]],
) -> dict[str, Any]:
    by_id: dict[str, dict[str, Any]] = {}
    for item in cached_items + fetched_items:
        if isinstance(item, dict) and item.get("id"):
            by_id[item["id"]] = item
    ordered = [by_id[vid] for vid in video_ids if vid in by_id]
    return {"items": ordered}


def playlist_cache_key(playlist_id: str, max_results: int, page_token: str | None = None) -> str:
    blob = json.dumps(
        {"playlistId": playlist_id, "maxResults": max_results, "pageToken": page_token or ""},
        sort_keys=True,
    )
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:48]


def channel_uploads_cache_key(channel_id: str) -> str:
    return hashlib.sha256(f"uploads:{channel_id}".encode("utf-8")).hexdigest()[:48]


def get_channel_uploads_cached(channel_id: str) -> str | None:
    with _LOCK:
        raw = _read_file(_root() / "channel_uploads" / f"{channel_uploads_cache_key(channel_id)}.json")
    if isinstance(raw, str) and raw:
        return raw
    return None


def put_channel_uploads_cached(channel_id: str, uploads_playlist_id: str) -> None:
    with _LOCK:
        _write_file(
            _root() / "channel_uploads" / f"{channel_uploads_cache_key(channel_id)}.json",
            uploads_playlist_id,
            TTL_PLAYLIST,
        )


def get_playlist_cached(key: str) -> dict[str, Any] | None:
    with _LOCK:
        raw = _read_file(_root() / "playlist" / f"{key}.json")
    return raw if isinstance(raw, dict) else None


def put_playlist_cached(key: str, payload: dict[str, Any]) -> None:
    with _LOCK:
        _write_file(_root() / "playlist" / f"{key}.json", payload, TTL_PLAYLIST)
