"""Catálogo Deezer (gêneros, artistas, álbuns, playlists). Sem áudio completo."""

from __future__ import annotations

import json
import sqlite3
import threading
import time
from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.parse import urlencode

import httpx

from app.deezer_resolve import stamp_known_audio
from app.downloader import downloads_root

_API = "https://api.deezer.com"
_UA = "RutsFy/1.0 (https://ruts.dev/rutsfy)"
_LOCK = threading.Lock()
_DAY_CACHE_TZ = timezone(timedelta(hours=-3))


class DeezerError(Exception):
    pass


_MEM_MAX = 4000
_MEM: dict[str, dict[str, Any]] = {}
_DB: sqlite3.Connection | None = None
_HTTP: httpx.AsyncClient | None = None


def _db() -> sqlite3.Connection:
    global _DB
    if _DB is None:
        conn = sqlite3.connect(downloads_root() / "deezer_cache.sqlite", check_same_thread=False, timeout=10)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("CREATE TABLE IF NOT EXISTS cache (key TEXT PRIMARY KEY, at REAL NOT NULL, data TEXT NOT NULL)")
        conn.execute("DELETE FROM cache WHERE at < ?", (time.time() - 14 * 86400,))
        conn.commit()
        _DB = conn
    return _DB


def _remember(key: str, entry: dict[str, Any]) -> None:
    if len(_MEM) >= _MEM_MAX:
        _MEM.pop(next(iter(_MEM)))
    _MEM[key] = entry


def _http() -> httpx.AsyncClient:
    global _HTTP
    if _HTTP is None or _HTTP.is_closed:
        _HTTP = httpx.AsyncClient(timeout=20.0, headers={"User-Agent": _UA, "Accept-Language": "pt-BR"})
    return _HTTP


def _last_6am(now: float | None = None) -> float:
    """Janela da semana começa segunda-feira às 6h em Brasília (UTC−3)."""
    current = datetime.fromtimestamp(now if now is not None else time.time(), tz=_DAY_CACHE_TZ)
    boundary = current.replace(hour=6, minute=0, second=0, microsecond=0)
    boundary -= timedelta(days=boundary.weekday())
    if current < boundary:
        boundary -= timedelta(days=7)
    return boundary.timestamp()


def _cache_entry(key: str) -> dict[str, Any] | None:
    entry = _MEM.get(key)
    if entry is not None:
        return entry
    with _LOCK:
        try:
            row = _db().execute("SELECT at, data FROM cache WHERE key = ?", (key,)).fetchone()
        except sqlite3.Error:
            return None
    if not row:
        return None
    try:
        entry = {"at": row[0], "data": json.loads(row[1])}
    except ValueError:
        return None
    _remember(key, entry)
    return entry


def _cache_get(key: str, ttl_sec: int, *, until_6am: bool = False) -> Any | None:
    entry = _cache_entry(key)
    if not entry:
        return None
    at = entry.get("at")
    if not isinstance(at, (int, float)):
        return None
    if until_6am:
        if float(at) < _last_6am():
            return None
    elif time.time() - float(at) > ttl_sec:
        return None
    data = entry.get("data")
    return data if isinstance(data, dict) else None


def _cache_stale(key: str) -> dict[str, Any] | None:
    entry = _cache_entry(key)
    if not entry:
        return None
    data = entry.get("data")
    return data if isinstance(data, dict) else None


def _cache_set(key: str, data: Any) -> None:
    at = time.time()
    _remember(key, {"at": at, "data": data})
    with _LOCK:
        try:
            _db().execute(
                "INSERT OR REPLACE INTO cache (key, at, data) VALUES (?, ?, ?)",
                (key, at, json.dumps(data, ensure_ascii=False)),
            )
            _db().commit()
        except sqlite3.Error:
            pass


def seconds_to_iso(value: Any) -> str | None:
    try:
        total = int(value)
    except (TypeError, ValueError):
        return None
    if total <= 0:
        return None
    hours, rem = divmod(total, 3600)
    minutes, seconds = divmod(rem, 60)
    if hours:
        return f"PT{hours}H{minutes}M{seconds}S"
    return f"PT{minutes}M{seconds}S"


