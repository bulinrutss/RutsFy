#!/usr/bin/env python3
"""Worker na LAN: pega jobs da Oracle, baixa com yt-dlp, envia e apaga local."""

from __future__ import annotations

import json
import mimetypes
import os
import re
import shutil
import socket
import subprocess
import sys
import threading
import time
import uuid
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
VIDEO_ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")
POLL_IDLE_SEC = 3
CLAIM_TIMEOUT_SEC = 45
HEARTBEAT_SEC = 30
TIMEOUT_SEC = 15 * 60
DEFAULT_UA = "RutsFy-LAN-Worker/1.0 (download-relay; +https://ruts.dev/rutsfy)"


def _user_agent() -> str:
    return (os.environ.get("WORKER_USER_AGENT") or DEFAULT_UA).strip() or DEFAULT_UA


def _api_base() -> str:
    base = (os.environ.get("RUTSFY_API_BASE") or "https://ruts.dev/rutsfy").strip().rstrip("/")
    return base


def _token() -> str:
    tok = (os.environ.get("WORKER_TOKEN") or "").strip()
    if not tok:
        print("Defina WORKER_TOKEN (igual LAN_DOWNLOAD_WORKER_TOKEN na Oracle).", file=sys.stderr)
        raise SystemExit(2)
    return tok


def _worker_id() -> str:
    return (os.environ.get("WORKER_ID") or socket.gethostname() or "lan-worker").strip()


def _download_dir() -> Path:
    raw = os.environ.get("LAN_DOWNLOAD_DIR") or str(Path.home() / "rutsfy-worker" / "dl")
    p = Path(raw).expanduser()
    p.mkdir(parents=True, exist_ok=True)
    return p


def _ffmpeg_location() -> str | None:
    custom = (os.environ.get("FFMPEG_LOCATION") or "").strip()
    if custom:
        p = Path(custom).expanduser()
        if p.is_file():
            return str(p.parent)
        if p.is_dir() and (p / "ffmpeg").is_file():
            return str(p)
    local = Path.home() / "rutsfy-worker" / "ffmpeg"
    if (local / "ffmpeg").is_file() and (local / "ffprobe").is_file():
        return str(local)
    if shutil.which("ffmpeg") and shutil.which("ffprobe"):
        return None
    return None


def _resolve_ytdlp() -> str:
    custom = (os.environ.get("YTDLP_BIN") or "").strip()
    if custom and Path(custom).is_file():
        return custom
    local = Path.home() / "rutsfy-worker" / "yt-dlp"
    if local.is_file():
        return str(local)
    found = shutil.which("yt-dlp") or shutil.which("yt-dlp.exe")
    if found:
        return found
    raise RuntimeError("yt-dlp não encontrado — rode install_lan_worker.py")


def _http_json(method: str, path: str, payload: dict | None = None, timeout: int = 120) -> dict:
    url = f"{_api_base()}{path}"
    data = None
    headers = {
        "Authorization": f"Bearer {_token()}",
        "Accept": "application/json",
        "User-Agent": _user_agent(),
    }
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = Request(url, data=data, headers=headers, method=method)
    try:
        with urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body) if body else {}
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {detail}") from exc
    except URLError as exc:
        raise RuntimeError(str(exc)) from exc


def _upload_multipart(job_id: str, path: Path) -> None:
    boundary = f"----RutsFy{uuid.uuid4().hex}"
    file_bytes = path.read_bytes()
    ctype = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    head = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{path.name}"\r\n'
        f"Content-Type: {ctype}\r\n\r\n"
    ).encode("utf-8")
    tail = f"\r\n--{boundary}--\r\n".encode("utf-8")
    body = head + file_bytes + tail
    url = f"{_api_base()}/api/worker/jobs/{job_id}/upload"
    req = Request(
        url,
        data=body,
        headers={
            "Authorization": f"Bearer {_token()}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "User-Agent": _user_agent(),
        },
        method="POST",
    )
    with urlopen(req, timeout=TIMEOUT_SEC) as resp:
        if resp.status >= 400:
            raise RuntimeError(resp.read().decode("utf-8", errors="replace"))


