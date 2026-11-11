from __future__ import annotations

import asyncio
import json
import re
from pathlib import Path
from typing import Any

from fastapi import Body, Cookie, Depends, FastAPI, File, HTTPException, Query, Response, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.auth import (
    clear_session_cookie,
    get_current_user,
    get_current_user_id,
    login_user,
    logout_user,
    public_user,
    register_user,
    remove_user_avatar,
    set_session_cookie,
    update_account_profile,
)
from app.config import settings
from app.public_paths import public_path
from app.users_db import (
    avatars_root,
    get_preferences,
    get_user_by_id,
    init_db,
    set_preferences,
    set_user_avatar_file,
)
from app.downloader import (
    DownloadError,
    download_audio,
    downloads_root,
    list_downloads,
    list_saved_library,
    set_library_membership,
    stored_catalog_entries,
    video_ids_needing_remote_details,
)
from app.worker_auth import require_worker_token
from app.youtube_cache import (
    get_channel_uploads_cached,
    get_playlist_cached,
    get_search_cached,
    playlist_cache_key,
    search_cache_key,
)
from app.metadata_util import resolve_track_artist
from app.mixes import get_mix, list_mix_categories, list_mixes
from app.quota import MultiKeyQuotaTracker
from app.youtube_api_keys import key_fingerprint, resolve_youtube_api_keys
from app.translate import ensure_portuguese
from app.youtube_client import QUOTA_EXCEEDED_MESSAGE, RotatingYouTubeClient, YouTubeApiError
from app.youtube_service import (
    get_channel_uploads_playlist_cached,
    get_playlist_items_cached,
    get_videos_cached,
    search_videos_cached,
)
from app.cover_art import fetch_track_cover, normalize_video_id


def _provider_error_hidden(message: str) -> bool:
    m = message.lower()
    return any(
        token in m
        for token in (
            "youtube",
            "googleapis",
            "google",
            "quota exceeded",
            "quotaexceeded",
            "project_number",
            "yt-dlp",
        )
    )


def _user_safe_detail(message: str, *, fallback: str = "Busca temporariamente indisponível. Tente mais tarde.") -> str:
    text = (message or "").strip()
    if not text or _provider_error_hidden(text):
        return fallback
    return text


def _http_from_youtube_error(exc: YouTubeApiError) -> HTTPException:
    if exc.quota_exceeded:
        return HTTPException(status_code=429, detail=QUOTA_EXCEEDED_MESSAGE)
    code = exc.status_code if 400 <= exc.status_code < 600 else 502
    detail = _user_safe_detail(str(exc))
    return HTTPException(status_code=code, detail=detail)


def _download_error_detail(exc: DownloadError) -> str:
    return _user_safe_detail(
        str(exc),
        fallback="Não foi possível baixar esta faixa. Tente outra ou mais tarde.",
    )

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"

_QUOTA_TRACKER: MultiKeyQuotaTracker | None = None

app = FastAPI(title="RutsFy", version="0.1.0")


@app.on_event("startup")
def _on_startup() -> None:
    init_db()
    from app.auth import ensure_builtin_admin

    ensure_builtin_admin()

if STATIC_DIR.is_dir():
    app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="assets")

APP_DIR = STATIC_DIR / "app"


@app.get("/api/app/version")
def app_version() -> dict[str, Any]:
    meta = APP_DIR / "version.json"
    apk = APP_DIR / "rutsfy.apk"
    if not meta.is_file() or not apk.is_file():
        return {"update": False}
    try:
        data = json.loads(meta.read_text(encoding="utf-8"))
        code = int(data.get("versionCode") or 0)
    except (OSError, ValueError, TypeError):
        return {"update": False}
    if code <= 0:
        return {"update": False}
    return {
        "update": True,
        "versionCode": code,
        "versionName": str(data.get("versionName") or ""),
        "url": public_path(f"/api/app/rutsfy-{code}.apk"),
    }


@app.get("/api/app/{filename}")
def app_apk(filename: str) -> FileResponse:
    if not re.fullmatch(r"rutsfy(?:-\d+)?\.apk", filename):
        raise HTTPException(status_code=404, detail="Nenhuma versão publicada")
    apk = APP_DIR / "rutsfy.apk"
    if not apk.is_file():
        raise HTTPException(status_code=404, detail="Nenhuma versão publicada")
    return FileResponse(
        apk,
        media_type="application/vnd.android.package-archive",
        filename="rutsfy.apk",
        headers={"Cache-Control": "no-store", "CDN-Cache-Control": "no-store"},
    )

origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _quota_tracker() -> MultiKeyQuotaTracker:
    # Persistido junto com os downloads (sobrevive a restarts do container)
    global _QUOTA_TRACKER
    if _QUOTA_TRACKER is None:
        keys = resolve_youtube_api_keys()
        ids = [key_fingerprint(k) for k in keys]
        _QUOTA_TRACKER = MultiKeyQuotaTracker(
            downloads_root() / "quota.json",
            settings.youtube_daily_quota,
            ids,
        )
    return _QUOTA_TRACKER


def _api_quota_can_search() -> bool:
    if not resolve_youtube_api_keys():
        return False
    return _quota_tracker().any_usable(settings.quota_min_remaining_search)


def _client() -> RotatingYouTubeClient:
    keys = resolve_youtube_api_keys()
    if not keys:
        raise HTTPException(
            status_code=503,
            detail="Chave da API de busca não configurada. Crie .env a partir de .env.example.",
        )
    mk = _quota_tracker()

    def _usable(kid: str) -> bool:
        return mk.is_usable(kid, min_remaining=0)

    return RotatingYouTubeClient(
        keys,
        key_id_for=key_fingerprint,
        quota_hook=mk.record,
        quota_exceeded_hook=mk.mark_quota_exceeded,
        is_key_usable=_usable,
    )


async def _metadata_for(video_id: str) -> dict[str, Any] | None:
    """Metadados vêm do catálogo ou do arquivo já salvo. Não consulta a API do YouTube."""
    return None


def _video_url(video_id: str) -> str:
    return f"https://www.youtube.com/watch?v={video_id}"


def _maybe_store_mix_covers(mix_id: str | None, items: list[dict[str, Any]]) -> None:
    if not mix_id or not items:
        return
    from app.mix_covers import add_mix_covers

    urls = [i["thumbnailUrl"] for i in items if i.get("thumbnailUrl")]
    if urls:
        add_mix_covers(mix_id, urls[:24])


