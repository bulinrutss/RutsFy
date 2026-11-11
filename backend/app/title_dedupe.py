"""Agrupa versões parecidas da mesma faixa (Official, PULSE, Remaster, etc.)."""

from __future__ import annotations

import re
import unicodedata
from typing import Any

from app.metadata_util import infer_artist_from_title

_ARTIST_TITLE_RE = re.compile(r"^(.+?)\s+[-–|·]\s+(.+)$", re.I)

_PART_WORD = {
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "i": "1",
    "ii": "2",
    "iii": "3",
    "iv": "4",
    "v": "5",
}

_NOISE_RE = re.compile(
    r"\b("
    r"official(?:\s+music)?\s+video|"
    r"official\s+audio|"
    r"lyrics?(?:\s+video)?|"
    r"remastered?(?:\s+\d{4})?|"
    r"restored|"
    r"re-?edited|"
    r"extended|"
    r"visuali[sz]er|"
    r"full\s+hd|"
    r"\bhd\b|"
    r"\b4k\b|"
    r"\b8k\b|"
    r"\bmv\b|"
    r"audio\s+only|"
    r"vevo|"
    r"pulse|"
    r"mono\s+mix|"
    r"stereo|"
    r"anniversary|"
    r"deluxe|"
    r"explicit|"
    r"clean\s+version|"
    r"radio\s+edit|"
    r"single\s+version|"
    r"album\s+version|"
    r"original\s+mix|"
    r"video\s+analysis|"
    r"\banalysis\b|"
    r"react(?:ion)?|"
    r"review|"
    r"explained|"
    r"breakdown|"
    r"meaning|"
    r"espanol|"
    r"español|"
    r"ingles|"
    r"ingl[eê]s|"
    r"english|"
    r"spanish|"
    r"subtitles?|"
    r"legendado?|"
    r"traducido|"
    r"translation|"
    r"with\s+lyrics"
    r")\b",
    re.I,
)

_JUNK_TITLE_SEGMENT_RE = re.compile(
    r"^(?:"
    r"video\s+analysis|analysis|react(?:ion)?|review|explained|breakdown|meaning|"
    r"espanol|español|ingles|ingl[eê]s|english|spanish|"
    r"subtitles?|legendado?|traducido|translation|"
    r"hd|4k|8k"
    r")(?:\s*[/|]\s*.*)?$",
    re.I,
)

_ARTIST_CHANNEL_NOISE_RE = re.compile(
    r"\s*[-–]\s*topic\s*$|\s+vevo\s*$|\s+official\s*$|\s+records\s*$|\s+music\s*$",
    re.I,
)


def _fold_ascii(text: str) -> str:
    folded = unicodedata.normalize("NFKD", text or "")
    return folded.encode("ascii", "ignore").decode("ascii")


def _normalize_part_token(raw: str) -> str:
    s = raw.strip().lower()
    if s.isdigit():
        return s
    return _PART_WORD.get(s, s)


def _part_from_text(text: str) -> str | None:
    m = re.search(
        r"(?:part|pt\.?)[\s,:-]*(" + "|".join(_PART_WORD.keys()) + r"|\d+)",
        text,
        re.I,
    )
    if not m:
        return None
    return _normalize_part_token(m.group(1))


def normalize_artist_key(artist: str | None, channel: str | None = None) -> str:
    for raw in (artist, channel):
        if not raw:
            continue
        a = _fold_ascii(str(raw).strip().lower())
        a = _ARTIST_CHANNEL_NOISE_RE.sub("", a)
        a = re.sub(r"[^\w\s]", " ", a)
        a = re.sub(r"\s+", " ", a).strip()
        if a:
            return a
    return ""


_JUNK_SEGMENT_WORDS = frozenset(
    {
        "analysis",
        "espanol",
        "español",
        "ingles",
        "inglês",
        "english",
        "spanish",
        "subtitles",
        "subtitle",
        "legendado",
        "traducido",
        "translation",
        "hd",
        "4k",
        "8k",
        "video",
        "react",
        "reaction",
        "review",
        "explained",
        "breakdown",
        "meaning",
    }
)


def _is_junk_title_segment(segment: str) -> bool:
    s = _fold_ascii((segment or "").strip().lower())
    s = re.sub(r"[^\w\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    if not s:
        return True
    if _JUNK_TITLE_SEGMENT_RE.match(s):
        return True
    tokens = [t for t in s.split() if t]
    return bool(tokens) and all(t in _JUNK_SEGMENT_WORDS for t in tokens)


def _strip_song_title(title: str, artist: str | None, channel: str | None) -> str:
    t = (title or "").strip()
    art = (infer_artist_from_title(t) or artist or channel or "").strip()
    if art:
        esc = re.escape(art)
        t = re.sub(rf"^{esc}\s*[-–|·:]\s*", "", t, flags=re.I).strip()
    else:
        m = _ARTIST_TITLE_RE.match(t)
        if m:
            t = m.group(2).strip()
    parts = re.split(r"\s[-–—]\s+", t)
    if len(parts) > 1:
        kept = [parts[0].strip()]
        for seg in parts[1:]:
            if seg.strip() and not _is_junk_title_segment(seg):
                kept.append(seg.strip())
        t = " - ".join(kept) if len(kept) > 1 else kept[0]
    return t


def normalize_song_core(song_title: str) -> str:
    t = _fold_ascii((song_title or "").strip().lower())
    if not t:
        return ""
    part = _part_from_text(t)
    t = re.sub(r'["\']', " ", t)
    t = re.sub(r"[\[\(\{][^\]\)\}]*[\]\)\}]", " ", t)
    t = _NOISE_RE.sub(" ", t)
    t = re.sub(
        r"\b(?:part|pt\.?)[\s,:-]*(" + "|".join(_PART_WORD.keys()) + r"|\d+)\b",
        " ",
        t,
        flags=re.I,
    )
    t = re.sub(r"\b\d{4}\b", " ", t)
    t = re.sub(r"[^\w\s]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    if part:
        t = f"{t} part {part}".strip()
    return t


def similar_track_dedupe_key(item: dict[str, Any]) -> str | None:
    title = item.get("title")
    if not title or not item.get("videoId"):
        return None
    from_title = infer_artist_from_title(str(title))
    artist_key = normalize_artist_key(
        from_title or item.get("artist"),
        item.get("channelTitle"),
    )
    song = _strip_song_title(str(title), from_title or item.get("artist"), item.get("channelTitle"))
    core = normalize_song_core(song)
    if not core:
        return None
    return f"{artist_key}|{core}"


def _dedupe_quality(item: dict[str, Any]) -> tuple[int, int, int]:
    title = str(item.get("title") or "").lower()
    junk = any(
        x in title
        for x in (
            "analysis",
            "español",
            "espanol",
            "inglés",
            "ingles",
            "react",
            "review",
            "explained",
            "legendado",
        )
    )
    official = "official" in title
    on_server = bool(item.get("onServer"))
    return (1 if on_server else 0, 1 if official else 0, 0 if junk else 1)


def dedupe_similar_tracks(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Uma faixa lógica por chave; prefere Official / já no servidor."""
    index_by_key: dict[str, int] = {}
    out: list[dict[str, Any]] = []
    for item in items:
        key = similar_track_dedupe_key(item)
        if not key:
            out.append(item)
            continue
        if key not in index_by_key:
            index_by_key[key] = len(out)
            out.append(item)
            continue
        idx = index_by_key[key]
        if _dedupe_quality(item) > _dedupe_quality(out[idx]):
            out[idx] = item
    return out
