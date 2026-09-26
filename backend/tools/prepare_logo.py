"""Mijoz logotipidan (logo/*.png — kulrang fonli 3D render) saytga mos tekis PNG'lar yasaydi.

    python tools/prepare_logo.py

Fon va soya yorugʻlik boʻyicha ajratiladi: belgi piksellari qorongʻi (< THRESHOLD),
fon va soya ochroq. Natijani koʻz bilan tekshiring; soya qoldigʻi koʻrinsa
THRESHOLD ni 120 ga tushiring, belgi chetlari yeyilsa 160 ga koʻtaring.
"""
from pathlib import Path

from PIL import Image, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parent.parent
SRC = next((ROOT / "logo").glob("*.png"))
OUT = ROOT / "core" / "static" / "core" / "img"

THRESHOLD = 150          # yorugʻlik: bundan past — belgi
EMBLEM_CUT = 0.545       # emblema va «TTT» harflari orasidagi chiziq (balandlik ulushi)
INK = (30, 37, 86)       # --brand-700
WHITE = (255, 255, 255)


def build_mask() -> Image.Image:
    gray = Image.open(SRC).convert("L")
    mask = gray.point(lambda v: 255 if v < THRESHOLD else 0)
    return mask.filter(ImageFilter.GaussianBlur(0.8))


def flat(mask: Image.Image, color: tuple, size: int) -> Image.Image:
    """Maska boʻyicha bir rangli, shaffof fonli kvadrat rasm."""
    mask = mask.crop(mask.getbbox())
    layer = Image.new("RGBA", mask.size, color + (0,))
    layer.paste(Image.new("RGBA", mask.size, color + (255,)), mask=mask)
    side = max(layer.size)
    layer = ImageOps.pad(layer, (side, side), color=(0, 0, 0, 0))
    return layer.resize((size, size), Image.LANCZOS)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    mask = build_mask()
    width, height = mask.size
    emblem = mask.crop((0, 0, width, int(height * EMBLEM_CUT)))

    flat(emblem, INK, 512).save(OUT / "logo-mark.png")
    flat(mask, INK, 1024).save(OUT / "logo-full.png")
    flat(mask, WHITE, 1024).save(OUT / "logo-full-white.png")
    flat(emblem, INK, 32).save(OUT / "favicon-32.png")
    flat(emblem, INK, 180).save(OUT / "apple-touch-icon.png")

    og = Image.new("RGBA", (1200, 630), WHITE + (255,))
    og.alpha_composite(flat(mask, INK, 480), ((1200 - 480) // 2, (630 - 480) // 2))
    og.save(OUT / "og-image.png")
    print("Tayyor:", sorted(p.name for p in OUT.iterdir()))


if __name__ == "__main__":
    main()
