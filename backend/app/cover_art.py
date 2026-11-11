"""Proxy de capas do YouTube (same-origin) para Media Session / notificação no celular."""

from __future__ import annotations

import re

import httpx

_YT_VIDEO_ID = re.compile(r"^[a-zA-Z0-9_-]{11}$")

_SIZE_TO_YT = {
    "1280": "maxresdefault",
    "480": "hqdefault",
    "320": "mqdefault",
}


def normalize_video_id(video_id: str) -> str | None:
    vid = (video_id or "").strip()
    if not _YT_VIDEO_ID.fullmatch(vid):
        return None
    return vid


async def fetch_track_cover(video_id: str, *, size: str = "1280") -> tuple[bytes, str]:
    vid = normalize_video_id(video_id)
    if not vid:
        raise ValueError("video_id inválido")

    yt_name = _SIZE_TO_YT.get(size, "maxresdefault")
    url = f"https://i.ytimg.com/vi/{vid}/{yt_name}.jpg"

    async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
        resp = await client.get(url)
        if resp.status_code == 404 and yt_name == "maxresdefault":
            return await fetch_track_cover(video_id, size="480")
        resp.raise_for_status()
        media = (resp.headers.get("content-type") or "image/jpeg").split(";")[0].strip()
        if not media.startswith("image/"):
            media = "image/jpeg"
        return resp.content, media
