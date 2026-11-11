#!/usr/bin/env python3
import os
from pathlib import Path

import paramiko

ROOT = Path(__file__).resolve().parents[1]
pwd = os.environ.get("LAN_SSH_PASSWORD", "").strip() or (
    ROOT / "senha.txt"
).read_text(encoding="utf-8").strip()
lc = paramiko.SSHClient()
lc.set_missing_host_key_policy(paramiko.AutoAddPolicy())
host = os.environ.get("LAN_SSH_HOST", "192.168.0.4")
lc.connect(host, username="rts", password=pwd, timeout=15)
_, o, _ = lc.exec_command(
    "ps auxww | grep -E 'python|yt-dlp' | grep -v grep; "
    "pid=$(pgrep -f lan_download_worker.py); echo pid=$pid; "
    "ss -tnp 2>/dev/null | grep python3 || true",
    timeout=15,
)
print(o.read().decode())
lc.close()
