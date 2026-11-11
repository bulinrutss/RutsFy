#!/usr/bin/env python3
import paramiko

KEY = r"C:\Users\svbul\Downloads\hosdt key\ssh-key-2026-09-01.key"

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect("147.15.80.246", username="ubuntu", key_filename=KEY, timeout=30)
cmds = [
    "sudo docker logs sound-api 2>&1 | tail -200 | grep download || true",
    "sudo docker exec sound-api sh -c 'ls -lt /data/downloads/*.opus 2>/dev/null | head -10'",
    """sudo docker exec sound-api python3 << 'PY'
import sqlite3
c=sqlite3.connect("/data/downloads/download_relay.db")
for row in c.execute(
    "select video_id, status, substr(coalesce(error,''),1,100), datetime(updated_at,'unixepoch') "
    "from download_jobs order by updated_at desc limit 12"
):
    print(row)
print("pending", c.execute("select count(*) from download_jobs where status='pending'").fetchone()[0])
print("claimed", c.execute("select count(*) from download_jobs where status='claimed'").fetchone()[0])
PY""",
]
for cmd in cmds:
    print("===", cmd.split(chr(10))[0][:70], "===")
    _, o, e = c.exec_command(cmd, timeout=90)
    print(o.read().decode())
    err = e.read().decode()
    if err.strip():
        print(err)
c.close()
