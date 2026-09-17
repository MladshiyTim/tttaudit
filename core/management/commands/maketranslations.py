"""Tarjimalarni yig'adi va .mo fayllarini kompilyatsiya qiladi.

Windows'da GNU gettext (xgettext/msgfmt) odatda o'rnatilmagan, shuning uchun
bu buyruq ularsiz ishlaydi:

  1. Shablon va .py fayllardan tarjima qilinadigan satrlarni topadi
  2. `locale/translations.json` bilan solishtiradi
  3. Har til uchun .po (o'qish uchun) va .mo (Django uchun) yozadi

    python manage.py maketranslations           # yig'adi va kompilyatsiya qiladi
    python manage.py maketranslations --report  # faqat yetishmayotganini ko'rsatadi

Yangi satr qo'shilsa: buyruqni ishga tushiring, `translations.json` da
bo'sh qolgan joyni to'ldiring, yana ishga tushiring.
"""
import json
import re
import struct
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

TEMPLATE_PATTERNS = [
    # {% translate "matn" %} va {% trans "matn" %}, `as var` bilan ham
    re.compile(r"{%\s*(?:translate|trans)\s+\"([^\"]+)\"(?:\s+as\s+\w+)?\s*%}"),
    re.compile(r"{%\s*(?:translate|trans)\s+'([^']+)'(?:\s+as\s+\w+)?\s*%}"),
]
# {% blocktranslate ... %}matn{% endblocktranslate %}
BLOCK_PATTERN = re.compile(
    r"{%\s*blocktranslate[^%]*%}(.*?){%\s*endblocktranslate\s*%}", re.DOTALL
)
# {{ var }} ichida blocktranslate — Django buni msgid'da `%(var)s` ga aylantiradi
# (runtime'da shu shaklda topadi), shu sababli extraction ham xuddi shunday qilishi kerak.
BLOCK_VAR_PATTERN = re.compile(r"{{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*}}")

# Bitta satr qatorli literal: "..." yoki '...' (backslash bilan escape qilingan
# tirnoqlarni ham hisobga oladi).
STRING_LITERAL = r'"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\''
STRING_LITERAL_RE = re.compile(STRING_LITERAL)
# _( ... ) chaqiruvi ichida — Python bir-biriga tutash turgan bir nechta
# satr literalini (implicit concatenation) bitta satrga birlashtiradi, masalan:
#   _("abc " "def")   yoki   _(\n    "abc "\n    "def"\n)
# shuning uchun bu yerda ham hammasini yig'ib bitta msgid qilamiz.
PY_PATTERN = re.compile(r"_\(\s*((?:%s)(?:\s*(?:%s))*)\s*\)" % (STRING_LITERAL, STRING_LITERAL))


def _unescape_literal(literal: str) -> str:
    """`"a\\"b"` yoki `'a\\'b'` kabi bitta Python satr literalini dekodlaydi."""
    quote = literal[0]
    body = literal[1:-1]
    return body.replace("\\" + quote, quote).replace("\\\\", "\\")


def _join_py_literals(blob: str) -> str:
    """`_( ... )` ichidagi bir yoki bir nechta tutash literalni bitta matnga birlashtiradi."""
    return "".join(_unescape_literal(piece) for piece in STRING_LITERAL_RE.findall(blob))


def _blocktranslate_msgid(text: str) -> str:
    """`{{ var }}` ni Django blocktranslate ishlatadigan `%(var)s` shakliga oʻtkazadi."""
    return BLOCK_VAR_PATTERN.sub(lambda m: f"%({m.group(1)})s", text)


def collect_sources(base_dir: Path):
    """Tarjima qidiriladigan fayllar."""
    for path in sorted((base_dir / "core" / "templates").rglob("*.html")):
        yield path
    for name in ("models.py", "views.py", "forms.py", "compliance.py"):
        path = base_dir / "core" / name
        if path.exists():
            yield path


def extract(base_dir: Path):
    """Barcha msgid larni topadi: {satr: [fayl, ...]}"""
    found = {}

    def add(text, path):
        text = text.strip()
        if not text:
            return
        found.setdefault(text, [])
        rel = str(path.relative_to(base_dir)).replace("\\", "/")
        if rel not in found[text]:
            found[text].append(rel)

    for path in collect_sources(base_dir):
        source = path.read_text(encoding="utf-8")
        if path.suffix == ".html":
            for pattern in TEMPLATE_PATTERNS:
                for match in pattern.finditer(source):
                    add(match.group(1), path)
            for match in BLOCK_PATTERN.finditer(source):
                add(_blocktranslate_msgid(match.group(1)), path)
        else:
            for match in PY_PATTERN.finditer(source):
                add(_join_py_literals(match.group(1)), path)
    return found


