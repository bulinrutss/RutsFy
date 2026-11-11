"""Download de áudio via yt-dlp + memória de metadados.

Baixa só a trilha de áudio e reconverte para Opus (bitrate configurável,
padrão 64 kbps). O navegador toca
Opus nativo, sem conversão no cliente. Metadados ficam em `library.json`.
"""

from __future__ import annotations

import asyncio
import json
import os
import re
import shutil
import subprocess
import sys
import threading
from collections.abc import Awaitable, Callable
from datetime import datetime
from pathlib import Path
from typing import Any

from app.config import settings
from app.metadata_util import resolve_track_artist
from app.public_paths import public_path

_VIDEO_ID_RE = re.compile(r"[A-Za-z0-9_-]{11}")
_TIMEOUT_SECONDS = 15 * 60
_LOCK = threading.Lock()
_async_guard = asyncio.Lock()
_video_async_locks: dict[str, asyncio.Lock] = {}
# Um yt-dlp por vez evita corrida no mesmo arquivo e reduz bloqueio do YouTube.
_YTDLP_SEM = asyncio.Semaphore(1)
_AUDIO_EXT = ".opus"
_AUDIO_SUFFIXES = {".m4a", ".webm", ".opus", ".ogg", ".mp3", ".mkv"}

MetadataProvider = Callable[[str], Awaitable[dict[str, Any] | None]]


class DownloadError(Exception):
    """Erro de download (yt-dlp ausente, falha de rede, vídeo indisponível etc.)."""


def _venv_sibling(name: str) -> Path | None:
    """Procura um executável na mesma pasta do Python em uso (ex.: .venv/Scripts)."""
    candidate = Path(sys.executable).parent / name
    return candidate if candidate.is_file() else None


def _winget_ytdlp() -> Path | None:
    """Fallback Windows: yt-dlp instalado via winget (se o PATH da sessão estiver velho)."""
    base = Path.home() / "AppData" / "Local" / "Microsoft" / "WinGet" / "Packages"
    for pkg in base.glob("yt-dlp.yt-dlp*"):
        exe = pkg / "yt-dlp.exe"
        if exe.is_file():
            return exe
    return None


def resolve_ytdlp() -> str:
    """Devolve o caminho do binário yt-dlp."""
    if settings.ytdlp_bin:
        if Path(settings.ytdlp_bin).is_file():
            return settings.ytdlp_bin
        raise DownloadError(f"YTDLP_BIN configurado mas não existe: {settings.ytdlp_bin}")

    exe_name = "yt-dlp.exe" if os.name == "nt" else "yt-dlp"
    for candidate in (
        shutil.which(exe_name),
        _venv_sibling(exe_name),
        _winget_ytdlp() if os.name == "nt" else None,
    ):
        if candidate:
            return str(candidate)

    raise DownloadError(
        "yt-dlp não encontrado. Instale com 'pip install yt-dlp' "
        "(ou 'winget install yt-dlp.yt-dlp' no Windows) e tente de novo."
    )


def audio_profile() -> str:
    bitrate = (settings.audio_bitrate or "64K").strip().upper()
    return f"opus{bitrate.lower()}"


def _ffmpeg_location() -> str | None:
    """Se o ffmpeg não estiver no PATH, procura o build empacotado do winget."""
    if shutil.which("ffmpeg"):
        return None  # yt-dlp já encontra sozinho pelo PATH
    if os.name != "nt":
        return None
    base = Path.home() / "AppData" / "Local" / "Microsoft" / "WinGet" / "Packages"
    for pkg in base.glob("yt-dlp.FFmpeg*"):
        for ffmpeg_exe in pkg.rglob("ffmpeg.exe"):
            return str(ffmpeg_exe.parent)
    return None


def resolve_ffmpeg() -> str:
    found = shutil.which("ffmpeg")
    if found:
        return found
    loc = _ffmpeg_location()
    if loc:
        exe = Path(loc) / ("ffmpeg.exe" if os.name == "nt" else "ffmpeg")
        if exe.is_file():
            return str(exe)
    raise DownloadError("ffmpeg não encontrado (necessário para comprimir o áudio).")


