"""Contas, faixas por usuário e preferências (SQLite). Áudio continua deduplicado em disco."""

from __future__ import annotations

import json
import sqlite3
import threading
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from app.downloader import downloads_root, find_existing

_LOCK = threading.Lock()
_META_KEYS = (
    "title",
    "artist",
    "channelId",
    "channelTitle",
    "description",
    "descriptionOriginal",
    "descriptionLang",
    "duration",
    "publishedAt",
    "viewCount",
    "thumbnailUrl",
    "album",
    "albumId",
    "artistId",
    "deezerId",
    "genre",
    "catalogSource",
    "url",
    "filename",
    "sizeBytes",
    "storedAt",
    "audioProfile",
)


def _db_path() -> Path:
    return downloads_root() / "rutsfy.db"


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(_db_path(), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    downloads_root()
    with _LOCK:
        conn = _connect()
        try:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    email TEXT NOT NULL UNIQUE COLLATE NOCASE,
                    password_hash TEXT NOT NULL,
                    display_name TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS sessions (
                    token TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    expires_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id);
                CREATE TABLE IF NOT EXISTS user_tracks (
                    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    video_id TEXT NOT NULL,
                    in_library INTEGER NOT NULL DEFAULT 0,
                    library_added_at TEXT,
                    last_played_at TEXT,
                    last_position_sec REAL,
                    meta_json TEXT NOT NULL DEFAULT '{}',
                    PRIMARY KEY (user_id, video_id)
                );
                CREATE INDEX IF NOT EXISTS idx_user_tracks_played
                    ON user_tracks(user_id, last_played_at DESC);
                CREATE TABLE IF NOT EXISTS user_preferences (
                    user_id TEXT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
                    prefs_json TEXT NOT NULL DEFAULT '{}',
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS app_meta (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS user_daily_searches (
                    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    quota_date TEXT NOT NULL,
                    search_count INTEGER NOT NULL DEFAULT 0,
                    PRIMARY KEY (user_id, quota_date)
                );
                """
            )
            _migrate_schema(conn)
            conn.commit()
        finally:
            conn.close()


def _migrate_schema(conn: sqlite3.Connection) -> None:
    cols = {row[1] for row in conn.execute("PRAGMA table_info(users)").fetchall()}
    if "avatar_file" not in cols:
        conn.execute("ALTER TABLE users ADD COLUMN avatar_file TEXT")
    if "avatar_updated_at" not in cols:
        conn.execute("ALTER TABLE users ADD COLUMN avatar_updated_at TEXT")
    if "nickname" not in cols:
        conn.execute("ALTER TABLE users ADD COLUMN nickname TEXT")
    if "is_admin" not in cols:
        conn.execute("ALTER TABLE users ADD COLUMN is_admin INTEGER NOT NULL DEFAULT 0")
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS user_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            kind TEXT NOT NULL,
            created_at TEXT NOT NULL,
            video_id TEXT NOT NULL DEFAULT '',
            title TEXT NOT NULL DEFAULT '',
            artist TEXT NOT NULL DEFAULT ''
        )
        """
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_user_events_kind_at ON user_events(kind, created_at)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_user_events_user_kind ON user_events(user_id, kind, created_at)"
    )
    _backfill_user_nicknames(conn)
    _backfill_play_events(conn)
    conn.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_users_nickname ON users(nickname COLLATE NOCASE)"
    )


def _backfill_user_nicknames(conn: sqlite3.Connection) -> None:
    rows = conn.execute(
        "SELECT id, email, display_name FROM users WHERE nickname IS NULL OR nickname = ''"
    ).fetchall()
    if not rows:
        return
    seen: set[str] = set()
    for row in rows:
        uid = row["id"]
        email = (row["email"] or "").strip()
        display = (row["display_name"] or "").strip()
        base = display or (email.split("@", 1)[0] if email else "") or "user"
        base = " ".join(base.split())[:32] or "user"
        nick = base
        suffix = 1
        while nick.lower() in seen:
            suffix += 1
            tail = f"-{suffix}"
            nick = f"{base[: max(2, 32 - len(tail))]}{tail}"
        seen.add(nick.lower())
        conn.execute("UPDATE users SET nickname = ? WHERE id = ?", (nick, uid))


def _backfill_play_events(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        INSERT INTO user_events (user_id, kind, created_at, video_id, title, artist)
        SELECT
            t.user_id,
            'play',
            t.last_played_at,
            t.video_id,
            COALESCE(json_extract(t.meta_json, '$.title'), ''),
            COALESCE(json_extract(t.meta_json, '$.artist'), '')
        FROM user_tracks t
        WHERE t.last_played_at IS NOT NULL AND t.last_played_at != ''
          AND NOT EXISTS (
            SELECT 1 FROM user_events e
            WHERE e.user_id = t.user_id AND e.kind = 'play' AND e.video_id = t.video_id
          )
        """
    )


def avatars_root() -> Path:
    path = downloads_root() / "avatars"
    path.mkdir(parents=True, exist_ok=True)
    return path


def update_user_display_name(user_id: str, display_name: str) -> None:
    name = display_name.strip()
    with _LOCK:
        conn = _connect()
        try:
            conn.execute(
                "UPDATE users SET display_name = ?, nickname = ? WHERE id = ?",
                (name, name, user_id),
            )
            conn.commit()
        except sqlite3.IntegrityError as exc:
            raise ValueError("Apelido já está em uso") from exc
        finally:
            conn.close()


def update_user_password_hash(user_id: str, password_hash: str) -> None:
    with _LOCK:
        conn = _connect()
        try:
            conn.execute(
                "UPDATE users SET password_hash = ? WHERE id = ?",
                (password_hash, user_id),
            )
            conn.commit()
        finally:
            conn.close()


def set_user_avatar_file(user_id: str, filename: str) -> None:
    now = _now_iso()
    with _LOCK:
        conn = _connect()
        try:
            conn.execute(
                "UPDATE users SET avatar_file = ?, avatar_updated_at = ? WHERE id = ?",
                (filename, now, user_id),
            )
            conn.commit()
        finally:
            conn.close()


def clear_user_avatar_file(user_id: str) -> None:
    with _LOCK:
        conn = _connect()
        try:
            conn.execute(
                "UPDATE users SET avatar_file = NULL, avatar_updated_at = ? WHERE id = ?",
                (_now_iso(), user_id),
            )
            conn.commit()
        finally:
            conn.close()


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def create_user(*, nickname: str, password_hash: str) -> dict[str, Any]:
    user_id = str(uuid.uuid4())
    nick = nickname.strip()
    # Coluna email legada (NOT NULL UNIQUE); contas novas não usam e-mail real.
    email_placeholder = f"{user_id}@users.local"
    created = _now_iso()
    with _LOCK:
        conn = _connect()
        try:
            conn.execute(
                """
                INSERT INTO users (id, email, password_hash, display_name, nickname, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (user_id, email_placeholder, password_hash, nick, nick, created),
            )
            conn.execute(
                """
                INSERT INTO user_preferences (user_id, prefs_json, updated_at)
                VALUES (?, '{}', ?)
                """,
                (user_id, created),
            )
            conn.commit()
        except sqlite3.IntegrityError as exc:
            raise ValueError("Apelido já cadastrado") from exc
        finally:
            conn.close()
    return {
        "id": user_id,
        "nickname": nick,
        "displayName": nick,
        "avatarUrl": None,
    }


def get_user_by_nickname(nickname: str) -> dict[str, Any] | None:
    nick = nickname.strip()
    if not nick:
        return None
    with _LOCK:
        conn = _connect()
        try:
            row = conn.execute(
                "SELECT * FROM users WHERE nickname = ? COLLATE NOCASE",
                (nick,),
            ).fetchone()
        finally:
            conn.close()
    return dict(row) if row else None


def get_user_by_email(email: str) -> dict[str, Any] | None:
    email_norm = email.strip().lower()
    with _LOCK:
        conn = _connect()
        try:
            row = conn.execute("SELECT * FROM users WHERE email = ?", (email_norm,)).fetchone()
        finally:
            conn.close()
    return dict(row) if row else None


def get_user_by_id(user_id: str) -> dict[str, Any] | None:
    with _LOCK:
        conn = _connect()
        try:
            row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        finally:
            conn.close()
    return dict(row) if row else None


def create_session(user_id: str, token: str, expires_at: str) -> None:
    with _LOCK:
        conn = _connect()
        try:
            conn.execute(
                "INSERT INTO sessions (token, user_id, expires_at) VALUES (?, ?, ?)",
                (token, user_id, expires_at),
            )
            conn.commit()
        finally:
            conn.close()


def delete_session(token: str) -> None:
    with _LOCK:
        conn = _connect()
        try:
            conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
            conn.commit()
        finally:
            conn.close()


def revoke_sessions_for_user(user_id: str) -> None:
    """Um token ativo por login — evita sessão antiga em outro dispositivo/aba."""
    with _LOCK:
        conn = _connect()
        try:
            conn.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))
            conn.commit()
        finally:
            conn.close()


