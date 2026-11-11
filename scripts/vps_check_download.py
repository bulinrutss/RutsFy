"""Recomprime os áudios já salvos na VPS e mostra o tamanho novo."""
from pathlib import Path

import paramiko

password = (Path(__file__).resolve().parents[1] / "senha.txt").read_text(encoding="utf-8").strip()

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("192.168.0.5", username="rts", password=password, timeout=15)


def run(cmd: str, timeout: int = 300) -> str:
    _stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode("utf-8", errors="replace")
    err = stderr.read().decode("utf-8", errors="replace").strip()
    return (out + (("\nstderr: " + err) if err else "")).strip()


print("=== arquivos atuais ===")
print(run("docker exec sound-api sh -c 'ls -lh /data/downloads'"))

print("\n=== comprimir BBB ===")
print(run("curl -s -X POST http://192.168.0.5:8090/api/download/aqz-KE-bpKQ -m 180"))

print("\n=== comprimir o grande (pode demorar) ===")
print(run("curl -s -X POST http://192.168.0.5:8090/api/download/4U3eYkvY9pE -m 280", timeout=300))

print("\n=== arquivos depois ===")
print(run("docker exec sound-api sh -c 'ls -lh /data/downloads'"))

client.close()
