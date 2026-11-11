"""Contador de cota da API de busca (Data API v3).

O Google NÃO oferece endpoint nem header para consultar a cota restante
(confirmado empiricamente). Custo por operação (documentação Google):
  - search:        100 unidades
  - videos:          1 unidade
  - playlistItems:   1 unidade
A cota diária padrão (10.000) reseta à meia-noite do fuso America/Los_Angeles.
"""

from __future__ import annotations

import json
import threading
from typing import Any
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

QUOTA_RESET_TZ = "America/Los_Angeles"


def quota_today() -> str:
    try:
        tz = ZoneInfo(QUOTA_RESET_TZ)
        return datetime.now(tz).date().isoformat()
    except (ZoneInfoNotFoundError, OSError):
        return datetime.utcnow().date().isoformat()


class QuotaTracker:
    """Contador único (legado). Preferir MultiKeyQuotaTracker com várias API keys."""

    def __init__(self, file_path: Path, limit: int) -> None:
        self._path = file_path
        self._limit = limit
        self._lock = threading.Lock()

    @staticmethod
    def _today() -> str:
        return quota_today()

    def _load(self) -> dict:
        try:
            data = json.loads(self._path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
        except (OSError, ValueError):
            pass
        return {}

    def _save(self, data: dict) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def record(self, units: int) -> None:
        """Registra consumo de `units` (chamado a cada request bem-sucedido)."""
        today = self._today()
        with self._lock:
            data = self._load()
            if data.get("date") != today:
                data = {"date": today}
            data["used"] = int(data.get("used", 0)) + int(units)
            self._save(data)

    def snapshot(self) -> dict:
        today = self._today()
        with self._lock:
            data = self._load()
            used = int(data.get("used", 0)) if data.get("date") == today else 0
        return {
            "date": today,
            "limit": self._limit,
            "used": used,
            "remaining": max(self._limit - used, 0),
            "resetsAt": f"meia-noite (fuso {QUOTA_RESET_TZ})",
        }


class MultiKeyQuotaTracker:
    """Cota estimada por chave; ao esgotar uma, o cliente tenta a próxima."""

    def __init__(self, file_path: Path, limit: int, key_ids: list[str]) -> None:
        self._path = file_path
        self._limit = limit
        self._key_ids = list(key_ids)
        self._lock = threading.Lock()

    def _today(self) -> str:
        return QuotaTracker._today()

    def _load(self) -> dict:
        try:
            data = json.loads(self._path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
        except (OSError, ValueError):
            pass
        return {}

    def _save(self, data: dict) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def _ensure_today(self, data: dict) -> dict:
        today = self._today()
        if data.get("date") != today:
            return {"date": today, "keys": {}}
        keys = data.get("keys")
        if not isinstance(keys, dict):
            data["keys"] = {}
        # Migra quota.json antigo (campo "used" único) para a 1ª chave.
        if self._key_ids and not data["keys"] and "used" in data:
            data["keys"][self._key_ids[0]] = {
                "used": int(data.get("used", 0)),
                "exhausted": int(data.get("used", 0)) >= self._limit,
            }
        return data

    def _entry(self, data: dict, key_id: str) -> dict:
        keys = data.setdefault("keys", {})
        ent = keys.get(key_id)
        if not isinstance(ent, dict):
            ent = {"used": 0, "exhausted": False}
            keys[key_id] = ent
        return ent

    def record(self, key_id: str, units: int) -> None:
        with self._lock:
            data = self._ensure_today(self._load())
            ent = self._entry(data, key_id)
            ent["used"] = int(ent.get("used", 0)) + int(units)
            self._save(data)

    def mark_quota_exceeded(self, key_id: str) -> None:
        with self._lock:
            data = self._ensure_today(self._load())
            ent = self._entry(data, key_id)
            ent["exhausted"] = True
            ent["used"] = max(int(ent.get("used", 0)), self._limit)
            self._save(data)

    def _key_snapshot(self, key_id: str, data: dict) -> dict[str, Any]:
        ent = data.get("keys", {}).get(key_id) if isinstance(data.get("keys"), dict) else None
        if not isinstance(ent, dict):
            used = 0
            exhausted = False
        else:
            used = int(ent.get("used", 0))
            exhausted = bool(ent.get("exhausted"))
        remaining = 0 if exhausted else max(self._limit - used, 0)
        return {
            "keyId": key_id,
            "used": used,
            "remaining": remaining,
            "exhausted": exhausted,
        }

    def is_usable(self, key_id: str, *, min_remaining: int = 0) -> bool:
        with self._lock:
            data = self._ensure_today(self._load())
            snap = self._key_snapshot(key_id, data)
        if snap["exhausted"]:
            return False
        return snap["remaining"] >= min_remaining

    def any_usable(self, min_remaining: int) -> bool:
        if not self._key_ids:
            return False
        return any(self.is_usable(k, min_remaining=min_remaining) for k in self._key_ids)

    def snapshot(self) -> dict[str, Any]:
        today = self._today()
        with self._lock:
            data = self._ensure_today(self._load())
            per_key = [self._key_snapshot(k, data) for k in self._key_ids]
        total_limit = self._limit * max(len(self._key_ids), 1)
        total_used = sum(p["used"] for p in per_key)
        total_remaining = sum(p["remaining"] for p in per_key)
        active = sum(1 for p in per_key if not p["exhausted"] and p["remaining"] > 0)
        return {
            "date": today,
            "limit": total_limit,
            "used": total_used,
            "remaining": total_remaining,
            "resetsAt": f"meia-noite (fuso {QUOTA_RESET_TZ})",
            "apiKeyCount": len(self._key_ids),
            "apiKeysActive": active,
            "apiKeys": per_key,
        }