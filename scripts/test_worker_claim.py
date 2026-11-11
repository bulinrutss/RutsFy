#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
token = os.environ.get("WORKER_TOKEN", "").strip()
if not token and (ROOT / "backend" / ".env").is_file():
    for line in (ROOT / "backend" / ".env").read_text(encoding="utf-8").splitlines():
        if line.startswith("LAN_DOWNLOAD_WORKER_TOKEN="):
            token = line.split("=", 1)[1].strip()
            break
if not token:
    sys.exit("WORKER_TOKEN missing")

req = Request(
    "https://ruts.dev/rutsfy/api/worker/jobs/claim",
    data=json.dumps({"workerId": "claim-test"}).encode(),
    method="POST",
    headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "RutsFy-LAN-Worker/1.0 (download-relay; +https://ruts.dev/rutsfy)",
    },
)
try:
    with urlopen(req, timeout=30) as resp:
        print("OK", resp.status, resp.read().decode()[:300])
except HTTPError as e:
    print("HTTP", e.code, e.read().decode()[:500])
