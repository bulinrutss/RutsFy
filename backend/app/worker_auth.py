"""Autenticação do worker de download na LAN."""

from __future__ import annotations

from fastapi import Header, HTTPException

from app.config import settings


def require_worker_token(
    authorization: str | None = Header(None, alias="Authorization"),
) -> None:
    expected = (settings.lan_download_worker_token or "").strip()
    if not expected:
        raise HTTPException(status_code=503, detail="Worker de download não configurado")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token do worker ausente")
    token = authorization[7:].strip()
    if token != expected:
        raise HTTPException(status_code=403, detail="Token do worker inválido")