def get_user_id_for_session(token: str) -> str | None:
    now = _now_iso()
    with _LOCK:
        conn = _connect()
        try:
            row = conn.execute(
                "SELECT user_id FROM sessions WHERE token = ? AND expires_at > ?",
                (token, now),
            ).fetchone()
            if not row:
                conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
                conn.commit()
                return None
        finally:
            conn.close()
    return row["user_id"] if row else None


def _parse_meta(row: sqlite3.Row) -> dict[str, Any]:
    try:
        meta = json.loads(row["meta_json"] or "{}")
    except (TypeError, ValueError):
        meta = {}
    if not isinstance(meta, dict):
        meta = {}
    out = {"videoId": row["video_id"], **meta}
    if row["in_library"]:
        out["inLibrary"] = True
    if row["library_added_at"]:
        out["libraryAddedAt"] = row["library_added_at"]
    if row["last_played_at"]:
        out["lastPlayedAt"] = row["last_played_at"]
    if row["last_position_sec"] is not None:
        out["lastPositionSec"] = row["last_position_sec"]
    return out


def upsert_user_track(
    user_id: str,
    video_id: str,
    *,
    patch_meta: dict[str, Any] | None = None,
    in_library: bool | None = None,
    library_added_at: str | None = None,
    clear_library_added_at: bool = False,
    last_played_at: str | None = None,
    last_position_sec: float | None = None,
) -> dict[str, Any]:
    with _LOCK:
        conn = _connect()
        try:
            row = conn.execute(
                "SELECT * FROM user_tracks WHERE user_id = ? AND video_id = ?",
                (user_id, video_id),
            ).fetchone()
            if row:
                meta = json.loads(row["meta_json"] or "{}")
                if not isinstance(meta, dict):
                    meta = {}
            else:
                meta = {}

            if patch_meta:
                for k, v in patch_meta.items():
                    if v is not None and k != "videoId":
                        meta[k] = v

            lib = row["in_library"] if row else 0
            if in_library is not None:
                lib = 1 if in_library else 0

            lib_at = row["library_added_at"] if row else None
            if clear_library_added_at:
                lib_at = None
            elif library_added_at:
                lib_at = library_added_at
            elif lib and not lib_at:
                lib_at = _now_iso()

            played = last_played_at if last_played_at is not None else (row["last_played_at"] if row else None)
            pos = (
                last_position_sec
                if last_position_sec is not None
                else (row["last_position_sec"] if row else None)
            )

            conn.execute(
                """
                INSERT INTO user_tracks (
                    user_id, video_id, in_library, library_added_at,
                    last_played_at, last_position_sec, meta_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id, video_id) DO UPDATE SET
                    in_library = excluded.in_library,
                    library_added_at = excluded.library_added_at,
                    last_played_at = COALESCE(excluded.last_played_at, user_tracks.last_played_at),
                    last_position_sec = COALESCE(excluded.last_position_sec, user_tracks.last_position_sec),
                    meta_json = excluded.meta_json
                """,
                (
                    user_id,
                    video_id,
                    lib,
                    lib_at,
                    played,
                    pos,
                    json.dumps(meta, ensure_ascii=False),
                ),
            )
            conn.commit()
            row = conn.execute(
                "SELECT * FROM user_tracks WHERE user_id = ? AND video_id = ?",
                (user_id, video_id),
            ).fetchone()
        finally:
            conn.close()
    return _parse_meta(row) if row else {}