def _picture(obj: dict[str, Any] | None, *keys: str) -> str:
    if not isinstance(obj, dict):
        return ""
    for key in keys:
        val = obj.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return ""


def _genre_name(obj: dict[str, Any] | None) -> str:
    if not isinstance(obj, dict):
        return ""
    genres = obj.get("genres")
    data = genres.get("data") if isinstance(genres, dict) else None
    if isinstance(data, list) and data:
        name = data[0].get("name") if isinstance(data[0], dict) else None
        if isinstance(name, str):
            return name.strip()
    return ""


def _track(
    raw: dict[str, Any],
    *,
    genre: str = "",
    album_title: str = "",
    album_id: Any = None,
    cover: str = "",
    artist_name: str = "",
    artist_id: Any = None,
) -> dict[str, Any] | None:
    title = str(raw.get("title") or "").strip()
    if not title or raw.get("id") is None:
        return None
    artist = raw.get("artist") if isinstance(raw.get("artist"), dict) else {}
    album = raw.get("album") if isinstance(raw.get("album"), dict) else {}
    name = str(artist.get("name") or artist_name or "").strip()
    alb = str(album.get("title") or album_title or "").strip()
    thumb = _picture(album, "cover_medium", "cover_big", "cover") or cover
    return {
        "deezerId": raw.get("id"),
        "title": title,
        "artist": name,
        "artistId": artist.get("id") if artist.get("id") is not None else artist_id,
        "album": alb,
        "albumId": album.get("id") if album.get("id") is not None else album_id,
        "genre": (genre or _genre_name(album) or _genre_name(raw)).strip(),
        "duration": seconds_to_iso(raw.get("duration")),
        "thumbnailUrl": thumb,
        "catalogSource": "deezer",
    }


async def _get(
    path: str,
    params: dict[str, Any] | None = None,
    *,
    ttl: int,
    until_6am: bool = False,
) -> dict[str, Any]:
    query = {k: v for k, v in (params or {}).items() if v is not None}
    key = path + ("?" + urlencode(sorted((str(k), str(v)) for k, v in query.items())) if query else "")
    cached = _cache_get(key, ttl, until_6am=until_6am)
    if isinstance(cached, dict):
        return cached
    url = f"{_API}{path}"
    try:
        response = await _http().get(url, params=query)
        payload = response.json()
    except (httpx.HTTPError, ValueError) as exc:
        if until_6am:
            stale = _cache_stale(key)
            if stale is not None:
                return stale
        if isinstance(exc, ValueError):
            raise DeezerError("Resposta inválida do catálogo.") from exc
        raise DeezerError("Catálogo indisponível no momento.") from exc
    if response.status_code != 200 or not isinstance(payload, dict):
        if until_6am:
            stale = _cache_stale(key)
            if stale is not None:
                return stale
        raise DeezerError("Catálogo indisponível no momento.")
    if isinstance(payload.get("error"), dict):
        if until_6am:
            stale = _cache_stale(key)
            if stale is not None:
                return stale
        message = str(payload["error"].get("message") or "").strip()
        raise DeezerError(message or "Catálogo indisponível no momento.")
    _cache_set(key, payload)
    return payload


def _rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    data = payload.get("data")
    if not isinstance(data, list):
        return []
    return [row for row in data if isinstance(row, dict)]


async def _maybe(awaitable: Any) -> dict[str, Any]:
    try:
        payload = await awaitable
    except DeezerError:
        return {}
    return payload if isinstance(payload, dict) else {}


async def home() -> dict[str, Any]:
    genres_payload, playlists_payload = await _gather(
        _get("/genre", ttl=6 * 3600),
        _maybe(_get("/chart/0/playlists", {"limit": 12}, ttl=0, until_6am=True)),
    )
    genres = []
    for row in _rows(genres_payload):
        if row.get("id") in (None, 0):
            continue
        name = str(row.get("name") or "").strip()
        if not name:
            continue
        genres.append(
            {
                "id": row.get("id"),
                "name": name,
                "picture": _picture(row, "picture_medium", "picture_big", "picture"),
            }
        )
    playlists = [_playlist_card(row) for row in _rows(playlists_payload)]
    return {"genres": genres, "playlists": [p for p in playlists if p]}


