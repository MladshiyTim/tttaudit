"""Bosh sahifa slayd-shousi uchun JPEG'lar yasaydi.

    python tools/prepare_photos.py

Manba: data/tttaudit/img/slides/ (Unsplash / Pexels litsenziyasi, roʻyxat — SOURCES.md).
Natija: core/static/core/img/slides/<nom>-1600.jpg (1280×1600) va <nom>-800.jpg (640×800).
Har bir surat hero nisbatida (4:5) kesiladi. Kesish markazi va masshtabi SLIDES'da:
- focus — kesish markazi (x, y), surat oʻlchamiga nisbatan 0..1;
- zoom — 4:5 nisbatdagi eng katta kesimning qancha qismi olinadi (1.0 — butun balandlik/kenglik).
Kichik zoom begona yozuvlarni (asbob markasi va h.k.) kadrdan chiqarish uchun ishlatiladi.

Ofis suratlari (office-hero*, office-entrance*) bosh sahifadan olib tashlangan; asl nusxalari
data/tttaudit/img/gallery/ da qoladi.
"""
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "tttaudit" / "img" / "slides"
OUT = ROOT / "core" / "static" / "core" / "img" / "slides"

RATIO = 4 / 5            # kenglik / balandlik
QUALITY = 80
SIZES = {"1600": (1280, 1600), "800": (640, 800)}

# nom: (focus_x, focus_y, zoom)
SLIDES = {
    "energy-clamp-meter": (0.52, 0.60, 0.80),
    "site-gnss-survey": (0.65, 0.40, 0.80),      # pastdagi reyka markasi kadrdan tashqarida
    "energy-heating-pipes": (0.53, 0.50, 1.0),
    "site-levelling": (0.36, 0.49, 0.82),        # kurtkadagi yamoq kadrdan tashqarida
    "energy-pipe-gauges": (0.55, 0.50, 1.0),
    "site-survey-tripod": (0.40, 0.50, 1.0),
}


def crop_box(size, focus_x, focus_y, zoom):
    """4:5 kesim: markaz fokusga yaqin, lekin surat chegarasidan chiqmaydi."""
    width, height = size
    crop_h = min(height, width / RATIO) * zoom
    crop_w = crop_h * RATIO
    left = min(max(width * focus_x - crop_w / 2, 0), width - crop_w)
    top = min(max(height * focus_y - crop_h / 2, 0), height - crop_h)
    return (round(left), round(top), round(left + crop_w), round(top + crop_h))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, (focus_x, focus_y, zoom) in SLIDES.items():
        image = ImageOps.exif_transpose(Image.open(SRC / f"{name}.jpg")).convert("RGB")
        cropped = image.crop(crop_box(image.size, focus_x, focus_y, zoom))
        for suffix, target_size in SIZES.items():
            target = OUT / f"{name}-{suffix}.jpg"
            cropped.resize(target_size, Image.LANCZOS).save(
                target, "JPEG", quality=QUALITY, optimize=True, progressive=True)
            print(f"{target.relative_to(ROOT)}: {target_size[0]}x{target_size[1]} (kesim {cropped.size})")


if __name__ == "__main__":
    main()
