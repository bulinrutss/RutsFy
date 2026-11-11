import asyncio
from pathlib import Path

import httpx

key = Path(__file__).resolve().parents[1].joinpath("backend", ".env").read_text(encoding="utf-8")
key = [l for l in key.splitlines() if l.startswith("YOUTUBE_API_KEY=")][0].split("=", 1)[1]


async def main() -> None:
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.get(
            "https://www.googleapis.com/youtube/v3/videos",
            params={"part": "snippet", "id": "aqz-KE-bpKQ", "key": key},
        )
        quota_headers = {
            k: v
            for k, v in r.headers.items()
            if "quota" in k.lower() or "rate" in k.lower()
        }
        print("Status:", r.status_code)
        print("Headers de cota/rate:", quota_headers if quota_headers else "NENHUM header de cota retornado")


asyncio.run(main())