#!/usr/bin/env python3
"""Instala ffmpeg estático na LAN (sem sudo) + atualiza worker."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import paramiko

ROOT = Path(__file__).resolve().parents[1]
LAN_HOST = os.environ.get("LAN_SSH_HOST", "192.168.0.4")
LAN_USER = os.environ.get("LAN_SSH_USER", "rts")
REMOTE_DIR = "/home/rts/rutsfy-worker"

INSTALL_FFMPEG_SH = r"""set -e
FFDIR="$HOME/rutsfy-worker/ffmpeg"
mkdir -p "$FFDIR"
if [ -x "$FFDIR/ffmpeg" ] && [ -x "$FFDIR/ffprobe" ]; then
  echo "ffmpeg já instalado em $FFDIR"
  "$FFDIR/ffmpeg" -version | head -1
  exit 0
fi
ARCH=$(uname -m)
case "$ARCH" in
  x86_64|amd64) SUF=linux64 ;;
  aarch64|arm64) SUF=linuxarm64 ;;
  *) echo "arch não suportada: $ARCH"; exit 1 ;;
esac
URL="https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-${SUF}-gpl.tar.xz"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
curl -fsSL -o "$TMP/ffmpeg.tar.xz" "$URL"
tar -xJf "$TMP/ffmpeg.tar.xz" -C "$TMP"
BIN=$(find "$TMP" -type f -name ffmpeg | head -1)
test -n "$BIN"
DIR=$(dirname "$BIN")
install -m 755 "$DIR/ffmpeg" "$DIR/ffprobe" "$FFDIR/"
"$FFDIR/ffmpeg" -version | head -1
"""


def _password() -> str:
    env = os.environ.get("LAN_SSH_PASSWORD", "").strip()
    if env:
        return env
    senha = ROOT / "senha.txt"
    if senha.is_file():
        return senha.read_text(encoding="utf-8").strip()
    print("Defina LAN_SSH_PASSWORD ou senha.txt", file=sys.stderr)
    raise SystemExit(2)


def main() -> None:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(LAN_HOST, username=LAN_USER, password=_password(), timeout=30)

    sftp = client.open_sftp()
    try:
        sftp.put(str(ROOT / "scripts" / "lan_download_worker.py"), f"{REMOTE_DIR}/lan_download_worker.py")
    finally:
        sftp.close()

    cmd = f"bash -s << 'EOF'\n{INSTALL_FFMPEG_SH}\nEOF\nsystemctl --user restart rutsfy-worker.service; sleep 2; journalctl --user -u rutsfy-worker -n 5 --no-pager"
    _stdin, stdout, stderr = client.exec_command(cmd, timeout=600)
    print(stdout.read().decode(errors="replace"))
    err = stderr.read().decode(errors="replace")
    if err:
        print(err, file=sys.stderr)
    code = stdout.channel.recv_exit_status()
    client.close()
    raise SystemExit(code)


if __name__ == "__main__":
    main()
