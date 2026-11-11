#!/usr/bin/env python3
"""Copia lan_download_worker.py para a LAN e reinicia o serviço."""
import os
import sys
from pathlib import Path

import paramiko

ROOT = Path(__file__).resolve().parents[1]
LOCAL = ROOT / "scripts" / "lan_download_worker.py"
REMOTE = "/home/rts/rutsfy-worker/lan_download_worker.py"


def main() -> None:
    pwd = os.environ.get("LAN_SSH_PASSWORD", "").strip() or (
        ROOT / "senha.txt"
    ).read_text(encoding="utf-8").strip()
    lc = paramiko.SSHClient()
    lc.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    host = os.environ.get("LAN_SSH_HOST", "192.168.0.4")
    lc.connect(host, username="rts", password=pwd, timeout=15)
    sftp = lc.open_sftp()
    sftp.put(str(LOCAL), REMOTE)
    sftp.close()
    _, o, e = lc.exec_command(
        "systemctl --user restart rutsfy-worker.service && "
        "systemctl --user is-active rutsfy-worker.service",
        timeout=30,
    )
    print(o.read().decode().strip() or e.read().decode(), file=sys.stderr)
    lc.close()
    print("[ok] worker atualizado na LAN")


if __name__ == "__main__":
    main()