def _artists_on_tracks(rows: list[Any], *, limit: int = 24) -> list[dict[str, Any]]:
    """Artistas que de fato aparecem nas faixas do gênero.

    /genre/{id}/artists devolve a parada do país, não o gênero.
    """
    artists: list[dict[str, Any]] = []
    seen: set[Any] = set()
    for row in rows:
        if not isinstance(row, dict):
            continue
        artist = row.get("artist") if isinstance(row.get("artist"), dict) else None
        if not artist or artist.get("id") in (None, "") or artist.get("id") in seen:
            continue
        artist_name = str(artist.get("name") or "").strip()
        if not artist_name:
            continue
        seen.add(artist.get("id"))
        artists.append(
            {
                "id": artist.get("id"),
                "name": artist_name,
                "picture": _picture(artist, "picture_medium", "picture_big", "picture"),
            }
        )
        if len(artists) >= limit:
            break
    return artists


async def genre_page(genre_id: int) -> dict[str, Any]:
    info, charts = await _gather(
        _get(f"/genre/{genre_id}", ttl=6 * 3600),
        _maybe(_get(f"/editorial/{genre_id}/charts", {"limit": 50}, ttl=0, until_6am=True)),
    )
    name = str(info.get("name") or "").strip() or "Gênero"
    if genre_id == 0:
        name = "Em alta"
    track_rows_raw = charts.get("tracks") if isinstance(charts.get("tracks"), dict) else {}
    chart_tracks = track_rows_raw.get("data") if isinstance(track_rows_raw.get("data"), list) else []
    artists = _artists_on_tracks(chart_tracks)
    track_rows = charts.get("tracks") if isinstance(charts.get("tracks"), dict) else {}
    playlist_rows = charts.get("playlists") if isinstance(charts.get("playlists"), dict) else {}
    tracks = []
    for row in track_rows.get("data") or []:
        if not isinstance(row, dict):
            continue
        item = _track(row, genre=name if genre_id else "")
        if item:
            tracks.append(item)
    playlists = []
    for row in playlist_rows.get("data") or []:
        if isinstance(row, dict):
            card = _playlist_card(row)
            if card:
                playlists.append(card)
    return {
        "genre": {
            "id": genre_id,
            "name": name,
            "picture": _picture(info, "picture_medium", "picture_big", "picture"),
        },
        "artists": artists,
        "tracks": stamp_known_audio(tracks),
        "playlists": playlists,
    }


async def artist_page(artist_id: int) -> dict[str, Any]:
    cache_key = f"artist_page:{artist_id}"
    cached = _cache_get(cache_key, 0, until_6am=True)
    if isinstance(cached, dict) and cached.get("artist"):
        return cached

    info, top, albums_payload = await _gather(
        _get(f"/artist/{artist_id}", ttl=0, until_6am=True),
        _get(f"/artist/{artist_id}/top", {"limit": 25}, ttl=0, until_6am=True),
        _get(f"/artist/{artist_id}/albums", {"limit": 40}, ttl=0, until_6am=True),
    )
    name = str(info.get("name") or "").strip() or "Artista"
    picture = _picture(info, "picture_medium", "picture_big", "picture")
    tracks = []
    for row in _rows(top):
        item = _track(row, artist_name=name, artist_id=artist_id)
        if item:
            tracks.append(item)
    albums = []
    for row in _rows(albums_payload):
        title = str(row.get("title") or "").strip()
        if not title or row.get("id") is None:
            continue
        albums.append(
            {
                "id": row.get("id"),
                "title": title,
                "picture": _picture(row, "cover_medium", "cover_big", "cover"),
                "releaseDate": row.get("release_date") or "",
            }
        )
    page = {
        "artist": {"id": artist_id, "name": name, "picture": picture},
        "tracks": stamp_known_audio(tracks),
        "albums": albums,
    }
    _cache_set(cache_key, page)
    return page


