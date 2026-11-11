#!/usr/bin/env python3
import os
import sys
from pathlib import Path

import paramiko

ROOT = Path(__file__).resolve().parents[1]
KEY = Path(r"C:\Users\svbul\Downloads\hosdt key\ssh-key-2026-09-01.key")


def main() -> None:
    oc = paramiko.SSHClient()
    oc.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    oc.connect("147.15.80.246", username="ubuntu", key_filename=str(KEY), timeout=30)
    py = r"""
import sqlite3
c=sqlite3.connect('/data/downloads/download_relay.db')
rows=c.execute(
    "select video_id, status, substr(coalesce(error,''),1,120) "
    "from download_jobs order by updated_at desc limit 15"
).fetchall()
print('jobs:', rows)
pending=c.execute("select count(*) from download_jobs where status='pending'").fetchone()[0]
claimed=c.execute("select count(*) from download_jobs where status='claimed'").fetchone()[0]
print('pending', pending, 'claimed', claimed)
"""
    _, o, e = oc.exec_command(
        "sudo docker exec sound-api python3 -c " + repr(py),
        timeout=60,
    )
    print(o.read().decode())
    err = e.read().decode()
    if err.strip():
        print(err, file=sys.stderr)
    _, o2, _ = oc.exec_command("sudo docker logs sound-api --tail 40 2>&1", timeout=60)
    print("=== api logs ===")
    print(o2.read().decode()[-4000:])
    oc.close()

    pwd = os.environ.get("LAN_SSH_PASSWORD", "").strip() or (ROOT / "senha.txt").read_text(encoding="utf-8").strip()
    lc = paramiko.SSHClient()
    lc.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    host = os.environ.get("LAN_SSH_HOST", "192.168.0.4")
    lc.connect(host, username="rts", password=pwd, timeout=15)
    _, o, _ = lc.exec_command(
        "journalctl --user -u rutsfy-worker -n 20 --no-pager --since '15 min ago'",
        timeout=30,
    )
    print("=== LAN worker (15 min) ===")
    print(o.read().decode())
    _, o, _ = lc.exec_command(
        "test -x ~/rutsfy-worker/ffmpeg/ffmpeg && ~/rutsfy-worker/ffmpeg/ffmpeg -version | head -1",
        timeout=15,
    )
    print("ffmpeg:", o.read().decode().strip())
    lc.close()


if __name__ == "__main__":
    main()
