"""Deploy RutsFy na Oracle — https://ruts.dev/rutsfy/

Uso normal (só código):
    python scripts/deploy_oracle.py

Copiar músicas/dados da LAN de novo:
    python scripts/migrate_lan_to_oracle_direct.py
"""

from __future__ import annotations

import argparse
import os
import sys
import textwrap
from pathlib import Path

import paramiko

ROOT = Path(__file__).resolve().parents[1]
ORACLE = ("147.15.80.246", "ubuntu")
LAN = ("192.168.0.5", "rts")
REMOTE = "/opt/rutsfy"
KEY = Path(r"C:\Users\svbul\Downloads\hosdt key\ssh-key-2026-09-01.key")
LAN_TAR = "/home/rts/rutsfy-downloads.tar"
ORACLE_TAR = "/tmp/rutsfy-downloads.tar"
SKIP_NAMES = {".venv", "__pycache__", ".pytest_cache", "senha.txt", "downloads", "data"}
UPLOAD_FILES = (
    "requirements.txt",
    "Dockerfile",
    "docker-compose.prod.yml",
    "Caddyfile",
)


def _connect(host: str, user: str, *, password: str | None = None) -> paramiko.SSHClient:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    if password:
        client.connect(host, username=user, password=password, timeout=60)
    else:
        client.connect(host, username=user, key_filename=str(KEY), timeout=60)
    return client


def _run(client: paramiko.SSHClient, cmd: str, *, sudo: bool = False) -> tuple[int, str, str]:
    if sudo:
        cmd = f"sudo -n bash -lc {repr(cmd)}"
    _stdin, stdout, stderr = client.exec_command(cmd, get_pty=True)
    out = stdout.read().decode(errors="replace")
    err = stderr.read().decode(errors="replace")
    code = stdout.channel.recv_exit_status()
    return code, out, err


def _sftp_mkdirs(sftp: paramiko.SFTPClient, remote: str) -> None:
    parts = remote.strip("/").split("/")
    path = ""
    for part in parts:
        path += f"/{part}"
        try:
            sftp.mkdir(path)
        except OSError:
            pass


def _upload_dir(sftp: paramiko.SFTPClient, local: Path, remote: str) -> None:
    _sftp_mkdirs(sftp, remote)
    for item in local.iterdir():
        if item.name in SKIP_NAMES:
            continue
        rpath = f"{remote}/{item.name}"
        if item.is_dir():
            _upload_dir(sftp, item, rpath)
        else:
            sftp.put(str(item), rpath)


def _build_env_content() -> tuple[str, str | None]:
    import secrets

    local_env = ROOT / "backend" / ".env"
    lines: dict[str, str] = {}
    new_token: str | None = None
    if local_env.is_file():
        for raw in local_env.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            lines[k.strip()] = v.strip()
    lines.setdefault("HOST", "0.0.0.0")
    lines.setdefault("PORT", "8090")
    lines["DOWNLOADS_DIR"] = "/data/downloads"
    lines["BASE_PATH"] = "/rutsfy"
    lines.pop("RUTSFY_BASE_PATH", None)
    lines["SESSION_COOKIE_SECURE"] = "true"
    lines["CORS_ORIGINS"] = "https://ruts.dev"
    lines.setdefault("DOWNLOAD_MODE", "lan_relay")
    lines["MAX_TRACK_FILE_SIZE_MB"] = "20"
    lines["USER_SEARCH_DAILY_LIMIT"] = "20"
    if not lines.get("LAN_DOWNLOAD_WORKER_TOKEN"):
        new_token = secrets.token_urlsafe(32)
        lines["LAN_DOWNLOAD_WORKER_TOKEN"] = new_token
    return "\n".join(f"{k}={v}" for k, v in lines.items()) + "\n", new_token


def _stream_sftp(src: paramiko.SFTPClient, spath: str, dst: paramiko.SFTPClient, dpath: str) -> None:
    chunk = 1024 * 1024
    with src.file(spath, "rb") as rf, dst.file(dpath, "wb") as wf:
        while True:
            data = rf.read(chunk)
            if not data:
                break
            wf.write(data)


def deploy_code(client: paramiko.SSHClient) -> None:
    code, _, err = _run(
        client,
        f"sudo mkdir -p {REMOTE}/data/downloads && sudo chown -R ubuntu:ubuntu {REMOTE}",
    )
    if code != 0:
        raise SystemExit(f"mkdir {REMOTE} falhou: {err}")
    sftp = client.open_sftp()
    _sftp_mkdirs(sftp, f"{REMOTE}/backend")
    _upload_dir(sftp, ROOT / "backend" / "app", f"{REMOTE}/backend/app")
    _upload_dir(sftp, ROOT / "backend" / "static", f"{REMOTE}/backend/static")
    for name in UPLOAD_FILES:
        local = ROOT / name if name != "requirements.txt" else ROOT / "backend" / "requirements.txt"
        if name == "requirements.txt":
            sftp.put(str(local), f"{REMOTE}/backend/requirements.txt")
        elif name == "Dockerfile":
            sftp.put(str(ROOT / "backend" / "Dockerfile"), f"{REMOTE}/backend/Dockerfile")
        elif local.is_file():
            sftp.put(str(local), f"{REMOTE}/{name}")
    env_path = f"{REMOTE}/backend/.env"
    env_body, new_token = _build_env_content()
    with sftp.file(env_path, "w") as f:
        f.write(env_body)
    if new_token:
        print(
            "[deploy] LAN_DOWNLOAD_WORKER_TOKEN gerado — copie para backend/.env e WORKER_TOKEN no LAN:\n"
            f"  {new_token}\n"
        )
    sftp.close()