def user_track_entry(user_id: str, video_id: str) -> dict[str, Any] | None:
    with _LOCK:
        conn = _connect()
        try:
            row = conn.execute(
                "SELECT * FROM user_tracks WHERE user_id = ? AND video_id = ?",
                (user_id, video_id),
            ).fetchone()
        finally:
            conn.close()
    return _parse_meta(row) if row else None


def user_stored_catalog(user_id: str | None, video_ids: list[str]) -> dict[str, dict[str, Any]]:
    if not user_id:
        return {}
    out: dict[str, dict[str, Any]] = {}
    with _LOCK:
        conn = _connect()
        try:
            for vid in video_ids:
                if not vid:
                    continue
                row = conn.execute(
                    "SELECT * FROM user_tracks WHERE user_id = ? AND video_id = ?",
                    (user_id, vid),
                ).fetchone()
                if row:
                    parsed = _parse_meta(row)
                    if parsed.get("title") or parsed.get("duration"):
                        out[vid] = parsed
        finally:
            conn.close()
    return out


def list_user_history(user_id: str) -> list[dict[str, Any]]:
    with _LOCK:
        conn = _connect()
        try:
            rows = conn.execute(
                """
                SELECT * FROM user_tracks
                WHERE user_id = ? AND last_played_at IS NOT NULL
                ORDER BY last_played_at DESC
                """,
                (user_id,),
            ).fetchall()
        finally:
            conn.close()

    items: list[dict[str, Any]] = []
    for row in rows:
        item = _hydrate_track_row(_parse_meta(row))
        if item:
            items.append(item)
    return items


