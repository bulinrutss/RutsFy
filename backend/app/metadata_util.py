from __future__ import annotations

import re

_ARTIST_TITLE_RE = re.compile(r"^(.+?)\s+[-–|·]\s+(.+)$")


def infer_artist_from_title(title: str | None) -> str | None:
    if not title:
        return None
    m = _ARTIST_TITLE_RE.match(title.strip())
    if not m:
        return None
    artist = m.group(1).strip()
    if not artist or len(artist) > 80:
        return None
    return artist


def resolve_track_artist(
    *,
    title: str | None,
    artist: str | None = None,
) -> str | None:
    if artist and str(artist).strip():
        return str(artist).strip()
    return infer_artist_from_title(title)
