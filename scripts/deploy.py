"""Atalho: deploy de produção na Oracle (ruts.dev/rutsfy)."""

from __future__ import annotations

import runpy
from pathlib import Path

if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).resolve().parent / "deploy_oracle.py"), run_name="__main__")
