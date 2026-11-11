#!/usr/bin/env python3
"""Testa yt-dlp + ffmpeg na LAN (vídeo curto)."""
from __future__ import annotations

import os
import sys
from pathlib import Path

import paramiko

ROOT = Path(__file__).resolve().parents[1]
VIDEO = sys.argv[1] if len(sys.argv) > 1 else "jNQXAC9IVRw"  # me at the zoo — curto
REMOTE = "/home/rts/rutsfy-worker"


def _password() -> str:
    env = os.environ.get("LAN_SSH_PASSWORD", "").strip()
    if env:
        return env
    return (ROOT / "senha.txt").read_text(encoding="utf-8").strip()


def main() -> None:
    cmd = (
        f"cd {REMOTE}/dl && rm -f {VIDEO}.* && "
        f"{REMOTE}/yt-dlp --ffmpeg-location {REMOTE}/ffmpeg -f bestaudio/best -x "
        f"--audio-format opus --audio-quality 64K --no-playlist -o '{VIDEO}.%(ext)s' "
        f"'https://www.youtube.com/watch?v={VIDEO}' && ls -la {VIDEO}.*"
    )
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    host = os.environ.get("LAN_SSH_HOST", "192.168.0.4")
    c.connect(host, username="rts", password=_password(), timeout=30)
    _, o, e = c.exec_command(cmd, timeout=300)
    print(o.read().decode())
    err = e.read().decode()
    if err:
        print(err, file=sys.stderr)
    print("exit", o.channel.recv_exit_status())
    c.close()


if __name__ == "__main__":
    main()