def downloads_root() -> Path:
    root = Path(settings.downloads_dir)
    if not root.is_absolute():
        root = Path(__file__).resolve().parent.parent / root
    root.mkdir(parents=True, exist_ok=True)
    return root


def _library_path() -> Path:
    return downloads_root() / "library.json"


_library_cache: tuple[tuple[int, int], dict[str, dict[str, Any]]] | None = None


def _load_library() -> dict[str, dict[str, Any]]:
    global _library_cache
    path = _library_path()
    try:
        st = path.stat()
    except OSError:
        return {}
    stamp = (st.st_mtime_ns, st.st_size)
    if _library_cache and _library_cache[0] == stamp:
        return dict(_library_cache[1])
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        videos = data.get("videos") if isinstance(data, dict) else None
        videos = videos if isinstance(videos, dict) else {}
    except (OSError, ValueError):
        return {}
    _library_cache = (stamp, videos)
    return dict(videos)


def is_in_library(video_id: str, user_id: str | None = None) -> bool:
    if user_id:
        from app.users_db import user_track_entry

        entry = user_track_entry(user_id, video_id)
        return bool(entry and entry.get("inLibrary"))
    return bool((_load_library().get(video_id) or {}).get("inLibrary"))


def stored_catalog_entries(
    video_ids: list[str], user_id: str | None = None
) -> dict[str, dict[str, Any]]:
    """Metadados já salvos (conta + library.json global) no formato do catálogo da UI."""
    from app.users_db import user_stored_catalog

    out: dict[str, dict[str, Any]] = dict(user_stored_catalog(user_id, video_ids))
    # Metadados globais (library.json) só sem conta logada — evita vazar catálogo legado entre usuários.
    if user_id:
        return out
    lib = _load_library()
    for vid in video_ids:
        if not vid or vid in out:
            continue
        entry = lib.get(vid) or {}
        title = entry.get("title")
        if not title:
            continue
        out[vid] = {
            "videoId": vid,
            "title": title,
            "channelTitle": entry.get("channelTitle"),
            "channelId": entry.get("channelId"),
            "artist": resolve_track_artist(title=title, artist=entry.get("artist")),
            "description": entry.get("description"),
            "descriptionOriginal": entry.get("descriptionOriginal"),
            "descriptionLang": entry.get("descriptionLang"),
            "duration": entry.get("duration"),
            "publishedAt": entry.get("publishedAt"),
            "viewCount": entry.get("viewCount"),
            "thumbnailUrl": entry.get("thumbnailUrl"),
            "url": entry.get("url"),
        }
    return out


def video_ids_needing_remote_details(
    video_ids: list[str], stored: dict[str, dict[str, Any]]
) -> list[str]:
    """IDs sem registro local ou sem duração (hydrate precisa de duration)."""
    need: list[str] = []
    for vid in video_ids:
        if not vid:
            continue
        local = stored.get(vid)
        if not local or not local.get("duration"):
            need.append(vid)
    return need