async def album_page(album_id: int) -> dict[str, Any]:
    info = await _get(f"/album/{album_id}", ttl=24 * 3600)
    title = str(info.get("title") or "").strip() or "Álbum"
    artist = info.get("artist") if isinstance(info.get("artist"), dict) else {}
    artist_name = str(artist.get("name") or "").strip()
    genre = _genre_name(info)
    cover = _picture(info, "cover_xl", "cover_big", "cover_medium", "cover")
    track_block = info.get("tracks") if isinstance(info.get("tracks"), dict) else {}
    rows = track_block.get("data") if isinstance(track_block.get("data"), list) else []
    nb = info.get("nb_tracks")
    if isinstance(nb, int) and nb > len(rows):
        extra = await _maybe(_get(f"/album/{album_id}/tracks", {"limit": 100}, ttl=24 * 3600))
        if _rows(extra):
            rows = _rows(extra)
    tracks = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        item = _track(
            row,
            genre=genre,
            album_title=title,
            album_id=album_id,
            cover=cover,
            artist_name=artist_name,
            artist_id=artist.get("id"),
        )
        if item:
            tracks.append(item)
    return {
        "album": {
            "id": album_id,
            "title": title,
            "artist": artist_name,
            "artistId": artist.get("id"),
            "genre": genre,
            "picture": cover,
        },
        "tracks": stamp_known_audio(tracks),
    }


async def playlist_page(playlist_id: int) -> dict[str, Any]:
    info = await _get(f"/playlist/{playlist_id}", ttl=0, until_6am=True)
    title = str(info.get("title") or "").strip() or "Playlist"
    cover = _picture(info, "picture_xl", "picture_big", "picture_medium", "picture")
    track_block = info.get("tracks") if isinstance(info.get("tracks"), dict) else {}
    rows = track_block.get("data") if isinstance(track_block.get("data"), list) else None
    if rows is None:
        extra = await _get(f"/playlist/{playlist_id}/tracks", {"limit": 100}, ttl=0, until_6am=True)
        rows = _rows(extra)
    tracks = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        item = _track(row, cover=cover)
        if item:
            if not item["thumbnailUrl"]:
                item["thumbnailUrl"] = cover
            tracks.append(item)
    return {
        "playlist": {"id": playlist_id, "title": title, "picture": cover, "nbTracks": info.get("nb_tracks")},
        "tracks": stamp_known_audio(tracks),
    }


def _playlist_card(row: dict[str, Any]) -> dict[str, Any] | None:
    title = str(row.get("title") or "").strip()
    if not title or row.get("id") is None:
        return None
    nb = row.get("nb_tracks")
    sub = f"{nb} faixas" if isinstance(nb, int) and nb > 0 else "Playlist"
    return {
        "id": row.get("id"),
        "title": title,
        "picture": _picture(row, "picture_medium", "picture_big", "picture"),
        "subtitle": sub,
    }


def _norm_name(value: str) -> str:
    import re
    import unicodedata

    text = unicodedata.normalize("NFKD", value or "")
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def _artist_card(row: dict[str, Any]) -> dict[str, Any] | None:
    name = str(row.get("name") or "").strip()
    if not name or row.get("id") is None:
        return None
    return {
        "id": row.get("id"),
        "name": name,
        "picture": _picture(row, "picture_medium", "picture_big", "picture"),
    }


def _album_card(row: dict[str, Any]) -> dict[str, Any] | None:
    title = str(row.get("title") or "").strip()
    if not title or row.get("id") is None:
        return None
    artist = row.get("artist") if isinstance(row.get("artist"), dict) else {}
    artist_name = str(artist.get("name") or "").strip()
    release = str(row.get("release_date") or "")
    sub = " · ".join(part for part in (artist_name, release[:4] if len(release) >= 4 else release) if part)
    return {
        "id": row.get("id"),
        "title": title,
        "picture": _picture(row, "cover_medium", "cover_big", "cover"),
        "releaseDate": release,
        "subtitle": sub,
    }


