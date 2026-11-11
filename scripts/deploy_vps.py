"""Deploy legado na LAN 192.168.0.5 — DESCONTINUADO.

Produção: python scripts/deploy_oracle.py
Local: uvicorn / docker compose na sua máquina

Use --lan-legacy apenas se souber que ainda precisa atualizar a LAN.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

import paramiko

ROOT = Path(__file__).resolve().parents[1]
REMOTE = "/home/rts/sound"
SKIP_NAMES = {".venv", "__pycache__", ".pytest_cache", "senha.txt", "downloads"}
FLAT_FILES = (
    "requirements.txt",
    "Dockerfile",
    ".env.example",
    ".env",
    "docker-compose.yml",
    "Caddyfile",
)


def _upload_dir(sftp: paramiko.SFTPClient, local: Path, remote: str) -> None:
    try:
        sftp.mkdir(remote)
    except OSError:
        pass
    for item in local.iterdir():
        if item.name in SKIP_NAMES:
            continue
        rpath = f"{remote}/{item.name}"
        if item.is_dir():
            _upload_dir(sftp, item, rpath)
        else:
            sftp.put(str(item), rpath)


def _sha1_local(path: Path) -> str:
    return hashlib.sha1(path.read_bytes()).hexdigest()


def _sha1_remote(ssh: paramiko.SSHClient, path: str) -> str | None:
    _stdin, stdout, _stderr = ssh.exec_command(f"sha1sum {path} 2>/dev/null | cut -d' ' -f1")
    out = stdout.read().decode().strip()
    return out or None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true", help="Força rebuild da imagem (deps mudaram)")
    parser.add_argument(
        "--lan-legacy",
        action="store_true",
        help="Confirma deploy na LAN 192.168.0.5 (não usado no fluxo normal)",
    )
    args = parser.parse_args()

    if not args.lan_legacy:
        print(
            "Deploy na LAN 192.168.0.5 está desativado.\n"
            "  Produção: python scripts/deploy_oracle.py\n"
            "  LAN legado: python scripts/deploy_vps.py --lan-legacy",
            file=sys.stderr,
        )
        raise SystemExit(2)

    password = (ROOT / "senha.txt").read_text(encoding="utf-8").strip()
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect("192.168.0.5", username="rts", password=password, timeout=30)

    try:
        sftp = client.open_sftp()

        _upload_dir(sftp, ROOT / "backend" / "app", f"{REMOTE}/backend/app")
        _upload_dir(sftp, ROOT / "backend" / "static", f"{REMOTE}/backend/static")
        certs = ROOT / "caddy" / "certs"
        if certs.is_dir():
            try:
                sftp.mkdir(f"{REMOTE}/caddy")
            except OSError:
                pass
            _upload_dir(sftp, certs, f"{REMOTE}/caddy/certs")
        for fname in FLAT_FILES:
            if fname in ("docker-compose.yml", "Caddyfile"):
                local = ROOT / fname
                remote_path = f"{REMOTE}/{fname}"
            else:
                local = ROOT / "backend" / fname
                remote_path = f"{REMOTE}/backend/{fname}"
            if local.is_file():
                sftp.put(str(local), remote_path)
        sftp.close()

        # Detecta mudança de deps automaticamente (mesmo sem --build)
        req_local = _sha1_local(ROOT / "backend" / "requirements.txt")
        req_remote = _sha1_remote(client, f"{REMOTE}/backend/requirements.txt")
        deps_changed = req_local != req_remote
        do_build = args.build or deps_changed

        cmd = (
            f"cd {REMOTE} && "
            + ("docker compose build && " if do_build else "")
            + "docker compose up -d && docker compose restart sound-api sound-caddy && docker compose ps"
        )
        _stdin, stdout, stderr = client.exec_command(cmd, get_pty=True)
        sys.stdout.buffer.write(stdout.read())
        err = stderr.read()
        if err:
            sys.stdout.buffer.write(err)

        print()
        print(f"[deploy] modo {'completo (rebuild)' if do_build else 'rápido (sem rebuild)'} · deps mudaram: {deps_changed}")
    finally:
        client.close()


if __name__ == "__main__":
    main()