def list_user_library(user_id: str) -> list[dict[str, Any]]:
    with _LOCK:
        conn = _connect()
        try:
            rows = conn.execute(
                """
                SELECT * FROM user_tracks
                WHERE user_id = ? AND in_library = 1
                ORDER BY library_added_at DESC
                """,
                (user_id,),
            ).fetchall()
        finally:
            conn.close()

    items: list[dict[str, Any]] = []
    for row in rows:
        item = _hydrate_track_row(_parse_meta(row))
        if item:
            items.append(item)
    return items


def _hydrate_track_row(meta: dict[str, Any]) -> dict[str, Any] | None:
    vid = meta.get("videoId")
    if not vid:
        return None
    path = find_existing(vid)
    item = dict(meta)
    if path and path.is_file():
        st = path.stat()
        item.setdefault("filename", path.name)
        item.setdefault("sizeBytes", st.st_size)
        item.setdefault("storedAt", datetime.fromtimestamp(st.st_mtime, tz=timezone.utc).isoformat())
        from app.public_paths import public_path

        item["url"] = public_path(f"/api/downloads/{path.name}")
    elif not item.get("url"):
        item["url"] = f"https://www.youtube.com/watch?v={vid}"
    item["inLibrary"] = bool(item.get("inLibrary"))
    return item


