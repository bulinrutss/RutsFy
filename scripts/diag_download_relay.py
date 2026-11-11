#!/usr/bin/env python3
"""Diagnóstico fila de download + worker LAN."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import paramiko

ROOT = Path(__file__).resolve().parents[1]
KEY = Path(r"C:\Users\svbul\Downloads\hosdt key\ssh-key-2026-09-01.key")
ORACLE = ("147.15.80.246", "ubuntu")
LAN = (os.environ.get("LAN_SSH_HOST", "192.168.0.4"), os.environ.get("LAN_SSH_USER", "rts"))


def run(client: paramiko.SSHClient, cmd: str) -> str:
    _stdin, stdout, stderr = client.exec_command(cmd, timeout=90)
    out = stdout.read().decode(errors="replace")
    err = stderr.read().decode(errors="replace")
    code = stdout.channel.recv_exit_status()
    return f"exit={code}\n{out}{err}"


def main() -> None:
    print("=== Oracle ===")
    oc = paramiko.SSHClient()
    oc.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    oc.connect(ORACLE[0], username=ORACLE[1], key_filename=str(KEY), timeout=30)
    print(run(oc, "sudo docker exec sound-api printenv DOWNLOAD_MODE"))
    print(run(oc, "sudo docker exec sound-api ls -la /data/downloads/download_relay.db"))
    print(
        run(
            oc,
            "sudo docker exec sound-api python3 -c \"import sqlite3; c=sqlite3.connect('/data/downloads/download_relay.db'); "
            "rows=c.execute('select video_id, status, substr(coalesce(error,''),0,80) from download_jobs order by created_at desc limit 8').fetchall(); "
            "print(rows)\"",
        )
    )
    oc.close()

    pwd = os.environ.get("LAN_SSH_PASSWORD", "").strip() or (ROOT / "senha.txt").read_text(encoding="utf-8").strip()
    print("=== LAN worker ===")
    lc = paramiko.SSHClient()
    lc.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    lc.connect(LAN[0], username=LAN[1], password=pwd, timeout=15)
    print(run(lc, "systemctl --user is-active rutsfy-worker.service"))
    print(run(lc, "journalctl --user -u rutsfy-worker -n 25 --no-pager"))
    print(run(lc, "test -x /home/rts/rutsfy-worker/yt-dlp && /home/rts/rutsfy-worker/yt-dlp --version"))
    lc.close()


if __name__ == "__main__":
    main()
