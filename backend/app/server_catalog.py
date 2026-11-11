"""Catálogo local: faixas já no disco, sem busca na API do YouTube."""

from __future__ import annotations

import re
import unicodedata
from functools import lru_cache
from typing import Any

from app.downloader import _enrich, _file_info, downloads_root
from app.metadata_util import resolve_track_artist
from app.mixes import MIX_CATEGORIES, _all_mixes_raw

_AUDIO_SUFFIXES = {".opus", ".ogg", ".m4a", ".mp3", ".webm", ".wav"}

_RECENT_SHELF_ID = "recentes"

_DECADE_SHELVES: list[tuple[str, str, list[str]]] = [
    ("decade:70", "Anos 70", ["70s", "anos 70", "1970", "1971", "1972", "1973", "1974", "1975", "1976", "1977", "1978", "1979"]),
    ("decade:80", "Anos 80", ["80s", "anos 80", "1980", "1981", "1982", "1983", "1984", "1985", "1986", "1987", "1988", "1989"]),
    ("decade:90", "Anos 90", ["90s", "anos 90", "1990", "1991", "1992", "1993", "1994", "1995", "1996", "1997", "1998", "1999"]),
    ("decade:00", "Anos 2000", ["2000s", "anos 2000", "2000", "2001", "2002", "2003", "2004", "2005", "2006", "2007", "2008", "2009"]),
    ("decade:10", "Anos 2010", ["2010s", "anos 2010", "2010", "2011", "2012", "2013", "2014", "2015", "2016", "2017", "2018", "2019"]),
    ("decade:20", "Anos 2020", ["2020s", "anos 2020", "2020", "2021", "2022", "2023", "2024", "2025", "2026"]),
]

_ARTIST_SECTION_ID = "artistas"

_CHANNEL_TOPIC_RE = re.compile(r"\s*-\s*topic\s*$", re.I)
_CHANNEL_VEVO_RE = re.compile(r"\s*vevo\s*$", re.I)
_JUNK_ARTIST_RE = re.compile(
    r"(atividade de|provided to youtube|auto-generated|youtube channel|official audio|lyrics video|music video)",
    re.I,
)


def _normalize_text(value: str) -> str:
    s = unicodedata.normalize("NFKD", value or "")
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return s.lower()


def _slug(text: str) -> str:
    s = _normalize_text(text)
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s or "artista"


def _item_haystack(item: dict[str, Any]) -> str:
    parts = [
        item.get("title") or "",
        item.get("artist") or "",
        item.get("channelTitle") or "",
        item.get("description") or "",
    ]
    return _normalize_text(" ".join(p for p in parts if p))


def _mix_tokens(query: str) -> list[str]:
    q = _normalize_text(query.replace("official audio", "").replace("…", " "))
    tokens = [t for t in re.split(r"\s+", q) if len(t) > 2]
    return tokens


