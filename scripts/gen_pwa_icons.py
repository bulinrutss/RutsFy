"""Gera ícones de marca a partir de logosemfundo.png (ou outro PNG com alpha)."""

from __future__ import annotations

import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError as exc:
    raise SystemExit("Instale Pillow: pip install pillow") from exc

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "backend" / "static" / "assets" / "icons"
DEFAULT_SRC = Path(r"C:\Users\svbul\Downloads\rutsfy\logosemfundo.png")
BG = (18, 18, 18)


def fit_square(im: Image.Image, size: int, *, bg: tuple[int, int, int] | None, padding: float = 0.12) -> Image.Image:
    pad = max(1, int(size * padding))
    inner = size - 2 * pad
    layer = im.copy()
    layer.thumbnail((inner, inner), Image.Resampling.LANCZOS)
    if bg is None:
        canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    else:
        canvas = Image.new("RGBA", (size, size), (*bg, 255))
    x = (size - layer.width) // 2
    y = (size - layer.height) // 2
    canvas.paste(layer, (x, y), layer)
    return canvas


def save_rgb(im: Image.Image, path: Path) -> None:
    if im.mode == "RGBA":
        flat = Image.new("RGB", im.size, BG)
        flat.paste(im, mask=im.split()[3])
        im = flat
    im.save(path, optimize=True)


def main() -> None:
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SRC
    if not src.is_file():
        raise SystemExit(f"Arquivo não encontrado: {src}")

    OUT.mkdir(parents=True, exist_ok=True)
    im = Image.open(src).convert("RGBA")

    logo = im.copy()
    logo.thumbnail((512, 512), Image.Resampling.LANCZOS)
    logo.save(OUT / "logo.png", optimize=True)

    for size in (16, 32, 192, 512):
        sq = fit_square(im, size, bg=BG)
        save_rgb(sq, OUT / f"icon-{size}.png")
        if size in (16, 32):
            save_rgb(sq, OUT / f"favicon-{size}.png")

    save_rgb(fit_square(im, 512, bg=BG, padding=0.22), OUT / "icon-512-maskable.png")
    save_rgb(fit_square(im, 256, bg=BG, padding=0.08), OUT / "avatar-default.png")

    ico_layers = []
    for s in (16, 32, 48):
        sq = fit_square(im, s, bg=BG)
        if sq.mode == "RGBA":
            flat = Image.new("RGB", sq.size, BG)
            flat.paste(sq, mask=sq.split()[3])
            sq = flat
        ico_layers.append(sq)
    ico_layers[0].save(OUT / "favicon.ico", format="ICO", sizes=[(s, s) for s in (16, 32, 48)])

    print(f"Ícones gerados em {OUT} a partir de {src}")


if __name__ == "__main__":
    main()
