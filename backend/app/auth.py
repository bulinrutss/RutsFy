"""Autenticação por sessão (cookie HttpOnly)."""

from __future__ import annotations

import hashlib
import hmac
import re
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import Cookie, Depends, HTTPException, Response

from app.config import settings
from app.users_db import (
    clear_user_avatar_file,
    create_session,
    create_user,
    delete_session,
    get_user_by_email,
    get_user_by_id,
    get_user_by_nickname,
    get_user_id_for_session,
    import_legacy_library_json,
    legacy_import_done,
    mark_legacy_import_done,
    update_user_display_name,
    update_user_password_hash,
    record_user_event,
    set_user_admin,
)

SESSION_COOKIE = "rutsfy_session"
SESSION_DAYS = 30
_PBKDF2_ITERS = 260_000
_NICKNAME_RE = re.compile(r"^[\w][\w\s.-]*[\w]$|^[\w]{2,}$", re.UNICODE)


def normalize_nickname(raw: str) -> str:
    nick = " ".join((raw or "").strip().split())
    if len(nick) < 2:
        raise ValueError("Apelido deve ter pelo menos 2 caracteres")
    if len(nick) > 32:
        raise ValueError("Apelido muito longo (máx. 32)")
    if not _NICKNAME_RE.match(nick):
        raise ValueError("Apelido inválido (use letras, números, espaço, . _ -)")
    return nick


def _hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _PBKDF2_ITERS)
    return f"pbkdf2_sha256${_PBKDF2_ITERS}${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        algo, iters_s, salt_hex, digest_hex = stored.split("$", 3)
        if algo != "pbkdf2_sha256":
            return False
        iters = int(iters_s)
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(digest_hex)
    except (ValueError, TypeError):
        return False
    got = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iters)
    return hmac.compare_digest(got, expected)


def _session_expiry() -> str:
    exp = datetime.now(timezone.utc) + timedelta(days=SESSION_DAYS)
    return exp.replace(microsecond=0).isoformat()


def _lookup_user_for_login(identifier: str) -> dict[str, Any] | None:
    ident = identifier.strip()
    if not ident:
        return None
    row = get_user_by_nickname(ident)
    if row:
        return row
    # Contas antigas (e-mail)
    if "@" in ident:
        return get_user_by_email(ident)
    return None


def register_user(*, nickname: str, password: str) -> dict[str, Any]:
    nick = normalize_nickname(nickname)
    if len(password) < 6:
        raise ValueError("Senha deve ter pelo menos 6 caracteres")
    if get_user_by_nickname(nick):
        raise ValueError("Apelido já cadastrado")
    pw_hash = _hash_password(password)
    user = create_user(nickname=nick, password_hash=pw_hash)
    return user


def login_user(*, nickname: str, password: str) -> tuple[dict[str, Any], str]:
    row = _lookup_user_for_login(nickname)
    if not row or not verify_password(password, row["password_hash"]):
        raise ValueError("Apelido ou senha incorretos")
    from app.users_db import revoke_sessions_for_user

    revoke_sessions_for_user(row["id"])
    token = secrets.token_urlsafe(32)
    create_session(row["id"], token, _session_expiry())
    try:
        record_user_event(row["id"], "login")
        record_user_event(row["id"], "visit")
    except Exception:
        pass
    return _public_user(row), token


def ensure_builtin_admin() -> None:
    nick = "admin"
    row = get_user_by_nickname(nick)
    if not row:
        register_user(nickname=nick, password="428766")
        row = get_user_by_nickname(nick)
    if row and not row.get("is_admin"):
        set_user_admin(row["id"], True)


def logout_user(token: str | None) -> None:
    if token:
        delete_session(token)


def _user_nickname(row: dict[str, Any]) -> str:
    nick = (row.get("nickname") or row.get("display_name") or "").strip()
    if nick:
        return nick
    email = (row.get("email") or "").strip()
    if email and "@" in email and not email.endswith("@users.local"):
        return email.split("@", 1)[0]
    return "Conta"


def public_user(row: dict[str, Any]) -> dict[str, Any]:
    nick = _user_nickname(row)
    out: dict[str, Any] = {
        "id": row["id"],
        "nickname": nick,
        "displayName": nick,
        "isAdmin": bool(row.get("is_admin")),
    }
    avatar_file = row.get("avatar_file")
    if avatar_file:
        ver = row.get("avatar_updated_at") or "1"
        out["avatarUrl"] = f"/api/me/avatar?v={ver}"
    else:
        out["avatarUrl"] = None
    return out


def _public_user(row: dict[str, Any]) -> dict[str, Any]:
    return public_user(row)


def update_account_profile(
    user_id: str,
    *,
    display_name: str | None = None,
    current_password: str | None = None,
    new_password: str | None = None,
) -> dict[str, Any]:
    row = get_user_by_id(user_id)
    if not row:
        raise ValueError("Usuário não encontrado")
    if new_password:
        if not current_password or not verify_password(current_password, row["password_hash"]):
            raise ValueError("Senha atual incorreta")
        if len(new_password) < 6:
            raise ValueError("Nova senha deve ter pelo menos 6 caracteres")
        update_user_password_hash(user_id, _hash_password(new_password))
    if display_name is not None:
        name = normalize_nickname(display_name)
        if name.lower() != _user_nickname(row).lower():
            taken = get_user_by_nickname(name)
            if taken and taken["id"] != user_id:
                raise ValueError("Apelido já está em uso")
        update_user_display_name(user_id, name)
    updated = get_user_by_id(user_id)
    if not updated:
        raise ValueError("Usuário não encontrado")
    return public_user(updated)


def remove_user_avatar(user_id: str) -> dict[str, Any]:
    from app.users_db import avatars_root

    row = get_user_by_id(user_id)
    if not row:
        raise ValueError("Usuário não encontrado")
    for path in avatars_root().glob(f"{user_id}.*"):
        try:
            path.unlink()
        except OSError:
            pass
    clear_user_avatar_file(user_id)
    updated = get_user_by_id(user_id)
    if not updated:
        raise ValueError("Usuário não encontrado")
    return public_user(updated)


def set_session_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=SESSION_COOKIE,
        value=token,
        httponly=True,
        samesite="lax",
        max_age=SESSION_DAYS * 86400,
        path=settings.cookie_path(),
        secure=settings.session_cookie_secure,
    )


def clear_session_cookie(response: Response) -> None:
    response.delete_cookie(SESSION_COOKIE, path=settings.cookie_path())


async def get_current_user_id(
    rutsfy_session: str | None = Cookie(default=None, alias=SESSION_COOKIE),
) -> str:
    if not rutsfy_session:
        raise HTTPException(status_code=401, detail="Faça login para continuar")
    user_id = get_user_id_for_session(rutsfy_session)
    if not user_id:
        raise HTTPException(status_code=401, detail="Sessão expirada. Entre de novo")
    return user_id


async def get_optional_user_id(
    rutsfy_session: str | None = Cookie(default=None, alias=SESSION_COOKIE),
) -> str | None:
    if not rutsfy_session:
        return None
    return get_user_id_for_session(rutsfy_session)


async def get_current_user(user_id: str = Depends(get_current_user_id)) -> dict[str, Any]:
    row = get_user_by_id(user_id)
    if not row:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")
    return _public_user(row)


def maybe_import_legacy_for_user(user_id: str) -> int:
    if legacy_import_done():
        return 0
    from app.downloader import _load_library

    videos = _load_library()
    if not videos:
        mark_legacy_import_done()
        return 0
    return import_legacy_library_json(user_id, videos)