async def _with_pt_description(item: dict[str, Any]) -> dict[str, Any]:
    """Garante descrição em português (cache em disco; se já for pt, não altera)."""
    if not item.get("description"):
        return item
    info = await ensure_portuguese(item["description"])
    if info["translated"]:
        item["descriptionOriginal"] = item["description"]
    item["description"] = info["text"]
    item["descriptionLang"] = info["lang"]
    return item


def _normalize_search_item(item: dict[str, Any]) -> dict[str, Any]:
    vid = (item.get("id") or {}).get("videoId")
    sn = item.get("snippet") or {}
    thumbs = sn.get("thumbnails") or {}
    thumb = (thumbs.get("medium") or thumbs.get("default") or {}).get("url")
    title = sn.get("title")
    return {
        "videoId": vid,
        "title": title,
        "channelTitle": sn.get("channelTitle"),
        "channelId": sn.get("channelId"),
        "artist": resolve_track_artist(title=title),
        "publishedAt": sn.get("publishedAt"),
        "thumbnailUrl": thumb,
        "url": _video_url(vid) if vid else None,
    }


def _normalize_video_item(item: dict[str, Any]) -> dict[str, Any]:
    vid = item.get("id")
    sn = item.get("snippet") or {}
    cd = item.get("contentDetails") or {}
    st = item.get("statistics") or {}
    thumbs = sn.get("thumbnails") or {}
    thumb = (thumbs.get("medium") or thumbs.get("default") or {}).get("url")
    title = sn.get("title")
    return {
        "videoId": vid,
        "title": title,
        "channelTitle": sn.get("channelTitle"),
        "channelId": sn.get("channelId"),
        "artist": resolve_track_artist(title=title),
        "description": sn.get("description"),
        "publishedAt": sn.get("publishedAt"),
        "duration": cd.get("duration"),
        "viewCount": st.get("viewCount"),
        "thumbnailUrl": thumb,
        "url": _video_url(vid) if vid else None,
    }


def _normalize_playlist_item(entry: dict[str, Any]) -> dict[str, Any] | None:
    sn = entry.get("snippet") or {}
    title = sn.get("title") or ""
    if title in ("Private video", "Deleted video"):
        return None
    vid = (entry.get("contentDetails") or {}).get("videoId") or (sn.get("resourceId") or {}).get(
        "videoId"
    )
    if not vid:
        return None
    thumbs = sn.get("thumbnails") or {}
    thumb = (thumbs.get("medium") or thumbs.get("default") or {}).get("url")
    return {
        "videoId": vid,
        "title": title,
        "channelTitle": sn.get("channelTitle"),
        "channelId": sn.get("channelId"),
        "artist": resolve_track_artist(title=title),
        "publishedAt": sn.get("publishedAt"),
        "thumbnailUrl": thumb,
        "url": _video_url(vid),
    }


async def _details_by_video_ids(
    client: YouTubeClient,
    video_ids: list[str],
    *,
    mix_id: str | None = None,
    user_id: str | None = None,
) -> tuple[dict[str, dict[str, Any]], bool]:
    """Detalhes normalizados por videoId; preferência por library.json."""
    ids = [v for v in video_ids if v]
    if not ids:
        return {}, True

    stored = stored_catalog_entries(ids, user_id)
    by_id: dict[str, dict[str, Any]] = {
        vid: dict(stored[vid]) for vid in stored if stored[vid].get("duration")
    }

    if mix_id:
        from app.mix_catalog_cache import get_mix_catalog_for_ids

        missing = [v for v in ids if not by_id.get(v, {}).get("duration")]
        mix_part = get_mix_catalog_for_ids(mix_id, missing)
        for vid, entry in mix_part.items():
            if entry.get("duration"):
                by_id[vid] = {**stored.get(vid, {}), **entry}

    need_api = [v for v in ids if not by_id.get(v, {}).get("duration")]
    from_cache = not need_api

    if need_api:
        try:
            details, api_cached = await get_videos_cached(client, need_api)
        except YouTubeApiError as exc:
            raise _http_from_youtube_error(exc) from exc
        from_cache = from_cache and api_cached
        for entry in details.get("items", []):
            extra = _normalize_video_item(entry)
            vid = extra.get("videoId")
            if not vid:
                continue
            merged = {**stored.get(vid, {}), **extra}
            by_id[vid] = merged

    for vid in ids:
        if vid not in by_id and vid in stored:
            by_id[vid] = dict(stored[vid])

    return by_id, from_cache


async def _attach_video_details(
    client: YouTubeClient,
    items: list[dict[str, Any]],
    *,
    user_id: str | None = None,
) -> list[dict[str, Any]]:
    video_ids = [i["videoId"] for i in items if i.get("videoId")]
    if video_ids:
        by_id, _from_cache = await _details_by_video_ids(client, video_ids, user_id=user_id)
        for item in items:
            extra = by_id.get(item.get("videoId") or "")
            if not extra:
                continue
            for key in (
                "duration",
                "description",
                "descriptionOriginal",
                "descriptionLang",
                "viewCount",
                "channelId",
                "channelTitle",
                "artist",
                "thumbnailUrl",
            ):
                if extra.get(key) is not None:
                    item[key] = extra[key]
    from app.duration_policy import mark_items_on_server

    items = mark_items_on_server(items)
    return list(await asyncio.gather(*(_with_pt_description(i) for i in items)))


def _search_cache_key_for_request(
    *,
    search_q: str,
    max_results: int,
    page_token: str | None,
    pub_after: str | None,
    pub_before: str | None,
    search_order: str | None,
    mix_id: str | None,
) -> str:
    return search_cache_key(
        q=search_q,
        max_results=max_results,
        page_token=page_token,
        published_after=pub_after,
        published_before=pub_before,
        order=search_order,
        mix_id=mix_id,
    )


def _user_search_quota_message() -> str:
    n = settings.user_search_daily_limit
    return (
        f"Você usou suas {n} buscas do dia (consultas que consomem cota da API). "
        "Enquanto isso, ouça em Recentes (buscas recentes), em Biblioteca "
        "(playlists salvas e músicas salvas) ou reabra resultados que já carregou hoje. "
        "Novas consultas amanhã."
    )


