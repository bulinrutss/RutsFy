"""Exporta cookies do navegador (yt-dlp) e envia para a VPS — uso manual ou tarefa agendada.

Log: C:\\Users\\svbul\\Downloads\\cokies\\rutsfy-cookies-upload.log
"""

from __future__ import annotations

import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from youtube_cookies_oracle import restart_sound_api, upload_cookies_to_oracle  # noqa: E402
from youtube_cookies_util import validate_youtube_cookies  # noqa: E402

COOKIES_DIR = Path(r"C:\Users\svbul\Downloads\cokies")
COOKIES_FILE = COOKIES_DIR / "www.youtube.com_cookies.txt"
LOG_FILE = COOKIES_DIR / "rutsfy-cookies-upload.log"
YTDLP = ROOT / "backend" / ".venv" / "Scripts" / "yt-dlp.exe"
PROBE_URL = "https://www.youtube.com/watch?v=jNQXAC9IVRw"
BROWSERS = ("chrome", "edge", "firefox", "brave")


def log(msg: str) -> None:
    COOKIES_DIR.mkdir(parents=True, exist_ok=True)
    line = f"{datetime.now(timezone.utc).astimezone().isoformat(timespec='seconds')} {msg}"
    print(line)
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def try_export_from_browser(browser: str) -> bool:
    if not YTDLP.is_file():
        log(f"yt-dlp não encontrado: {YTDLP}")
        return False
    tmp = COOKIES_FILE.with_suffix(".tmp.txt")
    cmd = [
        str(YTDLP),
        "--cookies-from-browser",
        browser,
        "--cookies",
        str(tmp),
        "--skip-download",
        "--print",
        "id",
        PROBE_URL,
    ]
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
    except subprocess.TimeoutExpired:
        log(f"export {browser}: timeout")
        return False
    if proc.returncode != 0:
        tail = (proc.stderr or proc.stdout or "").strip().splitlines()
        log(f"export {browser} falhou: {tail[-1] if tail else proc.returncode}")
        tmp.unlink(missing_ok=True)
        return False
    if not tmp.is_file():
        log(f"export {browser}: arquivo não criado")
        return False
    issues = validate_youtube_cookies(tmp)
    if issues:
        log(f"export {browser} incompleto: {'; '.join(issues)}")
        tmp.unlink(missing_ok=True)
        return False
    tmp.replace(COOKIES_FILE)
    log(f"export {browser}: OK → {COOKIES_FILE}")
    return True


def find_valid_cookie_file_in_dir() -> Path | None:
    if not COOKIES_DIR.is_dir():
        return None
    candidates = [
        p
        for p in COOKIES_DIR.glob("*.txt")
        if p.is_file() and "cookies" in p.name.lower()
    ]
    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    for path in candidates:
        if not validate_youtube_cookies(path):
            return path
    return None


def ensure_valid_cookies() -> Path:
    for browser in BROWSERS:
        if try_export_from_browser(browser):
            return COOKIES_FILE

    found = find_valid_cookie_file_in_dir()
    if found:
        if found.resolve() != COOKIES_FILE.resolve():
            import shutil

            shutil.copy2(found, COOKIES_FILE)
            log(f"usando cookies de {found.name} → {COOKIES_FILE}")
        else:
            log(f"usando cookies existentes: {COOKIES_FILE}")
        return COOKIES_FILE

    if COOKIES_FILE.is_file():
        issues = validate_youtube_cookies(COOKIES_FILE)
        if issues:
            log(f"cookies locais inválidos: {'; '.join(issues)}")

    raise SystemExit(
        "Não foi possível obter cookies válidos. Feche o Chrome/Edge, ou exporte com "
        '"Get cookies.txt LOCALLY" em youtube.com e salve em '
        f"{COOKIES_FILE}"
    )


def main() -> None:
    log("--- início renew_and_upload ---")
    try:
        path = ensure_valid_cookies()
        upload_cookies_to_oracle(path)
        log("upload Oracle: OK")
        restart_sound_api()
        log("restart sound-api: OK")
        log("--- concluído ---")
    except SystemExit as exc:
        log(f"ERRO: {exc}")
        raise
    except Exception as exc:
        log(f"ERRO: {exc}")
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
