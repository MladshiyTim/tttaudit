"""Energosamaradorlik toifasi (A-G) hisobi.

Chegaralar amaldagi me'yoriy hujjatdan olinishi kerak. Quyidagi qiymatlar
o'rinbosar — ular bitta joyda turibdi, chunki server (Django) va brauzer
(React vidjeti) bir xil natija berishi shart.
"""
from typing import List, Optional, TypedDict


class Band(TypedDict):
    letter: str
    upper: Optional[float]  # kVt*soat / m2 * yil, None = cheksiz
    label: str


# Quyidagi chegaralar oʻrinbosar. Faqat meʼyoriy hujjat (lex.uz) tekshirilib, mijoz
# tasdiqlagandan keyingina True qilinadi. False boʻlsa toifa (A–G) API, talab tekshiruvi
# va sahifada koʻrsatilmaydi — faqat solishtirma isteʼmol va energopasport talabi.
BANDS_VERIFIED = False

BANDS: List[Band] = [
    {"letter": "A", "upper": 40, "label": "< 40"},
    {"letter": "B", "upper": 65, "label": "40–65"},
    {"letter": "C", "upper": 95, "label": "65–95"},
    {"letter": "D", "upper": 135, "label": "95–135"},
    {"letter": "E", "upper": 180, "label": "135–180"},
    {"letter": "F", "upper": 240, "label": "180–240"},
    {"letter": "G", "upper": None, "label": "> 240"},
]

# Bino energopasporti majburiy: foydali maydon shu qiymatdan KATTA boʻlsa (qatʼiy >), m2.
PASSPORT_AREA_THRESHOLD_M2 = 200


def specific_consumption(annual_kwh: float, area_m2: float) -> Optional[float]:
    """Solishtirma iste'mol, kVt*soat / m2 * yil."""
    if not annual_kwh or not area_m2 or area_m2 <= 0:
        return None
    return annual_kwh / area_m2


def category_for(value: Optional[float]) -> Optional[str]:
    """Solishtirma iste'mol -> A..G harfi."""
    if value is None:
        return None
    for band in BANDS:
        if band["upper"] is None or value < band["upper"]:
            return band["letter"]
    return "G"


def passport_required(area_m2: float) -> bool:
    """Qonun: «200 m² dan katta» — aynan 200 m² da talab yoʻq."""
    return area_m2 > PASSPORT_AREA_THRESHOLD_M2


def bar_widths() -> List[int]:
    """Shkala ustunlari kengligi, foizda — dizayn tizimidagi qiymatlar."""
    return [22, 34, 47, 62, 75, 88, 100]


def ladder() -> List[dict]:
    """Shablon va React uchun tayyor shkala."""
    widths = bar_widths()
    return [
        {
            "letter": band["letter"],
            "label": band["label"],
            "upper": band["upper"],
            "width": widths[index],
        }
        for index, band in enumerate(BANDS)
    ]
