from __future__ import annotations

from typing import Any, Callable

import httpx

YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"

# Custo em unidades de cota por operação (docs: determine_quota_cost)
QUOTA_UNIT_COSTS: dict[str, int] = {
    "search": 100,
    "videos": 1,
    "playlistItems": 1,
    "channels": 1,
}


QUOTA_EXCEEDED_MESSAGE = (
    "Limite diário de buscas atingido. "
    "Tente de novo amanhã ou ouça faixas em Recentes e Biblioteca."
)


class YouTubeApiError(Exception):
    def __init__(self, status_code: int, message: str, details: Any | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.details = details

    @property
    def quota_exceeded(self) -> bool:
        if "quota exceeded" in str(self).lower():
            return True
        payload = self.details
        if not isinstance(payload, dict):
            return False
        err = payload.get("error")
        if not isinstance(err, dict):
            return False
        for item in err.get("errors") or []:
            if isinstance(item, dict) and item.get("reason") == "quotaExceeded":
                return True
        return False


class YouTubeClient:
    def __init__(self, api_key: str, quota_hook: Callable[[int], None] | None = None) -> None:
        self._api_key = api_key
        self._quota_hook = quota_hook

    async def _get(self, path: str, params: dict[str, str | int]) -> dict[str, Any]:
        query = {**params, "key": self._api_key}
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{YOUTUBE_API_BASE}/{path}", params=query)

        if response.status_code != 200:
            payload: Any
            try:
                payload = response.json()
            except Exception:
                payload = response.text
            message = "Falha na API de busca"
            if isinstance(payload, dict) and "error" in payload:
                err = payload["error"]
                message = err.get("message", message)
            raise YouTubeApiError(response.status_code, message, payload)

        if self._quota_hook:
            self._quota_hook(QUOTA_UNIT_COSTS.get(path, 1))

        return response.json()

    async def search_videos(
        self,
        q: str,
        max_results: int = 15,
        page_token: str | None = None,
        published_after: str | None = None,
        published_before: str | None = None,
        order: str | None = None,
    ) -> dict[str, Any]:
        params: dict[str, str | int] = {
            "part": "snippet",
            "type": "video",
            "q": q,
            "maxResults": max(1, min(max_results, 50)),
        }
        if page_token:
            params["pageToken"] = page_token
        if published_after:
            params["publishedAfter"] = published_after
        if published_before:
            params["publishedBefore"] = published_before
        if order:
            params["order"] = order
        return await self._get("search", params)

    async def get_videos(self, video_ids: list[str]) -> dict[str, Any]:
        if not video_ids:
            return {"items": []}
        return await self._get(
            "videos",
            {
                "part": "snippet,contentDetails,statistics",
                "id": ",".join(video_ids[:50]),
            },
        )

    async def get_playlist_items(
        self,
        playlist_id: str,
        max_results: int = 50,
        page_token: str | None = None,
    ) -> dict[str, Any]:
        params: dict[str, str | int] = {
            "part": "snippet,contentDetails",
            "playlistId": playlist_id,
            "maxResults": max(1, min(max_results, 50)),
        }
        if page_token:
            params["pageToken"] = page_token
        return await self._get("playlistItems", params)

    async def get_channel(self, channel_id: str) -> dict[str, Any]:
        return await self._get(
            "channels",
            {
                "part": "snippet,contentDetails",
                "id": channel_id,
            },
        )


class RotatingYouTubeClient:
    """Tenta as chaves em ordem; em quotaExceeded passa para a próxima."""

    def __init__(
        self,
        api_keys: list[str],
        *,
        key_id_for: Callable[[str], str],
        quota_hook: Callable[[str, int], None] | None = None,
        quota_exceeded_hook: Callable[[str], None] | None = None,
        is_key_usable: Callable[[str], bool] | None = None,
    ) -> None:
        if not api_keys:
            raise ValueError("api_keys vazio")
        self._api_keys = api_keys
        self._key_id_for = key_id_for
        self._quota_hook = quota_hook
        self._quota_exceeded_hook = quota_exceeded_hook
        self._is_key_usable = is_key_usable

    def _ordered_keys(self) -> list[tuple[str, str]]:
        pairs = [(k, self._key_id_for(k)) for k in self._api_keys]
        if not self._is_key_usable:
            return pairs
        usable = [(k, kid) for k, kid in pairs if self._is_key_usable(kid)]
        return usable or pairs

    async def _run(self, method: str, /, *args: Any, **kwargs: Any) -> dict[str, Any]:
        last_exc: YouTubeApiError | None = None
        for api_key, key_id in self._ordered_keys():
            hook = None
            if self._quota_hook:
                hook = lambda units, kid=key_id: self._quota_hook(kid, units)
            client = YouTubeClient(api_key, quota_hook=hook)
            try:
                return await getattr(client, method)(*args, **kwargs)
            except YouTubeApiError as exc:
                if exc.quota_exceeded and self._quota_exceeded_hook:
                    self._quota_exceeded_hook(key_id)
                    last_exc = exc
                    continue
                raise
        if last_exc:
            raise last_exc
        raise YouTubeApiError(429, QUOTA_EXCEEDED_MESSAGE)

    async def search_videos(
        self,
        q: str,
        max_results: int = 15,
        page_token: str | None = None,
        published_after: str | None = None,
        published_before: str | None = None,
        order: str | None = None,
    ) -> dict[str, Any]:
        return await self._run(
            "search_videos",
            q,
            max_results=max_results,
            page_token=page_token,
            published_after=published_after,
            published_before=published_before,
            order=order,
        )

    async def get_videos(self, video_ids: list[str]) -> dict[str, Any]:
        return await self._run("get_videos", video_ids)

    async def get_playlist_items(
        self,
        playlist_id: str,
        max_results: int = 50,
        page_token: str | None = None,
    ) -> dict[str, Any]:
        return await self._run(
            "get_playlist_items",
            playlist_id,
            max_results=max_results,
            page_token=page_token,
        )

    async def get_channel(self, channel_id: str) -> dict[str, Any]:
        return await self._run("get_channel", channel_id)