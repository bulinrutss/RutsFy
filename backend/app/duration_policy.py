"""Limite de duração para novas faixas (busca/download). Arquivos já no disco ficam."""

from __future__ import annotations

import re
from typing import Any

from app.config import settings

_ISO8601_DURATION = re.compile(
    r"^P"
    r"(?:(?P<days>\d+)D)?"
    r"(?:T"
    r"(?:(?P<hours>\d+)H)?"
    r"(?:(?P<minutes>\d+)M)?"
    r"(?:(?P<seconds>\d+(?:\.\d+)?)S)?"
    r")?$",
    re.IGNORECASE,
)

DOWNLOAD_TOO_LONG_MESSAGE = (
    "Faixas com mais de 20 minutos não podem ser baixadas. "
    "As que já estão no servidor continuam disponíveis."
)


def max_track_duration_seconds() -> int:
    return max(60, int(settings.max_track_duration_seconds))


def parse_duration_seconds(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        n = float(value)
        return n if n >= 0 else None
    s = str(value).strip()
    if not s:
        return None
    if re.fullmatch(r"\d+(?:\.\d+)?", s):
        return float(s)
    m = _ISO8601_DURATION.match(s.upper())
    if not m:
        return None
    days = int(m.group("days") or 0)
    hours = int(m.group("hours") or 0)
    minutes = int(m.group("minutes") or 0)
    seconds = float(m.group("seconds") or 0)
    return days * 86400 + hours * 3600 + minutes * 60 + seconds


def audio_on_server(video_id: str | None) -> bool:
    if not video_id:
        return False
    from app.downloader import find_existing

    return find_existing(video_id) is not None


def mark_items_on_server(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Marca faixas cujo áudio já está em downloads/."""
    for item in items:
        vid = item.get("videoId")
        if vid and audio_on_server(vid):
            item["onServer"] = True
    return items


def is_over_max_track_duration(duration: Any) -> bool:
    sec = parse_duration_seconds(duration)
    if sec is None:
        return False
    return sec > max_track_duration_seconds()


def should_hide_from_catalog(item: dict[str, Any]) -> bool:
    """Oculta em busca/explorar/canal; mantém se o áudio já foi baixado."""
    vid = item.get("videoId")
    if audio_on_server(vid):
        return False
    if vid:
        from app.download_blocklist import is_blocklisted

        if is_blocklisted(vid):
            return True
    from app.size_policy import is_over_max_estimated_file_size

    if is_over_max_estimated_file_size(item.get("duration")):
        return True
    if is_over_max_track_duration(item.get("duration")):
        return True
    return False


def filter_discoverable_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [i for i in items if not should_hide_from_catalog(i)]


def assert_download_allowed(*, video_id: str, duration: Any) -> None:
    from app.download_blocklist import assert_not_blocklisted
    from app.downloader import DownloadError

    if audio_on_server(video_id):
        return
    assert_not_blocklisted(video_id)
    sec = parse_duration_seconds(duration)
    if sec is not None and sec > max_track_duration_seconds():
        from app.download_blocklist import add_to_blocklist

        add_to_blocklist(
            video_id,
            reason="too_long",
            size_bytes=int(sec),
        )
        raise DownloadError(DOWNLOAD_TOO_LONG_MESSAGE)