def _ensure_search_quota_if_uncached(
    *,
    user_id: str,
    search_q: str,
    max_results: int,
    page_token: str | None,
    pub_after: str | None,
    pub_before: str | None,
    search_order: str | None,
    mix_id: str | None,
) -> None:
    key = _search_cache_key_for_request(
        search_q=search_q,
        max_results=max_results,
        page_token=page_token,
        pub_after=pub_after,
        pub_before=pub_before,
        search_order=search_order,
        mix_id=mix_id,
    )
    if get_search_cached(key) is not None:
        return
    from app.users_db import user_has_unlimited_search, user_search_quota_snapshot

    # Só a 1ª página conta no limite diário; "Mostrar mais" continua a mesma busca/mix.
    if not page_token and not user_has_unlimited_search(user_id):
        user_q = user_search_quota_snapshot(user_id, limit=settings.user_search_daily_limit)
        if user_q["remaining"] < 1:
            raise HTTPException(status_code=429, detail=_user_search_quota_message())
    if not _api_quota_can_search():
        raise HTTPException(status_code=429, detail=QUOTA_EXCEEDED_MESSAGE)


def _record_user_search_if_live(
    user_id: str, from_cache: bool, *, page_token: str | None = None
) -> None:
    if from_cache or page_token:
        return
    from app.users_db import record_user_search_api_call

    record_user_search_api_call(user_id)


def _ensure_channel_quota_if_uncached(
    *,
    channel_id: str,
    max_results: int,
    page_token: str | None,
) -> None:
    """Bloqueia só se canal/playlist precisarem de API e a cota local estiver baixa."""
    uploads_id = get_channel_uploads_cached(channel_id)
    playlist_cached = False
    if uploads_id:
        pl_key = playlist_cache_key(uploads_id, max_results, page_token)
        playlist_cached = get_playlist_cached(pl_key) is not None
    if uploads_id and playlist_cached:
        return
    if not _api_quota_can_search():
        raise HTTPException(status_code=429, detail=QUOTA_EXCEEDED_MESSAGE)