def _ytdlp_cmd(video_id: str, out_dir: Path) -> list[str]:
    cmd = [_resolve_ytdlp()]
    cookies = (os.environ.get("YTDLP_COOKIES") or "").strip()
    if cookies and Path(cookies).is_file():
        cmd += ["--cookies", cookies]
    if loc := _ffmpeg_location():
        cmd += ["--ffmpeg-location", loc]
    cmd += [
        "--retries",
        "3",
        "--fragment-retries",
        "3",
        "-f",
        "bestaudio/best",
        "-x",
        "--audio-format",
        "opus",
        "--audio-quality",
        (os.environ.get("AUDIO_BITRATE") or "64K").strip(),
        "--no-playlist",
        "--no-progress",
        "--print",
        "after_move:filepath",
        "-o",
        str(out_dir / f"{video_id}.%(ext)s"),
        f"https://www.youtube.com/watch?v={video_id}",
    ]
    return cmd


def download_local(video_id: str, out_dir: Path) -> Path:
    if not VIDEO_ID_RE.fullmatch(video_id):
        raise ValueError(f"videoId inválido: {video_id}")
    proc = subprocess.run(
        _ytdlp_cmd(video_id, out_dir),
        capture_output=True,
        text=True,
        timeout=TIMEOUT_SEC,
    )
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "").strip().splitlines()
        tail = err[-1] if err else proc.returncode
        raise RuntimeError(f"yt-dlp falhou: {tail}")
    lines = [ln.strip() for ln in (proc.stdout or "").splitlines() if ln.strip()]
    if not lines:
        raise RuntimeError("yt-dlp não devolveu caminho")
    file_path = Path(lines[-1])
    if not file_path.is_file():
        raise RuntimeError(f"arquivo não encontrado: {file_path}")
    return file_path


def claim_job() -> dict | None:
    data = _http_json(
        "POST",
        "/api/worker/jobs/claim",
        {"workerId": _worker_id()},
        timeout=CLAIM_TIMEOUT_SEC,
    )
    return data.get("job")


def fail_job(job_id: str, error: str) -> None:
    _http_json("POST", f"/api/worker/jobs/{job_id}/fail", {"error": error[:2000]})


def release_my_claims() -> None:
    try:
        data = _http_json(
            "POST",
            "/api/worker/jobs/release-claims",
            {"workerId": _worker_id()},
            timeout=CLAIM_TIMEOUT_SEC,
        )
        n = int(data.get("released") or 0)
        if n:
            print(f"liberados {n} job(s) claimed órfãos deste worker")
    except Exception as exc:
        print(f"release-claims: {exc}", file=sys.stderr)


def heartbeat_job(job_id: str) -> None:
    _http_json(
        "POST",
        f"/api/worker/jobs/{job_id}/heartbeat",
        {"workerId": _worker_id()},
        timeout=CLAIM_TIMEOUT_SEC,
    )


def _heartbeat_loop(job_id: str, stop: threading.Event) -> None:
    while not stop.wait(HEARTBEAT_SEC):
        try:
            heartbeat_job(job_id)
        except Exception:
            pass


def process_one(job: dict) -> None:
    job_id = job["jobId"]
    video_id = job["videoId"]
    out_dir = _download_dir()
    path: Path | None = None
    stop_beat = threading.Event()
    beat = threading.Thread(
        target=_heartbeat_loop, args=(job_id, stop_beat), daemon=True
    )
    beat.start()
    try:
        print(f"[job {job_id}] baixando {video_id}…", flush=True)
        path = download_local(video_id, out_dir)
        max_mb = int((os.environ.get("MAX_TRACK_FILE_SIZE_MB") or "0").strip() or "0")
        if max_mb > 0:
            limit = max_mb * 1024 * 1024
            sz = path.stat().st_size
            if sz > limit:
                raise RuntimeError(
                    f"Arquivo {sz} bytes excede limite {max_mb} MB — não enviado"
                )
        print(f"[job {job_id}] enviando {path.name}…", flush=True)
        _upload_multipart(job_id, path)
        print(f"[job {job_id}] ok", flush=True)
    except Exception as exc:
        print(f"[job {job_id}] erro: {exc}", file=sys.stderr, flush=True)
        try:
            fail_job(job_id, str(exc))
        except Exception:
            pass
    finally:
        stop_beat.set()
        if path and path.is_file():
            try:
                path.unlink()
            except OSError:
                pass


def main() -> None:
    print(f"Worker {_worker_id()} → {_api_base()}", flush=True)
    release_my_claims()
    while True:
        try:
            job = claim_job()
        except Exception as exc:
            print(f"claim falhou: {exc}", file=sys.stderr)
            time.sleep(POLL_IDLE_SEC)
            continue
        if not job:
            time.sleep(POLL_IDLE_SEC)
            continue
        process_one(job)


if __name__ == "__main__":
    main()