def set_library_membership(
    video_id: str,
    *,
    in_library: bool,
    meta: dict[str, Any] | None = None,
    user_id: str | None = None,
) -> dict[str, Any]:
    """Marca ou remove da biblioteca (curadoria); não apaga o arquivo do histórico."""
    now = datetime.now().isoformat(timespec="seconds")
    if user_id:
        from app.users_db import upsert_user_track

        return upsert_user_track(
            user_id,
            video_id,
            patch_meta=meta,
            in_library=in_library,
            library_added_at=now if in_library else None,
            clear_library_added_at=not in_library,
        )

    with _LOCK:
        library = _load_library()
        stored = dict(library.get(video_id) or {})
        stored["videoId"] = video_id
        stored["inLibrary"] = in_library
        if in_library:
            if not stored.get("libraryAddedAt"):
                stored["libraryAddedAt"] = now
            if meta:
                stored.update({k: v for k, v in meta.items() if v is not None and k != "videoId"})
        else:
            stored.pop("libraryAddedAt", None)
        library[video_id] = stored
        _library_path().write_text(
            json.dumps({"videos": library}, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        return stored


def _save_entry(entry: dict[str, Any]) -> dict[str, Any]:
    """Grava/atualiza o vídeo na memória; devolve o registro consolidado."""
    with _LOCK:
        library = _load_library()
        vid = entry["videoId"]
        stored = dict(library.get(vid) or {})
        stored.update({k: v for k, v in entry.items() if v is not None})
        library[vid] = stored
        _library_path().write_text(
            json.dumps({"videos": library}, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        return stored


def _enrich(info: dict[str, Any]) -> dict[str, Any]:
    """Anexa metadados salvos na memória ao item de arquivo."""
    entry = _load_library().get(info["videoId"]) or {}
    merged = {**info}
    for key in (
        "title",
        "artist",
        "channelId",
        "channelTitle",
        "description",
        "descriptionOriginal",
        "descriptionLang",
        "duration",
        "publishedAt",
        "thumbnailUrl",
        "album",
        "genre",
        "catalogSource",
        "inLibrary",
        "libraryAddedAt",
        "lastPlayedAt",
    ):
        if entry.get(key) is not None and not merged.get(key):
            merged[key] = entry[key]
    if entry.get("inLibrary"):
        merged["inLibrary"] = True
    merged["artist"] = resolve_track_artist(
        title=merged.get("title") or entry.get("title"),
        artist=merged.get("artist") or entry.get("artist"),
    )
    return merged


def _ytdlp_retry_args() -> list[str]:
    return [
        "--retries",
        "5",
        "--fragment-retries",
        "5",
        "--file-access-retries",
        "3",
        "--extractor-retries",
        "3",
    ]


def _youtube_cookie_names(path: Path) -> set[str]:
    names: set[str] = set()
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return names
    for ln in text.splitlines():
        if ln.startswith("#") or not ln.strip():
            continue
        parts = ln.split("\t")
        if len(parts) >= 6:
            names.add(parts[5])
    return names


def _youtube_cookies_session_ok(path: Path | None) -> bool:
    if not path or not path.is_file():
        return False
    names = _youtube_cookie_names(path)
    has_psid = "__Secure-1PSID" in names or "__Secure-3PSID" in names
    return has_psid and "LOGIN_INFO" in names


def _resolve_ytdlp_cookies_path() -> Path | None:
    raw = (settings.ytdlp_cookies_file or "").strip()
    if not raw:
        return None
    path = Path(raw)
    if not path.is_absolute():
        path = downloads_root() / path
    return path if path.is_file() else None


def _ytdlp_network_args() -> list[str]:
    """Cookies + runtime JS (deno no Docker) para extrator do YouTube."""
    args: list[str] = []
    cookies = _resolve_ytdlp_cookies_path()
    if cookies:
        args += ["--cookies", str(cookies)]
    if shutil.which("deno"):
        args += ["--js-runtimes", "deno", "--remote-components", "ejs:github"]
    return args


def _user_facing_ytdlp_error(raw: str) -> str:
    low = (raw or "").lower()
    if "sign in to confirm" in low or "not a bot" in low:
        cookies = _resolve_ytdlp_cookies_path()
        if cookies and not _youtube_cookies_session_ok(cookies):
            return (
                "Cookies do YouTube no servidor estão incompletos (falta sessão logada). "
                "Exporte de novo no PC com Get cookies.txt LOCALLY em youtube.com logado "
                "e rode upload_youtube_cookies.py."
            )
        if cookies:
            return (
                "YouTube pediu verificação — exporte cookies novos e envie com "
                "upload_youtube_cookies.py."
            )
        return (
            "YouTube bloqueou download no servidor (anti-bot). "
            "Coloque youtube_cookies.txt na pasta de downloads (exporte do navegador)."
        )
    if "private video" in low or "video unavailable" in low:
        return "Vídeo privado, removido ou indisponível nesta região."
    if "age-restricted" in low or "confirm your age" in low:
        return "Vídeo com restrição de idade — configure cookies do YouTube no servidor."
    return raw.strip() or "falha desconhecida no yt-dlp"


async def _video_async_lock(video_id: str) -> asyncio.Lock:
    async with _async_guard:
        lock = _video_async_locks.get(video_id)
        if lock is None:
            lock = asyncio.Lock()
            _video_async_locks[video_id] = lock
        return lock


def _ytdlp_error_message(proc: subprocess.CompletedProcess[str]) -> str:
    blob = "\n".join(
        ln
        for ln in ((proc.stderr or "") + "\n" + (proc.stdout or "")).splitlines()
        if ln.strip()
    )
    for ln in reversed(blob.splitlines()):
        if "ERROR:" in ln:
            return _user_facing_ytdlp_error(ln.split("ERROR:", 1)[-1].strip())
    stderr_tail = (proc.stderr or "").strip().splitlines()
    if stderr_tail:
        return _user_facing_ytdlp_error(stderr_tail[-1])
    return "Não foi possível baixar do YouTube."


def _probe_ytdlp_bestaudio_bytes(video_id: str) -> int | None:
    """Tamanho estimado do bestaudio (bytes), se o yt-dlp souber."""
    url = f"https://www.youtube.com/watch?v={video_id}"
    for field in ("filesize", "filesize_approx"):
        cmd = [
            resolve_ytdlp(),
            *_ytdlp_retry_args(),
            *_ytdlp_network_args(),
            "-f",
            "bestaudio/best",
            "--skip-download",
            "--no-playlist",
            "--print",
            field,
            url,
        ]
        if loc := _ffmpeg_location():
            cmd += ["--ffmpeg-location", loc]
        try:
            proc = subprocess.run(  # noqa: S603
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
            )
        except subprocess.TimeoutExpired:
            return None
        if proc.returncode != 0:
            continue
        line = (proc.stdout or "").strip().splitlines()
        if not line:
            continue
        raw = line[-1].strip()
        if not raw or raw.upper() in ("NA", "NONE", "N/A"):
            continue
        try:
            n = int(float(raw))
            return n if n > 0 else None
        except ValueError:
            continue
    return None


def _probe_ytdlp_duration_seconds(video_id: str) -> float | None:
    url = f"https://www.youtube.com/watch?v={video_id}"
    cmd = [
        resolve_ytdlp(),
        *_ytdlp_retry_args(),
        *_ytdlp_network_args(),
        "--print",
        "duration",
        "--skip-download",
        "--no-playlist",
        url,
    ]
    if loc := _ffmpeg_location():
        cmd += ["--ffmpeg-location", loc]
    try:
        proc = subprocess.run(  # noqa: S603
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
        )
    except subprocess.TimeoutExpired:
        return None
    if proc.returncode != 0:
        return None
    line = (proc.stdout or "").strip().splitlines()
    if not line:
        return None
    try:
        return float(line[-1].strip())
    except ValueError:
        return None


def find_existing(video_id: str) -> Path | None:
    """Se o áudio desse vídeo já foi baixado, devolve o arquivo existente."""
    preferred = downloads_root() / f"{video_id}{_AUDIO_EXT}"
    if preferred.is_file():
        return preferred
    for f in downloads_root().iterdir():
        if f.is_file() and f.stem == video_id and f.suffix.lower() in _AUDIO_SUFFIXES:
            return f
    return None


def _needs_compress(path: Path) -> bool:
    """True se o arquivo ainda não está no perfil compacto atual (opus 64k)."""
    entry = _load_library().get(path.stem) or {}
    if entry.get("audioProfile") == audio_profile() and path.suffix.lower() == _AUDIO_EXT:
        return False
    return True


def _compress_to_opus(src: Path) -> Path:
    """Reencoda qualquer áudio existente para Opus no bitrate configurado."""
    dest = src.with_suffix(_AUDIO_EXT)
    tmp = dest.with_suffix(".tmp.opus")
    bitrate = (settings.audio_bitrate or "64K").strip()
    cmd = [
        resolve_ffmpeg(),
        "-y",
        "-i",
        str(src),
        "-vn",
        "-c:a",
        "libopus",
        "-b:a",
        bitrate,
        "-vbr",
        "on",
        "-application",
        "audio",
        str(tmp),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=_TIMEOUT_SECONDS)
    if proc.returncode != 0 or not tmp.is_file():
        tmp.unlink(missing_ok=True)
        err = (proc.stderr or "").strip().splitlines()
        raise DownloadError(f"ffmpeg falhou ao comprimir: {err[-1] if err else 'erro desconhecido'}")
    tmp.replace(dest)
    if src.resolve() != dest.resolve():
        src.unlink(missing_ok=True)
    return dest


def _file_info(path: Path, *, already_existed: bool = False) -> dict[str, Any]:
    st = path.stat()
    return {
        "videoId": path.name.split(".")[0],
        "filename": path.name,
        "sizeBytes": st.st_size,
        "storedAt": datetime.fromtimestamp(st.st_mtime).isoformat(timespec="seconds"),
        "url": public_path(f"/api/downloads/{path.name}"),
        "alreadyExisted": already_existed,
    }


def list_downloads(user_id: str | None = None) -> list[dict[str, Any]]:
    """Histórico do usuário ou, sem login legado, arquivos globais."""
    if user_id:
        from app.users_db import list_user_history

        return list_user_history(user_id)

    root = downloads_root()
    lib = _load_library()
    files = [f for f in root.iterdir() if f.is_file() and f.suffix.lower() in _AUDIO_SUFFIXES]

    def sort_key(p: Path) -> str:
        vid = p.stem
        entry = lib.get(vid) or {}
        return entry.get("lastPlayedAt") or entry.get("storedAt") or datetime.fromtimestamp(p.stat().st_mtime).isoformat()

    files.sort(key=sort_key, reverse=True)
    return [_enrich(_file_info(f, already_existed=True)) for f in files]


def list_saved_library(user_id: str | None = None) -> list[dict[str, Any]]:
    """Biblioteca: faixas marcadas com '+'."""
    if user_id:
        from app.users_db import list_user_library

        return list_user_library(user_id)

    lib = _load_library()
    items: list[dict[str, Any]] = []
    for vid, entry in lib.items():
        if not entry.get("inLibrary"):
            continue
        info: dict[str, Any] = {"videoId": vid, **entry}
        path = find_existing(vid)
        if path:
            fi = _file_info(path, already_existed=True)
            info.update({k: fi[k] for k in ("filename", "sizeBytes", "storedAt", "url") if k in fi})
        if not info.get("url"):
            info["url"] = f"https://www.youtube.com/watch?v={vid}"
        items.append(_enrich(info))
    items.sort(key=lambda x: x.get("libraryAddedAt") or "", reverse=True)
    return items


async def _fetch_audio_with_ytdlp(video_id: str) -> Path:
    url = f"https://www.youtube.com/watch?v={video_id}"
    root = downloads_root()
    bitrate = (settings.audio_bitrate or "64K").strip()
    cmd = [
        resolve_ytdlp(),
        *_ytdlp_retry_args(),
        *_ytdlp_network_args(),
        "-f",
        "bestaudio/best",
        "-x",
        "--audio-format",
        "opus",
        "--audio-quality",
        bitrate,
        "--no-playlist",
        "--no-progress",
        "--no-overwrites",
        "--print",
        "after_move:filepath",
        "-o",
        str(root / f"{video_id}.%(ext)s"),
        url,
    ]
    if loc := _ffmpeg_location():
        cmd += ["--ffmpeg-location", loc]

    def _run() -> subprocess.CompletedProcess[str]:
        return subprocess.run(  # noqa: S603 - argumentos fixos, videoId validado
            cmd,
            capture_output=True,
            text=True,
            timeout=_TIMEOUT_SECONDS,
        )

    async with _YTDLP_SEM:
        try:
            proc = await asyncio.to_thread(_run)
        except subprocess.TimeoutExpired as exc:
            raise DownloadError("Tempo esgotado ao baixar (15 min).") from exc

    if proc.returncode != 0:
        recovered = find_existing(video_id)
        if recovered and recovered.is_file():
            return recovered
        raise DownloadError(f"yt-dlp falhou: {_ytdlp_error_message(proc)}")

    lines = [ln.strip() for ln in (proc.stdout or "").splitlines() if ln.strip()]
    if not lines:
        recovered = find_existing(video_id)
        if recovered and recovered.is_file():
            return recovered
        raise DownloadError("yt-dlp não devolveu o caminho do arquivo baixado.")

    path = Path(lines[-1])
    if not path.is_file():
        recovered = find_existing(video_id)
        if recovered and recovered.is_file():
            return recovered
        raise DownloadError(f"arquivo esperado não encontrado: {path.name}")
    return path


def _catalog_overlay(client_meta: dict[str, Any] | None) -> dict[str, Any]:
    """Nome, artista, álbum e gênero do catálogo substituem o título cru do YouTube."""
    if not client_meta or client_meta.get("catalogSource") != "deezer":
        return {}
    out: dict[str, Any] = {"catalogSource": "deezer"}
    for key in ("title", "artist", "album", "genre", "thumbnailUrl", "duration"):
        val = client_meta.get(key)
        if isinstance(val, str) and val.strip():
            out[key] = val.strip()
    for key in ("artistId", "albumId", "deezerId"):
        val = client_meta.get(key)
        if isinstance(val, bool) or val is None or val == "":
            continue
        try:
            out[key] = int(val)
        except (TypeError, ValueError):
            continue
    if not out.get("title"):
        return {}
    return out


async def download_audio(
    video_id: str,
    metadata_provider: MetadataProvider | None = None,
    user_id: str | None = None,
    client_meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Baixa só o áudio, comprime para Opus e garante os metadados na memória."""
    if not _VIDEO_ID_RE.fullmatch(video_id):
        raise DownloadError(f"videoId inválido: {video_id!r}")

    lock = await _video_async_lock(video_id)
    async with lock:
        return await _download_audio_locked(
            video_id,
            metadata_provider=metadata_provider,
            user_id=user_id,
            client_meta=client_meta,
        )


async def _download_audio_locked(
    video_id: str,
    *,
    metadata_provider: MetadataProvider | None,
    user_id: str | None,
    client_meta: dict[str, Any] | None,
) -> dict[str, Any]:
    existing = find_existing(video_id)
    had_audio_on_disk = existing is not None
    already = False

    pre_meta: dict[str, Any] | None = None
    duration_val: Any = None
    if not existing:
        from app.duration_policy import assert_download_allowed, parse_duration_seconds
        from app.size_policy import assert_estimated_size_allowed

        lan_relay = (settings.download_mode or "local").strip().lower() == "lan_relay"
        duration_val = (client_meta or {}).get("duration")

        if lan_relay:
            if parse_duration_seconds(duration_val) is None and metadata_provider:
                try:
                    pre_meta = await metadata_provider(video_id)
                except Exception:
                    pre_meta = None
                duration_val = (pre_meta or {}).get("duration") or duration_val
            assert_download_allowed(video_id=video_id, duration=duration_val)
            assert_estimated_size_allowed(video_id=video_id, duration=duration_val)
        else:
            if parse_duration_seconds(duration_val) is not None:
                assert_download_allowed(video_id=video_id, duration=duration_val)
            elif metadata_provider:
                try:
                    pre_meta = await metadata_provider(video_id)
                except Exception:
                    pre_meta = None
                duration_val = (pre_meta or {}).get("duration")
                assert_download_allowed(video_id=video_id, duration=duration_val)
                if parse_duration_seconds(duration_val) is None:
                    async with _YTDLP_SEM:
                        probed = await asyncio.to_thread(
                            _probe_ytdlp_duration_seconds, video_id
                        )
                    assert_download_allowed(video_id=video_id, duration=probed)
            else:
                async with _YTDLP_SEM:
                    probed = await asyncio.to_thread(_probe_ytdlp_duration_seconds, video_id)
                assert_download_allowed(video_id=video_id, duration=probed)
                duration_val = probed

            async with _YTDLP_SEM:
                size_est = await asyncio.to_thread(_probe_ytdlp_bestaudio_bytes, video_id)
            dur_for_size = parse_duration_seconds(duration_val)
            if dur_for_size is None and pre_meta:
                dur_for_size = parse_duration_seconds(pre_meta.get("duration"))
            assert_estimated_size_allowed(
                video_id=video_id,
                duration=dur_for_size,
                estimated_bytes=size_est,
            )

    if existing and not _needs_compress(existing):
        path = existing
        already = True
    elif existing:
        try:
            async with _YTDLP_SEM:
                path = await asyncio.to_thread(_compress_to_opus, existing)
        except subprocess.TimeoutExpired as exc:
            raise DownloadError("Tempo esgotado ao comprimir o áudio.") from exc
        already = True
    else:
        mode = (settings.download_mode or "local").strip().lower()
        if mode == "lan_relay":
            from app import download_relay

            job_id = download_relay.enqueue(
                video_id,
                user_id=user_id,
                client_meta=client_meta,
            )
            try:
                await asyncio.to_thread(
                    download_relay.wait_for_job,
                    job_id,
                    timeout_sec=float(_TIMEOUT_SECONDS),
                )
            except TimeoutError as exc:
                raise DownloadError(
                    "Tempo esgotado aguardando download na LAN (worker)."
                ) from exc
            except RuntimeError as exc:
                raise DownloadError(str(exc)) from exc
            existing = find_existing(video_id)
            if not existing:
                raise DownloadError("O worker LAN não entregou o arquivo de áudio.")
            if existing.suffix.lower() != _AUDIO_EXT and _needs_compress(existing):
                async with _YTDLP_SEM:
                    path = await asyncio.to_thread(_compress_to_opus, existing)
                already = True
            else:
                path = existing
                already = True
        else:
            path = await _fetch_audio_with_ytdlp(video_id)
            if path.suffix.lower() != _AUDIO_EXT:
                async with _YTDLP_SEM:
                    path = await asyncio.to_thread(_compress_to_opus, path)

    if not had_audio_on_disk:
        from app.size_policy import enforce_file_size_or_block

        title_hint = (client_meta or {}).get("title") or (pre_meta or {}).get("title")
        enforce_file_size_or_block(video_id, path, title=title_hint)

    info = _file_info(path, already_existed=already)

    # 2) Memória: metadados (capa, título, descrição) — só busca na API v3
    #    (1 unidade) se ainda não tiver salvo. Isso evita re-fetch futuro.
    entry = _load_library().get(video_id) or {}
    catalog = _catalog_overlay(client_meta)
    metadata: dict[str, Any] | None = None
    # Faixa vinda do catálogo já traz título, artista, álbum e gênero.
    # Não gasta videos.list (1 unidade) só para repetir o nome do YouTube.
    if metadata_provider and not entry.get("title") and not catalog.get("title"):
        try:
            metadata = await metadata_provider(video_id)
        except Exception:
            metadata = None  # metadado é bônus; o download em si não deve falhar
    played_at = datetime.now().isoformat(timespec="seconds")
    save_payload = {
        "videoId": video_id,
        "filename": info["filename"],
        "sizeBytes": info["sizeBytes"],
        "storedAt": info["storedAt"],
        "lastPlayedAt": played_at,
        "audioProfile": audio_profile(),
        "inLibrary": entry.get("inLibrary", False),
        "libraryAddedAt": entry.get("libraryAddedAt"),
        **(metadata or {}),
        **catalog,
    }
    stored = _save_entry(save_payload)

    if user_id:
        from app.users_db import upsert_user_track, user_track_entry

        prev = user_track_entry(user_id, video_id) or {}
        upsert_user_track(
            user_id,
            video_id,
            patch_meta={k: save_payload.get(k) for k in save_payload if k not in ("inLibrary", "libraryAddedAt")},
            in_library=bool(prev.get("inLibrary")),
            last_played_at=played_at,
        )
        stored = {**stored, **(user_track_entry(user_id, video_id) or {})}

    return {**info, "alreadyExisted": info["alreadyExisted"], **{k: v for k, v in stored.items() if k not in ("videoId", "filename", "sizeBytes", "savedAt", "url", "alreadyExisted")}}