@app.post("/api/auth/register")
async def auth_register(response: Response, body: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    nickname = str(
        body.get("nickname") or body.get("apelido") or body.get("displayName") or body.get("name") or ""
    ).strip()
    password = str(body.get("password") or "")
    try:
        register_user(nickname=nickname, password=password)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    user, token = login_user(nickname=nickname, password=password)
    set_session_cookie(response, token)
    return {"user": user}


@app.post("/api/auth/login")
async def auth_login(response: Response, body: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    nickname = str(body.get("nickname") or body.get("apelido") or body.get("email") or "").strip()
    password = str(body.get("password") or "")
    try:
        user, token = login_user(nickname=nickname, password=password)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    set_session_cookie(response, token)
    return {"user": user}


@app.post("/api/auth/logout")
async def auth_logout(
    response: Response,
    rutsfy_session: str | None = Cookie(default=None),
) -> dict[str, bool]:
    logout_user(rutsfy_session)
    clear_session_cookie(response)
    return {"ok": True}


@app.get("/api/auth/me")
async def auth_me(user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
    from app.users_db import record_user_event

    try:
        record_user_event(str(user["id"]), "visit")
    except Exception:
        pass
    return {"user": user}


@app.post("/api/me/plays")
async def me_record_play(
    body: dict[str, Any] = Body(default_factory=dict),
    user_id: str = Depends(get_current_user_id),
) -> dict[str, bool]:
    from app.users_db import record_user_event

    video_id = str(body.get("videoId") or "").strip()
    if not video_id:
        raise HTTPException(status_code=422, detail="Faixa inválida")
    record_user_event(
        user_id,
        "play",
        video_id=video_id,
        title=str(body.get("title") or ""),
        artist=str(body.get("artist") or ""),
    )
    return {"ok": True}


def _require_admin(user_id: str) -> None:
    from app.users_db import get_user_by_id

    row = get_user_by_id(user_id)
    if not row or not row.get("is_admin"):
        raise HTTPException(status_code=403, detail="Sem permissão")


@app.get("/api/admin/users")
async def admin_users(user_id: str = Depends(get_current_user_id)) -> dict[str, Any]:
    from app.users_db import list_admin_users

    _require_admin(user_id)
    return {"users": list_admin_users()}


@app.get("/api/admin/users/{target_id}/history")
async def admin_user_history(
    target_id: str,
    user_id: str = Depends(get_current_user_id),
) -> dict[str, Any]:
    from app.users_db import get_user_by_id, list_user_history

    _require_admin(user_id)
    row = get_user_by_id(target_id)
    if not row:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    nick = (row.get("nickname") or row.get("display_name") or "").strip() or "Conta"
    return {"user": {"id": target_id, "nickname": nick}, "items": list_user_history(target_id)}


@app.get("/api/admin/stats")
async def admin_stats_route(user_id: str = Depends(get_current_user_id)) -> dict[str, Any]:
    from app.users_db import admin_stats

    _require_admin(user_id)
    return admin_stats()


@app.get("/api/me/preferences")
async def me_preferences_get(user_id: str = Depends(get_current_user_id)) -> dict[str, Any]:
    return get_preferences(user_id)


@app.put("/api/me/preferences")
async def me_preferences_put(
    body: dict[str, Any] = Body(default_factory=dict),
    user_id: str = Depends(get_current_user_id),
) -> dict[str, Any]:
    from app.users_db import sanitize_user_preferences

    current = get_preferences(user_id)
    merged = {**current, **sanitize_user_preferences(body)}
    return set_preferences(user_id, merged)


_AVATAR_MAX_BYTES = 2 * 1024 * 1024
_AVATAR_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}


@app.patch("/api/me/profile")
async def me_profile_patch(
    body: dict[str, Any] = Body(default_factory=dict),
    user_id: str = Depends(get_current_user_id),
) -> dict[str, Any]:
    display_name = body.get("displayName")
    if display_name is not None:
        display_name = str(display_name)
    else:
        display_name = None
    current_password = body.get("currentPassword")
    new_password = body.get("newPassword")
    if current_password is not None:
        current_password = str(current_password)
    if new_password is not None:
        new_password = str(new_password)
    if display_name is None and not new_password:
        raise HTTPException(status_code=422, detail="Nada para atualizar")
    try:
        user = update_account_profile(
            user_id,
            display_name=display_name,
            current_password=current_password if new_password else None,
            new_password=new_password,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {"user": user}


@app.get("/api/me/avatar")
async def me_avatar_get(user_id: str = Depends(get_current_user_id)) -> FileResponse:
    row = get_user_by_id(user_id)
    if not row or not row.get("avatar_file"):
        raise HTTPException(status_code=404, detail="Sem foto")
    path = avatars_root() / str(row["avatar_file"])
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Sem foto")
    media = "image/jpeg"
    if path.suffix.lower() == ".png":
        media = "image/png"
    elif path.suffix.lower() == ".webp":
        media = "image/webp"
    return FileResponse(path, media_type=media)


@app.post("/api/me/avatar")
async def me_avatar_upload(
    user_id: str = Depends(get_current_user_id),
    file: UploadFile = File(...),
) -> dict[str, Any]:
    content_type = (file.content_type or "").split(";")[0].strip().lower()
    ext = _AVATAR_TYPES.get(content_type)
    if not ext:
        raise HTTPException(status_code=422, detail="Use JPG, PNG ou WebP")
    data = await file.read()
    if len(data) > _AVATAR_MAX_BYTES:
        raise HTTPException(status_code=413, detail="Imagem muito grande (máx. 2 MB)")
    if not data:
        raise HTTPException(status_code=422, detail="Arquivo vazio")
    root = avatars_root()
    for old in root.glob(f"{user_id}.*"):
        try:
            old.unlink()
        except OSError:
            pass
    filename = f"{user_id}{ext}"
    (root / filename).write_bytes(data)
    set_user_avatar_file(user_id, filename)
    row = get_user_by_id(user_id)
    if not row:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return {"user": public_user(row)}


@app.delete("/api/me/avatar")
async def me_avatar_delete(user_id: str = Depends(get_current_user_id)) -> dict[str, Any]:
    try:
        user = remove_user_avatar(user_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {"user": user}


def _inject_base_path(html: str) -> str:
    base = settings.normalized_base_path()
    if not base:
        return html
    inject = f'<script>window.RUTSFY_BASE="{base}";</script>'
    if inject not in html:
        html = html.replace("<head>", f"<head>\n    {inject}", 1)
    for token in ('href="/', 'src="/'):
        html = html.replace(token, f'{token[:-1]}{base}/')
    html = html.replace('register("/sw.js?v=3"', f'register("{base}/sw.js?v=3"')
    html = html.replace('register("/sw.js"', f'register("{base}/sw.js?v=3"')
    html = html.replace('scope: "/"', f'scope: "{base}/"')
    return html


@app.get("/")
async def index() -> HTMLResponse:
    index_file = STATIC_DIR / "index.html"
    if not index_file.is_file():
        raise HTTPException(status_code=404, detail="UI não instalada")
    html = index_file.read_text(encoding="utf-8")
    return HTMLResponse(_inject_base_path(html))


PWA_ICON_VERSION = "3"


@app.get("/manifest.webmanifest")
async def web_manifest() -> JSONResponse:
    path = STATIC_DIR / "manifest.webmanifest"
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Manifest não encontrado")
    import json

    data = json.loads(path.read_text(encoding="utf-8"))
    base = settings.normalized_base_path()
    if base:
        data["id"] = f"{base}/"
        data["start_url"] = f"{base}/?source=pwa"
        data["scope"] = f"{base}/"
    icons = data.get("icons") or []
    for icon in icons:
        src = (icon.get("src") or "").split("?", 1)[0]
        if not src.startswith("/"):
            continue
        icon["src"] = f"{public_path(src)}?v={PWA_ICON_VERSION}"
    return JSONResponse(
        data,
        media_type="application/manifest+json",
        headers={"Cache-Control": "no-cache, max-age=0"},
    )


@app.get("/sw.js")
async def service_worker() -> FileResponse:
    path = STATIC_DIR / "sw.js"
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Service worker não encontrado")
    return FileResponse(
        path,
        media_type="application/javascript",
        headers={"Cache-Control": "no-cache"},
    )


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/mixes")
async def mixes(_user_id: str = Depends(get_current_user_id)) -> dict[str, Any]:
    from app.mix_catalog_cache import list_loaded_mix_ids

    return {
        "categories": list_mix_categories(),
        "items": list_mixes(),
        "loadedMixIds": list_loaded_mix_ids(),
    }


@app.get("/api/catalog/free")
async def catalog_free(
    shelf_limit: int = Query(24, ge=4, le=80),
    _user_id: str = Depends(get_current_user_id),
) -> dict[str, Any]:
    """Faixas já no servidor — não consome cota de busca do usuário."""
    from app.server_catalog import free_catalog_summary

    return free_catalog_summary(shelf_limit=shelf_limit)


@app.get("/api/catalog/free/category/{category_id}")
async def catalog_free_category(
    category_id: str,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    _user_id: str = Depends(get_current_user_id),
) -> dict[str, Any]:
    from app.server_catalog import free_category_items

    try:
        return free_category_items(category_id, offset=offset, limit=limit)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/api/catalog/free/not-in-library")
async def catalog_free_not_in_library(
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=300),
    user_id: str = Depends(get_current_user_id),
) -> dict[str, Any]:
    from app.server_catalog import free_not_in_user_library

    return free_not_in_user_library(user_id, offset=offset, limit=limit)


@app.get("/api/catalog/free/search")
async def catalog_free_search(
    q: str = Query("", description="Filtro local (título, artista, canal)"),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    _user_id: str = Depends(get_current_user_id),
) -> dict[str, Any]:
    from app.server_catalog import search_server_catalog

    return search_server_catalog(q, offset=offset, limit=limit)


@app.get("/api/catalog/server-video-ids")
async def catalog_server_video_ids(
    _user_id: str = Depends(get_current_user_id),
) -> dict[str, Any]:
    """IDs de vídeo com áudio já em downloads/ (para ✓ na UI)."""
    from app.server_catalog import list_server_video_ids

    ids = list_server_video_ids()
    return {"videoIds": ids, "total": len(ids)}


@app.get("/api/catalog/download-blocklist")
async def catalog_download_blocklist(
    _user_id: str = Depends(get_current_user_id),
) -> dict[str, Any]:
    """Faixas bloqueadas para download (ex.: acima do limite de MB)."""
    from app.download_blocklist import list_video_ids
    from app.config import settings

    ids = list_video_ids()
    return {
        "videoIds": ids,
        "total": len(ids),
        "maxFileSizeMb": int(settings.max_track_file_size_mb or 0),
    }


@app.get("/api/mixes/{mix_id}/catalog")
async def mix_catalog_more(
    mix_id: str,
    exclude: str = Query("", description="videoIds já listados, separados por vírgula"),
    exclude_song_keys: str = Query(
        "",
        alias="exclude_song_keys",
        description="Chaves de dedupe (artista|faixa) já listadas",
    ),
    limit: int = Query(20, ge=1, le=100),
    user_id: str = Depends(get_current_user_id),
) -> dict[str, Any]:
    """Mais faixas do catálogo local do mix (sem nova busca na API do YouTube)."""
    if not get_mix(mix_id):
        raise HTTPException(status_code=404, detail="Mix não encontrado")
    from app.duration_policy import mark_items_on_server
    from app.mix_catalog_cache import mix_catalog_discoverable_count, mix_catalog_more_items

    skip = frozenset(x.strip() for x in exclude.split(",") if x.strip())
    song_keys = frozenset(x.strip() for x in exclude_song_keys.split(",") if x.strip())
    items = mix_catalog_more_items(mix_id, skip, exclude_song_keys=song_keys, limit=limit)
    items = mark_items_on_server(items)
    items = list(await asyncio.gather(*(_with_pt_description(i) for i in items)))
    from app.catalog_filters import prepare_discoverable_items

    items = prepare_discoverable_items(items)
    total = mix_catalog_discoverable_count(mix_id)
    return {
        "mixId": mix_id,
        "items": items,
        "total": total,
        "limit": limit,
        "mixCatalogLoaded": total > 0,
    }


@app.post("/api/mixes/{mix_id}/covers")
async def mix_covers_add(
    mix_id: str,
    body: dict[str, Any] = Body(default_factory=dict),
    _user_id: str = Depends(get_current_user_id),
) -> dict[str, Any]:
    if not get_mix(mix_id):
        raise HTTPException(status_code=404, detail="Mix não encontrado")
    raw = body.get("thumbnailUrls") or body.get("urls") or []
    if not isinstance(raw, list):
        raise HTTPException(status_code=422, detail="thumbnailUrls deve ser uma lista")
    from app.mix_covers import add_mix_covers, preview_covers_for_mix

    pool = add_mix_covers(mix_id, [u for u in raw if isinstance(u, str)])
    return {
        "mixId": mix_id,
        "stored": len(pool),
        "coverPreview": preview_covers_for_mix(mix_id),
    }


@app.get("/api/search")
async def search(
    q: str = Query("", description="Termo de busca"),
    max_results: int = Query(15, ge=1, le=50),
    light: bool = Query(False, description="Só metadados do search (rápido, 1 página API)"),
    page_token: str | None = Query(None, description="nextPageToken da busca anterior"),
    mix_id: str | None = Query(None, description="Preset Explorar (substitui q e filtros)"),
    published_after: str | None = Query(None, alias="published_after"),
    published_before: str | None = Query(None, alias="published_before"),
    order: str | None = Query(None, description="date | relevance | viewCount …"),
    user_id: str = Depends(get_current_user_id),
) -> dict[str, Any]:
    raise HTTPException(status_code=410, detail="A busca antiga foi desligada. Use o catálogo.")
    client = _client()

    search_q = q.strip()
    pub_after = published_after
    pub_before = published_before
    search_order = order

    if mix_id:
        mix = get_mix(mix_id)
        if not mix:
            raise HTTPException(status_code=404, detail="Mix não encontrado")
        from app.mixes import mix_for_client

        resolved = mix_for_client(mix)
        search_q = resolved["query"]
        pub_after = resolved.get("publishedAfter") or pub_after
        pub_before = resolved.get("publishedBefore") or pub_before
        search_order = resolved.get("order") or search_order

    if not search_q:
        raise HTTPException(status_code=422, detail="Informe q ou mix_id")

    _ensure_search_quota_if_uncached(
        user_id=user_id,
        search_q=search_q,
        max_results=max_results,
        page_token=page_token,
        pub_after=pub_after,
        pub_before=pub_before,
        search_order=search_order,
        mix_id=mix_id,
    )

    if light:
        try:
            raw, from_cache = await search_videos_cached(
                client,
                q=search_q,
                max_results=max_results,
                page_token=page_token,
                published_after=pub_after,
                published_before=pub_before,
                order=search_order,
                mix_id=mix_id,
            )
        except YouTubeApiError as exc:
            raise _http_from_youtube_error(exc) from exc
        _record_user_search_if_live(user_id, from_cache, page_token=page_token)
        items = [_normalize_search_item(i) for i in raw.get("items", [])]
        from app.mix_catalog_cache import enrich_items_from_disk_catalog

        items = enrich_items_from_disk_catalog(mix_id, items, user_id=user_id)
        from app.catalog_filters import prepare_discoverable_items
        from app.duration_policy import mark_items_on_server

        items = mark_items_on_server(items)
        items = prepare_discoverable_items(items)
        if mix_id and items:
            from app.mix_catalog_cache import store_mix_catalog_items

            store_mix_catalog_items(mix_id, items)
        _maybe_store_mix_covers(mix_id, items)
        payload: dict[str, Any] = {
            "query": search_q,
            "mixId": mix_id,
            "items": items,
            "total": len(items),
            "light": True,
            "nextPageToken": raw.get("nextPageToken"),
            "fromCache": from_cache,
        }
        if mix_id:
            from app.mix_covers import preview_covers_for_mix
            from app.mix_catalog_cache import mix_catalog_discoverable_count

            payload["coverPreview"] = preview_covers_for_mix(mix_id)
            total_cached = mix_catalog_discoverable_count(mix_id)
            payload["mixCatalogTotal"] = total_cached
            payload["mixCatalogLoaded"] = total_cached > 0
        return payload

    try:
        raw, from_cache = await search_videos_cached(
            client,
            q=search_q,
            max_results=max_results,
            page_token=page_token,
            published_after=pub_after,
            published_before=pub_before,
            order=search_order,
            mix_id=mix_id,
        )
    except YouTubeApiError as exc:
        raise _http_from_youtube_error(exc) from exc

    _record_user_search_if_live(user_id, from_cache, page_token=page_token)
    items = [_normalize_search_item(i) for i in raw.get("items", [])]
    items = await _attach_video_details(client, items, user_id=user_id)
    from app.catalog_filters import prepare_discoverable_items

    items = prepare_discoverable_items(items)
    if mix_id:
        from app.mix_catalog_cache import store_mix_catalog_items

        store_mix_catalog_items(mix_id, items)
    _maybe_store_mix_covers(mix_id, items)
    payload = {
        "query": search_q,
        "mixId": mix_id,
        "items": items,
        "total": len(items),
        "light": False,
        "fromCache": from_cache,
    }
    if mix_id:
        from app.mix_covers import preview_covers_for_mix

        payload["coverPreview"] = preview_covers_for_mix(mix_id)
    return payload


@app.get("/api/videos")
async def videos(
    ids: str = Query(..., description="IDs separados por vírgula"),
    mix_id: str | None = Query(None, alias="mix_id", description="Mix Explorar (cache local)"),
    user_id: str = Depends(get_current_user_id),
) -> dict[str, Any]:
    raise HTTPException(status_code=410, detail="A busca antiga foi desligada. Use o catálogo.")
    video_ids = [x.strip() for x in ids.split(",") if x.strip()]
    mix_key = mix_id.strip() if mix_id else None
    if mix_key and not get_mix(mix_key):
        mix_key = None
    by_id, from_cache = await _details_by_video_ids(
        _client(), video_ids, mix_id=mix_key, user_id=user_id
    )
    items = [by_id[v] for v in video_ids if v in by_id]
    items = list(await asyncio.gather(*(_with_pt_description(i) for i in items)))
    from app.duration_policy import filter_discoverable_items, mark_items_on_server

    items = mark_items_on_server(items)
    listed_ids = {i.get("videoId") for i in items if i.get("videoId")}
    items = filter_discoverable_items(items)
    kept_ids = {i.get("videoId") for i in items if i.get("videoId")}
    hidden_video_ids = sorted(vid for vid in listed_ids if vid not in kept_ids)
    if mix_key and items:
        from app.mix_catalog_cache import store_mix_catalog_items

        store_mix_catalog_items(mix_key, items)
    return {"items": items, "hiddenVideoIds": hidden_video_ids, "fromCache": from_cache}


@app.get("/api/playlist/{playlist_id}/items")
async def playlist_items(
    playlist_id: str,
    max_results: int = Query(50, ge=1, le=50),
) -> dict[str, Any]:
    raise HTTPException(status_code=410, detail="A busca antiga foi desligada. Use o catálogo.")
    try:
        raw, from_cache = await get_playlist_items_cached(
            _client(), playlist_id, max_results=max_results
        )
    except YouTubeApiError as exc:
        raise _http_from_youtube_error(exc) from exc

    items: list[dict[str, Any]] = []
    for entry in raw.get("items", []):
        sn = entry.get("snippet") or {}
        vid = (entry.get("contentDetails") or {}).get("videoId") or (sn.get("resourceId") or {}).get(
            "videoId"
        )
        thumbs = sn.get("thumbnails") or {}
        thumb = (thumbs.get("medium") or thumbs.get("default") or {}).get("url")
        items.append(
            {
                "videoId": vid,
                "title": sn.get("title"),
                "channelTitle": sn.get("channelTitle"),
                "position": sn.get("position"),
                "thumbnailUrl": thumb,
                "url": _video_url(vid) if vid else None,
            }
        )

    return {"playlistId": playlist_id, "items": items, "fromCache": from_cache}


@app.get("/api/channel/{channel_id}/videos")
async def channel_videos(
    channel_id: str,
    max_results: int = Query(15, ge=1, le=50),
    page_token: str | None = Query(None, alias="page_token"),
    light: bool = Query(False, description="Só metadados da playlist (sem videos.list)"),
    user_id: str = Depends(get_current_user_id),
) -> dict[str, Any]:
    """Vídeos publicados no canal (playlist de uploads), do mais recente."""
    raise HTTPException(status_code=410, detail="A busca antiga foi desligada. Use o catálogo.")
    channel_id = channel_id.strip()
    if not channel_id:
        raise HTTPException(status_code=422, detail="channel_id inválido")

    _ensure_channel_quota_if_uncached(
        channel_id=channel_id,
        max_results=max_results,
        page_token=page_token,
    )

    client = _client()
    try:
        uploads_id, uploads_cached = await get_channel_uploads_playlist_cached(client, channel_id)
    except YouTubeApiError as exc:
        raise _http_from_youtube_error(exc) from exc

    if not uploads_id:
        raise HTTPException(status_code=404, detail="Canal não encontrado ou sem uploads")

    try:
        raw, playlist_cached = await get_playlist_items_cached(
            client, uploads_id, max_results=max_results, page_token=page_token
        )
    except YouTubeApiError as exc:
        raise _http_from_youtube_error(exc) from exc

    items: list[dict[str, Any]] = []
    channel_title: str | None = None
    for entry in raw.get("items") or []:
        norm = _normalize_playlist_item(entry)
        if not norm:
            continue
        if not channel_title and norm.get("channelTitle"):
            channel_title = norm["channelTitle"]
        norm["channelId"] = channel_id
        items.append(norm)

    if not light:
        items = await _attach_video_details(client, items, user_id=user_id)
    from app.catalog_filters import prepare_discoverable_items

    items = prepare_discoverable_items(items)
    return {
        "channelId": channel_id,
        "channelTitle": channel_title,
        "items": items,
        "total": len(items),
        "light": light,
        "nextPageToken": raw.get("nextPageToken"),
        "fromCache": uploads_cached and playlist_cached,
    }


def _deezer_id(raw: str) -> int:
    try:
        value = int(raw)
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=404, detail="Item do catálogo não encontrado.") from exc
    if value < 0:
        raise HTTPException(status_code=404, detail="Item do catálogo não encontrado.")
    return value


@app.get("/api/catalog/deezer/search")
async def deezer_catalog_search(
    q: str = Query("", description="Artista, álbum ou faixa"),
    _user_id: str = Depends(get_current_user_id),
) -> dict[str, Any]:
    from app.deezer_catalog import DeezerError, search_catalog

    if not q.strip():
        raise HTTPException(status_code=422, detail="Informe o que buscar.")
    try:
        return await search_catalog(q)
    except DeezerError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.get("/api/catalog/deezer/home")
async def deezer_catalog_home(_user_id: str = Depends(get_current_user_id)) -> dict[str, Any]:
    from app.deezer_catalog import DeezerError, home as deezer_home

    try:
        return await deezer_home()
    except DeezerError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.get("/api/catalog/deezer/explore")
async def deezer_catalog_explore(_user_id: str = Depends(get_current_user_id)) -> dict[str, Any]:
    from app.deezer_catalog import DeezerError, explore_page

    try:
        return await explore_page()
    except DeezerError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.get("/api/catalog/deezer/library")
async def deezer_catalog_library(user_id: str = Depends(get_current_user_id)) -> dict[str, Any]:
    from app.deezer_catalog import DeezerError, artist_pictures, library_feed
    from app.users_db import user_catalog_taste

    taste = user_catalog_taste(user_id)
    artists = [dict(card) for card in taste.get("listenAgain") or []]
    try:
        feed = dict(await library_feed(taste.get("genreNames") or []))
        pictures = await artist_pictures([card.get("id") for card in artists])
    except DeezerError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    for card in artists:
        card["picture"] = pictures.get(str(card.get("id"))) or card.get("picture") or ""
    feed["listenAgain"] = artists
    return feed


@app.get("/api/catalog/deezer/genres/{genre_id}")
async def deezer_catalog_genre(
    genre_id: str,
    _user_id: str = Depends(get_current_user_id),
) -> dict[str, Any]:
    from app.deezer_catalog import DeezerError, genre_page

    try:
        return await genre_page(_deezer_id(genre_id))
    except DeezerError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.get("/api/catalog/deezer/artists/{artist_id}/related")
async def deezer_catalog_artist_related(
    artist_id: str,
    _user_id: str = Depends(get_current_user_id),
) -> dict[str, Any]:
    from app.deezer_catalog import DeezerError, artist_related

    try:
        return await artist_related(_deezer_id(artist_id))
    except DeezerError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.get("/api/catalog/deezer/artists/{artist_id}/radio")
async def deezer_catalog_artist_radio(
    artist_id: str,
    _user_id: str = Depends(get_current_user_id),
) -> dict[str, Any]:
    from app.deezer_catalog import DeezerError, artist_radio

    try:
        return await artist_radio(_deezer_id(artist_id))
    except DeezerError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.get("/api/catalog/deezer/artists/{artist_id}")
async def deezer_catalog_artist(
    artist_id: str,
    _user_id: str = Depends(get_current_user_id),
) -> dict[str, Any]:
    from app.deezer_catalog import DeezerError, artist_page

    try:
        return await artist_page(_deezer_id(artist_id))
    except DeezerError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.get("/api/catalog/deezer/albums/{album_id}")
async def deezer_catalog_album(
    album_id: str,
    _user_id: str = Depends(get_current_user_id),
) -> dict[str, Any]:
    from app.deezer_catalog import DeezerError, album_page

    try:
        return await album_page(_deezer_id(album_id))
    except DeezerError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.get("/api/catalog/deezer/playlists/{playlist_id}")
async def deezer_catalog_playlist(
    playlist_id: str,
    _user_id: str = Depends(get_current_user_id),
) -> dict[str, Any]:
    from app.deezer_catalog import DeezerError, playlist_page

    try:
        return await playlist_page(_deezer_id(playlist_id))
    except DeezerError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.post("/api/catalog/deezer/known")
async def deezer_catalog_known(
    body: dict[str, Any] = Body(default_factory=dict),
    _user_id: str = Depends(get_current_user_id),
) -> dict[str, Any]:
    """Quais faixas do catálogo já têm áudio no servidor, sem dar play."""
    from app.deezer_resolve import lookup_known_audio

    raw_ids = body.get("deezerIds")
    if not isinstance(raw_ids, list):
        raw_ids = []
    return {"items": lookup_known_audio(raw_ids[:200])}


@app.post("/api/catalog/deezer/resolve")
async def deezer_catalog_resolve(
    body: dict[str, Any] = Body(default_factory=dict),
    _user_id: str = Depends(get_current_user_id),
) -> dict[str, Any]:
    """Localiza o vídeo com yt-dlp. Não usa a cota de search.list."""
    from app.deezer_resolve import ResolveError, resolve_catalog_track
    from app.duration_policy import parse_duration_seconds

    title = str(body.get("title") or "").strip()
    if not title:
        raise HTTPException(status_code=400, detail="Faixa sem título.")
    try:
        found = await asyncio.to_thread(
            resolve_catalog_track,
            title=title,
            artist=str(body.get("artist") or ""),
            deezer_id=body.get("deezerId"),
            duration_sec=parse_duration_seconds(body.get("duration")),
        )
    except ResolveError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {
        "videoId": found["videoId"],
        "fromCache": found.get("fromCache", False),
        "title": title,
        "artist": str(body.get("artist") or "").strip(),
        "album": str(body.get("album") or "").strip(),
        "genre": str(body.get("genre") or "").strip(),
        "duration": body.get("duration") or "",
        "thumbnailUrl": str(body.get("thumbnailUrl") or "").strip(),
        "catalogSource": "deezer",
    }


@app.post("/api/download/{video_id}")
async def download(
    video_id: str,
    body: dict[str, Any] = Body(default_factory=dict),
    user_id: str = Depends(get_current_user_id),
) -> dict[str, Any]:
    """Baixa só o áudio do vídeo (formato original) e salva metadados na memória."""
    client_meta = {
        k: body.get(k)
        for k in (
            "title",
            "artist",
            "artistId",
            "album",
            "albumId",
            "deezerId",
            "genre",
            "catalogSource",
            "duration",
            "thumbnailUrl",
            "channelId",
            "channelTitle",
        )
        if body.get(k)
    }
    if body.get("downloadPriority") is not None:
        try:
            client_meta["downloadPriority"] = int(body["downloadPriority"])
        except (TypeError, ValueError):
            pass
    try:
        return await download_audio(
            video_id,
            metadata_provider=_metadata_for,
            user_id=user_id,
            client_meta=client_meta or None,
        )
    except DownloadError as exc:
        raise HTTPException(status_code=500, detail=_download_error_detail(exc)) from exc


@app.get("/api/quota")
async def quota(user_id: str = Depends(get_current_user_id)) -> dict[str, Any]:
    """Cota da API v3 usada hoje (o Google não expõe a restante; contamos a nossa)."""
    from app.users_db import user_search_quota_snapshot

    snap = _quota_tracker().snapshot()
    snap["minRemainingSearch"] = settings.quota_min_remaining_search
    snap["userSearch"] = user_search_quota_snapshot(
        user_id, limit=settings.user_search_daily_limit
    )
    return snap


@app.get("/api/downloads")
async def downloads(user_id: str = Depends(get_current_user_id)) -> dict[str, Any]:
    """Histórico: áudios já baixados no servidor."""
    from app.duration_policy import mark_items_on_server

    items = list_downloads(user_id)
    items = mark_items_on_server(items)
    items = list(await asyncio.gather(*(_with_pt_description(i) for i in items)))
    return {"items": items}


@app.get("/api/history")
async def history(user_id: str = Depends(get_current_user_id)) -> dict[str, Any]:
    """Alias do histórico (mesmo conteúdo de /api/downloads)."""
    return await downloads(user_id)


@app.get("/api/library")
async def library_list(user_id: str = Depends(get_current_user_id)) -> dict[str, Any]:
    """Biblioteca: faixas salvas com '+'."""
    from app.duration_policy import mark_items_on_server

    items = list_saved_library(user_id)
    items = mark_items_on_server(items)
    items = list(await asyncio.gather(*(_with_pt_description(i) for i in items)))
    return {"items": items}


@app.post("/api/library/{video_id}")
async def library_add(
    video_id: str,
    body: dict[str, Any] = Body(default_factory=dict),
    user_id: str = Depends(get_current_user_id),
) -> dict[str, Any]:
    """Adiciona à biblioteca, grava metadados e baixa o áudio se ainda não existir."""
    meta = {
        k: body.get(k)
        for k in (
            "title",
            "artist",
            "channelId",
            "channelTitle",
            "description",
            "duration",
            "thumbnailUrl",
            "url",
        )
        if body.get(k)
    }
    set_library_membership(video_id, in_library=True, meta=meta, user_id=user_id)
    try:
        result = await download_audio(video_id, metadata_provider=_metadata_for, user_id=user_id)
    except DownloadError as exc:
        raise HTTPException(status_code=500, detail=_download_error_detail(exc)) from exc
    return {**result, "inLibrary": True}


@app.delete("/api/library/{video_id}")
async def library_remove(
    video_id: str,
    user_id: str = Depends(get_current_user_id),
) -> dict[str, Any]:
    """Remove da biblioteca (mantém no histórico se já foi baixado)."""
    stored = set_library_membership(video_id, in_library=False, user_id=user_id)
    return {"videoId": video_id, "inLibrary": False, "item": stored}


@app.get("/api/tracks/{video_id}/cover.jpg")
async def track_cover_image(
    video_id: str,
    size: str = Query("1280", pattern="^(1280|480|320)$"),
    _user_id: str = Depends(get_current_user_id),
) -> Response:
    """Capa da faixa no nosso domínio — o celular usa na notificação (fundo + miniatura)."""
    if not normalize_video_id(video_id):
        raise HTTPException(status_code=422, detail="video_id inválido")
    try:
        data, media_type = await fetch_track_cover(video_id, size=size)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=404, detail="Capa não encontrada") from exc
    return Response(
        content=data,
        media_type=media_type,
        headers={"Cache-Control": "public, max-age=604800"},
    )


@app.post("/api/worker/jobs/claim")
async def worker_job_claim(
    body: dict[str, Any] = Body(default_factory=dict),
    _auth: None = Depends(require_worker_token),
) -> dict[str, Any]:
    from app import download_relay

    worker_id = str(body.get("workerId") or "lan-1").strip() or "lan-1"
    job = download_relay.claim_next(worker_id=worker_id)
    return {"job": job}


@app.post("/api/worker/jobs/release-claims")
async def worker_release_claims(
    body: dict[str, Any] = Body(default_factory=dict),
    _auth: None = Depends(require_worker_token),
) -> dict[str, Any]:
    from app import download_relay

    worker_id = str(body.get("workerId") or "lan-1").strip() or "lan-1"
    n = download_relay.release_worker_claims(worker_id=worker_id)
    return {"released": n}


@app.post("/api/worker/jobs/{job_id}/heartbeat")
async def worker_job_heartbeat(
    job_id: str,
    body: dict[str, Any] = Body(default_factory=dict),
    _auth: None = Depends(require_worker_token),
) -> dict[str, Any]:
    from app import download_relay

    worker_id = str(body.get("workerId") or "lan-1").strip() or "lan-1"
    if not download_relay.get_job(job_id):
        raise HTTPException(status_code=404, detail="Job não encontrado")
    ok = download_relay.touch_job(job_id, worker_id=worker_id)
    if not ok:
        raise HTTPException(status_code=409, detail="Job não está claimed por este worker")
    return {"ok": True}


@app.post("/api/worker/jobs/{job_id}/fail")
async def worker_job_fail(
    job_id: str,
    body: dict[str, Any] = Body(default_factory=dict),
    _auth: None = Depends(require_worker_token),
) -> dict[str, str]:
    from app import download_relay

    if not download_relay.get_job(job_id):
        raise HTTPException(status_code=404, detail="Job não encontrado")
    download_relay.mark_failed(job_id, str(body.get("error") or "falha no worker"))
    return {"ok": "true"}


@app.post("/api/worker/jobs/{job_id}/upload")
async def worker_job_upload(
    job_id: str,
    file: UploadFile = File(...),
    _auth: None = Depends(require_worker_token),
) -> dict[str, str]:
    from app import download_relay

    job = download_relay.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job não encontrado")
    if job.get("status") not in ("claimed", "pending"):
        raise HTTPException(status_code=409, detail="Job já finalizado")

    video_id = str(job.get("video_id") or "")
    if not video_id:
        raise HTTPException(status_code=422, detail="video_id inválido no job")

    root = downloads_root()
    root.mkdir(parents=True, exist_ok=True)
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in {".opus", ".ogg", ".m4a", ".webm", ".mp3", ".wav"}:
        suffix = ".opus"
    dest = root / f"{video_id}{suffix}"
    tmp = root / f".{video_id}.worker.tmp{suffix}"

    try:
        data = await file.read()
        if not data:
            raise HTTPException(status_code=422, detail="Arquivo vazio")
        tmp.write_bytes(data)
        from app.size_policy import enforce_file_size_or_block

        try:
            enforce_file_size_or_block(video_id, tmp)
        except Exception as exc:
            from app.downloader import DownloadError

            tmp.unlink(missing_ok=True)
            if isinstance(exc, DownloadError):
                download_relay.mark_failed(job_id, str(exc))
                raise HTTPException(status_code=422, detail=str(exc)) from exc
            raise
        tmp.replace(dest)
    except HTTPException:
        tmp.unlink(missing_ok=True)
        raise
    except OSError as exc:
        tmp.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=f"Falha ao gravar: {exc}") from exc

    download_relay.mark_completed(job_id)
    return {"ok": "true", "filename": dest.name}


@app.get("/api/downloads/{filename}")
async def download_file(
    filename: str,
    _user_id: str = Depends(get_current_user_id),
) -> FileResponse:
    """Devolve um áudio salvo no servidor (pra tocar ou baixar do navegador)."""
    root = downloads_root().resolve()
    target = (root / filename).resolve()
    if root not in target.parents or not target.is_file():
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    # Todos os arquivos da pasta são trilhas de áudio: garante o MIME correto
    # (ex.: .webm de áudio seria servido como video/webm e o <audio> pode falhar).
    audio_media_types = {
        ".m4a": "audio/mp4",
        ".webm": "audio/webm",
        ".opus": "audio/opus",
        ".ogg": "audio/ogg",
        ".mp3": "audio/mpeg",
        ".mkv": "audio/x-matroska",
    }
    media_type = audio_media_types.get(target.suffix.lower(), "application/octet-stream")
    return FileResponse(
        target,
        filename=filename,
        media_type=media_type,
        headers={"Cache-Control": "private, max-age=604800"},
    )
