import paramiko
from pathlib import Path

pwd = Path(__file__).resolve().parents[1] / "senha.txt"
password = pwd.read_text(encoding="utf-8").strip()

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("192.168.0.5", username="rts", password=password, timeout=15)

cmds = [
    "ls -la ~",
    "node --version 2>/dev/null || echo no-node",
    "python3 --version",
    "ss -tlnp 2>/dev/null | head -25",
    'docker ps --format "table {{.Names}}\t{{.Ports}}\t{{.Status}}" 2>/dev/null | head -15',
]

for cmd in cmds:
    _stdin, stdout, stderr = client.exec_command(cmd)
    print(f"=== {cmd} ===")
    print(stdout.read().decode())
    err = stderr.read().decode().strip()
    if err:
        print("stderr:", err)

client.close()
