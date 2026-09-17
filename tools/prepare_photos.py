"""Mijozning bosh ofis suratlaridan sayt uchun JPEG'lar yasaydi.

    python tools/prepare_photos.py

Manba: data/tttaudit/img/ (mijozning oʻz suratlari, 1280×960).
- office-hero*.jpg — bino. Oʻng tomondagi eski koʻrsatkich-lavha (eski faoliyat
  matni bilan) kesib tashlanadi: faqat bino va kirish qismi qoladi.
- office-entrance*.jpg — fasad va kirish eshigi.
Kattalashtirish yoʻq: manba 1280 px, shuning uchun eng katta variant ham manbadan oshmaydi.
"""
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "tttaudit" / "img"
OUT = ROOT / "core" / "static" / "core" / "img"

HERO_SRC = SRC / "gallery" / "4jSxK8EMpzid5DFjQSlW.jpg"
ENTRANCE_SRC = SRC / "gallery" / "OJeLGrChLNa1ciqXzPmU.jpg"

HERO_CROP_RIGHT = 0.68   # lavha x≈0.70 dan boshlanadi — undan oldin kesiladi
QUALITY = 80
LARGE, SMALL = 1600, 800


def save_variants(image: Image.Image, name: str) -> None:
    for suffix, long_side in (("", LARGE), ("-800", SMALL)):
        copy = image.copy()
        copy.thumbnail((long_side, long_side), Image.LANCZOS)   # faqat kichraytiradi
        target = OUT / f"{name}{suffix}.jpg"
        copy.save(target, "JPEG", quality=QUALITY, optimize=True, progressive=True)
        print(f"{target.relative_to(ROOT)}: {copy.size[0]}x{copy.size[1]}")


def main() -> None:
    hero = ImageOps.exif_transpose(Image.open(HERO_SRC)).convert("RGB")
    width, height = hero.size
    save_variants(hero.crop((0, 0, int(width * HERO_CROP_RIGHT), height)), "office-hero")

    entrance = ImageOps.exif_transpose(Image.open(ENTRANCE_SRC)).convert("RGB")
    save_variants(entrance, "office-entrance")


if __name__ == "__main__":
    main()
