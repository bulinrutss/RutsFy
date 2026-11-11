"""Upload de cookies para a Oracle + restart opcional da API."""

from __future__ import annotations

from pathlib import Path

import paramiko

ORACLE = ("147.15.80.246", "ubuntu")
REMOTE = "/opt/rutsfy/data/downloads/youtube_cookies.txt"
KEY = Path(r"C:\Users\svbul\Downloads\hosdt key\ssh-key-2026-09-01.key")


def _connect() -> paramiko.SSHClient:
    if not KEY.is_file():
        raise FileNotFoundError(f"Chave SSH não encontrada: {KEY}")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ORACLE[0], username=ORACLE[1], key_filename=str(KEY), timeout=60)
    return client


def upload_cookies_to_oracle(cookies_file: Path) -> None:
    src = cookies_file.expanduser().resolve()
    if not src.is_file():
        raise FileNotFoundError(f"Arquivo não encontrado: {src}")
    client = _connect()
    try:
        sftp = client.open_sftp()
        sftp.put(str(src), "/tmp/youtube_cookies.txt")
        sftp.close()
        cmd = (
            f"sudo mv /tmp/youtube_cookies.txt {REMOTE} "
            f"&& sudo chown ubuntu:ubuntu {REMOTE} && sudo chmod 600 {REMOTE}"
        )
        _stdin, stdout, stderr = client.exec_command(cmd)
        code = stdout.channel.recv_exit_status()
        if code != 0:
            err = stderr.read().decode(errors="replace")
            raise RuntimeError(err or f"upload falhou (exit {code})")
    finally:
        client.close()


def restart_sound_api() -> None:
    client = _connect()
    try:
        cmd = "cd /opt/rutsfy && sudo docker compose -f docker-compose.prod.yml restart sound-api"
        _stdin, stdout, stderr = client.exec_command(cmd, get_pty=True)
        code = stdout.channel.recv_exit_status()
        if code != 0:
            err = stderr.read().decode(errors="replace")
            raise RuntimeError(err or f"restart falhou (exit {code})")
    finally:
        client.close()
