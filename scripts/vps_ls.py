from pathlib import Path
import paramiko

p = Path(__file__).resolve().parents[1] / "senha.txt"
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("192.168.0.5", username="rts", password=p.read_text(encoding="utf-8").strip(), timeout=15)

ids = ["BgQg3J7xU1k", "NFeUko-lQHg", "qoX6AKuYWL8"]
for vid in ids:
    _i, o, _e = client.exec_command(f"curl -s -X POST http://192.168.0.5:8090/api/download/{vid} -m 180")
    body = o.read().decode("utf-8", errors="replace")
    # só tamanho/nome, pra não quebrar o console Windows
    if '"filename"' in body:
        name = body.split('"filename":"')[1].split('"')[0]
        size = body.split('"sizeBytes":')[1].split(",")[0]
        print(f"{vid} -> {name} {int(size)/1e6:.1f} MB")
    else:
        print(vid, "FAIL", body[:200])

_i, o, _e = client.exec_command("docker exec sound-api sh -c 'ls -lh /data/downloads'")
print(o.read().decode("utf-8", errors="replace"))
client.close()
