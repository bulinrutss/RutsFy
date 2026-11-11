"""Validação de youtube_cookies.txt (Netscape) para yt-dlp na VPS."""

from __future__ import annotations

from pathlib import Path

# Pelo menos um PSID + LOGIN_INFO costumam ser necessários no IP de datacenter.
_REQUIRED = ("LOGIN_INFO",)
_PSID_ANY = ("__Secure-1PSID", "__Secure-3PSID")


def cookie_names_in_file(path: Path) -> set[str]:
    names: set[str] = set()
    for ln in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if ln.startswith("#") or not ln.strip():
            continue
        parts = ln.split("\t")
        if len(parts) >= 6:
            names.add(parts[5])
    return names


def validate_youtube_cookies(path: Path) -> list[str]:
    """Lista problemas; vazia = OK para enviar ao servidor."""
    if not path.is_file():
        return [f"Arquivo não encontrado: {path}"]
    head = path.read_text(encoding="utf-8", errors="replace")[:200]
    if "# Netscape HTTP Cookie File" not in head:
        return ["Formato inválido — precisa ser Netscape (extensão Get cookies.txt LOCALLY)."]
    names = cookie_names_in_file(path)
    issues: list[str] = []
    if not any(n in names for n in _PSID_ANY):
        issues.append("Falta cookie de sessão (__Secure-1PSID ou __Secure-3PSID).")
    for n in _REQUIRED:
        if n not in names:
            issues.append(f"Falta {n} — exporte estando logado no YouTube.")
    if len(names) < 8:
        issues.append(f"Poucos cookies ({len(names)}); exporte de novo em youtube.com logado.")
    return issues
