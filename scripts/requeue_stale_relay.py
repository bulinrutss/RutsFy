#!/usr/bin/env python3
"""Requeue claimed relay jobs and restart LAN worker."""
import os
import sys
from pathlib import Path

import paramiko

ROOT = Path(__file__).resolve().parents[1]
KEY = Path(r"C:\Users\svbul\Downloads\hosdt key\ssh-key-2026-09-01.key")

REQUEUE = """
import sqlite3, time
c = sqlite3.connect("/data/downloads/download_relay.db")
now = time.time()
rows = c.execute(
    "select id, video_id, status, claimed_at from download_jobs where status='claimed'"
).fetchall()
print("before claimed:", rows)
c.execute(
    "UPDATE download_jobs SET status='pending', worker_id=NULL, "
    "claimed_at=NULL, updated_at=? WHERE status='claimed'",
    (now,),
)
c.commit()
print("requeued", c.total_changes)
"""


def main() -> None:
    oc = paramiko.SSHClient()
    oc.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    oc.connect("147.15.80.246", username="ubuntu", key_filename=str(KEY), timeout=30)
    sftp = oc.open_sftp()
    with sftp.file("/tmp/requeue_relay.py", "w") as f:
        f.write(REQUEUE)
    sftp.close()
    _, o, e = oc.exec_command(
        "sudo docker cp /tmp/requeue_relay.py sound-api:/tmp/requeue_relay.py && "
        "sudo docker exec sound-api python3 /tmp/requeue_relay.py",
        timeout=60,
    )
    print(o.read().decode())
    err = e.read().decode()
    if err.strip():
        print(err, file=sys.stderr)
    oc.close()

    pwd = os.environ.get("LAN_SSH_PASSWORD", "").strip() or (
        ROOT / "senha.txt"
    ).read_text(encoding="utf-8").strip()
    lc = paramiko.SSHClient()
    lc.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    host = os.environ.get("LAN_SSH_HOST", "192.168.0.4")
    lc.connect(host, username="rts", password=pwd, timeout=15)
    lc.exec_command("rm -f ~/rutsfy-worker/dl/*.webm ~/rutsfy-worker/dl/*.part", timeout=15)
    _, o, _ = lc.exec_command(
        "systemctl --user restart rutsfy-worker.service && sleep 2 && "
        "systemctl --user is-active rutsfy-worker.service",
        timeout=30,
    )
    print("worker restart:", o.read().decode().strip())
    lc.close()


if __name__ == "__main__":
    main()