def user_catalog_taste(user_id: str, *, limit: int = 80) -> dict[str, Any]:
    """Gêneros e artistas que a conta ouviu ou salvou, do mais recente."""
    with _LOCK:
        conn = _connect()
        try:
            rows = conn.execute(
                """
                SELECT meta_json FROM user_tracks
                WHERE user_id = ?
                ORDER BY COALESCE(last_played_at, library_added_at) DESC
                LIMIT ?
                """,
                (user_id, limit),
            ).fetchall()
        finally:
            conn.close()

    genre_counts: dict[str, int] = {}
    artists: list[dict[str, Any]] = []
    seen_artists: set[str] = set()
    for row in rows:
        try:
            meta = json.loads(row["meta_json"] or "{}")
        except (TypeError, ValueError):
            meta = {}
        if not isinstance(meta, dict):
            continue
        genre = str(meta.get("genre") or "").strip()
        if genre:
            genre_counts[genre] = genre_counts.get(genre, 0) + 1
        artist_id = meta.get("artistId")
        artist_name = str(meta.get("artist") or "").strip()
        picture = str(meta.get("thumbnailUrl") or "").strip()
        if artist_id is not None and artist_name and str(artist_id) not in seen_artists:
            seen_artists.add(str(artist_id))
            artists.append(
                {
                    "kind": "artist",
                    "id": artist_id,
                    "title": artist_name,
                    "picture": picture,
                    "subtitle": "Artista",
                }
            )
    ranked = sorted(genre_counts, key=lambda name: genre_counts[name], reverse=True)
    return {"genreNames": ranked[:3], "listenAgain": artists[:12]}


def get_preferences(user_id: str) -> dict[str, Any]:
    with _LOCK:
        conn = _connect()
        try:
            row = conn.execute(
                "SELECT prefs_json FROM user_preferences WHERE user_id = ?",
                (user_id,),
            ).fetchone()
        finally:
            conn.close()
    if not row:
        return {}
    try:
        data = json.loads(row["prefs_json"] or "{}")
        return data if isinstance(data, dict) else {}
    except (TypeError, ValueError):
        return {}


def sanitize_user_preferences(prefs: dict[str, Any]) -> dict[str, Any]:
    """Preferências são sempre por conta; não aceita chaves de outro usuário."""
    if not isinstance(prefs, dict):
        return {}
    allowed = {
        "volume",
        "lastListen",
        "themeId",
        "themeCustom",
        "colorScheme",
        "savedShortcuts",
        "recentSearches",
        "userPlaylists",
        "savedCollections",
    }
    clean: dict[str, Any] = {}
    for key in allowed:
        if key in prefs:
            clean[key] = prefs[key]
    return clean


def set_preferences(user_id: str, prefs: dict[str, Any]) -> dict[str, Any]:
    prefs = sanitize_user_preferences(prefs)
    now = _now_iso()
    blob = json.dumps(prefs, ensure_ascii=False)
    with _LOCK:
        conn = _connect()
        try:
            conn.execute(
                """
                INSERT INTO user_preferences (user_id, prefs_json, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    prefs_json = excluded.prefs_json,
                    updated_at = excluded.updated_at
                """,
                (user_id, blob, now),
            )
            conn.commit()
        finally:
            conn.close()
    return prefs


def legacy_import_done() -> bool:
    with _LOCK:
        conn = _connect()
        try:
            row = conn.execute(
                "SELECT value FROM app_meta WHERE key = 'legacy_library_imported'"
            ).fetchone()
        finally:
            conn.close()
    return bool(row and row["value"] == "1")


def mark_legacy_import_done() -> None:
    with _LOCK:
        conn = _connect()
        try:
            conn.execute(
                """
                INSERT INTO app_meta (key, value) VALUES ('legacy_library_imported', '1')
                ON CONFLICT(key) DO UPDATE SET value = '1'
                """
            )
            conn.commit()
        finally:
            conn.close()


def import_legacy_library_json(user_id: str, videos: dict[str, dict[str, Any]]) -> int:
    count = 0
    for vid, entry in videos.items():
        if not vid or not isinstance(entry, dict):
            continue
        meta = {k: entry.get(k) for k in _META_KEYS if entry.get(k) is not None}
        upsert_user_track(
            user_id,
            vid,
            patch_meta=meta,
            in_library=bool(entry.get("inLibrary")),
            library_added_at=entry.get("libraryAddedAt"),
            last_played_at=entry.get("lastPlayedAt"),
        )
        count += 1
    mark_legacy_import_done()
    return count


