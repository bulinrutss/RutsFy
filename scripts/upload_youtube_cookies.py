"""Envia youtube_cookies.txt (Netscape) para a Oracle — pasta de downloads do RutsFy.

Exporte no PC (exemplo com Chrome):
  yt-dlp --cookies-from-browser chrome --cookies youtube_cookies.txt --skip-download "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

Ou use extensão "Get cookies.txt LOCALLY" no YouTube logado.

Uso:
  python scripts/upload_youtube_cookies.py caminho\\youtube_cookies.txt
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from youtube_cookies_oracle import REMOTE, upload_cookies_to_oracle  # noqa: E402
from youtube_cookies_util import validate_youtube_cookies  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("cookies_file", type=Path, help="Arquivo Netscape cookies.txt")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Envia mesmo se faltar cookies de login (não recomendado)",
    )
    args = parser.parse_args()
    src = args.cookies_file.expanduser().resolve()
    if not src.is_file():
        raise SystemExit(f"Arquivo não encontrado: {src}")
    issues = validate_youtube_cookies(src)
    if issues and not args.force:
        print("Exportação incompleta — downloads na VPS provavelmente vão falhar:\n", file=sys.stderr)
        for line in issues:
            print(f"  • {line}", file=sys.stderr)
        print(
            "\nNo Chrome: abra https://www.youtube.com (logado), toque num vídeo, "
            'depois use "Get cookies.txt LOCALLY" → Export.\n'
            "Ou feche o Chrome e rode:\n"
            "  yt-dlp --cookies-from-browser chrome --cookies youtube_cookies.txt "
            '--skip-download "https://www.youtube.com/watch?v=jNQXAC9IVRw"\n'
            "Repita o upload ou use --force para ignorar este aviso.",
            file=sys.stderr,
        )
        raise SystemExit(2)
    try:
        upload_cookies_to_oracle(src)
    except FileNotFoundError as exc:
        raise SystemExit(str(exc)) from exc
    except RuntimeError as exc:
        raise SystemExit(str(exc)) from exc
    print(f"[ok] cookies em {REMOTE}")
    print("     Para reiniciar a API: python scripts/renew_and_upload_youtube_cookies.py")


if __name__ == "__main__":
    main()