def _score_mix(item: dict[str, Any], mix: dict[str, Any]) -> int:
    hay = _item_haystack(item)
    tokens = _mix_tokens(mix.get("query") or "")
    if not tokens:
        return 0
    score = 0
    for t in tokens:
        if t in hay:
            score += 3 if len(t) > 4 else 1
    # exige pelo menos metade dos tokens relevantes (mín. 2 pontos)
    need = max(2, len(tokens) // 2)
    return score if score >= need else 0


def _assign_mix_id(item: dict[str, Any]) -> str | None:
    best_id: str | None = None
    best_score = 0
    for mix in _all_mixes_raw():
        sc = _score_mix(item, mix)
        if sc > best_score:
            best_score = sc
            best_id = mix["id"]
    return best_id


def _year_from_published(value: Any) -> int | None:
    if not value:
        return None
    m = re.search(r"(19|20)\d{2}", str(value))
    if not m:
        return None
    try:
        return int(m.group(0))
    except ValueError:
        return None


def _decade_id_for_year(year: int) -> str | None:
    if 1970 <= year <= 1979:
        return "decade:70"
    if 1980 <= year <= 1989:
        return "decade:80"
    if 1990 <= year <= 1999:
        return "decade:90"
    if 2000 <= year <= 2009:
        return "decade:00"
    if 2010 <= year <= 2019:
        return "decade:10"
    if 2020 <= year <= 2039:
        return "decade:20"
    return None


def _assign_decade_id(item: dict[str, Any]) -> str | None:
    year = _year_from_published(item.get("publishedAt"))
    if year is not None:
        by_pub = _decade_id_for_year(year)
        if by_pub:
            return by_pub
    hay = _item_haystack(item)
    for shelf_id, _label, keys in _DECADE_SHELVES:
        for k in keys:
            if _normalize_text(k) in hay:
                return shelf_id
    return None


def _clean_channel_name(channel: str) -> str:
    c = channel.strip()
    c = _CHANNEL_TOPIC_RE.sub("", c).strip()
    c = _CHANNEL_VEVO_RE.sub("", c).strip()
    return c


def _display_artist(item: dict[str, Any]) -> str | None:
    art = resolve_track_artist(title=item.get("title"), artist=item.get("artist"))
    if art and not _JUNK_ARTIST_RE.search(art) and len(art) <= 80:
        return art.strip()
    ch = item.get("channelTitle") or ""
    if not ch or _JUNK_ARTIST_RE.search(ch):
        return None
    cleaned = _clean_channel_name(ch)
    if not cleaned or len(cleaned) > 80:
        return None
    low = _normalize_text(cleaned)
    if low in ("various artists", "soundtrack", "trilha sonora"):
        return None
    return cleaned


def _cover_preview(items: list[dict[str, Any]], n: int = 4) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for item in items:
        url = item.get("thumbnailUrl")
        if not url or url in seen:
            continue
        seen.add(url)
        out.append(str(url))
        if len(out) >= n:
            break
    return out


def _slice_item(item: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "videoId",
        "title",
        "artist",
        "channelId",
        "channelTitle",
        "duration",
        "thumbnailUrl",
        "url",
        "storedAt",
        "onServer",
    )
    return {k: item[k] for k in keys if item.get(k) is not None}


def _make_shelf(
    shelf_id: str,
    label: str,
    items: list[dict[str, Any]],
    *,
    subtitle: str | None = None,
    shelf_limit: int,
) -> dict[str, Any]:
    sub = subtitle or f"{len(items)} faixas no servidor"
    return {
        "id": shelf_id,
        "label": label,
        "subtitle": sub,
        "total": len(items),
        "coverPreview": _cover_preview(items),
        "items": [_slice_item(i) for i in items[:shelf_limit]],
    }


@lru_cache(maxsize=1)
def _cached_catalog_mtime() -> float:
    root = downloads_root()
    try:
        mt = root.stat().st_mtime
    except OSError:
        mt = 0.0
    for f in root.iterdir():
        if f.is_file() and f.suffix.lower() in _AUDIO_SUFFIXES:
            try:
                mt = max(mt, f.stat().st_mtime)
            except OSError:
                pass
    return mt


_catalog_cache: tuple[float, list[dict[str, Any]], dict[str, Any]] | None = None


def _build_catalog_index(items: list[dict[str, Any]]) -> dict[str, Any]:
    by_mix: dict[str, list[dict[str, Any]]] = {}
    by_decade: dict[str, list[dict[str, Any]]] = {}
    by_artist: dict[str, list[dict[str, Any]]] = {}
    artist_labels: dict[str, str] = {}

    for item in items:
        mix_id = _assign_mix_id(item)
        if mix_id:
            item["freeMixId"] = mix_id
            by_mix.setdefault(mix_id, []).append(item)

        decade_id = _assign_decade_id(item)
        if decade_id:
            item["freeDecadeId"] = decade_id
            by_decade.setdefault(decade_id, []).append(item)

        artist = _display_artist(item)
        if artist:
            slug = _slug(artist)
            item["freeArtistSlug"] = slug
            item["artist"] = artist
            by_artist.setdefault(slug, []).append(item)
            artist_labels[slug] = artist

    return {
        "byMix": by_mix,
        "byDecade": by_decade,
        "byArtist": by_artist,
        "artistLabels": artist_labels,
    }


def list_server_audio_items(*, force_refresh: bool = False) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    global _catalog_cache
    mtime = _cached_catalog_mtime()
    if not force_refresh and _catalog_cache and _catalog_cache[0] == mtime:
        return list(_catalog_cache[1]), dict(_catalog_cache[2])

    root = downloads_root()
    files = [
        f
        for f in root.iterdir()
        if f.is_file() and f.suffix.lower() in _AUDIO_SUFFIXES and not f.name.startswith(".")
    ]
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    items = [_enrich(_file_info(f, already_existed=True)) for f in files]
    for item in items:
        item["onServer"] = True
    index = _build_catalog_index(items)
    _catalog_cache = (mtime, items, index)
    return list(items), index


def free_catalog_summary(*, shelf_limit: int = 24) -> dict[str, Any]:
    items, index = list_server_audio_items()
    limit = max(1, min(int(shelf_limit), 80))
    by_mix = index["byMix"]
    by_decade = index["byDecade"]
    by_artist = index["byArtist"]
    artist_labels: dict[str, str] = index["artistLabels"]

    sections: list[dict[str, Any]] = []

    if items:
        sections.append(
            {
                "id": "destaques",
                "label": "Destaques",
                "shelves": [
                    _make_shelf(
                        _RECENT_SHELF_ID,
                        "Adicionadas recentemente",
                        items[: max(limit, 12)],
                        subtitle=f"As {min(len(items), limit)} mais recentes",
                        shelf_limit=limit,
                    )
                ],
            }
        )

    mix_by_id = {m["id"]: m for m in _all_mixes_raw()}
    for cat in MIX_CATEGORIES:
        shelves: list[dict[str, Any]] = []
        for mix in cat.get("mixes") or []:
            mid = mix["id"]
            bucket = by_mix.get(mid) or []
            if not bucket:
                continue
            meta = mix_by_id.get(mid) or mix
            shelves.append(
                _make_shelf(
                    f"mix:{mid}",
                    meta.get("label") or mid,
                    bucket,
                    subtitle=f"RutsFy · {meta.get('subtitle') or 'No servidor'}",
                    shelf_limit=limit,
                )
            )
        if shelves:
            sections.append({"id": cat["id"], "label": cat["label"], "shelves": shelves})

    decade_shelves: list[dict[str, Any]] = []
    for shelf_id, label, _keys in _DECADE_SHELVES:
        bucket = by_decade.get(shelf_id) or []
        if not bucket:
            continue
        decade_shelves.append(
            _make_shelf(
                shelf_id,
                label,
                bucket,
                subtitle="Década · no servidor",
                shelf_limit=limit,
            )
        )
    if decade_shelves:
        sections.append({"id": "decadas", "label": "Por década", "shelves": decade_shelves})

    artist_rank = sorted(by_artist.items(), key=lambda x: (-len(x[1]), artist_labels.get(x[0], x[0])))
    artist_shelves: list[dict[str, Any]] = []
    for slug, bucket in artist_rank[:48]:
        if not bucket:
            continue
        name = artist_labels.get(slug) or bucket[0].get("artist") or slug
        artist_shelves.append(
            _make_shelf(
                f"artist:{slug}",
                name,
                bucket,
                subtitle=f"{len(bucket)} faixas · artista",
                shelf_limit=limit,
            )
        )
    if artist_shelves:
        sections.append({"id": _ARTIST_SECTION_ID, "label": "Artistas", "shelves": artist_shelves})

    return {
        "total": len(items),
        "free": True,
        "noSearchQuota": True,
        "sections": sections,
    }


def _filter_category_items(category_id: str, items: list[dict[str, Any]], index: dict[str, Any]) -> tuple[list[dict[str, Any]], str]:
    cat_id = (category_id or "").strip()
    if cat_id == _RECENT_SHELF_ID:
        return items, "Adicionadas recentemente"

    if cat_id.startswith("mix:"):
        mid = cat_id[4:]
        mix = next((m for m in _all_mixes_raw() if m["id"] == mid), None)
        label = mix["label"] if mix else mid
        return list(index["byMix"].get(mid) or []), label

    if cat_id.startswith("artist:"):
        slug = cat_id[7:]
        bucket = list(index["byArtist"].get(slug) or [])
        label = index["artistLabels"].get(slug) or slug.replace("-", " ").title()
        return bucket, label

    if cat_id.startswith("decade:"):
        bucket = list(index["byDecade"].get(cat_id) or [])
        label = next((lbl for sid, lbl, _ in _DECADE_SHELVES if sid == cat_id), cat_id)
        return bucket, label

    raise ValueError("Categoria inválida")


def free_category_items(
    category_id: str,
    *,
    offset: int = 0,
    limit: int = 50,
) -> dict[str, Any]:
    items, index = list_server_audio_items()
    off = max(0, int(offset))
    lim = max(1, min(int(limit), 200))

    filtered, label = _filter_category_items(category_id, items, index)
    page = filtered[off : off + lim]
    return {
        "categoryId": category_id,
        "label": label,
        "total": len(filtered),
        "offset": off,
        "limit": lim,
        "items": [_slice_item(i) for i in page],
        "free": True,
        "noSearchQuota": True,
    }


def list_server_mix_ids() -> set[str]:
    _items, index = list_server_audio_items()
    return set(index["byMix"].keys())


def list_server_video_ids() -> list[str]:
    items, _index = list_server_audio_items()
    return [i["videoId"] for i in items if i.get("videoId")]


def free_not_in_user_library(
    user_id: str,
    *,
    offset: int = 0,
    limit: int = 100,
) -> dict[str, Any]:
    """Faixas no disco que o usuário ainda não salvou com +."""
    from app.users_db import list_user_library

    items, _index = list_server_audio_items()
    lib_ids = {x["videoId"] for x in list_user_library(user_id) if x.get("videoId")}
    extra = [i for i in items if i.get("videoId") and i["videoId"] not in lib_ids]
    off = max(0, int(offset))
    lim = max(1, min(int(limit), 300))
    page = extra[off : off + lim]
    return {
        "total": len(extra),
        "offset": off,
        "limit": lim,
        "items": [_slice_item(i) for i in page],
        "free": True,
        "noSearchQuota": True,
    }


def search_server_catalog(
    query: str,
    *,
    offset: int = 0,
    limit: int = 50,
) -> dict[str, Any]:
    q = (query or "").strip()
    items, _index = list_server_audio_items()
    off = max(0, int(offset))
    lim = max(1, min(int(limit), 200))

    if not q:
        page = items[off : off + lim]
        return {
            "query": "",
            "total": len(items),
            "offset": off,
            "limit": lim,
            "items": [_slice_item(i) for i in page],
            "free": True,
            "noSearchQuota": True,
        }

    tokens = [t for t in re.split(r"\s+", _normalize_text(q)) if t]
    matched: list[dict[str, Any]] = []
    for item in items:
        hay = _item_haystack(item)
        if all(t in hay for t in tokens):
            matched.append(item)

    page = matched[off : off + lim]
    return {
        "query": q,
        "total": len(matched),
        "offset": off,
        "limit": lim,
        "items": [_slice_item(i) for i in page],
        "free": True,
        "noSearchQuota": True,
    }
