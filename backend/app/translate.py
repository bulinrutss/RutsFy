"""Tradução de descrições para português.

Tenta o endpoint do Chrome Translate (sem API key). Se estiver bloqueado,
cai no MyMemory. Cada texto traduzido fica em cache em `translations.json`
dentro da pasta de downloads — traduzir 2x o mesmo texto custa zero.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import threading
from pathlib import Path

import httpx

from app.downloader import downloads_root

_LOCK = threading.Lock()
_SEM: asyncio.Semaphore | None = None
_MAX_LEN = 3500
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    )
}

_PT_MARKERS = (
    "ção",
    "ões",
    "não",
    "você",
    "música",
    "também",
    "está",
    "são",
    "para",
    "uma",
    "com",
    "que",
    "pelo",
    "pela",
)


def _cache_path() -> Path:
    return downloads_root() / "translations.json"


def _load_cache() -> dict[str, dict[str, str]]:
    try:
        data = json.loads(_cache_path().read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def _save_cache(data: dict[str, dict[str, str]]) -> None:
    try:
        _cache_path().write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    except OSError:
        pass


def _key(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()


def _looks_portuguese(text: str) -> bool:
    low = text.lower()
    hits = sum(1 for m in _PT_MARKERS if m in low)
    return hits >= 3


async def _via_chrome(text: str) -> dict[str, str] | None:
    async with httpx.AsyncClient(timeout=20.0, headers=_HEADERS, follow_redirects=True) as client:
        r = await client.post(
            "https://clients5.google.com/translate_a/t",
            params={"client": "dict-chrome-ex", "sl": "auto", "tl": "pt"},
            data={"q": text},
        )
        r.raise_for_status()
        payload = r.json()
    # Formatos possíveis: [["pt text","en"]]  ou  ["pt text"]
    translated = ""
    lang = ""
    if isinstance(payload, list) and payload:
        first = payload[0]
        if isinstance(first, list):
            translated = str(first[0] or "")
            lang = str(first[1] or "") if len(first) > 1 else ""
        else:
            translated = str(first or "")
    if not translated:
        return None
    return {"text": translated, "lang": lang}


async def _via_mymemory(text: str) -> dict[str, str] | None:
    # GET tem limite curto; corta em pedaços de ~450 chars
    chunks = [text[i : i + 450] for i in range(0, len(text), 450)] or [text]
    parts: list[str] = []
    lang = ""
    async with httpx.AsyncClient(timeout=20.0, headers=_HEADERS, follow_redirects=True) as client:
        for chunk in chunks:
            r = await client.get(
                "https://api.mymemory.translated.net/get",
                params={"q": chunk, "langpair": "autodetect|pt"},
            )
            r.raise_for_status()
            payload = r.json()
            data = payload.get("responseData") or {}
            piece = (data.get("translatedText") or "").strip()
            if not piece:
                return None
            parts.append(piece)
            if not lang:
                matches = payload.get("matches") or []
                if matches and isinstance(matches[0], dict):
                    lang = str(matches[0].get("source") or "")
    return {"text": "".join(parts), "lang": lang}


def _semaphore() -> asyncio.Semaphore:
    global _SEM
    if _SEM is None:
        _SEM = asyncio.Semaphore(5)
    return _SEM


async def translate_to_pt(text: str) -> dict[str, str]:
    """Traduz para pt; devolve {"text": texto_pt, "lang": idioma_detectado}."""
    text = (text or "").strip()
    if not text:
        return {"text": "", "lang": ""}

    key = _key(text)
    with _LOCK:
        cached = _load_cache().get(key)
    if cached:
        return {"text": cached["pt"], "lang": cached["lang"]}

    if len(text) > _MAX_LEN:
        text = text[:_MAX_LEN].rstrip() + " […]"

    result: dict[str, str] | None = None
    async with _semaphore():
        try:
            result = await _via_chrome(text)
        except Exception:
            result = None
        if result is None:
            try:
                result = await _via_mymemory(text)
            except Exception:
                result = None

    if result is None:
        return {"text": text, "lang": ""}

    with _LOCK:
        cache = _load_cache()
        cache[key] = {"pt": result["text"], "lang": result["lang"]}
        _save_cache(cache)
    return result


async def ensure_portuguese(text: str) -> dict[str, str]:
    """Garante o texto em português; se já for pt, devolve o original."""
    original = (text or "").strip()
    if not original:
        return {"text": "", "lang": "", "translated": False}
    if _looks_portuguese(original):
        return {"text": original, "lang": "pt", "translated": False}

    info = await translate_to_pt(original)
    lang = (info.get("lang") or "").lower()
    if lang.startswith("pt"):
        return {"text": original, "lang": lang or "pt", "translated": False}
    if not info.get("text") or info["text"] == original:
        # Falhou em traduzir: devolve o original, sem fingir que traduziu
        return {"text": original, "lang": lang, "translated": False}
    return {"text": info["text"], "lang": lang, "translated": True}
