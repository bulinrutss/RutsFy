#!/usr/bin/env python3
"""Copia youtube_cookies.txt da Oracle para a VPS LAN do worker."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import paramiko

ROOT = Path(__file__).resolve().parents[1]
KEY = Path(r"C:\Users\svbul\Downloads\hosdt key\ssh-key-2026-09-01.key")
ORACLE = ("147.15.80.246", "ubuntu")
LAN_HOST = os.environ.get("LAN_SSH_HOST", "192.168.0.4")
LAN_USER = os.environ.get("LAN_SSH_USER", "rts")
REMOTE_COOKIES = "/home/rts/rutsfy-worker/youtube_cookies.txt"
ORACLE_COOKIES = "/opt/rutsfy/data/downloads/youtube_cookies.txt"


def _lan_password() -> str:
    env = os.environ.get("LAN_SSH_PASSWORD", "").strip()
    if env:
        return env
    senha = ROOT / "senha.txt"
    if senha.is_file():
        return senha.read_text(encoding="utf-8").strip()
    raise SystemExit("LAN_SSH_PASSWORD ou senha.txt")


def main() -> None:
    oracle = paramiko.SSHClient()
    oracle.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    oracle.connect(ORACLE[0], username=ORACLE[1], key_filename=str(KEY), timeout=60)
    sftp_o = oracle.open_sftp()
    local_tmp = ROOT / ".tmp_youtube_cookies.txt"
    try:
        sftp_o.get(ORACLE_COOKIES, str(local_tmp))
    finally:
        sftp_o.close()
        oracle.close()

    lan = paramiko.SSHClient()
    lan.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    lan.connect(LAN_HOST, username=LAN_USER, password=_lan_password(), timeout=30)
    sftp_l = lan.open_sftp()
    try:
        try:
            sftp_l.mkdir("/home/rts/rutsfy-worker")
        except OSError:
            pass
        sftp_l.put(str(local_tmp), REMOTE_COOKIES)
    finally:
        sftp_l.close()
        lan.close()
    local_tmp.unlink(missing_ok=True)
    print(f"[ok] cookies → {LAN_USER}@{LAN_HOST}:{REMOTE_COOKIES}")


if __name__ == "__main__":
    main()
