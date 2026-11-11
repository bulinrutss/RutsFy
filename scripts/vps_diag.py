"""Quick VPS diagnostics for sound-api."""
from __future__ import annotations

import sys
from pathlib import Path

import paramiko

ROOT = Path(__file__).resolve().parents[1]
pw = (ROOT / "senha.txt").read_text(encoding="utf-8").strip()
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("192.168.0.5", username="rts", password=pw, timeout=30)

cmds = [
    "cd /home/rts/sound && docker compose ps -a",
    "cd /home/rts/sound && docker compose logs sound-api --tail 100 2>&1",
    "curl -s -o /dev/null -w 'health:%{http_code}' http://127.0.0.1:8090/health; echo",
    "curl -s -o /dev/null -w 'index:%{http_code}' http://127.0.0.1:8090/; echo",
]
try:
    for cmd in cmds:
        print("===", cmd)
        _i, stdout, stderr = client.exec_command(cmd)
        out = stdout.read().decode(errors="replace")
        err = stderr.read().decode(errors="replace")
        if out:
            print(out)
        if err:
            print("stderr:", err)
finally:
    client.close()