def write_po(path: Path, language: str, entries: list):
    """entries: [(msgid, msgstr, [joylar])]"""
    lines = [
        'msgid ""',
        'msgstr ""',
        '"Project-Id-Version: tttaudit\\n"',
        '"MIME-Version: 1.0\\n"',
        '"Content-Type: text/plain; charset=UTF-8\\n"',
        '"Content-Transfer-Encoding: 8bit\\n"',
        f'"Language: {language}\\n"',
        "",
    ]
    for msgid, msgstr, places in entries:
        for place in places:
            lines.append(f"#: {place}")
        lines.append("msgid " + json.dumps(msgid, ensure_ascii=False))
        lines.append("msgstr " + json.dumps(msgstr, ensure_ascii=False))
        lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def write_mo(path: Path, catalog: dict):
    """.mo binar formatini to'g'ridan-to'g'ri yozadi (msgfmt kerak emas).

    Format: https://www.gnu.org/software/gettext/manual/html_node/MO-Files.html
    """
    items = sorted((k, v) for k, v in catalog.items() if v)
    # Bo'sh msgid — sarlavha
    items.insert(0, ("", "Content-Type: text/plain; charset=UTF-8\n"))

    keys = [k.encode("utf-8") for k, _ in items]
    values = [v.encode("utf-8") for _, v in items]
    count = len(items)

    key_offset = 7 * 4 + 16 * count
    value_offset = key_offset + sum(len(k) + 1 for k in keys)

    key_table, offset = [], key_offset
    for key in keys:
        key_table.append((len(key), offset))
        offset += len(key) + 1

    value_table, offset = [], value_offset
    for value in values:
        value_table.append((len(value), offset))
        offset += len(value) + 1

    output = struct.pack(
        "<7I",
        0x950412DE,          # sehrli raqam
        0,                   # versiya
        count,               # satrlar soni
        7 * 4,               # msgid jadvali offseti
        7 * 4 + 8 * count,   # msgstr jadvali offseti
        0, 0,                # hash jadvali ishlatilmaydi
    )
    for length, off in key_table:
        output += struct.pack("<2I", length, off)
    for length, off in value_table:
        output += struct.pack("<2I", length, off)
    for key in keys:
        output += key + b"\x00"
    for value in values:
        output += value + b"\x00"

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(output)


class Command(BaseCommand):
    help = "Tarjimalarni yigʻadi va .mo fayllarini kompilyatsiya qiladi (gettext kerak emas)."

    def add_arguments(self, parser):
        parser.add_argument("--report", action="store_true",
                            help="Faqat yetishmayotgan tarjimalarni koʻrsatadi")

    def handle(self, *args, **options):
        base_dir = Path(settings.BASE_DIR)
        locale_dir = base_dir / "locale"
        store_path = locale_dir / "translations.json"

        found = extract(base_dir)
        self.stdout.write(f"Topilgan satrlar: {len(found)}")

        store = {}
        if store_path.exists():
            store = json.loads(store_path.read_text(encoding="utf-8"))

        languages = [code for code, _ in settings.LANGUAGES if code != "uz"]

        # Yangi satrlarni lug'atga bo'sh qiymat bilan qo'shamiz
        added = 0
        for msgid in found:
            entry = store.setdefault(msgid, {})
            for lang in languages:
                if lang not in entry:
                    entry[lang] = ""
                    added += 1
        # Ishlatilmayotgan satrlarni belgilaymiz, lekin o'chirmaymiz
        stale = [k for k in store if k not in found]

        store_path.parent.mkdir(parents=True, exist_ok=True)
        store_path.write_text(
            json.dumps(store, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )

        missing = {lang: [] for lang in languages}
        for msgid in sorted(found):
            for lang in languages:
                if not store.get(msgid, {}).get(lang):
                    missing[lang].append(msgid)

        for lang in languages:
            self.stdout.write(
                f"  {lang}: {len(found) - len(missing[lang])}/{len(found)} tarjima qilingan"
            )

        if options["report"]:
            for lang in languages:
                if missing[lang]:
                    self.stdout.write(self.style.WARNING(f"\n{lang} uchun yetishmaydi:"))
                    for msgid in missing[lang][:200]:
                        self.stdout.write(f"  {msgid}")
            return

        for lang in languages:
            catalog = {
                msgid: store.get(msgid, {}).get(lang, "")
                for msgid in found
            }
            entries = [
                (msgid, catalog[msgid], found[msgid])
                for msgid in sorted(found)
            ]
            write_po(locale_dir / lang / "LC_MESSAGES" / "django.po", lang, entries)
            write_mo(locale_dir / lang / "LC_MESSAGES" / "django.mo", catalog)
            self.stdout.write(f"  {lang}: .po va .mo yozildi")

        if added:
            self.stdout.write(self.style.WARNING(
                f"{added} ta yangi joy locale/translations.json ga qoʻshildi (boʻsh)."
            ))
        if stale:
            self.stdout.write(f"Endi ishlatilmayotgan satrlar: {len(stale)}")
        self.stdout.write(self.style.SUCCESS("Tayyor. Serverni qayta ishga tushiring."))
