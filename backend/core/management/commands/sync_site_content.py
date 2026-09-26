"""Admin panel uchun «Sayt matnlari» va slaydlarni tayyorlaydi (har ishga tushishda xavfsiz).

    python manage.py sync_site_content

1. `locale/translations.json` (shablon/kod satrlari) va `frontend/src/i18n.json` (vidjetlar)
   dagi har bir kalit uchun boʻsh `SiteText` yozuvi yaratadi. Mavjud yozuvlar va admin
   tahrirlari oʻzgarmaydi; manbadan olib tashlangan kalitlar oʻchiriladi (tahrir qilinmagan boʻlsa).
2. Slaydlar jadvali boʻsh boʻlsa — `static/core/img/slides/` dagi standart suratlardan toʻldiradi.
   Slaydni yashirish uchun uni oʻchirmang, «Koʻrsatilsin» belgisini olib tashlang.
"""
import json

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand

from core.models import SiteText, Slide
from core.sitetext import LANGS, UI_DICT_PATH, default_texts

SLIDES_DIR = settings.BASE_DIR / "core" / "static" / "core" / "img" / "slides"
# (fayl nomi, yorliq, izoh, alt, kadr markazi %) — matnlar translations.json dagi msgid
DEFAULT_SLIDES = (
    ("energy-clamp-meter", "Energoaudit", "elektr isteʼmolini taqsimlash shkafida oʻlchash",
     "Tok qisqichli oʻlchagich bilan taqsimlash shkafi shinalarida oʻlchov", 72),
    ("site-gnss-survey", "Nazorat oʻlchovi", "qurilish maydonida koordinata va balandliklarni oʻlchash",
     "Qurilish maydonida GNSS qabul qilgichli reyka bilan oʻlchayotgan mutaxassis", 60),
    ("energy-heating-pipes", "Energoaudit", "issiqlik quvurlari izolyatsiyasi va bosimini tekshirish",
     "Izolyatsiyalangan isitish quvurlari va manometr", 50),
    ("site-levelling", "Nazorat oʻlchovi", "nivelir bilan balandlik belgilarini tekshirish",
     "Nivelir orqali qarayotgan kaskali mutaxassis", 50),
    ("energy-pipe-gauges", "Energoaudit", "issiqlik tarmogʻida harorat va bosim koʻrsatkichlarini qayd etish",
     "Termometr va manometrlar oʻrnatilgan quvurlar tarmogʻi", 50),
    ("site-survey-tripod", "Nazorat oʻlchovi", "bajarilgan hajmni obyektda oʻlchash",
     "Qurilayotgan bino va minorali kran oldida shtativdagi geodezik asbob", 50),
)


class Command(BaseCommand):
    help = "Sayt matnlari roʻyxatini sinxronlaydi va boʻsh boʻlsa standart slaydlarni qoʻshadi"

    def handle(self, *args, **options):
        self._texts()
        self._slides()

    def _texts(self) -> None:
        wanted = {(kind, key) for kind, key, _values in default_texts()}
        existing = set(SiteText.objects.values_list("kind", "key"))
        missing = sorted(wanted - existing)
        SiteText.objects.bulk_create([SiteText(kind=kind, key=key) for kind, key in missing], ignore_conflicts=True)
        removed = 0
        for row in SiteText.objects.filter(text_uz="", text_ru="", text_en="").only("pk", "kind", "key"):
            if (row.kind, row.key) not in wanted:
                row.delete()
                removed += 1
        # Konsol xabari ASCII: Windows konsoli kirill/oʻ harflarini chiqara olmaydi
        self.stdout.write(f"Sayt matnlari: {len(missing)} qoshildi, {removed} eskisi olib tashlandi")

    def _slides(self) -> None:
        if Slide.objects.exists():
            return
        with open(UI_DICT_PATH, encoding="utf-8") as f:
            ui = json.load(f)

        def translations(msgid: str) -> dict[str, str]:
            return {lang: msgid if lang == "uz" else ui.get(msgid, {}).get(lang, "") for lang in LANGS}

        for order, (name, kicker, text, alt, focus_y) in enumerate(DEFAULT_SLIDES):
            slide = Slide(order=order, focus_y=focus_y)
            for field, msgid in (("kicker", kicker), ("text", text), ("alt", alt)):
                for lang, value in translations(msgid).items():
                    setattr(slide, f"{field}_{lang}", value)
            with (SLIDES_DIR / f"{name}-1600.jpg").open("rb") as handle:
                slide.image.save(f"{name}.jpg", File(handle), save=False)
            slide.save()
        self.stdout.write(f"Slaydlar: {len(DEFAULT_SLIDES)} ta standart slayd qoshildi")
