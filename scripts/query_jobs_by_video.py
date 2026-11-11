#!/usr/bin/env python3
"""Search download_jobs and library on Oracle for a video id or title fragment."""
import sys
from pathlib import Path

import paramiko

KEY = Path(r"C:\Users\svbul\Downloads\hosdt key\ssh-key-2026-09-01.key")
VID = sys.argv[1] if len(sys.argv) > 1 else "n5wxZ_OBUXk"

PY = f"""
import json, sqlite3
from pathlib import Path
vid = {VID!r}
c = sqlite3.connect("/data/downloads/download_relay.db")
print("jobs for", vid)
for row in c.execute(
    "select id, status, error, created_at, updated_at, claimed_at from download_jobs where video_id=? order by updated_at desc",
    (vid,),
):
    print(row)
lib = Path("/data/downloads/library.json")
if lib.is_file():
    data = json.loads(lib.read_text(encoding="utf-8"))
    ent = data.get(vid)
    print("library:", ent.get("title") if ent else None)
for p in Path("/data/downloads").glob(f"{{vid}}.*"):
    print("file:", p.name, p.stat().st_size)
"""


def main() -> None:
    oc = paramiko.SSHClient()
    oc.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    oc.connect("147.15.80.246", username="ubuntu", key_filename=str(KEY), timeout=30)
    sftp = oc.open_sftp()
    with sftp.file("/tmp/qjobs.py", "w") as f:
        f.write(PY)
    sftp.close()
    _, o, e = oc.exec_command(
        "sudo docker cp /tmp/qjobs.py sound-api:/tmp/qjobs.py && "
        "sudo docker exec sound-api python3 /tmp/qjobs.py",
        timeout=60,
    )
    print(o.read().decode())
    print(e.read().decode(), file=sys.stderr)
    oc.close()


if __name__ == "__main__":
    main()
