"""Chamadas YouTube com cache transparente (sem consumir cota em hit)."""

from __future__ import annotations

from typing import Any

from app.youtube_cache import (
    get_channel_uploads_cached,
    get_playlist_cached,
    get_search_cached,
    get_videos_cached as read_videos_cache,
    merge_videos_response,
    playlist_cache_key,
    put_channel_uploads_cached,
    put_playlist_cached,
    put_search_cached,
    put_videos_cached,
    search_cache_key,
    search_ttl_seconds,
)
from app.youtube_client import RotatingYouTubeClient, YouTubeClient

YouTubeClientLike = YouTubeClient | RotatingYouTubeClient


async def search_videos_cached(
    client: YouTubeClientLike,
    *,
    q: str,
    max_results: int = 15,
    page_token: str | None = None,
    published_after: str | None = None,
    published_before: str | None = None,
    order: str | None = None,
    mix_id: str | None = None,
) -> tuple[dict[str, Any], bool]:
    key = search_cache_key(
        q=q,
        max_results=max_results,
        page_token=page_token,
        published_after=published_after,
        published_before=published_before,
        order=order,
        mix_id=mix_id,
    )
    hit = get_search_cached(key)
    if hit is not None:
        return hit, True

    raw = await client.search_videos(
        q=q,
        max_results=max_results,
        page_token=page_token,
        published_after=published_after,
        published_before=published_before,
        order=order,
    )
    ttl = search_ttl_seconds(
        mix_id=mix_id,
        published_after=published_after,
        published_before=published_before,
        order=order,
    )
    put_search_cached(key, raw, ttl)
    return raw, False


async def get_videos_cached(client: YouTubeClient, video_ids: list[str]) -> tuple[dict[str, Any], bool]:
    ids = [v for v in video_ids if v][:50]
    if not ids:
        return {"items": []}, True

    cached_items, missing = read_videos_cache(ids)
    if not missing:
        return merge_videos_response(ids, cached_items, []), True

    fetched = await client.get_videos(missing)
    fetched_items = fetched.get("items") or []
    if fetched_items:
        put_videos_cached(fetched_items)

    return merge_videos_response(ids, cached_items, fetched_items), len(missing) == 0


async def get_playlist_items_cached(
    client: YouTubeClientLike,
    playlist_id: str,
    max_results: int = 50,
    page_token: str | None = None,
) -> tuple[dict[str, Any], bool]:
    key = playlist_cache_key(playlist_id, max_results, page_token)
    hit = get_playlist_cached(key)
    if hit is not None:
        return hit, True

    raw = await client.get_playlist_items(
        playlist_id, max_results=max_results, page_token=page_token
    )
    put_playlist_cached(key, raw)
    return raw, False


async def get_channel_uploads_playlist_cached(
    client: YouTubeClientLike,
    channel_id: str,
) -> tuple[str | None, bool]:
    cached = get_channel_uploads_cached(channel_id)
    if cached:
        return cached, True

    raw = await client.get_channel(channel_id)
    items = raw.get("items") or []
    if not items:
        return None, False
    uploads = (items[0].get("contentDetails") or {}).get("relatedPlaylists") or {}
    playlist_id = uploads.get("uploads")
    if isinstance(playlist_id, str) and playlist_id:
        put_channel_uploads_cached(channel_id, playlist_id)
        return playlist_id, False
    return None, False
