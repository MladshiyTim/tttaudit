"""14 hudud: kalit `uzmap.json` dagi `regions[].key` bilan bir xil, nomlar uz/ru/en."""
import json
from functools import lru_cache
from pathlib import Path

from django.utils.translation import get_language

REGIONS = {
    "qoraqalpogiston": ("Qoraqalpogʻiston Respublikasi", "Республика Каракалпакстан", "Republic of Karakalpakstan"),
    "andijon": ("Andijon viloyati", "Андижанская область", "Andijan Region"),
    "buxoro": ("Buxoro viloyati", "Бухарская область", "Bukhara Region"),
    "jizzax": ("Jizzax viloyati", "Джизакская область", "Jizzakh Region"),
    "qashqadaryo": ("Qashqadaryo viloyati", "Кашкадарьинская область", "Kashkadarya Region"),
    "navoiy": ("Navoiy viloyati", "Навоийская область", "Navoi Region"),
    "namangan": ("Namangan viloyati", "Наманганская область", "Namangan Region"),
    "samarqand": ("Samarqand viloyati", "Самаркандская область", "Samarkand Region"),
    "surxondaryo": ("Surxondaryo viloyati", "Сурхандарьинская область", "Surkhandarya Region"),
    "sirdaryo": ("Sirdaryo viloyati", "Сырдарьинская область", "Syrdarya Region"),
    "toshkent": ("Toshkent viloyati", "Ташкентская область", "Tashkent Region"),
    "fargona": ("Fargʻona viloyati", "Ферганская область", "Fergana Region"),
    "xorazm": ("Xorazm viloyati", "Хорезмская область", "Khorezm Region"),
    "toshkent_shahri": ("Toshkent shahri", "город Ташкент", "Tashkent City"),
}
LANG_INDEX = {"uz": 0, "ru": 1, "en": 2}
REGION_CHOICES = [(key, names[0]) for key, names in REGIONS.items()]
MAP_PATH = Path(__file__).with_name("uzmap.json")


def region_name(key: str, lang: str | None = None) -> str:
    """Hudud nomi joriy (yoki berilgan) tilda; nomaʼlum kalit — oʻzi."""
    names = REGIONS.get(key)
    if not names:
        return key
    code = (lang or get_language() or "uz").split("-")[0]
    return names[LANG_INDEX.get(code, 0)]


@lru_cache(maxsize=1)
def uzmap() -> dict:
    """Holst oʻlchami va viloyat yoʻllari (bir marta oʻqiladi)."""
    return json.loads(MAP_PATH.read_text(encoding="utf-8"))
