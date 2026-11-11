"""Limite de tamanho (MB) para novos downloads."""

from __future__ import annotations

from typing import Any

from app.config import settings
from app.downloader import DownloadError, find_existing


def max_track_file_bytes() -> int:
    mb = int(settings.max_track_file_size_mb or 0)
    if mb <= 0:
        return 0
    return mb * 1024 * 1024


def download_too_large_message() -> str:
    mb = int(settings.max_track_file_size_mb or 0)
    if mb <= 0:
        return "Faixa muito pesada para baixar."
    return (
        f"Faixa muito pesada (limite {mb} MB). "
        "Não será baixada; entrou na lista de bloqueio do servidor."
    )


def _opus_bitrate_bps() -> int:
    raw = (settings.audio_bitrate or "64K").strip().upper().rstrip("K")
    try:
        return max(32_000, int(raw) * 1000)
    except ValueError:
        return 64_000


def estimated_saved_opus_bytes(duration_sec: float) -> int:
    """Tamanho esperado do .opus no servidor (para ocultar em listas)."""
    return int(duration_sec * _opus_bitrate_bps() / 8 * 1.1)


def _estimate_bytes_from_duration(duration_sec: float | None) -> int | None:
    if duration_sec is None or duration_sec <= 0:
        return None
    # Áudio YouTube típico ≤ ~192 kbps antes do Opus; margem generosa.
    return int(duration_sec * 256_000 / 8)


def is_over_max_estimated_file_size(duration: Any) -> bool:
    from app.duration_policy import parse_duration_seconds

    limit = max_track_file_bytes()
    if limit <= 0:
        return False
    sec = parse_duration_seconds(duration)
    if sec is None:
        return False
    return estimated_saved_opus_bytes(sec) > limit


def assert_estimated_size_allowed(
    *,
    video_id: str,
    duration: Any = None,
    estimated_bytes: int | None = None,
) -> None:
    """Antes do download — estimativa via yt-dlp ou duração."""
    from app.duration_policy import parse_duration_seconds

    limit = max_track_file_bytes()
    if limit <= 0:
        return
    if find_existing(video_id):
        return

    est = estimated_bytes
    if est is None:
        sec = parse_duration_seconds(duration)
        est = _estimate_bytes_from_duration(sec)

    if est is not None and est > limit:
        from app.download_blocklist import add_to_blocklist

        add_to_blocklist(
            video_id,
            reason="too_large",
            size_bytes=est,
        )
        raise DownloadError(download_too_large_message())


def enforce_file_size_or_block(
    video_id: str,
    path: Any,
    *,
    title: str | None = None,
) -> None:
    """Depois do download/upload — apaga e blacklist se passou do limite."""
    from pathlib import Path

    from app.download_blocklist import add_to_blocklist

    limit = max_track_file_bytes()
    if limit <= 0:
        return
    p = Path(path)
    if not p.is_file():
        return
    size = p.stat().st_size
    if size <= limit:
        return
    add_to_blocklist(
        video_id,
        reason="too_large",
        size_bytes=size,
        title=title,
    )
    try:
        p.unlink()
    except OSError:
        pass
    raise DownloadError(download_too_large_message())
