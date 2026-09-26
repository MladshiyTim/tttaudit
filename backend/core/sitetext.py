"""Admin paneldagi «Sayt matnlari» ni gettext ustidan qoʻllash.

Shablonlardagi `{% translate %}` / `blocktranslate` va koddagi `gettext` / `gettext_lazy`
satrlari `SiteText.key` (oʻzbekcha msgid) boʻyicha qidiriladi: joriy tildagi maydon
toʻldirilgan boʻlsa — u, aks holda odatiy `.po` tarjimasi.

Keshlash: har bir jarayon (gunicorn worker) qayta yozuvlarni xotirada saqlaydi va
`CHECK_INTERVAL` soniyada bir marta umumiy cache'dagi versiyani tekshiradi. SiteText
saqlanganda/oʻchirilganda versiya oshadi — boshqa ishchilar ham yangilanadi.
"""
import json
import logging
import time
from functools import lru_cache
from pathlib import Path

from django.conf import settings
from django.core.cache import cache
from django.db import DatabaseError
from django.utils import translation
from django.utils.translation import trans_real

logger = logging.getLogger(__name__)

LANGS = ("uz", "ru", "en")
CACHE_KEY = "sitetext:version"
CHECK_INTERVAL = 5  # soniya
WIDGET_DICT_PATH = Path(settings.FRONTEND_DIR) / "src" / "i18n.json"
UI_DICT_PATH = Path(settings.BASE_DIR) / "locale" / "translations.json"

_state = {"version": None, "checked_at": 0.0, "ui": {}, "widget": {}}
_original_gettext = trans_real.gettext


def bump_version() -> None:
    cache.set(CACHE_KEY, time.time_ns(), None)
    _state["checked_at"] = 0.0  # shu jarayon keyingi soʻrovda darhol yangilansin


def _load() -> tuple[dict, dict]:
    from .models import SiteText

    ui = {lang: {} for lang in LANGS}
    widget = {lang: {} for lang in LANGS}
    rows = SiteText.objects.exclude(text_uz="", text_ru="", text_en="")
    for row in rows.only("kind", "key", "text_uz", "text_ru", "text_en"):
        target = widget if row.kind == SiteText.KIND_WIDGET else ui
        for lang in LANGS:
            value = row.value(lang)
            if value:
                target[lang][row.key] = value
    return ui, widget


def refresh(force: bool = False) -> None:
    """Versiya oʻzgargan boʻlsa qayta yozuvlarni bazadan qayta oʻqiydi."""
    now = time.monotonic()
    if not force and now - _state["checked_at"] < CHECK_INTERVAL:
        return
    _state["checked_at"] = now
    try:
        version = cache.get(CACHE_KEY)
        if version is None:
            cache.add(CACHE_KEY, time.time_ns(), None)
            version = cache.get(CACHE_KEY)
        if version == _state["version"] and not force:
            return
        _state["ui"], _state["widget"] = _load()
    except DatabaseError:
        # Migratsiya/createcachetable hali bajarilmagan — standart tarjimalar bilan davom etamiz
        logger.warning("Sayt matnlari oʻqilmadi — standart tarjimalar ishlatiladi", exc_info=True)
        return
    _state["version"] = version


def _current_lang() -> str:
    lang = (translation.get_language() or settings.LANGUAGE_CODE).split("-")[0]
    return lang if lang in LANGS else "uz"


def gettext(message: str) -> str:
    override = _state["ui"].get(_current_lang(), {}).get(message)
    return override if override is not None else _original_gettext(message)


def widget_overrides() -> dict[str, str]:
    """Joriy til uchun vidjet matnlari qayta yozuvlari (base.html dagi #site-texts JSON)."""
    return _state["widget"].get(_current_lang(), {})


def install() -> None:
    """`AppConfig.ready()` dan: gettext'ni qayta yozuvlarni hisobga oladigan qilib almashtiradi."""
    trans_real.gettext = gettext
    # `translation._trans` birinchi murojaatda funksiyani keshlaydi — u yerda ham almashtiramiz
    translation._trans.gettext = gettext


@lru_cache(maxsize=1)
def default_texts() -> tuple[tuple[str, str, dict[str, str]], ...]:
    """(kind, key, {til: standart matn}) — admin paneldagi sinxronlash va koʻrsatish uchun."""
    from .management.commands.maketranslations import extract
    from .models import SiteText

    # Faqat shablon/kodda hozir ishlatilayotgan satrlar (translations.json da eskilari ham bor)
    with open(UI_DICT_PATH, encoding="utf-8") as f:
        ui = json.load(f)
    out = [
        (SiteText.KIND_UI, key, {"uz": key, "ru": ui.get(key, {}).get("ru", ""), "en": ui.get(key, {}).get("en", "")})
        for key in sorted(extract(Path(settings.BASE_DIR)))
    ]
    with open(WIDGET_DICT_PATH, encoding="utf-8") as f:
        widget = json.load(f)
    for key, uz in widget["uz"].items():
        out.append((SiteText.KIND_WIDGET, key, {lang: widget.get(lang, {}).get(key) or uz for lang in LANGS}))
    return tuple(out)


def default_for(kind: str, key: str) -> dict[str, str]:
    for row_kind, row_key, values in default_texts():
        if row_kind == kind and row_key == key:
            return values
    return {}


class SiteTextMiddleware:
    """Har soʻrov boshida (koʻpi bilan CHECK_INTERVAL da bir marta) qayta yozuvlarni yangilaydi."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        refresh()
        return self.get_response(request)
