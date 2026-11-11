import sys
from pathlib import Path

import paramiko

ROOT = Path(__file__).resolve().parents[1]
password = (ROOT / "senha.txt").read_text(encoding="utf-8").strip()
cmd = sys.argv[1] if len(sys.argv) > 1 else "docker ps -a --filter name=sound-api; curl -s http://127.0.0.1:8090/health"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("192.168.0.5", username="rts", password=password, timeout=30)
_stdin, stdout, stderr = client.exec_command(cmd)
sys.stdout.buffer.write(stdout.read())
sys.stdout.buffer.write(stderr.read())
client.close()