async def search_catalog(query: str) -> dict[str, Any]:
    q = " ".join((query or "").split())
    if not q:
        raise DeezerError("Informe o que buscar.")
    search_key = f"search:{_norm_name(q)}"
    cached = _cache_get(search_key, 0, until_6am=True)
    if isinstance(cached, dict) and cached.get("query"):
        return cached

    artists_payload, albums_payload, tracks_payload = await _gather(
        _maybe(_get("/search/artist", {"q": q, "limit": 8}, ttl=0, until_6am=True)),
        _maybe(_get("/search/album", {"q": q, "limit": 12}, ttl=0, until_6am=True)),
        _maybe(_get("/search", {"q": q, "limit": 25}, ttl=0, until_6am=True)),
    )
    artists = [card for row in _rows(artists_payload) if (card := _artist_card(row))]
    albums = [card for row in _rows(albums_payload) if (card := _album_card(row))]
    tracks = [item for row in _rows(tracks_payload) if (item := _track(row))]
    wanted = _norm_name(q)
    focus = next((a for a in artists if _norm_name(a["name"]) == wanted), None)
    if focus is None and artists and wanted and wanted in _norm_name(artists[0]["name"]):
        focus = artists[0]
    artist_info = None
    if focus and focus.get("id") is not None:
        try:
            page = await artist_page(int(focus["id"]))
        except (DeezerError, TypeError, ValueError):
            page = None
        if page:
            artist_info = page.get("artist")
            if page.get("albums"):
                albums = [
                    {
                        "id": a.get("id"),
                        "title": a.get("title"),
                        "picture": a.get("picture"),
                        "releaseDate": a.get("releaseDate") or "",
                        "subtitle": (a.get("releaseDate") or "")[:4],
                    }
                    for a in page["albums"]
                ]
            if page.get("tracks"):
                tracks = page["tracks"]
    result = {
        "query": q,
        "artist": artist_info,
        "artists": artists,
        "albums": albums,
        "tracks": stamp_known_audio(tracks),
    }
    _cache_set(search_key, result)
    return result


def _charts_rows(payload: dict[str, Any], key: str) -> list[dict[str, Any]]:
    block = payload.get(key) if isinstance(payload, dict) else None
    data = block.get("data") if isinstance(block, dict) else None
    if not isinstance(data, list):
        return []
    return [row for row in data if isinstance(row, dict)]


def _typed_cards(rows: list[dict[str, Any]], kind: str, limit: int) -> list[dict[str, Any]]:
    cards: list[dict[str, Any]] = []
    for row in rows:
        if len(cards) >= limit:
            break
        if kind == "album":
            card = _album_card(row)
        elif kind == "artist":
            artist = _artist_card(row)
            card = (
                {
                    "id": artist["id"],
                    "title": artist["name"],
                    "picture": artist["picture"],
                    "subtitle": "Artista",
                }
                if artist
                else None
            )
        else:
            card = _playlist_card(row)
        if not card:
            continue
        card["kind"] = kind
        cards.append(card)
    return cards


def _editorial_genres(payload: dict[str, Any]) -> list[dict[str, Any]]:
    genres = []
    for row in _rows(payload):
        if row.get("id") in (None, 0):
            continue
        name = str(row.get("name") or "").strip()
        if not name:
            continue
        genres.append(
            {
                "id": row.get("id"),
                "name": name,
                "picture": _picture(row, "picture_medium", "picture_big", "picture"),
            }
        )
    return genres


def _pick_genres(genres: list[dict[str, Any]], names: list[str], limit: int = 3) -> list[dict[str, Any]]:
    by_name = {_norm_name(str(g.get("name") or "")): g for g in genres}
    picked: list[dict[str, Any]] = []
    seen: set[Any] = set()
    for name in names:
        genre = by_name.get(_norm_name(name))
        if not genre or genre.get("id") in seen:
            continue
        picked.append(genre)
        seen.add(genre.get("id"))
    for genre in genres:
        if len(picked) >= limit:
            break
        if genre.get("id") in seen:
            continue
        picked.append(genre)
        seen.add(genre.get("id"))
    return picked[:limit]


