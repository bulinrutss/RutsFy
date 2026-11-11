"""Metadados hidratados por mix (Explorar) — evita repetir videos.list ao reabrir."""

from __future__ import annotations

import json
import time
from pathlib import Path
from threading import Lock
from typing import Any

from app.youtube_cache import TTL_SEARCH_MIX

_LOCK = Lock()
_MAX_ENTRIES_PER_MIX = 1200

_CATALOG_KEYS = (
    "duration",
    "description",
    "descriptionOriginal",
    "descriptionLang",
    "viewCount",
    "channelId",
    "channelTitle",
    "artist",
    "thumbnailUrl",
    "title",
    "publishedAt",
    "url",
)


def _root() -> Path:
    from app.downloader import downloads_root

    p = downloads_root() / "youtube_api_cache" / "mix_catalog"
    p.mkdir(parents=True, exist_ok=True)
    return p


def _path(mix_id: str) -> Path:
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in mix_id.strip())
    return _root() / f"{safe or 'mix'}.json"


def _read_mix_file(mix_id: str) -> dict[str, Any] | None:
    path = _path(mix_id)
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
    entries = data.get("entries")
    return entries if isinstance(entries, dict) else None


def _write_mix_file(mix_id: str, entries: dict[str, Any]) -> None:
    path = _path(mix_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    now = time.time()
    body = {
        "mixId": mix_id,
        "cachedAt": now,
        "expiresAt": now + TTL_SEARCH_MIX,
        "entries": entries,
    }
    path.write_text(json.dumps(body, ensure_ascii=False), encoding="utf-8")


def _slice_catalog_item(item: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {"cachedAt": time.time()}
    for key in _CATALOG_KEYS:
        val = item.get(key)
        if val is not None and val != "":
            out[key] = val
    vid = item.get("videoId")
    if isinstance(vid, str) and vid:
        out["videoId"] = vid
    return out


def _trim_entries(entries: dict[str, Any]) -> dict[str, Any]:
    if len(entries) <= _MAX_ENTRIES_PER_MIX:
        return entries
    ranked = sorted(
        entries.items(),
        key=lambda kv: float((kv[1] or {}).get("cachedAt") or 0),
        reverse=True,
    )
    keep = dict(ranked[:_MAX_ENTRIES_PER_MIX])
    return keep


def get_mix_catalog_for_ids(mix_id: str | None, video_ids: list[str]) -> dict[str, dict[str, Any]]:
    if not mix_id:
        return {}
    ids = [v for v in video_ids if v]
    if not ids:
        return {}
    with _LOCK:
        entries = _read_mix_file(mix_id) or {}
        out: dict[str, dict[str, Any]] = {}
        for vid in ids:
            row = entries.get(vid)
            if isinstance(row, dict) and row.get("videoId"):
                out[vid] = {k: row[k] for k in _CATALOG_KEYS if k in row and row[k] is not None}
        return out


def _mix_catalog_entries_list(mix_id: str) -> list[dict[str, Any]]:
    with _LOCK:
        entries = _read_mix_file(mix_id) or {}
    items: list[dict[str, Any]] = []
    for row in entries.values():
        if isinstance(row, dict) and row.get("videoId"):
            items.append(dict(row))
    items.sort(key=lambda x: float(x.get("cachedAt") or 0), reverse=True)
    return items


def mix_catalog_entry_count(mix_id: str | None) -> int:
    if not mix_id:
        return 0
    with _LOCK:
        entries = _read_mix_file(mix_id) or {}
    return sum(
        1
        for row in entries.values()
        if isinstance(row, dict) and row.get("videoId")
    )


def mix_catalog_discoverable_count(mix_id: str | None) -> int:
    """Total de faixas listáveis (exclui blocklist / limite de tamanho e duração)."""
    if not mix_id:
        return 0
    from app.duration_policy import should_hide_from_catalog

    return sum(
        1
        for item in _mix_catalog_entries_list(mix_id)
        if not should_hide_from_catalog(item)
    )


def mix_catalog_more_items(
    mix_id: str,
    exclude_video_ids: set[str] | frozenset[str],
    *,
    exclude_song_keys: set[str] | frozenset[str] | None = None,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """Próximas faixas do catálogo local do mix que ainda não estão na lista da UI."""
    lim = max(1, min(int(limit), 100))
    out: list[dict[str, Any]] = []
    from app.duration_policy import should_hide_from_catalog
    from app.title_dedupe import similar_track_dedupe_key

    blocked_keys: set[str] = set(exclude_song_keys or ())
    seen_keys: set[str] = set(blocked_keys)
    if exclude_video_ids:
        for row in (get_mix_catalog_for_ids(mix_id, list(exclude_video_ids)) or {}).values():
            k = similar_track_dedupe_key(row)
            if k:
                seen_keys.add(k)

    for item in _mix_catalog_entries_list(mix_id):
        vid = item.get("videoId")
        if not isinstance(vid, str) or not vid or vid in exclude_video_ids:
            continue
        if should_hide_from_catalog(item):
            continue
        song_key = similar_track_dedupe_key(item)
        if song_key and song_key in seen_keys:
            continue
        out.append(item)
        if song_key:
            seen_keys.add(song_key)
        if len(out) >= lim:
            break
    return out


def list_loaded_mix_ids(*, min_entries: int = 1) -> list[str]:
    """Mixes cujo catálogo local já foi preenchido (playlist carregada)."""
    need = max(1, int(min_entries))
    root = _root()
    out: list[str] = []
    for path in root.glob("*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError, json.JSONDecodeError):
            continue
        if not isinstance(data, dict):
            continue
        expires = data.get("expiresAt")
        if isinstance(expires, (int, float)) and time.time() > expires:
            continue
        entries = data.get("entries")
        if not isinstance(entries, dict) or len(entries) < need:
            continue
        mix_id = data.get("mixId")
        if isinstance(mix_id, str) and mix_id.strip():
            out.append(mix_id.strip())
            continue
        stem = path.stem.replace("_", "-")
        if stem and stem != "mix":
            out.append(stem)
    return sorted(set(out))


def store_mix_catalog_items(mix_id: str | None, items: list[dict[str, Any]]) -> None:
    if not mix_id or not items:
        return
    with _LOCK:
        entries = dict(_read_mix_file(mix_id) or {})
        for item in items:
            if not isinstance(item, dict):
                continue
            sliced = _slice_catalog_item(item)
            vid = sliced.get("videoId")
            if not isinstance(vid, str) or not vid:
                continue
            prev = entries.get(vid) if isinstance(entries.get(vid), dict) else {}
            merged = {**prev, **sliced}
            entries[vid] = merged
        entries = _trim_entries(entries)
        _write_mix_file(mix_id, entries)


def _patch_item_from_sources(
    item: dict[str, Any], *sources: dict[str, Any] | None
) -> dict[str, Any]:
    patch: dict[str, Any] = {}
    for src in sources:
        if not src:
            continue
        for key in _CATALOG_KEYS:
            if src.get(key) is not None and not item.get(key) and key not in patch:
                patch[key] = src[key]
    return {**item, **patch} if patch else item


def enrich_items_from_disk_catalog(
    mix_id: str | None,
    items: list[dict[str, Any]],
    *,
    user_id: str | None = None,
) -> list[dict[str, Any]]:
    """Preenche duração/descrição a partir de conta, library.json e cache do mix."""
    if not items:
        return items
    ids = [i.get("videoId") for i in items if isinstance(i.get("videoId"), str)]
    if not ids:
        return items

    from app.downloader import stored_catalog_entries

    stored = stored_catalog_entries(ids, user_id)
    mix_cat = get_mix_catalog_for_ids(mix_id, ids) if mix_id else {}
    if not stored and not mix_cat:
        return items

    out: list[dict[str, Any]] = []
    for item in items:
        vid = item.get("videoId")
        if not isinstance(vid, str):
            out.append(item)
            continue
        out.append(_patch_item_from_sources(item, stored.get(vid), mix_cat.get(vid)))
    return out