def ensure_docker(client: paramiko.SSHClient) -> None:
    code, out, _ = _run(client, "command -v docker && sudo docker compose version")
    if code == 0 and "compose" in out.lower():
        return
    print("[oracle] instalando docker…")
    cmd = textwrap.dedent(
        """
        export DEBIAN_FRONTEND=noninteractive
        apt-get update -qq
        apt-get install -y -qq docker.io docker-compose-v2
        systemctl enable --now docker
        usermod -aG docker ubuntu
        """
    ).strip()
    _run(client, cmd, sudo=True)


def docker_up(client: paramiko.SSHClient) -> None:
    cmd = (
        f"cd {REMOTE} && sudo docker compose -f docker-compose.prod.yml build && "
        f"sudo docker compose -f docker-compose.prod.yml up -d && "
        f"sudo docker compose -f docker-compose.prod.yml ps"
    )
    code, out, err = _run(client, cmd)
    sys.stdout.write(out)
    if err:
        sys.stdout.write(err)
    if code != 0:
        raise SystemExit(code)


def configure_nginx(client: paramiko.SSHClient) -> None:
    snippet = (ROOT / "deploy" / "nginx-rutsfy.conf").read_text(encoding="utf-8")
    sftp = client.open_sftp()
    with sftp.file("/tmp/rutsfy-proxy.conf", "w") as f:
        f.write(snippet)
    sftp.close()
    script = textwrap.dedent(
        """
        set -e
        sudo cp /tmp/rutsfy-proxy.conf /etc/nginx/snippets/rutsfy-proxy.conf
        sudo python3 << 'PY'
        from pathlib import Path
        p = Path("/etc/nginx/sites-available/ruts.dev")
        text = p.read_text()
        inc = "    include /etc/nginx/snippets/rutsfy-proxy.conf;"
        if inc not in text:
            text = text.replace("    location / {", inc + "\\n    location / {")
            p.write_text(text)
        PY
        sudo nginx -t
        sudo systemctl reload nginx
        """
    ).strip()
    code, out, err = _run(client, script)
    sys.stdout.write(out)
    if err:
        sys.stdout.write(err)
    if code != 0:
        raise SystemExit(f"nginx falhou: {code}")


def migrate_data(lan_password: str) -> None:
    print("[lan] criando tarball dos downloads (pode demorar)…")
    lan = _connect(LAN[0], LAN[1], password=lan_password)
    tar_cmd = (
        "docker run --rm -v sound_sound-downloads:/data -v /home/rts:/out alpine "
        f"sh -c 'cd /data && tar cf /out/rutsfy-downloads.tar .'"
    )
    code, out, err = _run(lan, tar_cmd)
    sys.stdout.write(out)
    if code != 0:
        lan.close()
        raise SystemExit(f"tar LAN falhou: {err or out}")

    oracle = _connect(ORACLE[0], ORACLE[1])
    lan_sftp = lan.open_sftp()
    ora_sftp = oracle.open_sftp()
    print("[migrate] LAN → Oracle (stream SFTP)…")
    _stream_sftp(lan_sftp, LAN_TAR, ora_sftp, ORACLE_TAR)
    lan_sftp.close()
    lan.close()

    extract = textwrap.dedent(
        f"""
        set -e
        sudo mkdir -p {REMOTE}/data/downloads
        sudo tar xf {ORACLE_TAR} -C {REMOTE}/data/downloads
        sudo chown -R ubuntu:ubuntu {REMOTE}/data
        rm -f {ORACLE_TAR}
        rm -f {LAN_TAR}
        """
    ).strip()
    code, out, err = _run(oracle, extract)
    sys.stdout.write(out)
    ora_sftp.close()
    oracle.close()
    if code != 0:
        raise SystemExit(f"extract falhou: {err}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--with-data",
        action="store_true",
        help="Também migra downloads da LAN (lento; prefira migrate_lan_to_oracle_direct.py)",
    )
    parser.add_argument("--skip-nginx", action="store_true")
    parser.add_argument("--data-only", action="store_true", help="Só copia downloads da LAN (relay PC)")
    args = parser.parse_args()

    if not KEY.is_file():
        raise SystemExit(f"Chave SSH não encontrada: {KEY}")

    lan_pwd = (ROOT / "senha.txt").read_text(encoding="utf-8").strip()

    if args.data_only:
        migrate_data(lan_pwd)
        oracle = _connect(ORACLE[0], ORACLE[1])
        _run(
            oracle,
            f"cd {REMOTE} && sudo docker compose -f docker-compose.prod.yml restart sound-api",
        )
        oracle.close()
        print("\n[ok] dados migrados")
        return

    print("[oracle] conectando…")
    oracle = _connect(ORACLE[0], ORACLE[1])
    ensure_docker(oracle)
    deploy_code(oracle)
    docker_up(oracle)
    if not args.skip_nginx:
        configure_nginx(oracle)
    oracle.close()

    if args.with_data:
        migrate_data(lan_pwd)
        oracle = _connect(ORACLE[0], ORACLE[1])
        _run(
            oracle,
            f"cd {REMOTE} && sudo docker compose -f docker-compose.prod.yml restart sound-api",
        )
        oracle.close()

    print("\n[ok] https://ruts.dev/rutsfy/")


if __name__ == "__main__":
    main()
