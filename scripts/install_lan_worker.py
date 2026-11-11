#!/usr/bin/env python3
"""Instala o worker de download na VPS LAN (ex. rts@192.168.0.4).

Senha SSH: variável LAN_SSH_PASSWORD ou arquivo senha.txt na raiz do repo (não commitar).

  set LAN_SSH_PASSWORD=...
  python scripts/install_lan_worker.py
"""

from __future__ import annotations

import os
import sys
import textwrap
from pathlib import Path

import paramiko

ROOT = Path(__file__).resolve().parents[1]
LAN_HOST = os.environ.get("LAN_SSH_HOST", "192.168.0.4")
LAN_USER = os.environ.get("LAN_SSH_USER", "rts")
REMOTE_DIR = "/home/rts/rutsfy-worker"
WORKER_SCRIPT = ROOT / "scripts" / "lan_download_worker.py"


def _password() -> str:
    env = os.environ.get("LAN_SSH_PASSWORD", "").strip()
    if env:
        return env
    senha = ROOT / "senha.txt"
    if senha.is_file():
        return senha.read_text(encoding="utf-8").strip()
    print("Defina LAN_SSH_PASSWORD ou crie senha.txt", file=sys.stderr)
    raise SystemExit(2)


def main() -> None:
    token = os.environ.get("WORKER_TOKEN", "").strip()
    if not token:
        print("Defina WORKER_TOKEN (mesmo LAN_DOWNLOAD_WORKER_TOKEN na Oracle).", file=sys.stderr)
        raise SystemExit(2)

    api_base = os.environ.get("RUTSFY_API_BASE", "https://ruts.dev/rutsfy").strip().rstrip("/")
    cookies = os.environ.get("YTDLP_COOKIES", f"{REMOTE_DIR}/youtube_cookies.txt")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(LAN_HOST, username=LAN_USER, password=_password(), timeout=30)

    sftp = client.open_sftp()
    try:
        for d in (REMOTE_DIR, f"{REMOTE_DIR}/dl"):
            try:
                sftp.mkdir(d)
            except OSError:
                pass
        sftp.put(str(WORKER_SCRIPT), f"{REMOTE_DIR}/lan_download_worker.py")
    finally:
        sftp.close()

    max_mb = os.environ.get("MAX_TRACK_FILE_SIZE_MB", "20").strip() or "20"
    env_lines = textwrap.dedent(
        f"""\
        RUTSFY_API_BASE={api_base}
        WORKER_TOKEN={token}
        WORKER_ID=lan-{LAN_HOST.replace('.', '-')}
        LAN_DOWNLOAD_DIR={REMOTE_DIR}/dl
        YTDLP_COOKIES={cookies}
        MAX_TRACK_FILE_SIZE_MB={max_mb}
        """
    )
    unit = textwrap.dedent(
        f"""\
        [Unit]
        Description=RutsFy LAN download worker
        After=network-online.target

        [Service]
        Type=simple
        WorkingDirectory={REMOTE_DIR}
        Environment=PYTHONUNBUFFERED=1
        EnvironmentFile={REMOTE_DIR}/worker.env
        ExecStart=/usr/bin/python3 -u {REMOTE_DIR}/lan_download_worker.py
        Restart=always
        RestartSec=5

        [Install]
        WantedBy=default.target
        """
    )
    run_sh = textwrap.dedent(
        f"""\
        #!/bin/bash
        set -a
        source {REMOTE_DIR}/worker.env
        set +a
        cd {REMOTE_DIR}
        exec python3 {REMOTE_DIR}/lan_download_worker.py
        """
    )

    ytdlp_url = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp"
    ffmpeg_install = (
        f'FFDIR="{REMOTE_DIR}/ffmpeg"; mkdir -p "$FFDIR"; '
        'if [ ! -x "$FFDIR/ffmpeg" ]; then '
        'ARCH=$(uname -m); case "$ARCH" in x86_64|amd64) SUF=linux64;; aarch64|arm64) SUF=linuxarm64;; '
        '*) echo "arch $ARCH"; exit 1;; esac; '
        'TMP=$(mktemp -d); '
        'curl -fsSL -o "$TMP/f.tar.xz" "https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-${SUF}-gpl.tar.xz"; '
        'tar -xJf "$TMP/f.tar.xz" -C "$TMP"; '
        'BIN=$(find "$TMP" -type f -name ffmpeg | head -1); '
        'DIR=$(dirname "$BIN"); install -m 755 "$DIR/ffmpeg" "$DIR/ffprobe" "$FFDIR/"; rm -rf "$TMP"; fi'
    )
    cmds = [
        ffmpeg_install,
        f"cat > {REMOTE_DIR}/worker.env << 'ENVEOF'\n{env_lines}ENVEOF",
        f"curl -fsSL -o {REMOTE_DIR}/yt-dlp {ytdlp_url} && chmod +x {REMOTE_DIR}/yt-dlp",
        f"grep -q YTDLP_BIN {REMOTE_DIR}/worker.env || echo 'YTDLP_BIN={REMOTE_DIR}/yt-dlp' >> {REMOTE_DIR}/worker.env",
        f"cat > {REMOTE_DIR}/run-worker.sh << 'RUNEOF'\n{run_sh}RUNEOF",
        f"chmod +x {REMOTE_DIR}/run-worker.sh",
        "mkdir -p ~/.config/systemd/user",
        f"cat > ~/.config/systemd/user/rutsfy-worker.service << 'UNITEOF'\n{unit}UNITEOF",
        "systemctl --user daemon-reload",
        "systemctl --user enable rutsfy-worker.service",
        "systemctl --user restart rutsfy-worker.service",
        "systemctl --user is-active rutsfy-worker.service || (nohup "
        f"{REMOTE_DIR}/run-worker.sh >> {REMOTE_DIR}/worker.log 2>&1 & sleep 1 && pgrep -f lan_download_worker)",
        "echo 'Para IP fixo + boot automático: python scripts/setup_lan_vps_boot.py'",
    ]
    for cmd in cmds:
        _stdin, stdout, stderr = client.exec_command(cmd, timeout=120)
        out = stdout.read().decode(errors="replace")
        err = stderr.read().decode(errors="replace")
        code = stdout.channel.recv_exit_status()
        if code != 0:
            print(err or out, file=sys.stderr)
            client.close()
            raise SystemExit(code)
        if out.strip():
            print(out.strip())

    client.close()
    print(f"[ok] Worker em {LAN_USER}@{LAN_HOST} — copie youtube_cookies.txt para {cookies}")


if __name__ == "__main__":
    main()