def user_has_unlimited_search(user_id: str) -> bool:
    return get_user_by_id(user_id) is not None


def user_search_quota_snapshot(user_id: str, *, limit: int) -> dict[str, Any]:
    from app.quota import quota_today

    today = quota_today()
    if user_has_unlimited_search(user_id):
        return {
            "date": today,
            "limit": limit,
            "used": 0,
            "remaining": 999_999,
            "unitCost": 100,
            "unlimited": True,
        }
    with _LOCK:
        conn = _connect()
        try:
            row = conn.execute(
                """
                SELECT search_count FROM user_daily_searches
                WHERE user_id = ? AND quota_date = ?
                """,
                (user_id, today),
            ).fetchone()
            used = int(row["search_count"]) if row else 0
        finally:
            conn.close()
    remaining = max(limit - used, 0)
    return {
        "date": today,
        "limit": limit,
        "used": used,
        "remaining": remaining,
        "unitCost": 100,
    }


def record_user_search_api_call(user_id: str) -> None:
    from app.quota import quota_today

    today = quota_today()
    with _LOCK:
        conn = _connect()
        try:
            conn.execute(
                """
                INSERT INTO user_daily_searches (user_id, quota_date, search_count)
                VALUES (?, ?, 1)
                ON CONFLICT(user_id, quota_date) DO UPDATE SET
                    search_count = search_count + 1
                """,
                (user_id, today),
            )
            conn.commit()
        finally:
            conn.close()


def set_user_admin(user_id: str, is_admin: bool) -> None:
    with _LOCK:
        conn = _connect()
        try:
            conn.execute(
                "UPDATE users SET is_admin = ? WHERE id = ?",
                (1 if is_admin else 0, user_id),
            )
            conn.commit()
        finally:
            conn.close()


