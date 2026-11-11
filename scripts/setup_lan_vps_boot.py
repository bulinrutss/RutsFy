#!/usr/bin/env python3
"""IP estático na LAN + worker RutsFy no boot (systemd system-wide).

  set LAN_SSH_PASSWORD=...
  python scripts/setup_lan_vps_boot.py

IP estático na VM (= sempre .4, sem depender do DHCP do roteador).
"""

from __future__ import annotations

import base64
import os
import re
import sys
import textwrap
from pathlib import Path

import paramiko

ROOT = Path(__file__).resolve().parents[1]
LAN_HOST = os.environ.get("LAN_SSH_HOST", "192.168.0.4")
LAN_USER = os.environ.get("LAN_SSH_USER", "rts")
STATIC_IP = os.environ.get("LAN_STATIC_IP", "192.168.0.4")
REMOTE_DIR = "/home/rts/rutsfy-worker"
SYSTEM_UNIT = "/etc/systemd/system/rutsfy-worker.service"


def _password() -> str:
    env = os.environ.get("LAN_SSH_PASSWORD", "").strip()
    if env:
        return env
    senha = ROOT / "senha.txt"
    if senha.is_file():
        return senha.read_text(encoding="utf-8").strip()
    print("Defina LAN_SSH_PASSWORD ou senha.txt", file=sys.stderr)
    raise SystemExit(2)


def _sudo_password() -> str:
    return os.environ.get("LAN_SUDO_PASSWORD", "").strip() or _password()


def _run(client: paramiko.SSHClient, cmd: str, *, timeout: int = 120) -> tuple[int, str]:
    _stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout, get_pty=True)
    out = stdout.read().decode(errors="replace")
    err = stderr.read().decode(errors="replace")
    code = stdout.channel.recv_exit_status()
    return code, (out + err).strip()


def _upload_text(sftp: paramiko.SFTPClient, remote_path: str, content: str) -> None:
    with sftp.file(remote_path, "w") as f:
        f.write(content)


def main() -> None:
    ssh_pwd = _password()
    sudo_pwd = _sudo_password()

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f"[lan] conectando {LAN_USER}@{LAN_HOST}…")
    client.connect(LAN_HOST, username=LAN_USER, password=ssh_pwd, timeout=20)

    code, detect = _run(
        client,
        "GW=$(ip -4 route show default | awk '{print $3; exit}'); "
        "IF=$(ip -4 route show default | awk '{print $5; exit}'); "
        'echo "gateway=$GW interface=$IF"',
    )
    if code != 0:
        print(detect, file=sys.stderr)
        raise SystemExit(code)

    gateway = None
    iface = None
    for line in detect.splitlines():
        m = re.search(r"gateway=(\S+)\s+interface=(\S+)", line)
        if m:
            gateway, iface = m.group(1), m.group(2)
            break
    if not iface or not gateway or iface == "interface=":
        print("Não achei rota default / interface.", file=sys.stderr)
        print(detect)
        raise SystemExit(1)

    print(f"[net] {iface} via {gateway} → {STATIC_IP}/24")

    netplan = textwrap.dedent(
        f"""\
        network:
          version: 2
          renderer: networkd
          ethernets:
            {iface}:
              dhcp4: no
              dhcp6: no
              addresses:
                - {STATIC_IP}/24
              routes:
                - to: default
                  via: {gateway}
              nameservers:
                addresses: [{gateway}, 8.8.8.8, 1.1.1.1]
        """
    )

    worker_id = f"lan-{STATIC_IP.replace('.', '-')}"
    code, out = _run(
        client,
        f"test -f {REMOTE_DIR}/worker.env && "
        f"sed -i 's/^WORKER_ID=.*/WORKER_ID={worker_id}/' {REMOTE_DIR}/worker.env; "
        f"grep -E '^(WORKER_ID|RUTSFY_API_BASE)=' {REMOTE_DIR}/worker.env 2>/dev/null || true",
    )
    if out:
        print("[worker.env]", out)

    unit = textwrap.dedent(
        f"""\
        [Unit]
        Description=RutsFy LAN download worker
        After=network-online.target
        Wants=network-online.target

        [Service]
        Type=simple
        User={LAN_USER}
        Group={LAN_USER}
        WorkingDirectory={REMOTE_DIR}
        Environment=PYTHONUNBUFFERED=1
        EnvironmentFile=-{REMOTE_DIR}/worker.env
        ExecStart=/usr/bin/python3 -u {REMOTE_DIR}/lan_download_worker.py
        Restart=always
        RestartSec=5

        [Install]
        WantedBy=multi-user.target
        """
    )

    sftp = client.open_sftp()
    _upload_text(sftp, "/tmp/99-rutsfy-static.yaml", netplan)
    _upload_text(sftp, "/tmp/rutsfy-worker.service", unit)
    sftp.close()

    sudo_b64 = base64.b64encode(sudo_pwd.encode()).decode()
    install_cmd = (
        f"echo {sudo_b64} | base64 -d | sudo -S -p '' "
        f"install -m 600 /tmp/99-rutsfy-static.yaml /etc/netplan/99-rutsfy-static.yaml && "
        f"echo {sudo_b64} | base64 -d | sudo -S -p '' "
        f"install -m 644 /tmp/rutsfy-worker.service {SYSTEM_UNIT} && "
        f"echo {sudo_b64} | base64 -d | sudo -S -p '' netplan generate && "
        f"echo {sudo_b64} | base64 -d | sudo -S -p '' netplan apply && "
        f"echo {sudo_b64} | base64 -d | sudo -S -p '' systemctl daemon-reload && "
        f"echo {sudo_b64} | base64 -d | sudo -S -p '' systemctl enable rutsfy-worker.service && "
        f"echo {sudo_b64} | base64 -d | sudo -S -p '' systemctl restart rutsfy-worker.service && "
        f"echo {sudo_b64} | base64 -d | sudo -S -p '' loginctl enable-linger {LAN_USER} 2>/dev/null || true; "
        "systemctl --user disable rutsfy-worker.service 2>/dev/null || true; "
        "systemctl is-active rutsfy-worker.service; "
        "systemctl is-enabled rutsfy-worker.service"
    )
    code, out = _run(client, install_cmd, timeout=180)
    print(out)
    if code != 0:
        raise SystemExit(code)

    code, out = _run(
        client,
        "sleep 2; ip -4 -o addr show scope global; "
        "systemctl status rutsfy-worker --no-pager -l 2>&1 | head -18; "
        "journalctl -u rutsfy-worker -n 6 --no-pager 2>&1",
    )
    print(out)

    client.close()
    print(f"\n[ok] {STATIC_IP} fixo + rutsfy-worker sobe no boot.")


if __name__ == "__main__":
    main()
