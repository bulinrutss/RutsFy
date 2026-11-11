"""Acha o vídeo no YouTube via yt-dlp (sem search.list) para uma faixa do catálogo."""

from __future__ import annotations

import json
import re
import subprocess
import threading
import time
import unicodedata
from typing import Any

from app.config import settings
from app.downloader import downloads_root, resolve_ytdlp, _ytdlp_network_args

_VIDEO_ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")
_LOCK = threading.Lock()
_RESOLVE_TTL_SEC = 14 * 24 * 3600
_SEARCH_TIMEOUT_SEC = 45


class ResolveError(Exception):
    pass


def _fold(value: str) -> str:
    text = unicodedata.normalize("NFKD", value or "")
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def _cache_path():
    return downloads_root() / "deezer_resolve.json"


def _cache_get(key: str) -> str | None:
    try:
        raw = json.loads(_cache_path().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    entry = raw.get(key) if isinstance(raw, dict) else None
    if not isinstance(entry, dict):
        return None
    video_id = entry.get("videoId")
    at = entry.get("at")
    if not isinstance(video_id, str) or not _VIDEO_ID_RE.fullmatch(video_id):
        return None
    if not isinstance(at, (int, float)) or time.time() - float(at) > _RESOLVE_TTL_SEC:
        return None
    return video_id


def _cache_set(key: str, video_id: str) -> None:
    path = _cache_path()
    with _LOCK:
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(raw, dict):
                raw = {}
        except (OSError, ValueError):
            raw = {}
        raw[key] = {"videoId": video_id, "at": time.time()}
        path.write_text(json.dumps(raw, ensure_ascii=False), encoding="utf-8")


def lookup_known_audio(deezer_ids: list[Any]) -> dict[str, dict[str, Any]]:
    """videoId já resolvido e se o áudio está no disco. Não busca no YouTube."""
    wanted: list[str] = []
    seen: set[str] = set()
    for raw_id in deezer_ids:
        if raw_id is None:
            continue
        key = str(raw_id).strip()
        if not key or key in seen:
            continue
        seen.add(key)
        wanted.append(key)
    if not wanted:
        return {}
    try:
        raw = json.loads(_cache_path().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    if not isinstance(raw, dict):
        return {}
    now = time.time()
    found: dict[str, str] = {}
    for key in wanted:
        entry = raw.get(f"dz:{key}")
        if not isinstance(entry, dict):
            continue
        video_id = entry.get("videoId")
        at = entry.get("at")
        if not isinstance(video_id, str) or not _VIDEO_ID_RE.fullmatch(video_id):
            continue
        if not isinstance(at, (int, float)) or now - float(at) > _RESOLVE_TTL_SEC:
            continue
        found[key] = video_id
    if not found:
        return {}
    root = downloads_root()
    suffixes = (".opus", ".ogg", ".m4a", ".mp3", ".webm", ".wav")

    def on_disk(video_id: str) -> bool:
        return any((root / f"{video_id}{ext}").is_file() for ext in suffixes)

    return {
        key: {"videoId": video_id, "onServer": on_disk(video_id)}
        for key, video_id in found.items()
    }


def stamp_known_audio(tracks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    known = lookup_known_audio(
        [item.get("deezerId") for item in tracks if isinstance(item, dict)]
    )
    if not known:
        return tracks
    for item in tracks:
        if not isinstance(item, dict) or item.get("deezerId") is None:
            continue
        info = known.get(str(item.get("deezerId")))
        if not info:
            continue
        item["videoId"] = item.get("videoId") or info["videoId"]
        if info["onServer"]:
            item["onServer"] = True
    return tracks


def _cache_key(deezer_id: Any, artist: str, title: str) -> str:
    if deezer_id is not None and str(deezer_id).strip():
        return f"dz:{deezer_id}"
    return f"q:{_fold(artist)}|{_fold(title)}"


def pick_youtube_match(
    entries: list[dict[str, Any]],
    *,
    artist: str,
    title: str,
    duration_sec: float | None,
) -> dict[str, Any] | None:
    """Escolhe o vídeo cuja duração e título mais batem com a faixa do catálogo."""
    want_title = _fold(title)
    want_artist = _fold(artist)
    title_tokens = [tok for tok in want_title.split() if len(tok) > 2]
    max_sec = max(60, int(settings.max_track_duration_seconds))
    best: tuple[float, dict[str, Any]] | None = None
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        video_id = str(entry.get("id") or "")
        if not _VIDEO_ID_RE.fullmatch(video_id):
            continue
        yt_title = str(entry.get("title") or "")
        folded = _fold(yt_title)
        channel = _fold(str(entry.get("channel") or entry.get("uploader") or ""))
        if any(bad in folded for bad in ("full album", "album completo", "playlist completa")):
            continue
        duration = entry.get("duration")
        dur = float(duration) if isinstance(duration, (int, float)) and duration > 0 else None
        if dur is not None and dur > max_sec:
            continue
        score = 0.0
        if title_tokens:
            hits = sum(1 for tok in title_tokens if tok in folded)
            score += 8 * (hits / len(title_tokens))
        elif want_title and want_title in folded:
            score += 8
        if want_artist and (want_artist in folded or want_artist in channel):
            score += 4
        if dur is not None and duration_sec:
            delta = abs(dur - duration_sec)
            window = max(25.0, duration_sec * 0.2)
            if delta > window:
                score -= 6
            else:
                score += 5 * (1 - delta / window)
        elif dur is None:
            score -= 1
        if score < 3:
            continue
        if best is None or score > best[0]:
            best = (score, {"videoId": video_id, "score": score})
    return None if best is None else best[1]


def _search_entries(query: str) -> list[dict[str, Any]]:
    cmd = [
        resolve_ytdlp(),
        "--flat-playlist",
        "--no-warnings",
        "--no-playlist",
        "-J",
        *_ytdlp_network_args(),
        f"ytsearch5:{query}",
    ]
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=_SEARCH_TIMEOUT_SEC,
        )
    except subprocess.TimeoutExpired as exc:
        raise ResolveError("A busca do áudio demorou demais. Tente de novo.") from exc
    if proc.returncode != 0:
        raise ResolveError("Não foi possível procurar o áudio desta faixa.")
    try:
        payload = json.loads(proc.stdout or "{}")
    except ValueError as exc:
        raise ResolveError("Não foi possível procurar o áudio desta faixa.") from exc
    entries = payload.get("entries") if isinstance(payload, dict) else None
    if not isinstance(entries, list):
        return []
    return [row for row in entries if isinstance(row, dict)]


def resolve_catalog_track(
    *,
    title: str,
    artist: str = "",
    deezer_id: Any = None,
    duration_sec: float | None = None,
) -> dict[str, Any]:
    clean_title = (title or "").strip()
    if not clean_title:
        raise ResolveError("Faixa sem título.")
    clean_artist = (artist or "").strip()
    key = _cache_key(deezer_id, clean_artist, clean_title)
    cached = _cache_get(key)
    if cached:
        return {"videoId": cached, "fromCache": True}
    query = f"{clean_artist} - {clean_title}" if clean_artist else clean_title
    match = pick_youtube_match(
        _search_entries(query),
        artist=clean_artist,
        title=clean_title,
        duration_sec=duration_sec,
    )
    if not match:
        raise ResolveError("Não achei um áudio compatível com esta faixa.")
    _cache_set(key, match["videoId"])
    return {"videoId": match["videoId"], "fromCache": False}