def record_user_event(
    user_id: str,
    kind: str,
    *,
    video_id: str = "",
    title: str = "",
    artist: str = "",
) -> None:
    if kind not in ("login", "visit", "play"):
        return
    now = _now_iso()
    with _LOCK:
        conn = _connect()
        try:
            if kind == "visit":
                recent = conn.execute(
                    """
                    SELECT 1 FROM user_events
                    WHERE user_id = ? AND kind = 'visit' AND created_at > ?
                    LIMIT 1
                    """,
                    (user_id, _iso_minus(now, minutes=30)),
                ).fetchone()
                if recent:
                    return
            conn.execute(
                """
                INSERT INTO user_events (user_id, kind, created_at, video_id, title, artist)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (user_id, kind, now, video_id[:64], title[:180], artist[:180]),
            )
            conn.commit()
        finally:
            conn.close()


def _iso_minus(now_iso: str, *, minutes: int) -> str:
    try:
        current = datetime.fromisoformat(now_iso)
    except ValueError:
        current = datetime.now(timezone.utc)
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)
    return (current - timedelta(minutes=minutes)).replace(microsecond=0).isoformat()


def _br_now() -> datetime:
    return datetime.now(timezone(timedelta(hours=-3)))


def _as_br_date(raw: str) -> str:
    text = (raw or "").strip()
    if not text:
        return ""
    try:
        current = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return text[:10]
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)
    return current.astimezone(timezone(timedelta(hours=-3))).date().isoformat()


def list_admin_users() -> list[dict[str, Any]]:
    with _LOCK:
        conn = _connect()
        try:
            rows = conn.execute(
                """
                SELECT
                    u.id,
                    u.nickname,
                    u.display_name,
                    u.created_at,
                    u.is_admin,
                    (
                        SELECT COUNT(*) FROM user_events e
                        WHERE e.user_id = u.id AND e.kind = 'play'
                    ) AS play_count,
                    (
                        SELECT MAX(e.created_at) FROM user_events e
                        WHERE e.user_id = u.id AND e.kind IN ('visit', 'login')
                    ) AS last_access_at,
                    (
                        SELECT MAX(t.last_played_at) FROM user_tracks t
                        WHERE t.user_id = u.id
                    ) AS last_played_at
                FROM users u
                ORDER BY u.created_at DESC
                """
            ).fetchall()
        finally:
            conn.close()
    items = []
    for row in rows:
        nick = (row["nickname"] or row["display_name"] or "").strip() or "Conta"
        items.append(
            {
                "id": row["id"],
                "nickname": nick,
                "displayName": nick,
                "createdAt": row["created_at"],
                "isAdmin": bool(row["is_admin"]),
                "playCount": int(row["play_count"] or 0),
                "lastAccessAt": row["last_access_at"],
                "lastPlayedAt": row["last_played_at"],
            }
        )
    return items


def admin_stats() -> dict[str, Any]:
    today = _br_now().date()
    days = [(today - timedelta(days=offset)).isoformat() for offset in range(13, -1, -1)]
    day_set = set(days)
    buckets = {day: {"date": day, "plays": 0, "visits": 0, "logins": 0, "searches": 0} for day in days}
    since = (datetime.now(timezone.utc) - timedelta(days=16)).replace(microsecond=0).isoformat()
    with _LOCK:
        conn = _connect()
        try:
            events = conn.execute(
                """
                SELECT kind, created_at FROM user_events
                WHERE created_at >= ?
                """,
                (since,),
            ).fetchall()
            searches = conn.execute(
                """
                SELECT quota_date, SUM(search_count) AS total
                FROM user_daily_searches
                GROUP BY quota_date
                """
            ).fetchall()
            user_count = conn.execute("SELECT COUNT(*) AS n FROM users").fetchone()["n"]
            top_rows = conn.execute(
                """
                SELECT video_id, title, artist, COUNT(*) AS plays
                FROM user_events
                WHERE kind = 'play' AND video_id != ''
                GROUP BY video_id
                ORDER BY plays DESC
                LIMIT 8
                """
            ).fetchall()
            top_users = conn.execute(
                """
                SELECT e.user_id, COUNT(*) AS plays, u.nickname, u.display_name
                FROM user_events e
                JOIN users u ON u.id = e.user_id
                WHERE e.kind = 'play'
                GROUP BY e.user_id
                ORDER BY plays DESC
                LIMIT 8
                """
            ).fetchall()
        finally:
            conn.close()
    for row in searches:
        day = str(row["quota_date"] or "")
        if day in buckets:
            buckets[day]["searches"] = int(row["total"] or 0)
    for row in events:
        day = _as_br_date(row["created_at"])
        if day not in day_set:
            continue
        kind = row["kind"]
        if kind == "play":
            buckets[day]["plays"] += 1
        elif kind == "visit":
            buckets[day]["visits"] += 1
        elif kind == "login":
            buckets[day]["logins"] += 1
    today_key = today.isoformat()
    week = days[-7:]
    return {
        "users": int(user_count or 0),
        "playsToday": buckets[today_key]["plays"],
        "visitsToday": buckets[today_key]["visits"],
        "loginsToday": buckets[today_key]["logins"],
        "searchesToday": buckets[today_key]["searches"],
        "plays7d": sum(buckets[day]["plays"] for day in week),
        "visits7d": sum(buckets[day]["visits"] for day in week),
        "days": [buckets[day] for day in days],
        "topTracks": [
            {
                "videoId": row["video_id"],
                "title": row["title"] or row["video_id"],
                "artist": row["artist"] or "",
                "plays": int(row["plays"] or 0),
            }
            for row in top_rows
        ],
        "topUsers": [
            {
                "id": row["user_id"],
                "nickname": (row["nickname"] or row["display_name"] or "Conta").strip(),
                "plays": int(row["plays"] or 0),
            }
            for row in top_users
        ],
    }