async def explore_page() -> dict[str, Any]:
    cached = _cache_get("explore_page", 0, until_6am=True)
    if isinstance(cached, dict) and cached.get("releases") is not None:
        return cached

    editorial, charts = await _gather(
        _maybe(_get("/editorial", ttl=6 * 3600)),
        _maybe(_get("/editorial/0/charts", {"limit": 20}, ttl=0, until_6am=True)),
    )
    genres = _editorial_genres(editorial)
    page = {
        "chips": [
            {"id": "releases", "label": "Lançamentos"},
            {"id": "charts", "label": "Paradas"},
            {"id": "genres", "label": "Momentos e gêneros"},
        ],
        "releases": _typed_cards(_charts_rows(charts, "albums"), "album", 16),
        "genres": genres,
        "trending": stamp_known_audio(
            [item for row in _charts_rows(charts, "tracks") if (item := _track(row))]
        ),
        "chartPlaylists": _typed_cards(_charts_rows(charts, "playlists"), "playlist", 16),
    }
    _cache_set("explore_page", page)
    return page


async def library_feed(genre_names: list[str] | None = None) -> dict[str, Any]:
    taste_key = "|".join(sorted({_norm_name(n) for n in (genre_names or []) if str(n).strip()}))
    cache_key = f"library_feed:{taste_key or 'default'}"
    cached = _cache_get(cache_key, 0, until_6am=True)
    if isinstance(cached, dict) and cached.get("shelves") is not None:
        return cached

    editorial = await _maybe(_get("/editorial", ttl=6 * 3600))
    genres = _editorial_genres(editorial)
    picked = _pick_genres(genres, list(genre_names or []))
    calls = [_maybe(_get("/editorial/0/charts", {"limit": 16}, ttl=0, until_6am=True))]
    for genre in picked:
        calls.append(
            _maybe(_get(f"/editorial/{int(genre['id'])}/charts", {"limit": 12}, ttl=0, until_6am=True))
        )
    results = await _gather(*calls)
    global_charts = results[0] if results else {}
    shelves = []
    albums_for_you: list[dict[str, Any]] = []
    seen_albums: set[Any] = set()
    for genre, payload in zip(picked, results[1:]):
        cards = _typed_cards(_charts_rows(payload, "playlists"), "playlist", 12)
        if not cards:
            cards = _typed_cards(_charts_rows(payload, "albums"), "album", 12)
        if cards:
            shelves.append({"title": genre["name"], "cards": cards})
        for card in _typed_cards(_charts_rows(payload, "albums"), "album", 8):
            if card["id"] in seen_albums:
                continue
            seen_albums.add(card["id"])
            albums_for_you.append(card)
    releases = _typed_cards(_charts_rows(global_charts, "albums"), "album", 16)
    release_ids = {card["id"] for card in releases}
    albums_for_you = [card for card in albums_for_you if card["id"] not in release_ids][:16]
    playlists = _typed_cards(_charts_rows(global_charts, "playlists"), "playlist", 16)
    feed = {
        "shelves": shelves,
        "albumsForYou": albums_for_you,
        "hitsToday": playlists[:8],
        "featuredPlaylists": playlists[8:16],
        "newReleases": releases,
    }
    _cache_set(cache_key, feed)
    return feed


async def artist_pictures(artist_ids: list[Any]) -> dict[str, str]:
    ids: list[int] = []
    for raw in artist_ids:
        try:
            ids.append(int(raw))
        except (TypeError, ValueError):
            continue
    infos = await _gather(*(_maybe(_get(f"/artist/{i}", ttl=0, until_6am=True)) for i in ids))
    out: dict[str, str] = {}
    for artist_id, info in zip(ids, infos):
        picture = _picture(info, "picture_medium", "picture_big", "picture")
        if picture:
            out[str(artist_id)] = picture
    return out


async def artist_related(artist_id: int) -> dict[str, Any]:
    payload = await _maybe(_get(f"/artist/{artist_id}/related", {"limit": 12}, ttl=6 * 3600))
    artists = [card for row in _rows(payload) if (card := _artist_card(row))]
    return {"artists": artists}


async def artist_radio(artist_id: int) -> dict[str, Any]:
    payload = await _maybe(_get(f"/artist/{artist_id}/radio", {"limit": 25}, ttl=900))
    tracks = [item for row in _rows(payload) if (item := _track(row))]
    return {"tracks": stamp_known_audio(tracks)}


async def _gather(*aws):
    import asyncio

    return await asyncio.gather(*aws)
