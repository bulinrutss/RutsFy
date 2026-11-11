"""Copia rutsfy-downloads.tar da LAN → Oracle direto (sem passar pelo PC)."""

from __future__ import annotations

import sys
import time
from pathlib import Path

import paramiko

ROOT = Path(__file__).resolve().parents[1]
KEY = Path(r"C:\Users\svbul\Downloads\hosdt key\ssh-key-2026-09-01.key")
ORACLE = ("147.15.80.246", "ubuntu")
LAN = ("192.168.0.5", "rts")
LAN_TAR = "/home/rts/rutsfy-downloads.tar"
ORACLE_TAR = "/tmp/rutsfy-downloads.tar"
REMOTE = "/opt/rutsfy"


def main() -> None:
    lan_pwd = (ROOT / "senha.txt").read_text(encoding="utf-8").strip()
    key_bytes = KEY.read_bytes()

    lan = paramiko.SSHClient()
    lan.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    lan.connect(LAN[0], username=LAN[1], password=lan_pwd, timeout=30)

    sftp = lan.open_sftp()
    try:
        sftp.mkdir("/home/rts/.ssh")
    except OSError:
        pass
    with sftp.file("/home/rts/.ssh/oracle_deploy.key", "wb") as f:
        f.write(key_bytes)
    sftp.close()

    test_cmd = (
        "chmod 700 /home/rts/.ssh && chmod 600 /home/rts/.ssh/oracle_deploy.key && "
        "ssh -o StrictHostKeyChecking=accept-new -i /home/rts/.ssh/oracle_deploy.key "
        f"ubuntu@{ORACLE[0]} 'echo ORACLE_OK'"
    )
    _, out, err = lan.exec_command(test_cmd, timeout=120)
    text = out.read().decode() + err.read().decode()
    if "ORACLE_OK" not in text:
        print("LAN não alcança a Oracle pela internet. Use: python scripts/deploy_oracle.py --data-only")
        print(text)
        lan.close()
        sys.exit(1)

    print("[1/3] scp LAN → Oracle (3,9 GB, direto na rede)…")
    scp_cmd = (
        "ssh -i /home/rts/.ssh/oracle_deploy.key "
        f"ubuntu@{ORACLE[0]} 'rm -f {ORACLE_TAR}' && "
        "scp -o StrictHostKeyChecking=no -i /home/rts/.ssh/oracle_deploy.key "
        f"{LAN_TAR} ubuntu@{ORACLE[0]}:{ORACLE_TAR}"
    )
    _, out, err = lan.exec_command(scp_cmd, timeout=7200)
    code = out.channel.recv_exit_status()
    lan.exec_command("rm -f /home/rts/.ssh/oracle_deploy.key")
    lan.close()
    if code != 0:
        print(err.read().decode())
        print(out.read().decode())
        sys.exit(code)

    print("[2/3] extraindo na Oracle…")
    oracle = paramiko.SSHClient()
    oracle.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    oracle.connect(ORACLE[0], username=ORACLE[1], key_filename=str(KEY), timeout=60)
    extract = (
        f"sudo mkdir -p {REMOTE}/data/downloads && "
        f"sudo tar xf {ORACLE_TAR} -C {REMOTE}/data/downloads && "
        f"sudo chown -R ubuntu:ubuntu {REMOTE}/data && "
        f"rm -f {ORACLE_TAR}"
    )
    _, out, err = oracle.exec_command(extract, timeout=1800)
    if out.channel.recv_exit_status() != 0:
        print(err.read().decode())
        oracle.close()
        sys.exit(1)

    print("[3/3] reiniciando container…")
    oracle.exec_command(
        f"cd {REMOTE} && sudo docker compose -f docker-compose.prod.yml restart sound-api",
        timeout=120,
    )
    time.sleep(2)
    _, out, _ = oracle.exec_command(f"du -sh {REMOTE}/data/downloads")
    print(out.read().decode().strip())
    oracle.close()
    print("\n[ok] https://ruts.dev/rutsfy/")


if __name__ == "__main__":
    main()
