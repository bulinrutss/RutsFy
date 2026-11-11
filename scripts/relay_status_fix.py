#!/usr/bin/env python3
"""Relay DB + worker logs (fixed quoting)."""
import os
import sys
from pathlib import Path

import paramiko

ROOT = Path(__file__).resolve().parents[1]
KEY = Path(r"C:\Users\svbul\Downloads\hosdt key\ssh-key-2026-09-01.key")

SQL_PY = r"""
import sqlite3
c = sqlite3.connect("/data/downloads/download_relay.db")
q = (
    "select video_id, status, updated_at, "
    "substr(coalesce(error,''),1,80) from download_jobs "
    "order by updated_at desc limit 20"
)
for row in c.execute(q):
    print(row)
print("counts", dict(c.execute(
    "select status, count(*) from download_jobs group by status"
).fetchall()))
"""


def main() -> None:
    oc = paramiko.SSHClient()
    oc.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    oc.connect("147.15.80.246", username="ubuntu", key_filename=str(KEY), timeout=30)
    sftp = oc.open_sftp()
    remote = "/tmp/relay_query.py"
    with sftp.file(remote, "w") as f:
        f.write(SQL_PY)
    sftp.close()
    _, o, e = oc.exec_command(
        f"sudo docker cp {remote} sound-api:/tmp/relay_query.py && "
        "sudo docker exec sound-api python3 /tmp/relay_query.py",
        timeout=60,
    )
    print(o.read().decode())
    err = e.read().decode()
    if err.strip():
        print(err, file=sys.stderr)
    _, o2, _ = oc.exec_command(
        "sudo docker logs sound-api --tail 60 2>&1 | grep -E 'download|worker|claim|POST /api/download' || true",
        timeout=60,
    )
    print("=== api download/worker lines ===")
    print(o2.read().decode())
    oc.close()

    pwd = os.environ.get("LAN_SSH_PASSWORD", "").strip() or (
        ROOT / "senha.txt"
    ).read_text(encoding="utf-8").strip()
    lc = paramiko.SSHClient()
    lc.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    host = os.environ.get("LAN_SSH_HOST", "192.168.0.4")
    lc.connect(host, username="rts", password=pwd, timeout=15)
    _, o, _ = lc.exec_command(
        "systemctl --user is-active rutsfy-worker.service; "
        "journalctl --user -u rutsfy-worker -n 50 --no-pager",
        timeout=45,
    )
    print("=== LAN worker ===")
    print(o.read().decode())
    _, o, _ = lc.exec_command("ls -la ~/rutsfy-worker/dl 2>/dev/null | tail -5", timeout=15)
    print("=== dl dir ===")
    print(o.read().decode())
    _, o, _ = lc.exec_command(
        "date -Is; ps aux | grep yt-dlp | grep -v grep; "
        "journalctl --user -u rutsfy-worker --since '8 min ago' --no-pager",
        timeout=25,
    )
    print("=== worker now ===")
    print(o.read().decode())
    lc.close()


if __name__ == "__main__":
    main()
