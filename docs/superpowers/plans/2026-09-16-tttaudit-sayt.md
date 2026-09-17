# TTT Audit sayti — implementatsiya rejasi

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** «TTTaudit» MChJ uchun davlat portali (my.gov.uz / soliq.uz) uslubidagi jiddiy, uch tilli, SSR sayt — `D:\tttaudit` ichida, mijozning haqiqiy hujjatlari, 39 mutaxassisi va 143 loyihasi bilan.

**Architecture:** Django 5.2 barcha sahifalarni serverda render qiladi (SEO asosiy kanal); React 19 + Vite 7 faqat uchta interaktiv vidjet (talab tekshiruvchi, energiya baholagich, murojaat formasi) uchun `[data-react]` orollari sifatida. Backend (modellar, energy/compliance mantiq, forma, tarjima buyrugʻi) `C:\Users\Surface PC\reper` dan port qilinadi; front (shablonlar, CSS, JS) butunlay yangi «davlat portali» dizayn tizimida yoziladi. Mijoz maʼlumoti `data/tttaudit/*.json` dan ikkita buyruq bilan bazaga tushadi.

**Tech Stack:** Python 3.14, Django 5.2.17, whitenoise, gunicorn, Pillow, pytest-django; Node 24, Vite 7, React 19; SQLite (lokal) / PostgreSQL (`DATABASE_URL`, prod).

**Spec:** `D:\tttaudit\docs\superpowers\specs\2026-09-16-tttaudit-sayt-spec.md`

## Global Constraints

- Loyiha ildizi: `D:\tttaudit` (mavjud `mijozdan kelgan ma'lumot\` va `logo\` papkalariga tegilmaydi).
- Brend nomi faqat **«TTT Audit»** / **TTT AUDIT**; «REPER», «TTT Engineering Audit», «auditorlik tashkiloti» iboralari hech qayerda yoʻq.
- Kontent faqat **energoaudit** va **qurilishda nazorat oʻlchovi**; moliyaviy audit, MSFO, oʻquv markazi yoʻq.
- Xodimlar boʻlimi nomi: **«Rahbariyat va mutaxassislar»**. Filiallar boʻlimi yoʻq (Toshkent ofisi faqat aloqa sahifasida).
- Manbasiz daʼvo yoʻq: ish soatlari, muddat, narx — boʻsh qoldiriladi; qonun faqat `verified_on` toʻldirilgan boʻlsa chiqadi.
- Stok foto va generativ tasvir yoʻq. Surat boʻlmasa blok suratsiz ishlaydi.
- Dizayn tokenlari (aynan): fon `#F3F4F7`, karta `#FFFFFF`, chegara `#D9DEE7`, brend `#27306E`, toʻq `#1E2556`, sariq `#FFC424` (faqat sarlavha ostidagi 3px chiziq, faol menyu, «Diqqat» chegarasi), shrift **Inter**, radius 8px, soyasiz.
- Tillar: `uz` (birlamchi), `ru`, `en`; URL prefiks `/uz/ /ru/ /en/`.
- Har sahifa: `<title>`, meta description, canonical, hreflang, breadcrumbs (bosh sahifadan tashqari).
- Murojaat: 5 ta/soat/IP, fayl ≤ 25 MB, ruxsat etilgan kengaytmalar `.pdf .xlsx .xls .docx .doc .dwg .zip .rar .jpg .jpeg .png`.
- Testlar `pytest`, qamrov `core/` uchun ≥ 80%.
- Commit xabarlari: `<type>: <tavsif>` (feat, fix, chore, test, docs).
- Windows konsoli: Python chiqishi uchun `PYTHONIOENCODING=utf-8`; buyruqlar Git Bash sintaksisida (`/d/tttaudit`).

---

## Fayl tuzilmasi

```
D:\tttaudit\
  manage.py
  pytest.ini  requirements.txt  requirements-dev.txt  .env.example  .gitignore  README.md  Dockerfile
  config\            settings.py  urls.py  wsgi.py  __init__.py
  core\
    models.py        SiteSettings, Direction, Service, LegalAct, Project, Instrument, TeamMember,
                     Credential, Post, Stat, Client, Branch, Lead  (Segment YOʻQ)
    views.py         sahifalar + 3 API
    urls.py
    forms.py         LeadForm (reper'dan oʻzgarishsiz)
    energy.py        A–G toifalari (oʻzgarishsiz)
    compliance.py    talab qoidalari (oʻzgarishsiz)
    throttle.py      cache asosidagi chegara
    notify.py        Telegram
    sitemaps.py
    admin.py  apps.py  context_processors.py
    templatetags\sitetags.py   tr, tr_list, alt_url, qs_replace
    management\commands\  seed_content.py  import_tttaudit.py  maketranslations.py
    templates\core\  base.html  _crumbs.html  _icon.html  _compliance.html  _energy.html  _lead.html
                     home.html  services.html  direction.html  service.html  registry.html
                     credentials.html  legislation.html  news.html  post.html  company.html
                     team.html  instruments.html  requisites.html  contact.html  request.html
                     404.html  robots.txt
    static\core\     css\site.css  js\site.js  img\logo-mark.png  img\logo-full.png
                     img\logo-full-white.png  img\favicon-32.png  img\apple-touch-icon.png  img\og-image.png
    tests\           conftest.py  test_models.py  test_import.py  test_pages.py  test_api.py  test_seo.py
  data\tttaudit\     (reper'dan nusxa: facts.json staff.json projects.json clients.json img\...)
  frontend\          package.json  vite.config.js  src\{main.jsx,csrf.js,ComplianceCheck.jsx,EnergyEstimator.jsx,LeadForm.jsx,widgets.css}
  locale\            translations.json  uz\ ru\ en\
  tools\prepare_logo.py
  docs\superpowers\  specs\  plans\
```

---

### Task 0: Loyiha skeleti va backend porti

**Files:**
- Create: `D:\tttaudit\{manage.py, pytest.ini, requirements.txt, requirements-dev.txt, .gitignore, .env.example}`
- Create: `D:\tttaudit\config\{__init__.py, settings.py, urls.py, wsgi.py}`
- Create: `D:\tttaudit\core\{__init__.py, apps.py, models.py, urls.py, energy.py, compliance.py, forms.py, admin.py, context_processors.py, templatetags\__init__.py, templatetags\sitetags.py, management\__init__.py, management\commands\__init__.py}`
- Copy: `C:\Users\Surface PC\reper\data\tttaudit\` → `D:\tttaudit\data\tttaudit\`
- Test: `D:\tttaudit\core\tests\{__init__.py, conftest.py, test_models.py}`

**Interfaces:**
- Produces: modellar (quyidagi maydon qoʻshimchalari bilan), `core.energy`, `core.compliance`, `core.forms.LeadForm`, `{{ obj|tr:"field" }}` filtri, `{% alt_url request code %}`, `{% qs_replace page=2 %}`, `settings.SITE_URL`, `settings.TELEGRAM_BOT_TOKEN/CHAT_ID`, `settings.LEAD_RATE_LIMIT/LEAD_RATE_WINDOW_SECONDS`.

- [ ] **Step 1: Papka va git**

```bash
cd /d/tttaudit && git init -b main
mkdir -p config core/templatetags core/management/commands core/templates/core core/static/core/css core/static/core/js core/static/core/img core/tests frontend/src locale tools
cp -r "/c/Users/Surface PC/reper/data" /d/tttaudit/data
ls data/tttaudit   # facts.json staff.json projects.json clients.json img snapshot.json bulletin.json
```

- [ ] **Step 2: Konfiguratsiya fayllari**

`requirements.txt`:
```
Django==5.2.17
dj-database-url==3.1.2
gunicorn==26.2.0
pillow==12.3.0
psycopg[binary]==3.3.4
whitenoise==6.12.0
```
`requirements-dev.txt`:
```
-r requirements.txt
pytest==9.1.1
pytest-django==4.14.0
pytest-cov==7.1.0
```
`pytest.ini`:
```ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings
python_files = test_*.py
testpaths = core/tests
addopts = -p no:cacheprovider
```
`.gitignore`:
```
.venv/
__pycache__/
*.pyc
db.sqlite3
media/
staticfiles/
frontend/dist/
frontend/node_modules/
.env
*.log
.pytest_cache/
htmlcov/
.coverage
```
`.env.example`:
```
DJANGO_SECRET_KEY=uzun-tasodifiy-qiymat
DJANGO_DEBUG=0
DJANGO_ALLOWED_HOSTS=tttaudit.uz,www.tttaudit.uz
DJANGO_CSRF_TRUSTED_ORIGINS=https://tttaudit.uz,https://www.tttaudit.uz
SITE_URL=https://tttaudit.uz
# DATABASE_URL=postgresql://user:parol@host:5432/tttaudit
# TELEGRAM_BOT_TOKEN=
# TELEGRAM_CHAT_ID=
```
`manage.py` — `C:\Users\Surface PC\reper\manage.py` dan oʻzgarishsiz nusxa. `config/__init__.py` boʻsh. `config/wsgi.py`:
```python
import os
from django.core.wsgi import get_wsgi_application
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
application = get_wsgi_application()
```

- [ ] **Step 3: settings.py**

`C:\Users\Surface PC\reper\config\settings.py` ni nusxalab quyidagi oʻzgarishlarni kiriting:
1. `MIDDLEWARE` dan `"core.middleware.ThemeCookieMiddleware",` qatorini oʻchiring.
2. `INSTALLED_APPS` ga `"django.contrib.sitemaps",` qoʻshing (`"core"` dan oldin).
3. `TEMPLATES[...]["OPTIONS"]["context_processors"]` ga `"django.template.context_processors.i18n",` qoʻshing.
4. `PREVIEW_THEMES = False` qatorini va uning izohini oʻchiring.
5. `DEFAULT_AUTO_FIELD` qatoridan keyin qoʻshing:
```python
# Mutlaq havolalar (sitemap, canonical, OG)
SITE_URL = os.environ.get("SITE_URL", "https://tttaudit.uz").rstrip("/")

# Murojaat bildirishnomasi (boʻsh boʻlsa yuborilmaydi)
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

# Murojaat chegarasi: bitta IP dan soatiga
LEAD_RATE_LIMIT = 5
LEAD_RATE_WINDOW_SECONDS = 3600

CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
```
6. Fayl boshidagi docstringni `"""Django settings — TTT Audit sayti (tttaudit.uz)."""` qiling.

- [ ] **Step 4: config/urls.py va boʻsh core/urls.py**

`config/urls.py`:
```python
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("i18n/", include("django.conf.urls.i18n")),
]

# Har bir til oʻz prefiksida: /uz/ /ru/ /en/
urlpatterns += i18n_patterns(
    path("", include("core.urls")),
    prefix_default_language=True,
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```
`core/urls.py` (Task 3 da toʻldiriladi):
```python
from django.urls import path

app_name = "core"
urlpatterns = []
```

- [ ] **Step 5: core/models.py — port va oʻzgarishlar**

`C:\Users\Surface PC\reper\core\models.py` ni nusxalab quyidagi tahrirlarni aynan bajaring:

1. **Segment sinfini butunlay oʻchiring** (`# ---- segment` izohidan uning `get_absolute_url` gacha).
2. `Direction` da `ACCENT_INK = "ink"` va `(ACCENT_INK, _("Neytral — moliyaviy audit")),` qatorlarini oʻchiring.
3. `SiteSettings` da `org_name = models.CharField(...)` ni quyidagiga almashtiring, `__str__` da `return self.org_name_uz`:
```python
    org_name_uz = models.CharField(_("Tashkilot (rasmiy nomi)"), max_length=120, default="«TTTaudit» MChJ")
    org_name_ru = models.CharField(max_length=120, blank=True)
    org_name_en = models.CharField(max_length=120, blank=True)
```
4. `SiteSettings` ga `founded_year` dan keyin qoʻshing:
```python
    director_uz = models.CharField(_("Rahbar"), max_length=120, blank=True)
    director_ru = models.CharField(max_length=120, blank=True)
    director_en = models.CharField(max_length=120, blank=True)
    office_tashkent_uz = models.CharField(_("Toshkent ofisi"), max_length=200, blank=True)
    office_tashkent_ru = models.CharField(max_length=200, blank=True)
    office_tashkent_en = models.CharField(max_length=200, blank=True)
    map_lat = models.FloatField(null=True, blank=True)
    map_lng = models.FloatField(null=True, blank=True)
    experience_years = models.PositiveSmallIntegerField(default=29)
    staff_total = models.PositiveSmallIntegerField(default=50)
    staff_energy = models.PositiveSmallIntegerField(default=24)
    staff_supervision = models.PositiveSmallIntegerField(default=16)
```
5. `SiteSettings` defaultlari: `brand_name` → `"TTT AUDIT"`, `brand_descriptor` → `"Energoaudit · nazorat oʻlchovi"`, `founded_year` → `1997`, `work_hours_uz` → `""`, `hero_kicker_uz` → `"Ekspert tashkiloti · Fargʻona · 1997-yildan"`, `hero_title_uz` → `"Energoaudit va qurilishda nazorat oʻlchovi"`, `hero_accent_uz` default `""`, `seo_title_uz` → `"Energoaudit va qurilishda nazorat oʻlchovi — TTT Audit, Fargʻona"`, `hero_text_uz` → `"Majburiy energoaudit va bino energopasporti, bajarilgan ish hajmlarining nazorat oʻlchovi, loyiha-smeta hujjatlari ekspertizasi va texnik nazorat. Xulosa davlat organi, bank va sud uchun dalil boʻladi."`. `hero_image.help_text` → `_("Boʻsh boʻlsa blok suratsiz chiqadi. Stok foto ishlatilmaydi.")`.
6. `Project`: `year` dan keyin `client = models.CharField(_("Buyurtmachi"), max_length=250, blank=True)`; `get_absolute_url` metodini **oʻchiring** (loyiha alohida sahifasiz — reestr jadvali); `Meta.ordering = ["-year", "order", "pk"]`.
7. `Instrument`: `model_name` dan keyin:
```python
    serial = models.CharField(_("Zavod raqami"), max_length=60, blank=True)
    valid_until = models.DateField(_("Qiyoslash amal qiladi"), null=True, blank=True)
    range_uz = models.CharField(_("Oʻlchov chegarasi"), max_length=160, blank=True)
    range_ru = models.CharField(max_length=160, blank=True)
    range_en = models.CharField(max_length=160, blank=True)
```
8. `TeamMember`: `email` dan keyin:
```python
    DEPT_ENERGY = "energy"
    DEPT_CONSTRUCTION = "construction"
    DEPT_CHOICES = [(DEPT_ENERGY, _("Energoaudit")), (DEPT_CONSTRUCTION, _("Qurilishda nazorat oʻlchovi"))]
    dept = models.CharField(_("Boʻlim"), max_length=16, choices=DEPT_CHOICES, default=DEPT_ENERGY)
    is_leadership = models.BooleanField(_("Rahbariyat"), default=False)
```
   `Meta.ordering = ["-is_leadership", "order"]`, `verbose_name_plural = _("Rahbariyat va mutaxassislar")`.
9. `Credential`: `KIND_REGISTRY = "registry"`, `KIND_INSURANCE = "insurance"` va `KIND_CHOICES` ga `(KIND_REGISTRY, _("Reestr")), (KIND_INSURANCE, _("Sugʻurta"))`.
10. `Branch`: `head` dan oldin:
```python
    address_uz = models.CharField(max_length=200, blank=True)
    address_ru = models.CharField(max_length=200, blank=True)
    address_en = models.CharField(max_length=200, blank=True)
```
11. `Post.Meta.verbose_name_plural = _("Yangiliklar")`.
12. Docstringga: `Segment modeli yoʻq — «kimga kerak» boʻlimi saytda yoʻq.`

- [ ] **Step 6: Oʻzgarishsiz nusxalanadigan fayllar va kichik tahrirlar**

```bash
cd /d/tttaudit && R="/c/Users/Surface PC/reper/core"
cp "$R/energy.py" "$R/compliance.py" "$R/forms.py" "$R/apps.py" core/
cp "$R/templatetags/__init__.py" "$R/templatetags/sitetags.py" core/templatetags/
cp "$R/management/__init__.py" core/management/ && cp "$R/management/commands/__init__.py" core/management/commands/
touch core/__init__.py core/tests/__init__.py
```
`core/admin.py`: reper `admin.py` nusxasi; `Segment` importi va `@admin.register(Segment)` bloki oʻchiriladi; `SiteSettingsAdmin.fieldsets` «Rekvizitlar»da `"org_name"` → `"org_name_uz", "org_name_ru", "org_name_en"` va oxiriga `"director_uz", "director_ru", "director_en", "office_tashkent_uz", "office_tashkent_ru", "office_tashkent_en", "map_lat", "map_lng", "experience_years", "staff_total", "staff_energy", "staff_supervision"`; `ProjectAdmin.list_display = ["title_uz", "client", "direction", "year", "order"]`, `search_fields = ["title_uz", "title_ru", "client"]`; `TeamMemberAdmin.list_display = ["full_name", "role_uz", "dept", "is_leadership", "order"]`, `list_filter = ["dept", "is_leadership"]`, `list_editable = ["is_leadership", "order"]`; `InstrumentAdmin.list_display = ["name_uz", "serial", "certificate_no", "verified_on", "valid_until", "order"]`.

`core/context_processors.py`:
```python
"""Har bir shablonga sayt sozlamalari, menyu yoʻnalishlari va SITE_URL."""
from django.conf import settings

from .models import Direction, SiteSettings


def site_settings(request):
    return {
        "site": SiteSettings.load(),
        "nav_directions": Direction.objects.all(),
        "SITE_URL": settings.SITE_URL,
    }
```

`core/templatetags/sitetags.py` oxiriga:
```python
from django.urls import translate_url


@register.simple_tag
def alt_url(request, lang_code):
    """Joriy sahifaning boshqa tildagi mutlaq manzili (hreflang, til almashtirgich)."""
    return request.build_absolute_uri(translate_url(request.path, lang_code))


@register.simple_tag(takes_context=True)
def qs_replace(context, **kwargs):
    """Joriy GET parametrlarini saqlab bittasini almashtiradi: {% qs_replace page=2 %}"""
    query = context["request"].GET.copy()
    for key, value in kwargs.items():
        if value in (None, ""):
            query.pop(key, None)
        else:
            query[key] = value
    encoded = query.urlencode()
    return f"?{encoded}" if encoded else "?"
```

- [ ] **Step 7: Yozilmagan test (models)**

`core/tests/conftest.py` (Task 1 da `django_db_setup` qoʻshiladi):
```python
import pytest
from django.core.cache import cache


@pytest.fixture(autouse=True)
def clear_cache():
    cache.clear()
    yield
    cache.clear()
```
`core/tests/test_models.py`:
```python
import pytest
from django.utils import translation

from core import compliance, energy
from core.models import Direction, SiteSettings


@pytest.mark.django_db
def test_tr_falls_back_to_uz_when_translation_empty():
    d = Direction.objects.create(slug="energoaudit", title_uz="Energoaudit", title_ru="", summary_uz="x")
    with translation.override("ru"):
        assert d.tr("title") == "Energoaudit"
    d.title_ru = "Энергоаудит"
    with translation.override("ru"):
        assert d.tr("title") == "Энергоаудит"


@pytest.mark.django_db
def test_site_settings_load_creates_single_row():
    assert SiteSettings.objects.count() == 0
    site = SiteSettings.load()
    assert site.org_name_uz == "«TTTaudit» MChJ"
    assert SiteSettings.load().pk == site.pk


def test_energy_category_bands():
    assert energy.category_for(30) == "A"
    assert energy.category_for(100) == "D"
    assert energy.category_for(500) == "G"
    assert energy.category_for(None) is None


def test_compliance_registry_threshold_triggers_mandatory_audit():
    result = compliance.evaluate(object_kind="industrial", annual_kwh=5_000_000)
    assert "mandatory_energy_audit" in [r.key for r in result.requirements]


def test_compliance_budget_construction_gives_fee_cap():
    result = compliance.evaluate(object_kind="construction", funding="budget", estimate_value="1000000")
    assert result.estimated_fee == "3 000"
```

- [ ] **Step 8: Muhit, migratsiya, test**

```bash
cd /d/tttaudit && python -m venv .venv && source .venv/Scripts/activate && pip install -r requirements-dev.txt
python manage.py makemigrations core && python manage.py migrate
PYTHONIOENCODING=utf-8 pytest -q
```
Kutilgan: `5 passed`. Agar `AttributeError: org_name_uz` — Step 5 band 3 bajarilmagan.

- [ ] **Step 9: Commit**

```bash
git add -A && git commit -m "chore: TTT Audit sayti skeleti — Django backend porti, mijoz maʼlumoti, testlar"
```

---

### Task 1: Tahririy kontent va mijoz faktlari importi

**Files:**
- Create: `core/management/commands/seed_content.py` (reper'dan port, tahrir bilan)
- Create: `core/management/commands/import_tttaudit.py` (qaytadan)
- Modify: `core/tests/conftest.py`
- Test: `core/tests/test_import.py`

**Interfaces:**
- Consumes: Task 0 modellari.
- Produces: `seed_content [--force]` → `Direction` (`energoaudit`, `olchov-auditi`), `Service` (8: `majburiy, energopasport, termografiya, ekspress` / `nazorat-olchovi, smeta-auditi, texnik-nazorat, nizo`), `LegalAct` (4, 2 tasi `verified_on` bilan), `Post`, `SiteSettings` matnlari. `import_tttaudit [--force]` → rekvizitlar, `Branch` (2), `Credential` (8), `Instrument` (5), `Stat` (4), `TeamMember` (39), `Project` (143), `Client`.

- [ ] **Step 1: Yozilmagan test**

`core/tests/test_import.py`:
```python
import pytest
from django.core.management import call_command

from core.models import (
    Branch, Client, Credential, Direction, Instrument, Project, Service,
    SiteSettings, Stat, TeamMember,
)


@pytest.mark.django_db
def test_seed_content_creates_two_directions_and_eight_services():
    assert set(Direction.objects.values_list("slug", flat=True)) == {"energoaudit", "olchov-auditi"}
    assert Service.objects.count() == 8
    assert not Service.objects.filter(slug__in=["msfo", "konsalting", "malaka-oshirish"]).exists()


@pytest.mark.django_db
def test_import_loads_client_facts():
    site = SiteSettings.load()
    assert site.tin == "202216926"
    assert site.director_uz.startswith("Botirov")
    assert Branch.objects.count() == 2
    assert Credential.objects.count() == 8
    assert Credential.objects.filter(kind="insurance").exists()
    assert Instrument.objects.count() == 5
    assert Stat.objects.count() == 4
    assert TeamMember.objects.count() == 39
    assert TeamMember.objects.filter(dept="energy").count() == 24
    assert TeamMember.objects.exclude(photo="").count() >= 30
    assert Project.objects.count() == 143
    assert Project.objects.filter(direction__slug="olchov-auditi").count() == 95
    assert Client.objects.count() > 0


@pytest.mark.django_db
def test_import_is_idempotent_without_force():
    before = Project.objects.count()
    call_command("import_tttaudit")
    assert Project.objects.count() == before
```

- [ ] **Step 2: conftest.py toʻliq**

```python
import pytest
from django.core.cache import cache
from django.core.management import call_command


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    """Bazani bir marta toʻldiradi: tahririy kontent + mijoz faktlari."""
    with django_db_blocker.unblock():
        call_command("seed_content")
        call_command("import_tttaudit")


@pytest.fixture(autouse=True)
def clear_cache():
    cache.clear()
    yield
    cache.clear()
```

- [ ] **Step 3: Test — muvaffaqiyatsizlik**

Run: `PYTHONIOENCODING=utf-8 pytest -q core/tests/test_import.py` → `Unknown command: 'seed_content'`.

- [ ] **Step 4: seed_content.py port**

`C:\Users\Surface PC\reper\core\management\commands\seed_content.py` ni nusxalab:
1. Import: `from core.models import Direction, LegalAct, Post, Service, SiteSettings` (Segment yoʻq).
2. `DIRECTIONS` dan `"slug": "moliyaviy-audit"` boʻlgan uchinchi lugʻatni butunlay oʻchiring.
3. `SERVICES` dan `"moliyaviy-audit": [...]` kalitini (4 xizmat) butunlay oʻchiring.
4. `SEGMENTS = [...]`, `_segments` metodi va `handle` dagi `self._segments(services)` — oʻchiring.
5. `"olchov-auditi"` yoʻnalishi: `title_uz = "Qurilishda nazorat oʻlchovi"`, `title_ru = "Контрольный обмер в строительстве"`, `title_en = "Construction control measurement"`.
6. `VERIFIED_ON` dan keyin `SITE` lugʻatini qoʻshing va `handle` boshida `self._site()` chaqiring:
```python
SITE = {
    "hero_kicker_uz": "Ekspert tashkiloti · Fargʻona · 1997-yildan",
    "hero_kicker_ru": "Экспертная организация · Фергана · с 1997 года",
    "hero_kicker_en": "Expert organisation · Fergana · since 1997",
    "hero_title_uz": "Energoaudit va qurilishda nazorat oʻlchovi",
    "hero_title_ru": "Энергоаудит и контрольный обмер в строительстве",
    "hero_title_en": "Energy audit and construction control measurement",
    "hero_accent_uz": "", "hero_accent_ru": "", "hero_accent_en": "",
    "seo_title_uz": "Energoaudit va qurilishda nazorat oʻlchovi — TTT Audit, Fargʻona",
    "seo_title_ru": "Энергоаудит и контрольный обмер в строительстве — TTT Audit, Фергана",
    "seo_title_en": "Energy audit and construction control measurement — TTT Audit, Fergana",
    "hero_text_uz": (
        "Majburiy energoaudit va bino energopasporti, bajarilgan ish hajmlarining "
        "nazorat oʻlchovi, loyiha-smeta hujjatlari ekspertizasi va texnik nazorat. "
        "Xulosa davlat organi, bank va sud uchun dalil boʻladi."
    ),
    "hero_text_ru": (
        "Обязательный энергоаудит и энергопаспорт здания, контрольный обмер выполненных "
        "объёмов работ, экспертиза проектно-сметной документации и технический надзор. "
        "Заключение служит доказательством для госоргана, банка и суда."
    ),
    "hero_text_en": (
        "Mandatory energy audit and building energy passport, control measurement of "
        "completed construction work, design-estimate expertise and technical supervision. "
        "Our report is evidence for state bodies, banks and courts."
    ),
    "about_uz": (
        "Ekspert tashkiloti Oʻzbekiston Respublikasida 1997-yil 12-martdan rasman faoliyat "
        "yuritadi. Tashkilot Oʻzbekiston muhandis-konsultantlar uyushmasi (UZACE) aʼzosi "
        "sifatida energoaudit va nazorat oʻlchovi sohasida ishlaydi.\n\n"
        "Bugun tashkilotda 50 xodim ishlaydi: 24 nafari energoaudit va energosamaradorlik "
        "boʻyicha, 16 nafari texnik nazorat boʻyicha mutaxassis. Menejment tizimi "
        "ISO 9001:2015, ISO 45001:2018 va ISO 27001:2022 boʻyicha sertifikatlangan.\n\n"
        "Kasbiy faoliyat «Imkon-sugʻurta» AJ tomonidan 10 000 000 000 soʻmga sugʻurtalangan."
    ),
    "about_ru": (
        "Экспертная организация официально действует в Республике Узбекистан с 12 марта "
        "1997 года и является членом Ассоциации инженеров-консультантов Узбекистана (UZACE) "
        "в области энергоаудита и контрольного обмера.\n\n"
        "В организации работает 50 человек: 24 специалиста по энергоаудиту и "
        "энергоэффективности и 16 специалистов по техническому надзору. Система менеджмента "
        "сертифицирована по ISO 9001:2015, ISO 45001:2018 и ISO 27001:2022.\n\n"
        "Профессиональная деятельность застрахована АО «Imkon-sug’urta» на сумму "
        "10 000 000 000 сум."
    ),
    "about_en": (
        "The expert organisation has operated in Uzbekistan since 12 March 1997 and is a "
        "member of the Association of Consulting Engineers of Uzbekistan (UZACE) for energy "
        "audit and control measurement.\n\n"
        "Staff of 50: 24 energy audit and efficiency specialists and 16 technical "
        "supervision specialists. Management system certified to ISO 9001:2015, "
        "ISO 45001:2018 and ISO 27001:2022.\n\n"
        "Professional liability insured by Imkon-sug'urta JSC for UZS 10,000,000,000."
    ),
}
```
```python
    def _site(self) -> None:
        site = SiteSettings.load()
        for field, value in SITE.items():
            setattr(site, field, value)
        site.save()
```

- [ ] **Step 5: import_tttaudit.py — toʻliq yangi**

```python
"""Mijoz faktlarini data/tttaudit/*.json dan bazaga yuklaydi.

    python manage.py import_tttaudit           # boʻsh jadvallarni toʻldiradi
    python manage.py import_tttaudit --force   # jadvallarni fayldagi holatga qaytaradi

Oldin `seed_content` ishga tushirilgan boʻlishi shart (yoʻnalishlar kerak).

Manba fayllar:
    facts.json     kompaniya rekvizitlari, hujjatlar (skan bilan), asboblar, raqamlar
    staff.json     39 mutaxassis (byulleten), suratlar img/staff/
    projects.json  143 loyiha (byulleten), buyurtmachi nomi bilan
    clients.json   eski saytdagi mijozlar roʻyxati (soha bilan)

Egalik qilinadigan jadvallar: Branch, Credential, Instrument, Stat, TeamMember,
Project, Client. --force ularni qayta yaratadi — admin paneldagi tahrirlar yoʻqoladi.
SiteSettings da faqat rekvizit maydonlari yangilanadi (matnlar seed_content'da).
"""
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.models import (
    Branch, Client, Credential, Direction, Instrument, Project, SiteSettings, Stat, TeamMember,
)

DATA_DIR = Path(settings.BASE_DIR) / "data" / "tttaudit"
DEPT_TO_DIRECTION = {"energy": "energoaudit", "construction": "olchov-auditi"}
LEADERSHIP_WORDS = ("директор", "начальник", "руководител")


def load_json(name: str) -> dict:
    path = DATA_DIR / name
    if not path.exists():
        raise CommandError(f"{path} topilmadi")
    return json.loads(path.read_text(encoding="utf-8"))


def parse_date(value: str | None) -> dt.date | None:
    return dt.date.fromisoformat(value) if value else None


def attach(field, rel_path: str | None) -> None:
    """data/tttaudit/<rel_path> faylini ImageField/FileField ga nusxalaydi."""
    if not rel_path:
        return
    source = DATA_DIR / rel_path
    if not source.exists():
        raise CommandError(f"Fayl topilmadi: {source}")
    with source.open("rb") as handle:
        field.save(source.name, File(handle), save=False)


class Command(BaseCommand):
    help = "data/tttaudit/*.json dagi mijoz faktlarini bazaga yuklaydi."

    def add_arguments(self, parser):
        parser.add_argument("--force", action="store_true", help="Jadvallarni qayta yaratish.")

    def handle(self, *args, **options):
        facts = load_json("facts.json")
        staff = load_json("staff.json")
        projects = load_json("projects.json")
        clients = load_json("clients.json")
        force = options["force"]

        directions = {d.slug: d for d in Direction.objects.all()}
        missing = set(DEPT_TO_DIRECTION.values()) - set(directions)
        if missing:
            raise CommandError(f"Yonalish topilmadi: {sorted(missing)}. Avval: python manage.py seed_content")

        with transaction.atomic():
            self._site(facts["company"])
            self._table(Branch, force, lambda: self._branches(facts["company"]))
            self._table(Credential, force, lambda: self._credentials(facts["credentials"]))
            self._table(Instrument, force, lambda: self._instruments(facts["instruments"], directions))
            self._table(Stat, force, lambda: self._stats(facts["stats"]))
            self._table(TeamMember, force, lambda: self._team(staff["staff"]))
            self._table(Project, force, lambda: self._projects(projects["projects"], directions))
            self._table(Client, force, lambda: self._clients(clients))

        # Konsol xabari ASCII: Windows konsoli oʻ/gʻ ni chiqara olmaydi
        self.stdout.write(self.style.SUCCESS(
            f"Yuklandi: {Branch.objects.count()} ofis / {Credential.objects.count()} hujjat / "
            f"{Instrument.objects.count()} asbob / {Stat.objects.count()} raqam / "
            f"{TeamMember.objects.count()} mutaxassis / {Project.objects.count()} loyiha / "
            f"{Client.objects.count()} mijoz"
        ))

    def _table(self, model, force: bool, fill) -> None:
        if model.objects.exists() and not force:
            self.stdout.write(f"{model.__name__}: malumot bor - otkazib yuborildi (--force).")
            return
        for obj in model.objects.all():
            for field in obj._meta.fields:
                if field.get_internal_type() in ("FileField", "ImageField"):
                    getattr(obj, field.name).delete(save=False)
        model.objects.all().delete()
        fill()

    def _site(self, company: dict) -> None:
        site = SiteSettings.load()
        site.brand_name = "TTT AUDIT"
        site.org_name_uz = company["legal_name_uz"]
        site.org_name_ru = company["legal_name_ru"]
        site.org_name_en = company["legal_name_en"]
        site.tin = company["tin"]
        site.founded_year = company["founded_year"]
        site.experience_years = company["experience_years"]
        site.staff_total = company["staff_total"]
        site.staff_energy = company["staff_energy"]
        site.staff_supervision = company["staff_supervision"]
        site.phone = company["phone"]
        site.phone_second = company["phone_second"]
        site.email = company["email"]
        site.director_uz = company["director"]
        site.director_ru = company["director_ru"]
        site.director_en = company["director"]
        site.map_lat = company["map_lat"]
        site.map_lng = company["map_lng"]
        for lang in ("uz", "ru", "en"):
            setattr(site, f"address_{lang}", company[f"address_{lang}"])
            setattr(site, f"office_tashkent_{lang}",
                    company.get(f"office_tashkent_{lang}") or company["office_tashkent_uz"])
        site.report_turnaround_days = None
        site.work_hours_uz = site.work_hours_ru = site.work_hours_en = ""
        site.save()

    def _branches(self, company: dict) -> None:
        Branch.objects.bulk_create([
            Branch(city_uz="Fargʻona", city_ru="Фергана", city_en="Fergana",
                   address_uz=company["address_uz"], address_ru=company["address_ru"],
                   address_en=company["address_en"], head=company["director"],
                   phone=company["phone"], is_head_office=True, order=0),
            Branch(city_uz="Toshkent", city_ru="Ташкент", city_en="Tashkent",
                   address_uz=company["office_tashkent_uz"], address_ru=company["office_tashkent_ru"],
                   address_en=company.get("office_tashkent_en") or company["office_tashkent_uz"],
                   head="", phone=company["phone_second"], is_head_office=False, order=1),
        ])

    def _credentials(self, credentials: list[dict]) -> None:
        valid = {key for key, _ in Credential.KIND_CHOICES}
        for order, c in enumerate(c for c in credentials if c.get("show")):
            if c["kind"] not in valid:
                raise CommandError(f"facts.json: nomalum hujjat turi {c['kind']!r}, ruxsat: {sorted(valid)}")
            obj = Credential(
                kind=c["kind"], number=c["number"],
                issuer_uz=c["issuer_uz"], issuer_ru=c["issuer_ru"], issuer_en=c["issuer_en"],
                scope_uz=c["scope_uz"], scope_ru=c["scope_ru"], scope_en=c["scope_en"],
                issued_on=parse_date(c.get("issued_on")), valid_until=parse_date(c.get("valid_until")),
                show_in_hero=order < 3, order=order,
            )
            attach(obj.scan, c.get("scan"))
            obj.save()

    def _instruments(self, instruments: list[dict], directions: dict) -> None:
        construction = directions["olchov-auditi"]
        Instrument.objects.bulk_create([
            Instrument(
                name_uz=i["name_uz"], name_ru=i.get("name_ru", ""), name_en=i.get("name_en", ""),
                serial=i.get("serial", ""), certificate_no=i.get("cert", ""),
                verified_on=parse_date(i.get("verified_on")), valid_until=parse_date(i.get("valid_until")),
                range_uz=i.get("range_uz", ""), direction=construction, order=order,
            )
            for order, i in enumerate(instruments)
        ])

    def _stats(self, stats: list[dict]) -> None:
        Stat.objects.bulk_create([
            Stat(value=s["value"], label_uz=s["label_uz"], label_ru=s["label_ru"],
                 label_en=s["label_en"], order=order)
            for order, s in enumerate(stats)
        ])

    def _team(self, staff: list[dict]) -> None:
        for order, row in enumerate(staff):
            role_ru = (row.get("role_ru") or "").lower()
            obj = TeamMember(
                full_name=row["name_uz"] or row["name_ru"], full_name_ru=row["name_ru"],
                role_uz=row["role_uz"], role_ru=row["role_ru"], role_en=row["role_en"],
                certificates_uz=row.get("cert_uz", ""), dept=row["dept"],
                is_leadership=any(word in role_ru for word in LEADERSHIP_WORDS), order=order,
            )
            if row.get("photo"):
                attach(obj.photo, row["photo"])
            obj.save()

    def _projects(self, projects: list[dict], directions: dict) -> None:
        rows = []
        for index, p in enumerate(projects, start=1):
            rows.append(Project(
                slug=f"{p['dept']}-{index:03d}", direction=directions[DEPT_TO_DIRECTION[p["dept"]]],
                order=index, year=p.get("year"), client=p.get("client", ""),
                title_uz=p["title_uz"][:200], title_ru=p["title_ru"][:200], title_en="",
            ))
        Project.objects.bulk_create(rows)

    def _clients(self, data: dict) -> None:
        valid = {key for key, _ in Client.SECTOR_CHOICES}
        unknown = {c["sector"] for c in data["clients"]} - valid
        if unknown:
            raise CommandError(f"clients.json da nomalum soha: {sorted(unknown)}")
        Client.objects.bulk_create([
            Client(name_uz=c["name_uz"], name_ru=c.get("name_ru", ""), name_en=c.get("name_en", ""),
                   sector=c["sector"], featured=c.get("featured", False), order=order)
            for order, c in enumerate(data["clients"])
        ])
```

- [ ] **Step 6: Testlar oʻtadi**

Run: `PYTHONIOENCODING=utf-8 pytest -q` → hammasi PASS (8 ta).

- [ ] **Step 7: Lokal baza va commit**

```bash
PYTHONIOENCODING=utf-8 python manage.py seed_content && PYTHONIOENCODING=utf-8 python manage.py import_tttaudit
git add -A && git commit -m "feat: tahririy kontent va mijoz faktlari (39 mutaxassis, 143 loyiha, 8 hujjat) bazaga"
```

---

### Task 2: Logotipni saytga tayyorlash

**Files:**
- Create: `tools/prepare_logo.py`
- Create (skript chiqaradi): `core/static/core/img/{logo-mark.png, logo-full.png, logo-full-white.png, favicon-32.png, apple-touch-icon.png, og-image.png}`
- Test: `core/tests/test_logo.py`

**Interfaces:**
- Consumes: `D:\tttaudit\logo\*.png` (1254×1254 RGB, kulrang fon ~#EAEAEA, belgi toʻq kulrang/qora, 3D soya bilan; emblema yuqori ~54%, ostida «TTT» va «audit» soʻzlari).
- Produces: shaffof fonli tekis PNG'lar. `logo-mark.png` — faqat emblema (sarlavha, 44px), `logo-full.png` / `logo-full-white.png` — toʻliq belgi (futer, OG), favicon 32 va 180, `og-image.png` 1200×630.

- [ ] **Step 1: Yozilmagan test**

`core/tests/test_logo.py`:
```python
from pathlib import Path

from PIL import Image

IMG = Path(__file__).resolve().parents[1] / "static" / "core" / "img"


def test_logo_files_exist_and_are_transparent():
    for name in ("logo-mark.png", "logo-full.png", "logo-full-white.png", "favicon-32.png", "apple-touch-icon.png"):
        im = Image.open(IMG / name)
        assert im.mode == "RGBA", name
        assert im.getpixel((0, 0))[3] == 0, f"{name}: burchak shaffof emas"


def test_logo_sizes():
    assert Image.open(IMG / "favicon-32.png").size == (32, 32)
    assert Image.open(IMG / "apple-touch-icon.png").size == (180, 180)
    assert Image.open(IMG / "og-image.png").size == (1200, 630)
    assert Image.open(IMG / "logo-mark.png").size == (512, 512)
```

- [ ] **Step 2: Test — muvaffaqiyatsizlik**

Run: `pytest -q core/tests/test_logo.py` → `FileNotFoundError`.

- [ ] **Step 3: Skript**

`tools/prepare_logo.py`:
```python
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
```

- [ ] **Step 4: Ishga tushirish va koʻz bilan tekshirish**

```bash
cd /d/tttaudit && python tools/prepare_logo.py
```
`core/static/core/img/logo-mark.png` va `logo-full.png` ni Read tool bilan oching. Tekshiruv: (1) `logo-mark.png` da «TTT» harflari yoʻq, faqat emblema — boʻlmasa `EMBLEM_CUT` ni 0.52–0.56 orasida sozlang; (2) belgi atrofida kulrang soya dogʻlari yoʻq — boʻlsa `THRESHOLD = 120`; (3) ingichka chiziqlar (chaqmoq, strelka) uzilmagan — uzilsa `THRESHOLD = 165`. Sozlagach qayta ishga tushiring.

- [ ] **Step 5: Test oʻtadi va commit**

```bash
pytest -q core/tests/test_logo.py
git add -A && git commit -m "feat: mijoz logotipidan sayt uchun emblema, favicon va OG tasvir"
```

---

### Task 3: Dizayn tizimi va asosiy shablon

**Files:**
- Create: `core/static/core/css/site.css`, `core/static/core/js/site.js`
- Create: `core/templates/core/{base.html, _crumbs.html, _icon.html, 404.html}`
- Create: `core/views.py` (yordamchilar + vaqtinchalik `home`); Modify: `core/urls.py` (barcha nomlar)
- Test: `core/tests/test_base.py`

**Interfaces:**
- Produces: `base.html` bloklari `title`, `description`, `og_title`, `head`, `main`; kontekst kalitlari `nav` (`services|registry|credentials|legislation|company|news|contact`), `crumbs` (list of `(title, url_or_None)`); CSS klasslari `.wrap .card .grid .grid--2/3/4 .split .btn .btn--ghost .btn--sm .badge .badge--ok/--warn/--accent .table .table-wrap .doc .notice .notice--info/--ok/--danger .steps .faq .stats .stat .phead .sec .sec--white .sec__head .filters .input .select .textarea .pager .person .cat .cat__ico .cat__all .news .prose .muted .nums`; `views.page(request, template, nav="", crumbs=(), **context)`, `views.form_context()`, `views.compliance_context()`, `views.energy_context()`; URL nomlari `core:home services direction service registry credentials legislation news post company team instruments requisites contact request`.

- [ ] **Step 1: Yozilmagan test**

`core/tests/test_base.py`:
```python
import pytest
from django.template.loader import render_to_string
from django.test import RequestFactory
from django.utils import translation


@pytest.mark.django_db
def test_base_template_has_gov_portal_chrome():
    request = RequestFactory().get("/uz/")
    with translation.override("uz"):
        html = render_to_string("core/base.html", {"nav": "", "crumbs": []}, request=request)
    assert 'class="ubar"' in html                       # yuqori xizmat paneli
    assert "Maxsus imkoniyatlar" in html                # a11y rejimi
    assert 'hreflang="ru"' in html and 'hreflang="en"' in html
    assert "logo-mark.png" in html
    assert "TTT AUDIT" in html
    assert "REPER" not in html
    assert "auditorlik tashkiloti" not in html.lower()


@pytest.mark.django_db
def test_404_page_renders(client):
    response = client.get("/uz/bunday-sahifa-yoq/")
    assert response.status_code == 404
    assert "Sahifa topilmadi".encode() in response.content
```

- [ ] **Step 2: Test — muvaffaqiyatsizlik**

Run: `PYTHONIOENCODING=utf-8 pytest -q core/tests/test_base.py` → `TemplateDoesNotExist: core/base.html`.

- [ ] **Step 3: site.css — dizayn tizimi**

`core/static/core/css/site.css`:
```css
/* TTT Audit — dizayn tizimi. Davlat portali uslubi: och kulrang fon, oq kartalar,
   toʻq koʻk brend, sariq faqat belgi sifatida. Soyasiz, serifsiz. */
:root{
  --bg:#F3F4F7; --card:#FFFFFF; --ink:#16213E; --ink-2:#3C465E; --muted:#6B7280;
  --line:#D9DEE7; --line-2:#E8EBF1;
  --brand:#27306E; --brand-700:#1E2556; --brand-50:#EEF0F8; --brand-100:#DDE1F2;
  --link:#1F3F9E;
  --accent:#FFC424; --accent-100:#FFF4D1; --accent-ink:#6B4E00;
  --ok:#1E7F4F; --ok-50:#E7F5EC; --warn:#B45309; --warn-50:#FFF3E0; --danger:#B42318; --danger-50:#FDECEA;
  --radius:8px; --wrap:1200px; --gut:clamp(16px,4vw,32px);
  --font:"Inter",system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
}
*,*::before,*::after{box-sizing:border-box}
html{-webkit-text-size-adjust:100%;scroll-behavior:smooth}
body{margin:0;font:400 16px/1.55 var(--font);color:var(--ink);background:var(--bg)}
html[data-a11y="on"] body{font-size:19px;filter:grayscale(1)}
html[data-a11y="on"] a{text-decoration:underline}
img{max-width:100%;height:auto;display:block}
a{color:var(--link)}
h1,h2,h3,h4{font-weight:600;line-height:1.25;margin:0 0 .5em}
p{margin:0 0 1em}
.muted{color:var(--muted)}
.nums{font-variant-numeric:tabular-nums}
.wrap{max-width:var(--wrap);margin:0 auto;padding:0 var(--gut)}
.skip{position:absolute;left:-999px;top:8px;background:#fff;padding:8px 12px;border:2px solid var(--brand);z-index:100}
.skip:focus{left:8px}

/* ---- yuqori xizmat paneli ---- */
.ubar{background:var(--brand-700);color:#fff;font-size:13px}
.ubar .wrap{display:flex;align-items:center;justify-content:space-between;min-height:36px;gap:16px}
.ubar a{color:#fff;text-decoration:none}
.ubar a:hover{text-decoration:underline}
.ubar__l,.ubar__r{display:flex;gap:18px;align-items:center}
.lang{display:flex;gap:2px}
.lang a{padding:2px 8px;border-radius:4px;text-transform:uppercase;font-weight:600;letter-spacing:.04em}
.lang a[aria-current]{background:#fff;color:var(--brand-700)}
.a11y-btn{background:transparent;border:1px solid rgba(255,255,255,.45);color:#fff;border-radius:4px;padding:3px 10px;font:inherit;font-size:13px;cursor:pointer}
.a11y-btn[aria-pressed="true"]{background:#fff;color:var(--brand-700)}

/* ---- sarlavha ---- */
.hdr{background:#fff;border-bottom:3px solid var(--accent);position:sticky;top:0;z-index:50}
.hdr .wrap{display:flex;align-items:center;gap:28px;min-height:72px;position:relative}
.logo{display:flex;align-items:center;gap:12px;text-decoration:none;color:var(--ink)}
.logo img{height:44px;width:44px}
.logo__t{display:flex;flex-direction:column;line-height:1.1}
.logo__t b{font-size:18px;letter-spacing:.08em}
.logo__t span{font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.05em;margin-top:3px}
.nav{margin-left:auto;display:flex;gap:2px}
.nav a{padding:10px 12px;color:var(--ink);text-decoration:none;font-weight:500;font-size:15px;border-radius:6px}
.nav a:hover{background:var(--brand-50)}
.nav a[aria-current]{color:var(--brand);box-shadow:inset 0 -3px 0 var(--accent);border-radius:6px 6px 0 0}
.nav-toggle{display:none}

/* ---- tugmalar ---- */
.btn{display:inline-flex;align-items:center;gap:8px;padding:10px 18px;border-radius:6px;border:1px solid var(--brand);background:var(--brand);color:#fff;font:600 15px/1.2 var(--font);text-decoration:none;cursor:pointer;white-space:nowrap}
.btn:hover{background:var(--brand-700);border-color:var(--brand-700)}
.btn--ghost{background:#fff;color:var(--brand)}
.btn--ghost:hover{background:var(--brand-50);color:var(--brand)}
.btn--sm{padding:7px 12px;font-size:14px}
.btn[disabled]{opacity:.55;cursor:default}

/* ---- breadcrumbs va sahifa boshi ---- */
.crumbs{font-size:13px;color:var(--muted);padding:14px 0 0}
.crumbs ol{list-style:none;margin:0;padding:0;display:flex;flex-wrap:wrap;gap:6px}
.crumbs li+li::before{content:"/";margin-right:6px;color:#B7BECB}
.crumbs a{color:var(--muted);text-decoration:none}
.crumbs a:hover{color:var(--link)}
.phead{padding:10px 0 24px}
.phead h1{font-size:clamp(26px,3.2vw,34px);letter-spacing:-.01em;margin:0 0 8px}
.phead p{margin:0;color:var(--ink-2);max-width:760px;font-size:17px}
.phead__meta{margin-top:10px;font-size:13px;color:var(--muted)}

/* ---- boʻlim va kartalar ---- */
.sec{padding:28px 0}
.sec--white{background:#fff;border-top:1px solid var(--line);border-bottom:1px solid var(--line)}
.sec__head{display:flex;align-items:end;justify-content:space-between;gap:16px;margin-bottom:16px}
.sec__head h2{font-size:22px;margin:0}
.sec__head a{font-size:14px;font-weight:600;text-decoration:none}
.card{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:20px}
.grid{display:grid;gap:16px}
.grid--2{grid-template-columns:repeat(2,1fr)}
.grid--3{grid-template-columns:repeat(3,1fr)}
.grid--4{grid-template-columns:repeat(4,1fr)}
.split{display:grid;grid-template-columns:1.25fr .75fr;gap:20px;align-items:start}

/* ---- xizmat toifasi kartasi (my.gov.uz uslubi) ---- */
.cat{position:relative;padding:22px 22px 18px}
.cat h3{margin:0 64px 10px 0;font-size:19px}
.cat h3 a{text-decoration:none;color:var(--ink)}
.cat ul{list-style:none;padding:0;margin:0 0 12px}
.cat li{padding:7px 0;border-top:1px solid var(--line-2)}
.cat li:first-child{border-top:0}
.cat li a{text-decoration:none;font-weight:500}
.cat li a:hover{text-decoration:underline}
.cat__all{font-size:14px;font-weight:600;text-decoration:none}
.cat__ico{position:absolute;right:18px;top:18px;width:44px;height:44px;border-radius:50%;background:var(--brand-50);color:var(--brand);display:grid;place-items:center}
.cat__ico svg{width:22px;height:22px}

/* ---- raqamlar ---- */
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}
.stat{padding:18px 20px}
.stat b{display:block;font-size:30px;line-height:1;color:var(--brand);font-variant-numeric:tabular-nums}
.stat span{display:block;margin-top:6px;font-size:14px;color:var(--ink-2)}

/* ---- jadval (reestr) ---- */
.table-wrap{overflow-x:auto;border:1px solid var(--line);border-radius:var(--radius);background:#fff}
.table{width:100%;border-collapse:collapse;font-size:14.5px}
.table th,.table td{padding:10px 12px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
.table tr:last-child td{border-bottom:0}
.table th{background:var(--brand-50);color:var(--brand-700);font-weight:600;font-size:13px;letter-spacing:.02em;white-space:nowrap}
.table td.num{font-variant-numeric:tabular-nums;color:var(--muted);white-space:nowrap}
.table td.nowrap{white-space:nowrap}

/* ---- nishon, ogohlantirish ---- */
.badge{display:inline-block;padding:2px 8px;border-radius:4px;font-size:12px;font-weight:600;background:var(--brand-50);color:var(--brand-700);white-space:nowrap}
.badge--ok{background:var(--ok-50);color:var(--ok)}
.badge--warn{background:var(--warn-50);color:var(--warn)}
.badge--accent{background:var(--accent-100);color:var(--accent-ink)}
.notice{border-left:4px solid var(--accent);background:var(--accent-100);padding:12px 16px;border-radius:0 6px 6px 0;font-size:15px}
.notice--info{border-color:var(--brand);background:var(--brand-50)}
.notice--ok{border-color:var(--ok);background:var(--ok-50)}
.notice--danger{border-color:var(--danger);background:var(--danger-50)}
.notice p:last-child{margin:0}

/* ---- hujjat kartasi ---- */
.doc{display:grid;grid-template-columns:96px 1fr;gap:14px;padding:14px}
.doc__scan{aspect-ratio:3/4;border:1px solid var(--line);background:#fff;overflow:hidden;border-radius:4px;display:block}
.doc__scan img{width:100%;height:100%;object-fit:cover;object-position:top}
.doc__k{font-size:12px;color:var(--muted);text-transform:uppercase;letter-spacing:.05em}
.doc__n{font-weight:600;margin:2px 0}
.doc__s{font-size:14px;color:var(--ink-2)}
.doc__d{font-size:13px;color:var(--muted);margin-top:6px}

/* ---- qadamlar, savollar ---- */
.steps{list-style:none;counter-reset:s;padding:0;margin:0;display:grid;grid-template-columns:repeat(4,1fr);gap:16px}
.steps li{counter-increment:s;padding:18px;font-size:14.5px;color:var(--ink-2)}
.steps li::before{content:counter(s,decimal-leading-zero);display:block;font-size:13px;font-weight:700;color:var(--brand);letter-spacing:.06em;margin-bottom:8px}
.steps b{display:block;margin-bottom:4px;color:var(--ink)}
.faq details{border:1px solid var(--line);border-radius:6px;background:#fff;margin-bottom:8px}
.faq summary{padding:14px 16px;font-weight:600;cursor:pointer;list-style:none;display:flex;justify-content:space-between;gap:12px}
.faq summary::-webkit-details-marker{display:none}
.faq summary::after{content:"+";color:var(--muted);font-weight:400}
.faq details[open] summary::after{content:"–"}
.faq p{margin:0;padding:0 16px 14px;color:var(--ink-2)}

/* ---- forma elementlari, filtr, sahifalash ---- */
.filters{display:flex;flex-wrap:wrap;gap:10px;align-items:end;margin-bottom:14px}
.filters > div{min-width:160px}
.filters label{font-size:13px;color:var(--muted);display:block;margin-bottom:4px}
.input,.select,.textarea{width:100%;padding:9px 12px;border:1px solid var(--line);border-radius:6px;font:inherit;background:#fff;color:var(--ink)}
.input:focus,.select:focus,.textarea:focus{outline:2px solid var(--brand);outline-offset:1px;border-color:var(--brand)}
.textarea{min-height:120px;resize:vertical}
.pager{display:flex;flex-wrap:wrap;gap:6px;margin-top:16px;font-size:14px}
.pager a,.pager span{padding:6px 10px;border:1px solid var(--line);border-radius:4px;background:#fff;text-decoration:none;color:var(--ink)}
.pager [aria-current]{background:var(--brand);color:#fff;border-color:var(--brand)}

/* ---- mutaxassis ---- */
.person{display:flex;gap:14px;padding:14px}
.person img,.person__ph{width:72px;height:90px;flex:none;object-fit:cover;border-radius:4px;border:1px solid var(--line);background:var(--brand-50)}
.person b{display:block}
.person span{display:block;font-size:14px;color:var(--ink-2)}
.person small{display:block;font-size:12.5px;color:var(--muted);margin-top:4px}

/* ---- yangilik, matn ---- */
.news{padding:16px 18px;margin-bottom:10px}
.news time{font-size:12.5px;color:var(--muted)}
.news h3{font-size:16px;margin:4px 0 6px}
.news h3 a{text-decoration:none;color:var(--ink)}
.news p{margin:0;font-size:14.5px;color:var(--ink-2)}
.prose{max-width:760px;font-size:16.5px}
.prose p{margin:0 0 1em}

/* ---- futer ---- */
.ftr{background:var(--brand-700);color:#C9CEE6;margin-top:48px;font-size:14px}
.ftr a{color:#fff;text-decoration:none}
.ftr a:hover{text-decoration:underline}
.ftr__grid{display:grid;grid-template-columns:1.4fr 1fr 1fr 1fr;gap:24px;padding:36px 0}
.ftr__logo{height:56px;width:auto;margin-bottom:12px}
.ftr h4{color:#fff;margin:0 0 10px;font-size:13px;text-transform:uppercase;letter-spacing:.06em}
.ftr ul{list-style:none;margin:0;padding:0}
.ftr li{margin:6px 0}
.ftr__bot{border-top:1px solid rgba(255,255,255,.15);padding:14px 0;display:flex;justify-content:space-between;gap:16px;font-size:13px;flex-wrap:wrap}

/* ---- skan koʻrgich ---- */
.lb{position:fixed;inset:0;background:rgba(10,14,30,.82);display:none;place-items:center;z-index:200;padding:24px;border:0;max-width:none;max-height:none;width:100%;height:100%}
.lb[open]{display:grid}
.lb img{max-height:90vh;max-width:min(900px,95vw);background:#fff}

/* ---- moslashuvchan ---- */
@media (max-width:960px){
  .grid--3,.grid--4,.stats,.steps{grid-template-columns:repeat(2,1fr)}
  .split{grid-template-columns:1fr}
  .ftr__grid{grid-template-columns:1fr 1fr}
  .nav{display:none;position:absolute;left:0;right:0;top:100%;background:#fff;flex-direction:column;padding:8px var(--gut) 16px;border-bottom:1px solid var(--line)}
  .nav.is-open{display:flex}
  .nav-toggle{display:inline-flex;margin-left:auto}
  .hdr .btn--req{display:none}
}
@media (max-width:600px){
  .grid--2,.grid--3,.grid--4,.stats,.steps{grid-template-columns:1fr}
  .ubar__l{display:none}
  .ftr__grid{grid-template-columns:1fr}
  .doc{grid-template-columns:72px 1fr}
  .sec__head{flex-direction:column;align-items:start}
}
```

- [ ] **Step 4: site.js**

`core/static/core/js/site.js`:
```js
/* Sayt JS: menyu, «Maxsus imkoniyatlar» rejimi, skan koʻrgich. Vidjetlar alohida (widgets.js). */
(function () {
  "use strict";
  var root = document.documentElement;

  // --- Maxsus imkoniyatlar: katta shrift + kulrang rejim, localStorage'da saqlanadi
  var A11Y_KEY = "ttt-a11y";
  function applyA11y(on) {
    root.setAttribute("data-a11y", on ? "on" : "off");
    document.querySelectorAll("[data-a11y-toggle]").forEach(function (btn) {
      btn.setAttribute("aria-pressed", on ? "true" : "false");
    });
  }
  var saved = false;
  try { saved = localStorage.getItem(A11Y_KEY) === "on"; } catch (e) { saved = false; }
  applyA11y(saved);
  document.addEventListener("click", function (event) {
    var btn = event.target.closest("[data-a11y-toggle]");
    if (!btn) return;
    var on = root.getAttribute("data-a11y") !== "on";
    applyA11y(on);
    try { localStorage.setItem(A11Y_KEY, on ? "on" : "off"); } catch (e) { /* xususiy rejim */ }
  });

  // --- Mobil menyu
  document.addEventListener("click", function (event) {
    var toggle = event.target.closest("[data-nav-toggle]");
    if (!toggle) return;
    var nav = document.getElementById(toggle.getAttribute("aria-controls"));
    if (!nav) return;
    var open = nav.classList.toggle("is-open");
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
  });

  // --- Skan koʻrgich: <a data-lightbox data-alt="..." href="scan.png">
  var box = document.getElementById("lightbox");
  if (box && typeof box.showModal === "function") {
    var img = box.querySelector("img");
    document.addEventListener("click", function (event) {
      var link = event.target.closest("[data-lightbox]");
      if (link) {
        event.preventDefault();
        img.src = link.getAttribute("href");
        img.alt = link.getAttribute("data-alt") || "";
        box.showModal();
      } else if (event.target === box) {
        box.close();
      }
    });
  }
})();
```

- [ ] **Step 5: _icon.html va _crumbs.html**

`core/templates/core/_icon.html` (`{% include "core/_icon.html" with name="bolt" %}`):
```django
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{% if name == "bolt" %}<path d="M13 2 3 14h7l-1 8 10-12h-7l1-8z"/>{% elif name == "ruler" %}<path d="M3 17 17 3l4 4L7 21H3v-4z"/><path d="m6 14 2 2m1-5 2 2m1-5 2 2m1-5 2 2"/>{% elif name == "file" %}<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6M9 13h6M9 17h6"/>{% elif name == "users" %}<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>{% elif name == "phone" %}<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.6a2 2 0 0 1-.5 2.1L8 9.7a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.8.3 1.7.5 2.6.7a2 2 0 0 1 1.7 2z"/>{% elif name == "check" %}<path d="M20 6 9 17l-5-5"/>{% elif name == "pin" %}<path d="M21 10c0 7-9 13-9 13S3 17 3 10a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>{% endif %}</svg>
```

`core/templates/core/_crumbs.html`:
```django
{% load i18n %}{% if crumbs %}<nav class="crumbs wrap" aria-label="{% translate "Siz bu yerdasiz" %}"><ol>
  <li><a href="{% url 'core:home' %}">{% translate "Bosh sahifa" %}</a></li>
  {% for title, url in crumbs %}<li>{% if url %}<a href="{{ url }}">{{ title }}</a>{% else %}<span aria-current="page">{{ title }}</span>{% endif %}</li>{% endfor %}
</ol></nav>{% endif %}
```

- [ ] **Step 6: base.html**

`core/templates/core/base.html`:
```django
{% load i18n static sitetags %}<!DOCTYPE html>
<html lang="{{ LANGUAGE_CODE }}" data-a11y="off">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{% get_available_languages as langs %}
<title>{% block title %}{{ site|tr:"seo_title" }}{% endblock %}</title>
<meta name="description" content="{% block description %}{{ site|tr:"hero_text"|truncatechars:160 }}{% endblock %}">
<link rel="canonical" href="{{ SITE_URL }}{{ request.path }}">
{% for code, name in langs %}<link rel="alternate" hreflang="{{ code }}" href="{% alt_url request code %}">
{% endfor %}<link rel="alternate" hreflang="x-default" href="{% alt_url request 'uz' %}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="TTT Audit">
<meta property="og:title" content="{% block og_title %}{{ site|tr:"seo_title" }}{% endblock %}">
<meta property="og:description" content="{{ site|tr:"hero_text"|truncatechars:200 }}">
<meta property="og:url" content="{{ SITE_URL }}{{ request.path }}">
<meta property="og:image" content="{{ SITE_URL }}{% static 'core/img/og-image.png' %}">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{% static 'core/css/site.css' %}">
<link rel="stylesheet" href="{% static 'widgets/style.css' %}">
<link rel="icon" type="image/png" sizes="32x32" href="{% static 'core/img/favicon-32.png' %}">
<link rel="apple-touch-icon" href="{% static 'core/img/apple-touch-icon.png' %}">
<script type="application/ld+json">{"@context":"https://schema.org","@type":"ProfessionalService","name":"TTT Audit","legalName":"{{ site|tr:"org_name"|escapejs }}","url":"{{ SITE_URL }}/","logo":"{{ SITE_URL }}{% static 'core/img/logo-full.png' %}","telephone":["{{ site.phone|escapejs }}"{% if site.phone_second %},"{{ site.phone_second|escapejs }}"{% endif %}],"email":"{{ site.email|escapejs }}","taxID":"{{ site.tin|escapejs }}","foundingDate":"{{ site.founded_year }}","address":{"@type":"PostalAddress","streetAddress":"{{ site|tr:"address"|escapejs }}","addressLocality":"Fargʻona","addressCountry":"UZ"}{% if site.map_lat %},"geo":{"@type":"GeoCoordinates","latitude":{{ site.map_lat|stringformat:".5f" }},"longitude":{{ site.map_lng|stringformat:".5f" }}}{% endif %},"areaServed":{"@type":"Country","name":"Uzbekistan"},"knowsLanguage":["uz","ru","en"]}</script>
{% block head %}{% endblock %}
</head>
<body>
<a class="skip" href="#main">{% translate "Asosiy mazmunga oʻtish" %}</a>

<div class="ubar"><div class="wrap">
  <div class="ubar__l">
    <a href="tel:{{ site.phone|cut:' ' }}">{{ site.phone }}</a>
    <a href="mailto:{{ site.email }}">{{ site.email }}</a>
    {% if site|tr:"work_hours" %}<span>{{ site|tr:"work_hours" }}</span>{% endif %}
  </div>
  <div class="ubar__r">
    <button class="a11y-btn" type="button" data-a11y-toggle aria-pressed="false">{% translate "Maxsus imkoniyatlar" %}</button>
    <nav class="lang" aria-label="{% translate "Til" %}">{% for code, name in langs %}<a href="{% alt_url request code %}" hreflang="{{ code }}" lang="{{ code }}"{% if code == LANGUAGE_CODE %} aria-current="true"{% endif %}>{{ code }}</a>{% endfor %}</nav>
  </div>
</div></div>

<header class="hdr"><div class="wrap">
  <a class="logo" href="{% url 'core:home' %}" aria-label="TTT Audit, {% translate "bosh sahifa" %}">
    <img src="{% static 'core/img/logo-mark.png' %}" alt="" width="44" height="44">
    <span class="logo__t"><b>TTT AUDIT</b><span>{{ site|tr:"brand_descriptor" }}</span></span>
  </a>
  <button class="btn btn--ghost btn--sm nav-toggle" type="button" data-nav-toggle aria-expanded="false" aria-controls="nav">{% translate "Menyu" %}</button>
  <nav class="nav" id="nav" aria-label="{% translate "Asosiy menyu" %}">
    <a href="{% url 'core:services' %}"{% if nav == "services" %} aria-current="page"{% endif %}>{% translate "Xizmatlar" %}</a>
    <a href="{% url 'core:registry' %}"{% if nav == "registry" %} aria-current="page"{% endif %}>{% translate "Reestr" %}</a>
    <a href="{% url 'core:credentials' %}"{% if nav == "credentials" %} aria-current="page"{% endif %}>{% translate "Hujjatlar" %}</a>
    <a href="{% url 'core:legislation' %}"{% if nav == "legislation" %} aria-current="page"{% endif %}>{% translate "Qonunchilik" %}</a>
    <a href="{% url 'core:company' %}"{% if nav == "company" %} aria-current="page"{% endif %}>{% translate "Tashkilot" %}</a>
    <a href="{% url 'core:news' %}"{% if nav == "news" %} aria-current="page"{% endif %}>{% translate "Yangiliklar" %}</a>
    <a href="{% url 'core:contact' %}"{% if nav == "contact" %} aria-current="page"{% endif %}>{% translate "Aloqa" %}</a>
  </nav>
  <a class="btn btn--sm btn--req" href="{% url 'core:request' %}">{% translate "Murojaat yuborish" %}</a>
</div></header>

{% include "core/_crumbs.html" %}
<main id="main">{% block main %}{% endblock %}</main>

<footer class="ftr"><div class="wrap">
  <div class="ftr__grid">
    <div>
      <img class="ftr__logo" src="{% static 'core/img/logo-full-white.png' %}" alt="TTT Audit">
      <p>{{ site|tr:"org_name" }}<br>{{ site|tr:"address" }}</p>
      <p>{% translate "STIR" %} {{ site.tin }}</p>
    </div>
    <div><h4>{% translate "Xizmatlar" %}</h4><ul>{% for d in nav_directions %}<li><a href="{{ d.get_absolute_url }}">{{ d|tr:"title" }}</a></li>{% endfor %}<li><a href="{% url 'core:registry' %}">{% translate "Bajarilgan ishlar reestri" %}</a></li></ul></div>
    <div><h4>{% translate "Tashkilot" %}</h4><ul>
      <li><a href="{% url 'core:company' %}">{% translate "Tashkilot haqida" %}</a></li>
      <li><a href="{% url 'core:team' %}">{% translate "Rahbariyat va mutaxassislar" %}</a></li>
      <li><a href="{% url 'core:credentials' %}">{% translate "Litsenziya va sertifikatlar" %}</a></li>
      <li><a href="{% url 'core:instruments' %}">{% translate "Oʻlchov asboblari" %}</a></li>
      <li><a href="{% url 'core:legislation' %}">{% translate "Qonunchilik" %}</a></li>
      <li><a href="{% url 'core:requisites' %}">{% translate "Rekvizitlar" %}</a></li>
    </ul></div>
    <div><h4>{% translate "Aloqa" %}</h4><ul>
      <li><a href="tel:{{ site.phone|cut:' ' }}">{{ site.phone }}</a></li>
      {% if site.phone_second %}<li><a href="tel:{{ site.phone_second|cut:' ' }}">{{ site.phone_second }}</a></li>{% endif %}
      <li><a href="mailto:{{ site.email }}">{{ site.email }}</a></li>
      <li><a href="{% url 'core:request' %}">{% translate "Murojaat yuborish" %}</a></li>
    </ul></div>
  </div>
  <div class="ftr__bot"><span>© {% now "Y" %} {{ site|tr:"org_name" }}</span><span>{% translate "Ekspert tashkiloti, 1997-yildan" %}</span></div>
</div></footer>

<dialog class="lb" id="lightbox" aria-label="{% translate "Hujjat skani" %}"><img src="" alt=""></dialog>
<script src="{% static 'core/js/site.js' %}" defer></script>
<script type="module" src="{% static 'widgets/widgets.js' %}"></script>
</body>
</html>
```

`core/templates/core/404.html`:
```django
{% extends "core/base.html" %}{% load i18n %}
{% block title %}{% translate "Sahifa topilmadi" %} — TTT Audit{% endblock %}
{% block main %}<div class="wrap"><div class="phead"><h1>{% translate "Sahifa topilmadi" %}</h1><p>{% translate "Manzil oʻzgargan yoki notoʻgʻri terilgan boʻlishi mumkin." %}</p></div><p><a class="btn" href="{% url 'core:home' %}">{% translate "Bosh sahifaga" %}</a></p></div>{% endblock %}
```

- [ ] **Step 7: views.py yordamchilari, vaqtinchalik home, toʻliq URL nomlari**

`core/views.py`:
```python
"""Barcha sahifalar serverda render qilinadi. React faqat [data-react] orollari uchun."""
import json

from django.conf import settings
from django.shortcuts import render

from . import compliance, energy
from .models import Direction


def page(request, template, nav="", crumbs=(), **context):
    """Umumiy render: `nav` — faol menyu kaliti, `crumbs` — [(sarlavha, url|None), ...]."""
    context.update({"nav": nav, "crumbs": list(crumbs)})
    return render(request, template, context)


def form_context():
    """Murojaat formasi vidjeti uchun umumiy kontekst."""
    directions = list(Direction.objects.all())
    return {
        "form_directions": directions,
        "form_directions_json": json.dumps(
            [{"id": d.pk, "title": d.tr("title"), "accent": d.accent, "slug": d.slug} for d in directions],
            ensure_ascii=False,
        ),
        "max_upload_mb": settings.LEAD_MAX_UPLOAD_BYTES // (1024 * 1024),
    }


def compliance_context():
    return {"compliance": {
        "passport_area": compliance.PASSPORT_AREA_M2,
        "registry_kwh": compliance.REGISTRY_KWH,
        "registry_gas": compliance.REGISTRY_GAS_M3,
        "periodic_years": compliance.PERIODIC_YEARS,
    }}


def energy_context():
    ladder = energy.ladder()
    return {
        "energy_ladder": ladder,
        "energy_ladder_json": json.dumps(ladder, ensure_ascii=False),
        "passport_threshold": energy.PASSPORT_AREA_THRESHOLD_M2,
    }


def home(request):
    return page(request, "core/base.html")
```
`core/urls.py` (barcha nomlar hozirdan — `{% url %}` teglari uchun; keyingi tasklar `views.home` oʻrniga oʻz funksiyasini qoʻyadi):
```python
from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("xizmatlar/", views.home, name="services"),
    path("xizmatlar/<slug:direction_slug>/", views.home, name="direction"),
    path("xizmatlar/<slug:direction_slug>/<slug:slug>/", views.home, name="service"),
    path("reestr/", views.home, name="registry"),
    path("hujjatlar/", views.home, name="credentials"),
    path("qonunchilik/", views.home, name="legislation"),
    path("yangiliklar/", views.home, name="news"),
    path("yangiliklar/<slug:slug>/", views.home, name="post"),
    path("tashkilot/", views.home, name="company"),
    path("tashkilot/mutaxassislar/", views.home, name="team"),
    path("tashkilot/asboblar/", views.home, name="instruments"),
    path("tashkilot/rekvizitlar/", views.home, name="requisites"),
    path("aloqa/", views.home, name="contact"),
    path("murojaat/", views.home, name="request"),
]
```

- [ ] **Step 8: Test oʻtadi, brauzerda koʻrish, commit**

```bash
PYTHONIOENCODING=utf-8 pytest -q core/tests/test_base.py
python manage.py runserver 8000   # http://127.0.0.1:8000/uz/ — panel, sarlavha, futer koʻrinadi (widgets 404 hozircha normal)
git add -A && git commit -m "feat: davlat portali dizayn tizimi, asosiy shablon, 404"
```

---

### Task 4: Bosh sahifa

**Files:**
- Modify: `core/views.py` (`home`, `HOME_FAQ`), `core/static/core/css/site.css` (hero qoʻshimchasi)
- Create: `core/templates/core/home.html`, `core/templates/core/_compliance.html`
- Test: `core/tests/test_pages.py`

**Interfaces:**
- Consumes: Task 3 `page()`, `compliance_context()`, `form_context()`; Task 1 maʼlumoti.
- Produces: `_compliance.html` (talab tekshiruvchi oroli, `compliance` kontekst kaliti bilan) — Task 5 ham ishlatadi; `HOME_FAQ` roʻyxati.

- [ ] **Step 1: Yozilmagan test**

`core/tests/test_pages.py` (keyingi tasklar shu faylga qoʻshadi):
```python
import pytest


@pytest.mark.django_db
def test_home_renders_gov_style_sections(client):
    response = client.get("/uz/")
    assert response.status_code == 200
    html = response.content.decode()
    assert "Energoaudit va qurilishda nazorat oʻlchovi" in html      # hero H1
    assert "Vakolat hujjatlari" in html                               # litsenziya bloki
    assert 'data-react="compliance-check"' in html                    # talab tekshiruvchi
    assert "Bajarilgan ishlar reestri" in html
    assert "Koʻp soʻraladigan savollar" in html
    assert "№ 518159" in html                                         # qurilish litsenziyasi raqami
    assert "moliyaviy audit" not in html.lower()
    assert "REPER" not in html


@pytest.mark.django_db
def test_home_ru_and_en_render(client):
    assert client.get("/ru/").status_code == 200
    assert "Энергоаудит".encode() in client.get("/ru/").content
    assert client.get("/en/").status_code == 200


@pytest.mark.django_db
def test_root_redirects_to_uz(client):
    response = client.get("/")
    assert response.status_code == 302
    assert response["Location"].startswith("/uz/")
```

- [ ] **Step 2: Test — muvaffaqiyatsizlik**

Run: `PYTHONIOENCODING=utf-8 pytest -q core/tests/test_pages.py` → `assert "Vakolat hujjatlari" in html` FAIL.

- [ ] **Step 3: views.home**

`core/views.py` — importlarni kengaytiring va `home` ni almashtiring:
```python
from django.utils.translation import gettext_lazy as _

from .models import Credential, Direction, Post, Project, Stat

HOME_FAQ = [
    (_("Energoaudit kimga majburiy?"),
     _("ЗРУ-940 ga koʻra davriy energoaudit majburiy tartibda besh yilda kamida bir marta oʻtkaziladi. "
       "Davlat energetika reestriga kiritilgan korxonalar va davlat ishtirokidagi tashkilotlar uchun "
       "audit majburiy; boshqalar uchun ixtiyoriy.")),
    (_("Qaysi binolarga energosamaradorlik toifasi belgilanadi?"),
     _("Foydalaniladigan maydoni 200 m² dan katta bino va inshootlarga. Energopasport yangi, mavjud, "
       "rekonstruksiya va modernizatsiya qilinayotgan obyektlar uchun rasmiylashtiriladi.")),
    (_("Nazorat oʻlchovi uchun qurilishni toʻxtatish kerakmi?"),
     _("Yoʻq. Oʻlchov ish jarayoniga xalaqit bermaydi; yashirin ishlar yopilishidan oldin qayd etiladi.")),
    (_("Ishlab chiqarishni toʻxtatmasdan energoaudit qilsa boʻladimi?"),
     _("Ha — aksincha, oʻlchovlar real ish rejimida olinishi kerak.")),
    (_("Hujjatlarimiz uchinchi shaxsga beriladimi?"),
     _("Yoʻq. Hujjatlar faqat shartnoma doirasida ishlatiladi; axborot xavfsizligi tizimi ISO 27001:2022 "
       "boʻyicha sertifikatlangan.")),
]


def home(request):
    context = {
        "directions": Direction.objects.prefetch_related("services").all(),
        "stats": Stat.objects.all(),
        "hero_credentials": Credential.objects.filter(show_in_hero=True),
        "projects": Project.objects.select_related("direction").exclude(year__isnull=True)[:8],
        "posts": Post.objects.filter(is_published=True)[:3],
        "faq": [{"q": q, "a": a} for q, a in HOME_FAQ],
    }
    context.update(compliance_context())
    return page(request, "core/home.html", **context)
```

- [ ] **Step 4: _compliance.html**

`core/templates/core/_compliance.html` (`compliance` kaliti `compliance_context()` dan):
```django
{% load i18n %}<div data-react="compliance-check" data-endpoint="{% url 'core:compliance_check' %}" data-request-url="{% url 'core:request' %}">
  <p>{% translate "Uch savolga javob bering — obyektingizga qaysi talab tegishli ekanini, muddatini va qonuniy asosini koʻrasiz." %}</p>
  <ul>
    <li>{% blocktranslate with kwh=compliance.registry_kwh gas=compliance.registry_gas %}Yillik isteʼmol {{ kwh }} kVt·soat elektr yoki {{ gas }} m³ gazdan oshsa — Davlat energetika reestri subyekti, davriy energoaudit majburiy.{% endblocktranslate %}</li>
    <li>{% blocktranslate with years=compliance.periodic_years %}Davriy energoaudit — {{ years }} yilda kamida bir marta (ЗРУ-940).{% endblocktranslate %}</li>
    <li>{% blocktranslate with area=compliance.passport_area %}Foydalaniladigan maydoni {{ area }} m² dan katta binoga energosamaradorlik toifasi va energopasport belgilanadi.{% endblocktranslate %}</li>
    <li>{% translate "Byudjet mablagʻi hisobiga qurilishda bajarilgan hajm nazorat oʻlchovidan oʻtadi; xizmat haqi qurilish qiymatining 0,3% dan oshmaydi." %}</li>
  </ul>
  <a class="btn btn--ghost btn--sm" href="{% url 'core:request' %}">{% translate "Muhandisdan soʻrash" %}</a>
</div>
```
(`core:compliance_check` URL nomi Task 10 da qoʻshiladi; hozircha `core/urls.py` ga vaqtinchalik `path("api/compliance/", views.home, name="compliance_check")` qoʻshing.)

- [ ] **Step 5: home.html**

```django
{% extends "core/base.html" %}{% load i18n static sitetags %}
{% block main %}
<section class="hero"><div class="wrap">
  <div>
    <div class="hero__k">{{ site|tr:"hero_kicker" }}</div>
    <h1>{{ site|tr:"hero_title" }}</h1>
    <p>{{ site|tr:"hero_text" }}</p>
    <div class="hero__cta">
      <a class="btn" href="{% url 'core:request' %}">{% translate "Murojaat yuborish" %}</a>
      <a class="btn btn--ghost" href="#talab">{% translate "Qaysi talab tegishli?" %}</a>
    </div>
  </div>
  <aside class="hero__side">
    <h2>{% translate "Vakolat hujjatlari" %}</h2>
    <ul>{% for c in hero_credentials %}<li><div><b>{{ c.get_kind_display }} {{ c.number }}</b><span>{{ c|tr:"issuer" }}{% if c.valid_until %} · {% translate "amal qiladi" %} {{ c.valid_until|date:"d.m.Y" }}{% elif c.kind == "license" %} · {% translate "muddatsiz" %}{% endif %}</span></div></li>{% endfor %}</ul>
    <a class="cat__all" href="{% url 'core:credentials' %}">{% translate "Barcha hujjatlar" %} →</a>
  </aside>
</div></section>

<section class="sec"><div class="wrap">
  <div class="sec__head"><h2>{% translate "Xizmatlar" %}</h2><a href="{% url 'core:services' %}">{% translate "Barchasi" %} →</a></div>
  <div class="grid grid--2">
  {% for d in directions %}
    <article class="card cat">
      <span class="cat__ico">{% if d.accent == "amber" %}{% include "core/_icon.html" with name="bolt" %}{% else %}{% include "core/_icon.html" with name="ruler" %}{% endif %}</span>
      <h3><a href="{{ d.get_absolute_url }}">{{ d|tr:"title" }}</a></h3>
      <ul>{% for s in d.services.all %}<li><a href="{{ s.get_absolute_url }}">{{ s|tr:"title" }}</a></li>{% endfor %}</ul>
      <a class="cat__all" href="{{ d.get_absolute_url }}">{% translate "Barchasi" %} →</a>
    </article>
  {% endfor %}
  </div>
</div></section>

<section class="sec"><div class="wrap"><div class="stats">
  {% for s in stats %}<div class="card stat"><b>{{ s.value }}</b><span>{{ s|tr:"label" }}</span></div>{% endfor %}
</div></div></section>

<section class="sec sec--white" id="talab"><div class="wrap">
  <div class="sec__head"><h2>{% translate "Obyektingizga qaysi talab tegishli?" %}</h2></div>
  <div class="split">
    <div class="card">{% include "core/_compliance.html" %}</div>
    <div class="notice notice--info"><p><b>{% translate "Asos" %}:</b> ЗРУ-940 «{% translate "Energiyani tejash, undan oqilona foydalanish va energiya samaradorligini oshirish toʻgʻrisida" %}», {% translate "VM qarori" %} № 690. {% translate "Natija yoʻnaltiruvchi hisob, rasmiy xulosa emas — aniq talab va muddat hujjatlaringiz asosida tasdiqlanadi." %}</p><p><a href="{% url 'core:legislation' %}">{% translate "Meʼyoriy hujjatlar" %} →</a></p></div>
  </div>
</div></section>

<section class="sec"><div class="wrap">
  <div class="sec__head"><h2>{% translate "Bajarilgan ishlar reestri" %}</h2><a href="{% url 'core:registry' %}">{% translate "Toʻliq reestr" %} →</a></div>
  <div class="table-wrap"><table class="table">
    <thead><tr><th>№</th><th>{% translate "Ish" %}</th><th>{% translate "Buyurtmachi" %}</th><th>{% translate "Yoʻnalish" %}</th><th>{% translate "Yil" %}</th></tr></thead>
    <tbody>{% for p in projects %}<tr><td class="num">{{ forloop.counter }}</td><td>{{ p|tr:"title" }}</td><td>{{ p.client }}</td><td><span class="badge">{{ p.direction|tr:"title" }}</span></td><td class="num">{{ p.year }}</td></tr>{% endfor %}</tbody>
  </table></div>
</div></section>

<section class="sec"><div class="wrap">
  <div class="sec__head"><h2>{% translate "Ish tartibi" %}</h2></div>
  <ol class="steps">
    <li class="card"><b>{% translate "Murojaat va suhbat" %}</b>{% translate "Obyekt, maqsad va muddatni aniqlaymiz, qaysi talab tegishli ekanini aytamiz." %}</li>
    <li class="card"><b>{% translate "Hujjatlar" %}</b>{% translate "Loyiha-smeta, dalolatnomalar yoki isteʼmol maʼlumotlari — roʻyxatni oldindan beramiz." %}</li>
    <li class="card"><b>{% translate "Obyektda oʻlchov" %}</b>{% translate "Oʻlchov va koʻrik tomonlar ishtirokida, qiyoslangan asboblar bilan." %}</li>
    <li class="card"><b>{% translate "Xulosa" %}</b>{% translate "Dalolatnoma, energopasport yoki ekspert xulosasi — imzo va muhr bilan." %}</li>
  </ol>
</div></section>

<section class="sec"><div class="wrap"><div class="grid grid--2">
  <div>
    <div class="sec__head"><h2>{% translate "Yangiliklar va tushuntirishlar" %}</h2><a href="{% url 'core:news' %}">{% translate "Barchasi" %} →</a></div>
    {% for p in posts %}<article class="card news"><time datetime="{{ p.published_on|date:'Y-m-d' }}">{{ p.published_on|date:"d.m.Y" }}</time><h3><a href="{{ p.get_absolute_url }}">{{ p|tr:"title" }}</a></h3><p>{{ p|tr:"excerpt" }}</p></article>{% empty %}<p class="muted">{% translate "Hozircha yangiliklar yoʻq." %}</p>{% endfor %}
  </div>
  <div>
    <div class="sec__head"><h2>{% translate "Koʻp soʻraladigan savollar" %}</h2></div>
    <div class="faq">{% for f in faq %}<details><summary>{{ f.q }}</summary><p>{{ f.a }}</p></details>{% endfor %}</div>
  </div>
</div></div></section>

<section class="sec"><div class="wrap"><div class="card contact-strip">
  <div><span class="doc__k">{% translate "Bosh ofis" %}</span><b>{{ site|tr:"address" }}</b></div>
  <div><span class="doc__k">{% translate "Telefon" %}</span><b><a href="tel:{{ site.phone|cut:' ' }}">{{ site.phone }}</a></b></div>
  <div><span class="doc__k">{% translate "E-pochta" %}</span><b><a href="mailto:{{ site.email }}">{{ site.email }}</a></b></div>
  <a class="btn" href="{% url 'core:contact' %}">{% translate "Aloqa va xarita" %}</a>
</div></div></section>
{% endblock %}
```

- [ ] **Step 6: site.css qoʻshimchasi (bosh sahifa)**

`site.css` oxiriga (`/* ---- moslashuvchan ---- */` dan OLDIN) qoʻshing:
```css
/* ---- bosh sahifa ---- */
.hero{background:#fff;border-bottom:1px solid var(--line)}
.hero .wrap{display:grid;grid-template-columns:1.3fr 1fr;gap:40px;padding-top:40px;padding-bottom:40px;align-items:center}
.hero__k{font-size:13px;text-transform:uppercase;letter-spacing:.08em;color:var(--brand);font-weight:600}
.hero h1{font-size:clamp(28px,3.6vw,40px);line-height:1.15;margin:10px 0 14px;letter-spacing:-.01em}
.hero p{font-size:17px;color:var(--ink-2);margin:0 0 22px;max-width:620px}
.hero__cta{display:flex;gap:10px;flex-wrap:wrap}
.hero__side{border:1px solid var(--line);border-radius:var(--radius);background:var(--bg);padding:18px}
.hero__side h2{font-size:13px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);margin:0 0 10px}
.hero__side ul{list-style:none;margin:0 0 10px;padding:0}
.hero__side li{padding:9px 0;border-top:1px solid var(--line)}
.hero__side li:first-child{border-top:0;padding-top:0}
.hero__side b{font-size:14px;display:block}
.hero__side span{font-size:13px;color:var(--muted);display:block}
.contact-strip{display:grid;grid-template-columns:1.4fr 1fr 1fr auto;gap:20px;align-items:center}
.contact-strip b{display:block;font-size:15px}
```
va `@media (max-width:960px)` blokiga `.hero .wrap{grid-template-columns:1fr}.contact-strip{grid-template-columns:1fr 1fr}` va `@media (max-width:600px)` ga `.contact-strip{grid-template-columns:1fr}` qoʻshing.

- [ ] **Step 7: Test oʻtadi, brauzerda koʻrish, commit**

```bash
PYTHONIOENCODING=utf-8 pytest -q
python manage.py runserver 8000   # /uz/ — hero, 2 toifa kartasi, raqamlar, reestr jadvali, FAQ
git add -A && git commit -m "feat: bosh sahifa — vakolat hujjatlari, xizmat toifalari, reestr, talab tekshiruvchi oroli"
```

---

### Task 5: Xizmatlar — hub, yoʻnalish va xizmat sahifalari

**Files:**
- Modify: `core/views.py` (`services`, `direction`, `service`), `core/urls.py`
- Create: `core/templates/core/{services.html, direction.html, service.html, _energy.html}`
- Test: `core/tests/test_pages.py` (qoʻshimcha)

**Interfaces:**
- Consumes: `page()`, `compliance_context()`, `energy_context()`, `_compliance.html`.
- Produces: `_energy.html` (energiya baholagich oroli); URL `core:services`, `core:direction`, `core:service` haqiqiy view'lar bilan.

- [ ] **Step 1: Yozilmagan test**

`core/tests/test_pages.py` ga qoʻshing:
```python
@pytest.mark.django_db
def test_services_hub_lists_both_directions(client):
    html = client.get("/uz/xizmatlar/").content.decode()
    assert "Energosamaradorlik auditi" in html
    assert "Qurilishda nazorat oʻlchovi" in html
    assert html.count('class="card cat"') == 2


@pytest.mark.django_db
def test_energy_direction_has_widgets_and_legal_basis(client):
    response = client.get("/uz/xizmatlar/energoaudit/")
    assert response.status_code == 200
    html = response.content.decode()
    assert 'data-react="compliance-check"' in html
    assert 'data-react="energy-estimator"' in html
    assert "ЗРУ-940" in html


@pytest.mark.django_db
def test_construction_direction_lists_instruments(client):
    html = client.get("/uz/xizmatlar/olchov-auditi/").content.decode()
    assert "SNOWAY SW-M100" in html
    assert 'data-react="energy-estimator"' not in html


@pytest.mark.django_db
def test_service_page_and_404(client):
    response = client.get("/uz/xizmatlar/olchov-auditi/nazorat-olchovi/")
    assert response.status_code == 200
    assert "Nazorat oʻlchovi".encode() in response.content
    assert client.get("/uz/xizmatlar/olchov-auditi/yoq-xizmat/").status_code == 404
```

- [ ] **Step 2: Test — muvaffaqiyatsizlik**

Run: `PYTHONIOENCODING=utf-8 pytest -q core/tests/test_pages.py` → `test_services_hub_lists_both_directions` FAIL.

- [ ] **Step 3: view'lar**

`core/views.py` ga (`from django.shortcuts import get_object_or_404, render`; `from .models import ... Instrument, LegalAct, Service`; `from django.urls import reverse`):
```python
def services(request):
    return page(
        request, "core/services.html", nav="services",
        crumbs=[(_("Xizmatlar"), None)],
        directions=Direction.objects.prefetch_related("services").all(),
    )


def direction(request, direction_slug):
    obj = get_object_or_404(Direction.objects.prefetch_related("services", "legal_acts"), slug=direction_slug)
    is_energy = obj.accent == Direction.ACCENT_AMBER
    context = {
        "direction": obj,
        "is_energy": is_energy,
        "services": obj.services.all(),
        "legal_acts": obj.legal_acts.filter(verified_on__isnull=False),
        "projects": obj.projects.exclude(year__isnull=True)[:6],
        "instruments": Instrument.objects.all() if not is_energy else [],
        "project_total": obj.projects.count(),
    }
    if is_energy:
        context.update(compliance_context())
        context.update(energy_context())
    return page(
        request, "core/direction.html", nav="services",
        crumbs=[(_("Xizmatlar"), reverse("core:services")), (obj.tr("title"), None)],
        **context,
    )


def service(request, direction_slug, slug):
    obj = get_object_or_404(Service.objects.select_related("direction"), direction__slug=direction_slug, slug=slug)
    return page(
        request, "core/service.html", nav="services",
        crumbs=[(_("Xizmatlar"), reverse("core:services")),
                (obj.direction.tr("title"), obj.direction.get_absolute_url()), (obj.tr("title"), None)],
        service=obj, direction=obj.direction,
        siblings=obj.direction.services.exclude(pk=obj.pk),
        legal_acts=obj.direction.legal_acts.filter(verified_on__isnull=False),
    )
```
`core/urls.py` da `services`, `direction`, `service` yoʻllarini shu view'larga ulang.

- [ ] **Step 4: services.html**

```django
{% extends "core/base.html" %}{% load i18n sitetags %}
{% block title %}{% translate "Xizmatlar" %} — TTT Audit{% endblock %}
{% block description %}{% translate "Energoaudit, bino energopasporti, qurilishda nazorat oʻlchovi, smeta ekspertizasi va texnik nazorat — Oʻzbekiston boʻylab." %}{% endblock %}
{% block main %}<div class="wrap">
<div class="phead"><h1>{% translate "Xizmatlar" %}</h1><p>{% translate "Ikki yoʻnalish: energiya isteʼmolini tekshirish va qurilishda bajarilgan ish hajmini oʻlchash. Ikkalasi ham davlat hujjati bilan tasdiqlangan vakolat asosida." %}</p></div>
<div class="grid grid--2">
{% for d in directions %}
  <article class="card cat">
    <span class="cat__ico">{% if d.accent == "amber" %}{% include "core/_icon.html" with name="bolt" %}{% else %}{% include "core/_icon.html" with name="ruler" %}{% endif %}</span>
    <h3><a href="{{ d.get_absolute_url }}">{{ d|tr:"title" }}</a></h3>
    <p class="muted">{{ d|tr:"summary" }}</p>
    <ul>{% for s in d.services.all %}<li><a href="{{ s.get_absolute_url }}">{{ s|tr:"title" }}</a><br><small class="muted">{{ s|tr:"summary" }}</small></li>{% endfor %}</ul>
    <a class="cat__all" href="{{ d.get_absolute_url }}">{% translate "Yoʻnalish sahifasi" %} →</a>
  </article>
{% endfor %}
</div>
<div class="sec"><div class="notice"><p>{% translate "Qaysi xizmat kerakligini bilmaysizmi? Obyekt haqida qisqacha yozing — muhandis qaysi talab tegishli ekanini birinchi suhbatda aytadi." %} <a href="{% url 'core:request' %}">{% translate "Murojaat yuborish" %} →</a></p></div></div>
</div>{% endblock %}
```

- [ ] **Step 5: _energy.html va direction.html**

`core/templates/core/_energy.html` (`energy_context()` kalitlari):
```django
{% load i18n %}<div data-react="energy-estimator" data-endpoint="{% url 'core:energy_estimate' %}" data-ladder="{{ energy_ladder_json }}" data-threshold="{{ passport_threshold }}">
  <p>{% translate "Bino maydoni va yillik elektr isteʼmoli boʻyicha dastlabki energosamaradorlik toifasi (A–G)." %}</p>
  <table class="table"><thead><tr><th>{% translate "Toifa" %}</th><th>{% translate "Solishtirma isteʼmol, kVt·soat/m²·yil" %}</th></tr></thead>
  <tbody>{% for b in energy_ladder %}<tr><td><span class="badge">{{ b.letter }}</span></td><td class="num">{{ b.label }}</td></tr>{% endfor %}</tbody></table>
  <p class="muted"><small>{% translate "Chegaralar yoʻnaltiruvchi; rasmiy toifa energopasportda belgilanadi." %}</small></p>
</div>
```
(`core:energy_estimate` — Task 10; hozircha `core/urls.py` ga `path("api/energy-estimate/", views.home, name="energy_estimate")`.)

`core/templates/core/direction.html`:
```django
{% extends "core/base.html" %}{% load i18n sitetags %}
{% block title %}{{ direction|tr:"title" }} — TTT Audit{% endblock %}
{% block description %}{{ direction|tr:"summary" }}{% endblock %}
{% block main %}<div class="wrap">
<div class="phead"><h1>{{ direction|tr:"title" }}</h1><p>{{ direction|tr:"summary" }}</p>
  <div class="phead__meta">{% if is_energy %}{% translate "Vakolat: Energosamaradorlik milliy agentligi reestri (VM qarori № 673), 24 mutaxassis" %}{% else %}{% translate "Vakolat: Qurilish vazirligi litsenziyasi № 518159, 16 mutaxassis" %}{% endif %}</div></div>

<div class="grid grid--2">
{% for s in services %}<article class="card"><h3><a href="{{ s.get_absolute_url }}">{{ s|tr:"title" }}</a></h3><p class="muted">{{ s|tr:"summary" }}</p>{% if s|tr:"duration" %}<span class="badge">{{ s|tr:"duration" }}</span>{% endif %}</article>{% endfor %}
</div>

{% if direction|tr:"problem_title" %}<section class="sec"><div class="split">
  <div class="card prose"><h2>{{ direction|tr:"problem_title" }}</h2>{{ direction|tr:"problem_body"|linebreaks }}</div>
  <div>
    {% if legal_acts %}<div class="card"><h3>{% translate "Meʼyoriy asos" %}</h3><ul>{% for a in legal_acts %}<li><b>{{ a.number }}</b> — {{ a|tr:"title" }}{% if a.lex_url %} <a href="{{ a.lex_url }}" rel="noopener" target="_blank">lex.uz</a>{% endif %}</li>{% endfor %}</ul></div>{% endif %}
    {% if direction|tr:"legal_note" %}<div class="notice notice--info"><p>{{ direction|tr:"legal_note" }}</p></div>{% endif %}
  </div>
</div></section>{% endif %}

{% if is_energy %}
<section class="sec" id="talab"><div class="sec__head"><h2>{% translate "Obyektingizga qaysi talab tegishli?" %}</h2></div><div class="split"><div class="card">{% include "core/_compliance.html" %}</div><div class="card">{% include "core/_energy.html" %}</div></div></section>
{% else %}
<section class="sec"><div class="sec__head"><h2>{% translate "Oʻlchov asboblari va qiyoslash" %}</h2><a href="{% url 'core:instruments' %}">{% translate "Toʻliq roʻyxat" %} →</a></div>
<div class="table-wrap"><table class="table"><thead><tr><th>{% translate "Asbob" %}</th><th>{% translate "Oʻlchov chegarasi" %}</th><th>{% translate "Guvohnoma" %}</th><th>{% translate "Amal qiladi" %}</th></tr></thead>
<tbody>{% for i in instruments %}<tr><td>{{ i|tr:"name" }}</td><td>{{ i|tr:"range" }}</td><td class="nowrap">{{ i.certificate_no }}</td><td class="num">{{ i.valid_until|date:"d.m.Y" }}</td></tr>{% endfor %}</tbody></table></div></section>
{% endif %}

{% if direction.deliverables %}<section class="sec"><div class="sec__head"><h2>{% translate "Natijada olasiz" %}</h2></div><div class="grid grid--3">{% for item in direction|tr_list:"deliverables" %}<div class="card">{% include "core/_icon.html" with name="check" %} {{ item }}</div>{% endfor %}</div></section>{% endif %}

<section class="sec"><div class="sec__head"><h2>{% translate "Bajarilgan ishlar" %} — {{ project_total }}</h2><a href="{% url 'core:registry' %}?d={{ direction.slug }}">{% translate "Reestrda koʻrish" %} →</a></div>
<div class="table-wrap"><table class="table"><thead><tr><th>№</th><th>{% translate "Ish" %}</th><th>{% translate "Buyurtmachi" %}</th><th>{% translate "Yil" %}</th></tr></thead>
<tbody>{% for p in projects %}<tr><td class="num">{{ forloop.counter }}</td><td>{{ p|tr:"title" }}</td><td>{{ p.client }}</td><td class="num">{{ p.year }}</td></tr>{% endfor %}</tbody></table></div></section>

<section class="sec"><div class="notice"><p>{% translate "Obyekt haqida qisqacha yozing — muhandis qaysi talab tegishli ekanini va ish hajmini birinchi suhbatda aniqlaydi." %} <a href="{% url 'core:request' %}">{% translate "Murojaat yuborish" %} →</a></p></div></section>
</div>{% endblock %}
```

- [ ] **Step 6: service.html**

```django
{% extends "core/base.html" %}{% load i18n sitetags %}
{% block title %}{{ service|tr:"title" }} — {{ direction|tr:"title" }} — TTT Audit{% endblock %}
{% block description %}{{ service|tr:"summary" }}{% endblock %}
{% block main %}<div class="wrap">
<div class="phead"><h1>{{ service|tr:"title" }}</h1><p>{{ service|tr:"summary" }}</p>{% if service|tr:"duration" %}<div class="phead__meta">{% translate "Muddat" %}: {{ service|tr:"duration" }}</div>{% endif %}</div>
<div class="split">
  <div>
    {% if service|tr:"body" %}<div class="card prose">{{ service|tr:"body"|linebreaks }}</div>{% endif %}
    {% if service.process %}<section class="sec"><div class="sec__head"><h2>{% translate "Ish tartibi" %}</h2></div><ol class="steps steps--col">{% for step in service|tr_list:"process" %}<li class="card">{{ step }}</li>{% endfor %}</ol></section>{% endif %}
    {% if service.faq %}<section class="sec"><div class="sec__head"><h2>{% translate "Savollar" %}</h2></div><div class="faq">{% for f in service.faq_pairs %}<details><summary>{{ f.q }}</summary><p>{{ f.a }}</p></details>{% endfor %}</div></section>{% endif %}
  </div>
  <aside>
    {% if service.deliverables %}<div class="card"><h3>{% translate "Natijada olasiz" %}</h3><ul>{% for item in service|tr_list:"deliverables" %}<li>{{ item }}</li>{% endfor %}</ul></div>{% endif %}
    {% if legal_acts %}<div class="card"><h3>{% translate "Meʼyoriy asos" %}</h3><ul>{% for a in legal_acts %}<li><b>{{ a.number }}</b> — {{ a|tr:"title" }}</li>{% endfor %}</ul><a href="{% url 'core:legislation' %}">{% translate "Qonunchilik" %} →</a></div>{% endif %}
    <div class="card"><h3>{% translate "Shu yoʻnalishdagi boshqa xizmatlar" %}</h3><ul>{% for s in siblings %}<li><a href="{{ s.get_absolute_url }}">{{ s|tr:"title" }}</a></li>{% endfor %}</ul></div>
    <a class="btn" href="{% url 'core:request' %}">{% translate "Murojaat yuborish" %}</a>
  </aside>
</div>
</div>{% endblock %}
```
`site.css` ga: `.steps--col{grid-template-columns:1fr}`.

- [ ] **Step 7: Test oʻtadi va commit**

```bash
PYTHONIOENCODING=utf-8 pytest -q
git add -A && git commit -m "feat: xizmatlar hub, ikki yoʻnalish va 8 xizmat sahifasi"
```

---

### Task 6: Bajarilgan ishlar reestri

**Files:**
- Modify: `core/views.py` (`registry`), `core/urls.py`
- Create: `core/templates/core/registry.html`
- Test: `core/tests/test_pages.py` (qoʻshimcha)

**Interfaces:**
- Consumes: `Project` (143), `qs_replace` tegi.
- Produces: `/reestr/?d=<slug>&y=<yil>&q=<matn>&page=<n>` — 25 tadan, yil kamayish tartibida, yili yoʻqlar oxirida.

- [ ] **Step 1: Yozilmagan test**

```python
@pytest.mark.django_db
def test_registry_paginates_and_filters(client):
    html = client.get("/uz/reestr/").content.decode()
    assert "143" in html                                   # jami soni sarlavhada
    assert html.count("<tr>") == 26                         # 1 sarlavha + 25 qator
    assert 'aria-current="page"' in html                    # sahifalash

    energy = client.get("/uz/reestr/?d=energoaudit").content.decode()
    assert "48" in energy and "Energosamaradorlik" in energy

    year = client.get("/uz/reestr/?y=2023").content.decode()
    assert "20 ta" in year

    search = client.get("/uz/reestr/?q=AGROBANK").content.decode()
    assert "AGROBANK" in search and "1 ta" in search

    assert client.get("/uz/reestr/?page=999").status_code == 200   # oxirgi sahifaga tushadi
```

- [ ] **Step 2: Test — muvaffaqiyatsizlik**

Run: `PYTHONIOENCODING=utf-8 pytest -q core/tests/test_pages.py -k registry` → FAIL (base.html render).

- [ ] **Step 3: view**

`core/views.py` (`from django.core.paginator import Paginator`; `from django.db.models import F, Q`):
```python
REGISTRY_PAGE_SIZE = 25


def registry(request):
    queryset = Project.objects.select_related("direction").order_by(F("year").desc(nulls_last=True), "order", "pk")
    direction_slug = request.GET.get("d", "")
    year = request.GET.get("y", "")
    query = request.GET.get("q", "").strip()
    if direction_slug:
        queryset = queryset.filter(direction__slug=direction_slug)
    if year.isdigit():
        queryset = queryset.filter(year=int(year))
    if query:
        queryset = queryset.filter(Q(title_uz__icontains=query) | Q(title_ru__icontains=query) | Q(client__icontains=query))
    paginator = Paginator(queryset, REGISTRY_PAGE_SIZE)
    page_obj = paginator.get_page(request.GET.get("page"))
    return page(
        request, "core/registry.html", nav="registry",
        crumbs=[(_("Bajarilgan ishlar reestri"), None)],
        page_obj=page_obj, total=Project.objects.count(), found=paginator.count,
        directions=Direction.objects.all(),
        years=Project.objects.exclude(year__isnull=True).values_list("year", flat=True).distinct().order_by("-year"),
        active={"d": direction_slug, "y": year, "q": query},
        offset=page_obj.start_index() - 1,
    )
```

- [ ] **Step 4: registry.html**

```django
{% extends "core/base.html" %}{% load i18n sitetags %}
{% block title %}{% translate "Bajarilgan ishlar reestri" %} — TTT Audit{% endblock %}
{% block description %}{% blocktranslate %}{{ total }} ta energoaudit va nazorat oʻlchovi ishi, 2019–2025: buyurtmachi, yoʻnalish, yil.{% endblocktranslate %}{% endblock %}
{% block main %}<div class="wrap">
<div class="phead"><h1>{% translate "Bajarilgan ishlar reestri" %}</h1>
  <p>{% blocktranslate %}Jami {{ total }} ta ish. Manba: tashkilotning 2026-yilgi axborot byulletenlari; buyurtmachi nomlari byulletendagidek.{% endblocktranslate %}</p></div>

<form class="filters" method="get" action="">
  <div><label for="f-d">{% translate "Yoʻnalish" %}</label><select class="select" id="f-d" name="d"><option value="">{% translate "Barchasi" %}</option>{% for d in directions %}<option value="{{ d.slug }}"{% if active.d == d.slug %} selected{% endif %}>{{ d|tr:"title" }}</option>{% endfor %}</select></div>
  <div><label for="f-y">{% translate "Yil" %}</label><select class="select" id="f-y" name="y"><option value="">{% translate "Barchasi" %}</option>{% for y in years %}<option value="{{ y }}"{% if active.y == y|stringformat:"s" %} selected{% endif %}>{{ y }}</option>{% endfor %}</select></div>
  <div style="flex:1"><label for="f-q">{% translate "Buyurtmachi yoki ish nomi" %}</label><input class="input" id="f-q" name="q" value="{{ active.q }}" placeholder="{% translate "masalan, AGROBANK" %}"></div>
  <div><button class="btn" type="submit">{% translate "Qidirish" %}</button> {% if active.d or active.y or active.q %}<a class="btn btn--ghost" href="{% url 'core:registry' %}">{% translate "Tozalash" %}</a>{% endif %}</div>
</form>
<p class="muted">{% blocktranslate with n=found %}Topildi: {{ n }} ta{% endblocktranslate %}</p>

<div class="table-wrap"><table class="table">
  <thead><tr><th>№</th><th>{% translate "Ish" %}</th><th>{% translate "Buyurtmachi" %}</th><th>{% translate "Yoʻnalish" %}</th><th>{% translate "Yil" %}</th></tr></thead>
  <tbody>{% for p in page_obj %}<tr><td class="num">{{ offset|add:forloop.counter }}</td><td>{{ p|tr:"title" }}</td><td>{{ p.client }}</td><td><span class="badge">{{ p.direction|tr:"title" }}</span></td><td class="num">{{ p.year|default:"—" }}</td></tr>{% empty %}<tr><td colspan="5" class="muted">{% translate "Hech narsa topilmadi." %}</td></tr>{% endfor %}</tbody>
</table></div>

{% if page_obj.paginator.num_pages > 1 %}<nav class="pager" aria-label="{% translate "Sahifalar" %}">
  {% if page_obj.has_previous %}<a href="{% qs_replace page=page_obj.previous_page_number %}">‹</a>{% endif %}
  {% for n in page_obj.paginator.get_elided_page_range %}{% if n == page_obj.paginator.ELLIPSIS %}<span>…</span>{% elif n == page_obj.number %}<span aria-current="page">{{ n }}</span>{% else %}<a href="{% qs_replace page=n %}">{{ n }}</a>{% endif %}{% endfor %}
  {% if page_obj.has_next %}<a href="{% qs_replace page=page_obj.next_page_number %}">›</a>{% endif %}
</nav>{% endif %}
</div>{% endblock %}
```

- [ ] **Step 5: Test oʻtadi va commit**

```bash
PYTHONIOENCODING=utf-8 pytest -q
git add -A && git commit -m "feat: bajarilgan ishlar reestri — filtr, qidiruv, sahifalash"
```

---

### Task 7: Hujjatlar va oʻlchov asboblari

**Files:**
- Modify: `core/views.py` (`credentials`, `instruments`), `core/urls.py`
- Create: `core/templates/core/{credentials.html, instruments.html}`
- Test: `core/tests/test_pages.py` (qoʻshimcha)

- [ ] **Step 1: Yozilmagan test**

```python
@pytest.mark.django_db
def test_credentials_page_shows_all_eight_documents_with_scans(client):
    html = client.get("/uz/hujjatlar/").content.decode()
    assert html.count('class="card doc"') == 8
    assert "data-lightbox" in html
    assert "№ 518159" in html and "ISO 9001:2015" in html and "Imkon" in html
    assert "АФ № 00773" not in html                       # Moliya vazirligi litsenziyasi — yoʻq


@pytest.mark.django_db
def test_instruments_page_table(client):
    html = client.get("/uz/tashkilot/asboblar/").content.decode()
    assert html.count("<tr>") == 6                          # sarlavha + 5 asbob
    assert "Milliy Metrologiya" in html
```

- [ ] **Step 2: Test — muvaffaqiyatsizlik** → `html.count(...) == 8` FAIL.

- [ ] **Step 3: view'lar**

```python
def credentials(request):
    return page(
        request, "core/credentials.html", nav="credentials",
        crumbs=[(_("Hujjatlar"), None)],
        credentials=Credential.objects.all(),
    )


def instruments(request):
    return page(
        request, "core/instruments.html", nav="company",
        crumbs=[(_("Tashkilot"), reverse("core:company")), (_("Oʻlchov asboblari"), None)],
        instruments=Instrument.objects.all(),
    )
```

- [ ] **Step 4: credentials.html**

```django
{% extends "core/base.html" %}{% load i18n sitetags %}
{% block title %}{% translate "Litsenziya, reestr, sertifikatlar" %} — TTT Audit{% endblock %}
{% block description %}{% translate "Qurilish vazirligi litsenziyasi № 518159, energoaudit reestri, UZACE aʼzoligi, ISO 9001/45001/27001, kasbiy javobgarlik sugʻurtasi — skanlar bilan." %}{% endblock %}
{% block main %}<div class="wrap">
<div class="phead"><h1>{% translate "Hujjatlar" %}</h1><p>{% translate "Vakolat va sifat hujjatlari. Asl nusxalar Fargʻonadagi bosh ofisda; skanni kattalashtirish uchun ustiga bosing." %}</p></div>
<div class="grid grid--2">
{% for c in credentials %}
  <article class="card doc">
    {% if c.scan %}<a class="doc__scan" href="{{ c.scan.url }}" data-lightbox data-alt="{{ c.get_kind_display }} {{ c.number }}"><img src="{{ c.scan.url }}" alt="{{ c.get_kind_display }} {{ c.number }}" loading="lazy"></a>{% else %}<span class="doc__scan"></span>{% endif %}
    <div>
      <div class="doc__k">{{ c.get_kind_display }}</div>
      <div class="doc__n">{{ c.number }}</div>
      <div class="doc__s">{{ c|tr:"scope" }}</div>
      <div class="doc__d">{{ c|tr:"issuer" }}{% if c.issued_on %} · {% translate "berilgan" %} {{ c.issued_on|date:"d.m.Y" }}{% endif %}{% if c.valid_until %} · {% translate "amal qiladi" %} {{ c.valid_until|date:"d.m.Y" }}{% elif c.kind == "license" %} · {% translate "muddatsiz" %}{% endif %}</div>
    </div>
  </article>
{% endfor %}
</div>
<div class="sec"><div class="notice notice--info"><p>{% translate "Litsenziya va reestr maʼlumotlarini rasmiy manbada tekshirish mumkin: litsenziya — license.gov.uz, energoaudit reestri — Energosamaradorlik milliy agentligi." %}</p></div></div>
</div>{% endblock %}
```

- [ ] **Step 5: instruments.html**

```django
{% extends "core/base.html" %}{% load i18n sitetags %}
{% block title %}{% translate "Oʻlchov asboblari va qiyoslash" %} — TTT Audit{% endblock %}
{% block main %}<div class="wrap">
<div class="phead"><h1>{% translate "Oʻlchov asboblari va qiyoslash" %}</h1><p>{% translate "Qiyoslanmagan asbob bilan olingan oʻlchov hisobotga kiritilmaydi. Qiyoslash guvohnomalari «Oʻzbekiston Milliy Metrologiya Instituti» davlat muassasasi tomonidan berilgan." %}</p></div>
<div class="table-wrap"><table class="table">
  <thead><tr><th>№</th><th>{% translate "Asbob" %}</th><th>{% translate "Zavod raqami" %}</th><th>{% translate "Oʻlchov chegarasi" %}</th><th>{% translate "Guvohnoma" %}</th><th>{% translate "Qiyoslangan" %}</th><th>{% translate "Amal qiladi" %}</th></tr></thead>
  <tbody>{% for i in instruments %}<tr><td class="num">{{ forloop.counter }}</td><td>{{ i|tr:"name" }}</td><td class="nowrap">{{ i.serial|default:"—" }}</td><td>{{ i|tr:"range" }}</td><td class="nowrap">{{ i.certificate_no }}</td><td class="num">{{ i.verified_on|date:"d.m.Y" }}</td><td class="num">{{ i.valid_until|date:"d.m.Y" }}</td></tr>{% endfor %}</tbody>
</table></div>
</div>{% endblock %}
```

- [ ] **Step 6: Test oʻtadi va commit**

```bash
PYTHONIOENCODING=utf-8 pytest -q
git add -A && git commit -m "feat: hujjatlar sahifasi (8 skan) va oʻlchov asboblari jadvali"
```

---

### Task 8: Qonunchilik va yangiliklar

**Files:**
- Modify: `core/views.py` (`legislation`, `news`, `post`), `core/urls.py`
- Create: `core/templates/core/{legislation.html, news.html, post.html}`
- Test: `core/tests/test_pages.py` (qoʻshimcha)

- [ ] **Step 1: Yozilmagan test**

```python
@pytest.mark.django_db
def test_legislation_shows_only_verified_acts(client):
    html = client.get("/uz/qonunchilik/").content.decode()
    assert "ЗРУ-940" in html and "lex.uz" in html
    assert "A–G toifalari" not in html                     # verified_on=None — koʻrinmaydi


@pytest.mark.django_db
def test_news_list_and_detail(client):
    html = client.get("/uz/yangiliklar/").content.decode()
    assert "energoaudit-kimga-majburiy" in html
    detail = client.get("/uz/yangiliklar/energoaudit-kimga-majburiy/")
    assert detail.status_code == 200
    assert client.get("/uz/yangiliklar/yoq-maqola/").status_code == 404
```

- [ ] **Step 2: Test — muvaffaqiyatsizlik** → `"lex.uz" in html` FAIL.

- [ ] **Step 3: view'lar**

```python
def legislation(request):
    return page(
        request, "core/legislation.html", nav="legislation",
        crumbs=[(_("Qonunchilik"), None)],
        acts=LegalAct.objects.prefetch_related("directions").filter(verified_on__isnull=False),
        posts=Post.objects.filter(is_published=True)[:4],
    )


def news(request):
    return page(
        request, "core/news.html", nav="news",
        crumbs=[(_("Yangiliklar"), None)],
        posts=Post.objects.filter(is_published=True),
    )


def post(request, slug):
    published = Post.objects.filter(is_published=True).select_related("legal_act")
    obj = get_object_or_404(published, slug=slug)
    return page(
        request, "core/post.html", nav="news",
        crumbs=[(_("Yangiliklar"), reverse("core:news")), (obj.tr("title"), None)],
        post=obj, others=published.exclude(pk=obj.pk)[:3],
    )
```

- [ ] **Step 4: legislation.html**

```django
{% extends "core/base.html" %}{% load i18n sitetags %}
{% block title %}{% translate "Qonunchilik — energoaudit va nazorat oʻlchovi" %} — TTT Audit{% endblock %}
{% block description %}{% translate "ЗРУ-940, VM qarori № 690 va boshqa meʼyoriy hujjatlar: kimga tegishli, talab, muddat, lex.uz havolasi." %}{% endblock %}
{% block main %}<div class="wrap">
<div class="phead"><h1>{% translate "Meʼyoriy hujjatlar" %}</h1><p>{% translate "Faqat lex.uz dagi amaldagi tahrir bilan solishtirilgan hujjatlar koʻrsatiladi. Tekshiruv sanasi har qatorda." %}</p></div>
<div class="table-wrap"><table class="table">
  <thead><tr><th>{% translate "Hujjat" %}</th><th>{% translate "Kimga tegishli" %}</th><th>{% translate "Talab" %}</th><th>{% translate "Muddat" %}</th><th>{% translate "Tekshirilgan" %}</th></tr></thead>
  <tbody>{% for a in acts %}<tr>
    <td><b>{{ a.number }}</b><br><small>{{ a|tr:"title" }}</small>{% if a.lex_url %}<br><a href="{{ a.lex_url }}" rel="noopener" target="_blank">lex.uz</a>{% endif %}</td>
    <td>{{ a|tr:"applies_to" }}</td><td>{{ a|tr:"requirement" }}</td><td>{{ a|tr:"deadline" }}</td>
    <td class="num">{{ a.verified_on|date:"d.m.Y" }}</td>
  </tr>{% endfor %}</tbody>
</table></div>
{% if posts %}<section class="sec"><div class="sec__head"><h2>{% translate "Tushuntirishlar" %}</h2><a href="{% url 'core:news' %}">{% translate "Barchasi" %} →</a></div><div class="grid grid--2">{% for p in posts %}<article class="card news"><time>{{ p.published_on|date:"d.m.Y" }}</time><h3><a href="{{ p.get_absolute_url }}">{{ p|tr:"title" }}</a></h3><p>{{ p|tr:"excerpt" }}</p></article>{% endfor %}</div></section>{% endif %}
</div>{% endblock %}
```

- [ ] **Step 5: news.html va post.html**

`news.html`:
```django
{% extends "core/base.html" %}{% load i18n sitetags %}
{% block title %}{% translate "Yangiliklar va tushuntirishlar" %} — TTT Audit{% endblock %}
{% block main %}<div class="wrap">
<div class="phead"><h1>{% translate "Yangiliklar va tushuntirishlar" %}</h1></div>
{% for p in posts %}<article class="card news"><time datetime="{{ p.published_on|date:'Y-m-d' }}">{{ p.published_on|date:"d.m.Y" }}</time>{% if p.legal_act %} <span class="badge">{{ p.legal_act.number }}</span>{% endif %}<h3><a href="{{ p.get_absolute_url }}">{{ p|tr:"title" }}</a></h3><p>{{ p|tr:"excerpt" }}</p></article>{% empty %}<p class="muted">{% translate "Hozircha yangiliklar yoʻq." %}</p>{% endfor %}
</div>{% endblock %}
```
`post.html`:
```django
{% extends "core/base.html" %}{% load i18n sitetags %}
{% block title %}{{ post|tr:"title" }} — TTT Audit{% endblock %}
{% block description %}{{ post|tr:"excerpt" }}{% endblock %}
{% block og_title %}{{ post|tr:"title" }}{% endblock %}
{% block main %}<div class="wrap"><div class="split">
  <article>
    <div class="phead"><h1>{{ post|tr:"title" }}</h1><div class="phead__meta"><time datetime="{{ post.published_on|date:'Y-m-d' }}">{{ post.published_on|date:"d.m.Y" }}</time>{% if post.legal_act %} · {{ post.legal_act.number }}{% endif %}</div></div>
    <div class="card prose">{{ post|tr:"body"|linebreaks }}</div>
  </article>
  <aside>
    {% if post.legal_act %}<div class="card"><h3>{% translate "Meʼyoriy asos" %}</h3><p><b>{{ post.legal_act.number }}</b><br>{{ post.legal_act|tr:"title" }}</p>{% if post.legal_act.lex_url %}<a href="{{ post.legal_act.lex_url }}" rel="noopener" target="_blank">lex.uz</a>{% endif %}</div>{% endif %}
    {% if others %}<div class="card"><h3>{% translate "Boshqa maqolalar" %}</h3><ul>{% for o in others %}<li><a href="{{ o.get_absolute_url }}">{{ o|tr:"title" }}</a></li>{% endfor %}</ul></div>{% endif %}
    <a class="btn" href="{% url 'core:request' %}">{% translate "Murojaat yuborish" %}</a>
  </aside>
</div></div>{% endblock %}
```

- [ ] **Step 6: Test oʻtadi va commit**

```bash
PYTHONIOENCODING=utf-8 pytest -q
git add -A && git commit -m "feat: qonunchilik jadvali va yangiliklar"
```

---

### Task 9: Tashkilot, rahbariyat va mutaxassislar, rekvizitlar

**Files:**
- Modify: `core/views.py` (`company`, `team`, `requisites`), `core/urls.py`
- Create: `core/templates/core/{company.html, team.html, requisites.html}`
- Test: `core/tests/test_pages.py` (qoʻshimcha)

- [ ] **Step 1: Yozilmagan test**

```python
@pytest.mark.django_db
def test_company_page(client):
    html = client.get("/uz/tashkilot/").content.decode()
    assert "1997" in html and "UZACE" in html and "ISO 27001" in html
    assert "Botirov" in html
    assert "filial" not in html.lower()


@pytest.mark.django_db
def test_team_page_groups_by_department(client):
    html = client.get("/uz/tashkilot/mutaxassislar/").content.decode()
    assert "Rahbariyat va mutaxassislar" in html
    assert html.count('class="card person"') == 40      # 39 mutaxassis + direktor kartasi
    assert "Energoaudit" in html and "Qurilishda nazorat oʻlchovi" in html
    assert "Jamoa" not in html


@pytest.mark.django_db
def test_requisites_page(client):
    html = client.get("/uz/tashkilot/rekvizitlar/").content.decode()
    assert "202216926" in html and "«TTTaudit» MChJ" in html
```

- [ ] **Step 2: Test — muvaffaqiyatsizlik** → `"UZACE" in html` FAIL.

- [ ] **Step 3: view'lar**

```python
from .models import Branch, Client, TeamMember


def company(request):
    return page(
        request, "core/company.html", nav="company",
        crumbs=[(_("Tashkilot"), None)],
        credentials=Credential.objects.all(),
        stats=Stat.objects.all(),
        leadership=TeamMember.objects.filter(is_leadership=True)[:4],
        clients=Client.objects.filter(featured=True)[:12],
    )


def team(request):
    members = TeamMember.objects.all()
    return page(
        request, "core/team.html", nav="company",
        crumbs=[(_("Tashkilot"), reverse("core:company")), (_("Rahbariyat va mutaxassislar"), None)],
        leadership=members.filter(is_leadership=True),
        energy=members.filter(is_leadership=False, dept=TeamMember.DEPT_ENERGY),
        construction=members.filter(is_leadership=False, dept=TeamMember.DEPT_CONSTRUCTION),
        total=members.count(),
    )


def requisites(request):
    return page(
        request, "core/requisites.html", nav="company",
        crumbs=[(_("Tashkilot"), reverse("core:company")), (_("Rekvizitlar"), None)],
        branches=Branch.objects.all(),
    )
```

- [ ] **Step 4: company.html**

```django
{% extends "core/base.html" %}{% load i18n sitetags %}
{% block title %}{% translate "Tashkilot haqida" %} — TTT Audit{% endblock %}
{% block description %}{{ site|tr:"about"|truncatechars:160 }}{% endblock %}
{% block main %}<div class="wrap">
<div class="phead"><h1>{{ site|tr:"org_name" }}</h1><p>{{ site|tr:"hero_title" }}</p><div class="phead__meta">{% translate "Ekspert tashkiloti" %} · {% translate "Fargʻona" %} · {{ site.founded_year }}</div></div>
<div class="stats">{% for s in stats %}<div class="card stat"><b>{{ s.value }}</b><span>{{ s|tr:"label" }}</span></div>{% endfor %}</div>
<section class="sec"><div class="split">
  <div class="card prose">{{ site|tr:"about"|linebreaks }}</div>
  <div>
    <div class="card"><h3>{% translate "Rahbar" %}</h3><p><b>{{ site|tr:"director" }}</b><br><span class="muted">{% translate "Bosh direktor" %}</span></p>
      {% for m in leadership %}<p><b>{{ m.display_name }}</b><br><span class="muted">{{ m|tr:"role" }}</span></p>{% endfor %}
      <a href="{% url 'core:team' %}">{% translate "Rahbariyat va mutaxassislar" %} →</a></div>
    <div class="card"><h3>{% translate "Hamkorlik" %}</h3><ul>
      <li>{% translate "Oʻzbekiston muhandis-konsultantlar uyushmasi (UZACE) aʼzosi" %}</li>
      <li>{% translate "Qurilish va uy-joy kommunal xoʻjaligi vazirligi bilan hamkorlik" %}</li>
      <li>{% translate "Vazirlar Mahkamasi huzuridagi Elektr energiyasi, neft mahsulotlari va gazdan foydalanishni nazorat qilish inspeksiyasi bilan hamkorlik" %}</li>
    </ul></div>
  </div>
</div></section>
<section class="sec"><div class="sec__head"><h2>{% translate "Vakolat va sifat hujjatlari" %}</h2><a href="{% url 'core:credentials' %}">{% translate "Skanlar bilan" %} →</a></div>
<div class="grid grid--4">{% for c in credentials %}<div class="card"><div class="doc__k">{{ c.get_kind_display }}</div><div class="doc__n">{{ c.number }}</div><div class="doc__s">{{ c|tr:"scope" }}</div></div>{% endfor %}</div></section>
{% if clients %}<section class="sec"><div class="sec__head"><h2>{% translate "Buyurtmachilar orasida" %}</h2><a href="{% url 'core:registry' %}">{% translate "Reestr" %} →</a></div><div class="grid grid--3">{% for c in clients %}<div class="card">{{ c|tr:"name" }}</div>{% endfor %}</div></section>{% endif %}
</div>{% endblock %}
```
- [ ] **Step 5: team.html**

```django
{% extends "core/base.html" %}{% load i18n sitetags %}
{% block title %}{% translate "Rahbariyat va mutaxassislar" %} — TTT Audit{% endblock %}
{% block description %}{% blocktranslate with n=total %}{{ n }} mutaxassis: energoaudit va qurilishda nazorat oʻlchovi boʻyicha, davlat namunasidagi sertifikatlar bilan.{% endblocktranslate %}{% endblock %}
{% block main %}<div class="wrap">
<div class="phead"><h1>{% translate "Rahbariyat va mutaxassislar" %}</h1><p>{% blocktranslate with n=site.staff_total e=site.staff_energy c=site.staff_supervision %}Jami {{ n }} xodim: {{ e }} energoaudit, {{ c }} texnik nazorat. Quyida byulletenda keltirilgan mutaxassislar.{% endblocktranslate %}</p></div>
<section class="sec"><div class="sec__head"><h2>{% translate "Rahbariyat" %}</h2></div><div class="grid grid--3">
  <div class="card person"><span class="person__ph"></span><div><b>{{ site|tr:"director" }}</b><span>{% translate "Bosh direktor" %}</span></div></div>
  {% for m in leadership %}{% include "core/_person.html" %}{% endfor %}
</div></section>
<section class="sec"><div class="sec__head"><h2>{% translate "Energoaudit" %}</h2></div><div class="grid grid--3">{% for m in energy %}{% include "core/_person.html" %}{% endfor %}</div></section>
<section class="sec"><div class="sec__head"><h2>{% translate "Qurilishda nazorat oʻlchovi" %}</h2></div><div class="grid grid--3">{% for m in construction %}{% include "core/_person.html" %}{% endfor %}</div></section>
</div>{% endblock %}
```
`core/templates/core/_person.html`:
```django
{% load sitetags %}<div class="card person">{% if m.photo %}<img src="{{ m.photo.url }}" alt="{{ m.display_name }}" loading="lazy" width="72" height="90">{% else %}<span class="person__ph"></span>{% endif %}<div><b>{{ m.display_name }}</b><span>{{ m|tr:"role" }}</span>{% if m.certificate_lines %}<small>{{ m.certificate_lines|join:"; " }}</small>{% endif %}</div></div>
```
Direktor kartasi ham `card person` — shuning uchun Step 1 testida soni **40** (39 mutaxassis + direktor).

- [ ] **Step 6: requisites.html**

```django
{% extends "core/base.html" %}{% load i18n sitetags %}
{% block title %}{% translate "Rekvizitlar" %} — TTT Audit{% endblock %}
{% block main %}<div class="wrap">
<div class="phead"><h1>{% translate "Rekvizitlar" %}</h1></div>
<div class="table-wrap"><table class="table"><tbody>
  <tr><th>{% translate "Rasmiy nomi" %}</th><td>{{ site|tr:"org_name" }}</td></tr>
  <tr><th>{% translate "STIR" %}</th><td class="nums">{{ site.tin }}</td></tr>
  <tr><th>{% translate "Rahbar" %}</th><td>{{ site|tr:"director" }}</td></tr>
  <tr><th>{% translate "Yuridik manzil" %}</th><td>{{ site|tr:"address" }}</td></tr>
  {% for b in branches %}{% if not b.is_head_office %}<tr><th>{{ b|tr:"city" }}</th><td>{{ b|tr:"address" }}{% if b.phone %} · {{ b.phone }}{% endif %}</td></tr>{% endif %}{% endfor %}
  <tr><th>{% translate "Telefon" %}</th><td>{{ site.phone }}{% if site.phone_second %}, {{ site.phone_second }}{% endif %}</td></tr>
  <tr><th>{% translate "E-pochta" %}</th><td><a href="mailto:{{ site.email }}">{{ site.email }}</a></td></tr>
  {% if site|tr:"bank_details" %}<tr><th>{% translate "Bank rekvizitlari" %}</th><td>{{ site|tr:"bank_details"|linebreaksbr }}</td></tr>{% endif %}
  <tr><th>{% translate "Litsenziya" %}</th><td>{% translate "Qurilish vazirligi litsenziyasi № 518159 (muddatsiz)" %} · <a href="{% url 'core:credentials' %}">{% translate "skan" %}</a></td></tr>
  <tr><th>{% translate "Sugʻurta" %}</th><td>{% translate "Kasbiy javobgarlik — 10 mlrd soʻm, «Imkon-sugʻurta» AJ" %}</td></tr>
</tbody></table></div>
</div>{% endblock %}
```

- [ ] **Step 7: Test oʻtadi va commit**

```bash
PYTHONIOENCODING=utf-8 pytest -q
git add -A && git commit -m "feat: tashkilot, rahbariyat va mutaxassislar (39), rekvizitlar"
```

---

### Task 10: Aloqa, murojaat formasi, API, chegara va Telegram

**Files:**
- Create: `core/throttle.py`, `core/notify.py`, `core/templates/core/{contact.html, request.html, _lead.html}`
- Modify: `core/views.py` (`contact`, `request_page`, `lead_create`, `compliance_check`, `energy_estimate`), `core/urls.py`
- Test: `core/tests/test_api.py`, `core/tests/test_pages.py` (qoʻshimcha)

**Interfaces:**
- Produces: `POST /uz/api/lead/` (forma yoki JSON javob `{"ok": true, "message": ...}` / 400 `{"ok": false, "errors": {...}}` / 429), `GET /uz/api/compliance/?object_kind=&area_m2=&annual_kwh=&annual_gas_m3=&estimate_value=&funding=&has_dispute=`, `GET /uz/api/energy-estimate/?area=&kwh=`; `throttle.allow(key, limit, window) -> bool`; `notify.notify_telegram(lead) -> bool`.

- [ ] **Step 1: Yozilmagan test**

`core/tests/test_api.py`:
```python
import pytest
from django.conf import settings

from core import throttle
from core.models import Lead


def test_throttle_allows_up_to_limit_then_blocks():
    assert all(throttle.allow("t:1", limit=3, window=60) for _ in range(3))
    assert throttle.allow("t:1", limit=3, window=60) is False
    assert throttle.allow("t:2", limit=3, window=60) is True


@pytest.mark.django_db
def test_lead_post_creates_lead_and_returns_json(client, monkeypatch):
    sent = []
    monkeypatch.setattr("core.views.notify_telegram", lambda lead: sent.append(lead) or True)
    response = client.post("/uz/api/lead/", {"name": "Test", "phone": "+998901234567", "note": "Bino"},
                           HTTP_X_REQUESTED_WITH="XMLHttpRequest")
    assert response.status_code == 200 and response.json()["ok"] is True
    assert Lead.objects.count() == 1 and Lead.objects.get().language == "uz"
    assert len(sent) == 1


@pytest.mark.django_db
def test_lead_post_invalid_phone_returns_400(client):
    response = client.post("/uz/api/lead/", {"name": "Test", "phone": "12"}, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
    assert response.status_code == 400 and "phone" in response.json()["errors"]


@pytest.mark.django_db
def test_lead_post_without_js_redirects(client):
    response = client.post("/uz/api/lead/", {"name": "Test", "phone": "+998901234567"})
    assert response.status_code == 302 and response["Location"].endswith("/uz/murojaat/?sent=1")


@pytest.mark.django_db
def test_lead_rate_limit(client):
    for _ in range(settings.LEAD_RATE_LIMIT):
        client.post("/uz/api/lead/", {"name": "T", "phone": "+998901234567"}, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
    response = client.post("/uz/api/lead/", {"name": "T", "phone": "+998901234567"}, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
    assert response.status_code == 429


@pytest.mark.django_db
def test_compliance_api_returns_requirements_with_service_links(client):
    response = client.get("/uz/api/compliance/", {"object_kind": "construction", "funding": "budget", "estimate_value": "5000000"})
    data = response.json()
    assert data["ok"] and data["estimated_fee"] == "15 000"
    assert data["requirements"][0]["service_url"].endswith("/xizmatlar/olchov-auditi/nazorat-olchovi/")


@pytest.mark.django_db
def test_energy_api(client):
    assert client.get("/uz/api/energy-estimate/", {"area": "1000", "kwh": "100000"}).json()["category"] == "D"
    assert client.get("/uz/api/energy-estimate/", {"area": "x"}).status_code == 400
```
`core/tests/test_pages.py` ga:
```python
@pytest.mark.django_db
def test_contact_and_request_pages(client):
    contact = client.get("/uz/aloqa/").content.decode()
    assert "Toshkent" in contact and "Yangiobod" in contact and 'data-react="lead-form"' in contact
    request_page = client.get("/uz/murojaat/").content.decode()
    assert 'name="csrfmiddlewaretoken"' in request_page and 'enctype="multipart/form-data"' in request_page
```

- [ ] **Step 2: Test — muvaffaqiyatsizlik** → `ModuleNotFoundError: core.throttle`.

- [ ] **Step 3: throttle.py va notify.py**

`core/throttle.py`:
```python
"""Oddiy chegara: cache'da hisoblagich. Prodda cache umumiy (DatabaseCache/Redis) boʻlishi kerak,
LocMem har gunicorn ishchisida alohida sanaydi — README da qayd etilgan."""
from django.core.cache import cache


def client_ip(request) -> str:
    """Teskari proksi ortida X-Real-IP (Railway/nginx), aks holda REMOTE_ADDR."""
    return (request.META.get("HTTP_X_REAL_IP") or request.META.get("REMOTE_ADDR") or "").strip()


def allow(key: str, limit: int, window: int) -> bool:
    """`window` soniya ichida `limit` tagacha ruxsat; oshsa False."""
    cache_key = f"throttle:{key}"
    cache.add(cache_key, 0, timeout=window)
    try:
        count = cache.incr(cache_key)
    except ValueError:  # kalit oynada oʻchib ketgan
        cache.set(cache_key, 1, timeout=window)
        count = 1
    return count <= limit
```
`core/notify.py`:
```python
"""Yangi murojaat haqida Telegram xabari. Xato soʻrovni yiqitmaydi: murojaat bazada, xabar ikkinchi darajali."""
import json
import logging
import urllib.request

from django.conf import settings

log = logging.getLogger(__name__)


def notify_telegram(lead) -> bool:
    token, chat = settings.TELEGRAM_BOT_TOKEN, settings.TELEGRAM_CHAT_ID
    if not token or not chat:
        return False
    lines = [
        "Saytdan yangi murojaat",
        f"Ism: {lead.name}",
        f"Telefon: {lead.phone}",
        f"E-pochta: {lead.email}" if lead.email else "",
        f"Yoʻnalish: {lead.direction.title_uz}" if lead.direction_id else "",
        f"Obyekt: {lead.object_type}" if lead.object_type else "",
        f"Izoh: {lead.note}" if lead.note else "",
        f"Sahifa: {lead.source}" if lead.source else "",
    ]
    payload = json.dumps({"chat_id": chat, "text": "\n".join(filter(None, lines)),
                          "disable_web_page_preview": True}).encode()
    request = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage", data=payload,
        headers={"Content-Type": "application/json"},
    )
    try:
        urllib.request.urlopen(request, timeout=8).read()
        return True
    except Exception as error:  # noqa: BLE001 — tarmoq xatosi turli sinflarda keladi
        log.warning("Telegram: yuborilmadi — %s", error)
        return False
```

- [ ] **Step 4: view'lar va API**

`core/views.py` ga (`from django.http import JsonResponse`; `from django.shortcuts import redirect`; `from django.views.decorators.http import require_POST`; `from .forms import LeadForm`; `from .notify import notify_telegram`; `from . import throttle`):
```python
def _wants_json(request) -> bool:
    return request.headers.get("X-Requested-With") == "XMLHttpRequest" or "application/json" in request.headers.get("Accept", "")


def contact(request):
    site = SiteSettings.load()
    map_bbox = ""
    if site.map_lat and site.map_lng:
        map_bbox = f"{site.map_lng - 0.01:.5f},{site.map_lat - 0.006:.5f},{site.map_lng + 0.01:.5f},{site.map_lat + 0.006:.5f}"
    context = {"branches": Branch.objects.all(), "map_bbox": map_bbox}
    context.update(form_context())
    return page(request, "core/contact.html", nav="contact", crumbs=[(_("Aloqa"), None)], **context)


def request_page(request):
    context = {"hero_credentials": Credential.objects.filter(show_in_hero=True), "sent": request.GET.get("sent") == "1",
               "error": request.GET.get("error", "")}
    context.update(form_context())
    return page(request, "core/request.html", nav="contact", crumbs=[(_("Murojaat"), None)], **context)


@require_POST
def lead_create(request):
    """React formasi JSON kutadi; JS oʻchiq boʻlsa oddiy forma redirect oladi."""
    if not throttle.allow(f"lead:{throttle.client_ip(request)}", settings.LEAD_RATE_LIMIT, settings.LEAD_RATE_WINDOW_SECONDS):
        if _wants_json(request):
            return JsonResponse({"ok": False, "error": _("Juda koʻp soʻrov. Birozdan soʻng urinib koʻring yoki qoʻngʻiroq qiling.")}, status=429)
        return redirect(reverse("core:request") + "?error=limit")

    form = LeadForm(request.POST, request.FILES)
    if not form.is_valid():
        if _wants_json(request):
            return JsonResponse({"ok": False, "errors": form.errors}, status=400)
        return redirect(reverse("core:request") + "?error=1")

    lead = form.save(commit=False)
    lead.language = request.LANGUAGE_CODE
    lead.source = (request.META.get("HTTP_REFERER") or "")[:200]
    lead.save()
    notify_telegram(lead)

    message = _("Murojaat qabul qilindi. Bir ish kuni ichida muhandis bogʻlanadi.")
    if _wants_json(request):
        return JsonResponse({"ok": True, "message": message})
    return redirect(reverse("core:request") + "?sent=1")


def compliance_check(request):
    result = compliance.evaluate(
        object_kind=request.GET.get("object_kind", ""),
        area_m2=request.GET.get("area_m2"), annual_kwh=request.GET.get("annual_kwh"),
        annual_gas_m3=request.GET.get("annual_gas_m3"), estimate_value=request.GET.get("estimate_value"),
        funding=request.GET.get("funding", ""),
        has_dispute=request.GET.get("has_dispute") in ("1", "true", "on"),
    )
    payload = result.as_dict()
    slugs = {r["service_slug"] for r in payload["requirements"] if r["service_slug"]}
    urls = {s.slug: {"url": s.get_absolute_url(), "title": s.tr("title")}
            for s in Service.objects.select_related("direction").filter(slug__in=slugs)} if slugs else {}
    for item in payload["requirements"]:
        info = urls.get(item["service_slug"])
        if info:
            item["service_url"], item["service_title"] = info["url"], info["title"]
    return JsonResponse({"ok": True, **payload})


def energy_estimate(request):
    try:
        area = float(request.GET.get("area") or 0)
        kwh = float(request.GET.get("kwh") or 0)
    except (TypeError, ValueError):
        return JsonResponse({"ok": False, "error": _("Notoʻgʻri qiymat")}, status=400)
    value = energy.specific_consumption(kwh, area)
    return JsonResponse({
        "ok": True, "specific": round(value, 1) if value is not None else None,
        "category": energy.category_for(value),
        "passport_required": area >= energy.PASSPORT_AREA_THRESHOLD_M2,
        "threshold": energy.PASSPORT_AREA_THRESHOLD_M2,
    })
```
`core/urls.py` da `contact`, `request` yoʻllarini ulang va vaqtinchalik API yoʻllarini almashtiring:
```python
    path("api/lead/", views.lead_create, name="lead_create"),
    path("api/compliance/", views.compliance_check, name="compliance_check"),
    path("api/energy-estimate/", views.energy_estimate, name="energy_estimate"),
```
Endi `core/urls.py` da `views.home` faqat `""` yoʻlida qolishi kerak — tekshiring.

- [ ] **Step 5: _lead.html (JS oʻchiq holat uchun toʻliq forma), request.html, contact.html**

`core/templates/core/_lead.html`:
```django
{% load i18n sitetags %}<div data-react="lead-form" data-endpoint="{% url 'core:lead_create' %}" data-directions="{{ form_directions_json }}" data-max-mb="{{ max_upload_mb }}">
<form class="form" method="post" action="{% url 'core:lead_create' %}" enctype="multipart/form-data">
  {% csrf_token %}
  <div class="grid grid--2">
    <div class="field"><label class="field__label" for="l-direction">{% translate "Yoʻnalish" %}</label><select class="select" id="l-direction" name="direction"><option value="">{% translate "Tanlang" %}</option>{% for d in form_directions %}<option value="{{ d.pk }}">{{ d|tr:"title" }}</option>{% endfor %}</select></div>
    <div class="field"><label class="field__label" for="l-object">{% translate "Obyekt turi" %}</label><input class="input" id="l-object" name="object_type" placeholder="{% translate "masalan, maʼmuriy bino, 4 qavat" %}"></div>
    <div class="field"><label class="field__label" for="l-name">{% translate "Ism" %} <span class="field__req">*</span></label><input class="input" id="l-name" name="name" required></div>
    <div class="field"><label class="field__label" for="l-phone">{% translate "Telefon" %} <span class="field__req">*</span></label><input class="input" id="l-phone" name="phone" type="tel" required placeholder="+998"></div>
    <div class="field"><label class="field__label" for="l-email">{% translate "E-pochta" %}</label><input class="input" id="l-email" name="email" type="email"></div>
    <div class="field"><label class="field__label" for="l-region">{% translate "Viloyat" %}</label><input class="input" id="l-region" name="region"></div>
    <div class="field form__full"><label class="field__label" for="l-note">{% translate "Izoh" %}</label><textarea class="textarea" id="l-note" name="note"></textarea></div>
    <div class="field form__full"><label class="field__label" for="l-file">{% translate "Fayl" %} <small class="muted">({% blocktranslate with mb=max_upload_mb %}{{ mb }} MB gacha: PDF, Excel, Word, DWG, ZIP, rasm{% endblocktranslate %})</small></label><input class="input" id="l-file" name="attachment" type="file"></div>
  </div>
  <div class="form__foot"><button class="btn" type="submit">{% translate "Yuborish" %}</button><span class="form__privacy">{% translate "Maʼlumotlar faqat murojaatni koʻrib chiqish uchun ishlatiladi." %}</span></div>
</form>
</div>
```
`core/templates/core/request.html`:
```django
{% extends "core/base.html" %}{% load i18n sitetags %}
{% block title %}{% translate "Murojaat yuborish" %} — TTT Audit{% endblock %}
{% block main %}<div class="wrap">
<div class="phead"><h1>{% translate "Murojaat yuborish" %}</h1><p>{% translate "Obyekt haqida qisqacha yozing yoki qoʻngʻiroq qiling. Qaysi talab tegishli ekanini va ish hajmini birinchi suhbatda aniqlaymiz." %}</p></div>
{% if sent %}<div class="notice notice--ok"><p>{% translate "Murojaat qabul qilindi. Bir ish kuni ichida muhandis bogʻlanadi." %}</p></div>
{% elif error == "limit" %}<div class="notice notice--danger"><p>{% translate "Juda koʻp soʻrov. Birozdan soʻng urinib koʻring yoki qoʻngʻiroq qiling." %}</p></div>
{% elif error %}<div class="notice notice--danger"><p>{% translate "Forma toʻldirilmagan: ism va telefon majburiy." %}</p></div>{% endif %}
<div class="split">
  <div class="card">{% include "core/_lead.html" %}</div>
  <aside>
    <div class="card"><h3>{% translate "Telefon" %}</h3><p><a href="tel:{{ site.phone|cut:' ' }}">{{ site.phone }}</a>{% if site.phone_second %}<br><a href="tel:{{ site.phone_second|cut:' ' }}">{{ site.phone_second }}</a>{% endif %}</p><h3>{% translate "E-pochta" %}</h3><p><a href="mailto:{{ site.email }}">{{ site.email }}</a></p></div>
    <div class="card"><h3>{% translate "Vakolat" %}</h3><ul>{% for c in hero_credentials %}<li>{{ c.get_kind_display }} {{ c.number }}</li>{% endfor %}</ul></div>
  </aside>
</div>
</div>{% endblock %}
```
`core/templates/core/contact.html`:
```django
{% extends "core/base.html" %}{% load i18n sitetags %}
{% block title %}{% translate "Aloqa" %} — TTT Audit{% endblock %}
{% block main %}<div class="wrap">
<div class="phead"><h1>{% translate "Aloqa" %}</h1></div>
<div class="grid grid--2">
{% for b in branches %}<div class="card"><div class="doc__k">{% if b.is_head_office %}{% translate "Bosh ofis" %}{% else %}{% translate "Ofis" %}{% endif %}</div><h3>{{ b|tr:"city" }}</h3><p>{{ b|tr:"address" }}</p>{% if b.phone %}<p><a href="tel:{{ b.phone|cut:' ' }}">{{ b.phone }}</a></p>{% endif %}{% if b.head %}<p class="muted">{{ b.head }}</p>{% endif %}</div>{% endfor %}
</div>
{% if map_bbox %}<section class="sec"><div class="card map-card"><iframe title="{% translate "Xarita" %}" width="100%" height="360" loading="lazy" referrerpolicy="no-referrer-when-downgrade" src="https://www.openstreetmap.org/export/embed.html?bbox={{ map_bbox|urlencode }}&amp;layer=mapnik&amp;marker={{ site.map_lat }}%2C{{ site.map_lng }}"></iframe></div><p class="muted"><a href="https://www.openstreetmap.org/?mlat={{ site.map_lat }}&amp;mlon={{ site.map_lng }}#map=17/{{ site.map_lat }}/{{ site.map_lng }}" rel="noopener" target="_blank">{% translate "Kattaroq xarita" %}</a></p></section>{% endif %}
<section class="sec"><div class="sec__head"><h2>{% translate "Murojaat yuborish" %}</h2></div><div class="card">{% include "core/_lead.html" %}</div></section>
</div>{% endblock %}
```
`site.css` ga `.map-card{padding:0;overflow:hidden}` va forma klasslari (`.field .field__label .field__req .field__err .form__full .form__foot .form__privacy .form-error .form-done`) — Task 11 dagi `widgets.css` da beriladi (React ham, oddiy forma ham bir xil koʻrinsin).

- [ ] **Step 6: Test oʻtadi va commit**

```bash
PYTHONIOENCODING=utf-8 pytest -q
git add -A && git commit -m "feat: aloqa, murojaat formasi, API (lead, compliance, energy), chegara va Telegram"
```

---

### Task 11: React vidjetlari (Vite) — port va yangi uslub

**Files:**
- Create: `frontend/package.json`, `frontend/vite.config.js`, `frontend/src/widgets.css`
- Copy: `C:\Users\Surface PC\reper\frontend\src\{main.jsx, csrf.js, ComplianceCheck.jsx, EnergyEstimator.jsx, LeadForm.jsx}` → `frontend/src/` (oʻzgarishsiz; `main.jsx` ga bitta import qoʻshiladi)
- Test: `core/tests/test_widgets_build.py`

**Interfaces:**
- Consumes: `[data-react="compliance-check"|"energy-estimator"|"lead-form"]` orollari (Task 4, 5, 10) va ularning `data-*` atributlari: `data-endpoint`, `data-request-url`, `data-ladder`, `data-threshold`, `data-directions`, `data-max-mb`.
- Produces: `frontend/dist/widgets/widgets.js` (ES module) va `frontend/dist/widgets/style.css` — `base.html` ularni `{% static 'widgets/...' %}` orqali oladi.

- [ ] **Step 1: Yozilmagan test**

`core/tests/test_widgets_build.py`:
```python
from pathlib import Path

DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist" / "widgets"


def test_widget_bundle_is_built():
    assert (DIST / "widgets.js").exists(), "cd frontend && npm run build"
    assert (DIST / "style.css").exists()
    css = (DIST / "style.css").read_text(encoding="utf-8")
    for cls in (".check", ".est", ".form", ".reqs", ".ladder", ".field"):
        assert cls in css, cls
```

- [ ] **Step 2: Test — muvaffaqiyatsizlik** → `assert (DIST / "widgets.js").exists()` FAIL.

- [ ] **Step 3: package.json va vite.config.js**

`frontend/package.json`:
```json
{
  "name": "tttaudit-widgets",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "description": "Django SSR sahifasiga oʻrnatiladigan React vidjetlari",
  "scripts": { "dev": "vite build --watch", "build": "vite build" },
  "dependencies": { "react": "^19.2.0", "react-dom": "^19.2.0" },
  "devDependencies": { "@vitejs/plugin-react": "^5.1.0", "vite": "^7.2.0" }
}
```
`frontend/vite.config.js` — `C:\Users\Surface PC\reper\frontend\vite.config.js` dan oʻzgarishsiz nusxa (chiqish: `dist/widgets/widgets.js`, `dist/widgets/[name][extname]` → CSS `style.css`).

- [ ] **Step 4: JSX fayllarni nusxalash va CSS importi**

```bash
cd /d/tttaudit && cp "/c/Users/Surface PC/reper/frontend/src/"{main.jsx,csrf.js,ComplianceCheck.jsx,EnergyEstimator.jsx,LeadForm.jsx} frontend/src/
```
`frontend/src/main.jsx` da `import "./csrf.js";` qatoridan oldin `import "./widgets.css";` qoʻshing.

- [ ] **Step 5: widgets.css — vidjet klasslari yangi dizayn tokenlarida**

`frontend/src/widgets.css` (JSX dagi klasslar: `check*`, `est*`, `ladder*`, `reqs*`, `form*`, `field*`, `file*`, `input select textarea radios nums btn`):
```css
/* Vidjetlar va oddiy forma uchun umumiy uslub. Tokenlar site.css dagi :root dan. */
.form{display:block}
.form__full{grid-column:1 / -1}
.form__foot{display:flex;align-items:center;gap:16px;margin-top:16px;flex-wrap:wrap}
.form__privacy{font-size:13px;color:var(--muted)}
.form-error{border-left:4px solid var(--danger);background:var(--danger-50);padding:10px 14px;margin-bottom:14px;font-size:14.5px}
.form-done{padding:24px;text-align:left}
.form-done__t{font-size:20px;font-weight:600;margin-bottom:6px;color:var(--ok)}
.form-done__d{color:var(--ink-2)}
.field{margin-bottom:12px}
.field__label{display:block;font-size:13.5px;font-weight:500;margin-bottom:5px;color:var(--ink-2)}
.field__req{color:var(--danger)}
.field__err{display:block;font-size:12.5px;color:var(--danger);margin-top:4px}
.file{font-size:14px}
.file__hint{display:block;font-size:12.5px;color:var(--muted);margin-top:4px}
.radios{display:flex;gap:14px;flex-wrap:wrap;font-size:14.5px}
.radios label{display:flex;gap:6px;align-items:center}

/* Talab tekshiruvchi */
.check{display:block}
.check__head{display:flex;justify-content:space-between;align-items:center;gap:12px;margin-bottom:12px;font-size:13px;color:var(--muted)}
.check__step{font-weight:600;color:var(--brand);letter-spacing:.04em;text-transform:uppercase}
.check__body{min-height:200px}
.check__q{font-size:17px;font-weight:600;margin:0 0 12px}
.check__opts{display:grid;gap:8px;margin-bottom:12px}
.check__opts--row{grid-template-columns:repeat(3,1fr)}
.check__opt{display:block;text-align:left;padding:12px 14px;border:1px solid var(--line);border-radius:6px;background:#fff;font:inherit;cursor:pointer;color:var(--ink)}
.check__opt:hover{border-color:var(--brand)}
.check__opt[aria-pressed="true"]{border-color:var(--brand);background:var(--brand-50);box-shadow:inset 0 0 0 1px var(--brand)}
.check__opt-t{display:block;font-weight:600;font-size:15px}
.check__opt-n{display:block;font-size:13px;color:var(--muted);margin-top:2px}
.check__fields{display:grid;grid-template-columns:repeat(2,1fr);gap:12px;margin-bottom:12px}
.check__label{display:block;font-size:13.5px;color:var(--ink-2);margin-bottom:5px}
.check__toggle{display:flex;gap:8px;align-items:center;font-size:14.5px;margin-bottom:12px}
.check__hint{font-size:13px;color:var(--muted);margin:8px 0 0}
.check__hint--err{color:var(--danger)}
.check__hint--legal{border-left:3px solid var(--accent);padding-left:10px;color:var(--ink-2)}
.check__foot{display:flex;gap:10px;align-items:center;margin-top:14px;flex-wrap:wrap}
.check__back{background:none;border:0;color:var(--link);font:inherit;cursor:pointer;padding:0}
.check__result{border-top:1px solid var(--line);padding-top:14px;margin-top:6px}
.check__cat{display:flex;gap:16px;align-items:baseline;margin-bottom:10px}
.check__cat-k{font-size:13px;color:var(--muted)}
.check__cat-v{font-size:28px;font-weight:700;color:var(--brand);font-variant-numeric:tabular-nums}
.reqs{list-style:none;margin:0;padding:0}
.reqs li{border:1px solid var(--line);border-radius:6px;background:#fff;padding:12px 14px;margin-bottom:8px}
.reqs__top{display:flex;justify-content:space-between;gap:10px;align-items:start}
.reqs__t{font-weight:600}
.reqs__n{font-size:14px;color:var(--ink-2);margin:6px 0}
.reqs__meta{font-size:13px;color:var(--muted)}
.reqs__r{font-size:13px;color:var(--brand);font-weight:600}
.reqs__sev{font-size:12px;font-weight:600;padding:2px 8px;border-radius:4px;white-space:nowrap}
.reqs__sev--required{background:var(--danger-50);color:var(--danger)}
.reqs__sev--likely{background:var(--warn-50);color:var(--warn)}
.reqs__sev--optional{background:var(--brand-50);color:var(--brand-700)}

/* Energiya baholagich */
.est{display:block}
.est__head{font-size:13px;color:var(--muted);margin-bottom:10px}
.est__body{display:grid;gap:12px}
.est__fields{display:grid;grid-template-columns:repeat(2,1fr);gap:12px}
.est__out{display:flex;gap:16px;align-items:baseline}
.est__val{font-size:26px;font-weight:700;color:var(--brand);font-variant-numeric:tabular-nums}
.est__cat{font-size:14px;color:var(--ink-2)}
.est__note{font-size:13px;color:var(--muted)}
.est__note--flag{color:var(--warn)}
.ladder{list-style:none;margin:0;padding:0;display:grid;gap:4px}
.ladder__row{display:grid;grid-template-columns:28px 1fr 90px;gap:8px;align-items:center;font-size:13px}
.ladder__l{font-weight:700;color:var(--brand)}
.ladder__bar{height:10px;border-radius:3px;background:var(--brand-100)}
.ladder__row[aria-current="true"] .ladder__bar{background:var(--accent)}
.ladder__kwh{color:var(--muted);text-align:right;font-variant-numeric:tabular-nums}
.nums{font-variant-numeric:tabular-nums}

@media (max-width:600px){
  .check__opts--row,.check__fields,.est__fields{grid-template-columns:1fr}
}
```
JSX ichida `className` qiymatlari yuqoridagi roʻyxatga mos; agar biror klass CSS'da yoʻq boʻlsa (`grep -ohE 'className="[^"]+"' frontend/src/*.jsx | sort -u` bilan tekshiring) — shu faylga tokenlar bilan qoʻshing.

- [ ] **Step 6: Build va test**

```bash
cd /d/tttaudit/frontend && npm install && npm run build && cd .. && ls frontend/dist/widgets
PYTHONIOENCODING=utf-8 pytest -q
python manage.py runserver 8000   # /uz/ da talab tekshiruvchi ishlaydi; /uz/murojaat/ da forma yuboriladi (Network: /uz/api/lead/ 200)
```
Brauzerda tekshiring: uch vidjet ham yuklanadi, konsolda xato yoʻq; JS oʻchirilganda forma POST orqali `?sent=1` ga qaytadi.

- [ ] **Step 7: Commit**

```bash
git add -A && git commit -m "feat: React vidjetlari — talab tekshiruvchi, energiya baholagich, murojaat formasi (yangi uslub)"
```

---

### Task 12: Uch til, sitemap, robots, SEO tekshiruvi

**Files:**
- Copy: `C:\Users\Surface PC\reper\core\management\commands\maketranslations.py` → `core/management/commands/`; `C:\Users\Surface PC\reper\locale\translations.json` → `locale/`
- Create: `core/sitemaps.py`, `core/templates/core/robots.txt`
- Modify: `config/urls.py`, `locale/translations.json`
- Test: `core/tests/test_seo.py`

**Interfaces:**
- Produces: `/sitemap.xml` (uch til, `xhtml:link` alternates), `/robots.txt`; `python manage.py maketranslations [--report]`.

- [ ] **Step 1: Yozilmagan test**

`core/tests/test_seo.py`:
```python
import re

import pytest
from django.core.management import call_command


@pytest.mark.django_db
def test_sitemap_lists_pages_in_three_languages(client):
    response = client.get("/sitemap.xml")
    assert response.status_code == 200
    xml = response.content.decode()
    assert "/uz/xizmatlar/energoaudit/" in xml and "/ru/xizmatlar/energoaudit/" in xml and "/en/reestr/" in xml
    assert 'hreflang="ru"' in xml
    assert "/uz/yangiliklar/energoaudit-kimga-majburiy/" in xml


def test_robots_txt(client):
    response = client.get("/robots.txt")
    assert response.status_code == 200 and response["Content-Type"].startswith("text/plain")
    assert "Sitemap: https://tttaudit.uz/sitemap.xml" in response.content.decode()
    assert "Disallow: /admin/" in response.content.decode()


@pytest.mark.django_db
def test_every_page_has_title_canonical_and_hreflang(client):
    for path in ("/uz/", "/uz/xizmatlar/", "/uz/reestr/", "/uz/hujjatlar/", "/uz/qonunchilik/",
                 "/uz/tashkilot/", "/uz/tashkilot/mutaxassislar/", "/uz/aloqa/", "/uz/murojaat/"):
        html = client.get(path).content.decode()
        assert re.search(r"<title>[^<]{10,}</title>", html), path
        assert f'rel="canonical" href="https://tttaudit.uz{path}"' in html, path
        assert 'hreflang="en"' in html, path


@pytest.mark.django_db
def test_no_missing_translations(capsys):
    call_command("maketranslations", "--report")
    out = capsys.readouterr().out
    assert "yetishmayapti: 0" in out or "0 ta" in out, out
```
(`maketranslations --report` chiqishi formatini nusxalangan fayldan oʻqib, oxirgi `assert` ni uning aniq soʻziga moslang — masalan `"Boʻsh: 0"`.)

- [ ] **Step 2: Test — muvaffaqiyatsizlik** → `/sitemap.xml` 404.

- [ ] **Step 3: sitemaps.py, robots.txt, urls**

`core/sitemaps.py`:
```python
"""Sitemap: statik sahifalar, yoʻnalishlar, xizmatlar, maqolalar — uch tilda alternates bilan."""
from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Direction, Post, Service


class StaticSitemap(Sitemap):
    i18n = True
    alternates = True
    x_default = True
    changefreq = "monthly"
    priority = 0.8

    def items(self):
        return ["core:home", "core:services", "core:registry", "core:credentials", "core:legislation",
                "core:news", "core:company", "core:team", "core:instruments", "core:requisites",
                "core:contact", "core:request"]

    def location(self, item):
        return reverse(item)


class DirectionSitemap(Sitemap):
    i18n = True
    alternates = True
    priority = 0.9

    def items(self):
        return Direction.objects.all()


class ServiceSitemap(Sitemap):
    i18n = True
    alternates = True
    priority = 0.9

    def items(self):
        return Service.objects.select_related("direction")


class PostSitemap(Sitemap):
    i18n = True
    alternates = True
    changefreq = "weekly"

    def items(self):
        return Post.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.published_on


SITEMAPS = {"static": StaticSitemap, "directions": DirectionSitemap, "services": ServiceSitemap, "posts": PostSitemap}
```
`core/templates/core/robots.txt`:
```
User-agent: *
Disallow: /admin/
Disallow: /uz/api/
Disallow: /ru/api/
Disallow: /en/api/
Sitemap: {{ SITE_URL }}/sitemap.xml
```
`config/urls.py` — til prefiksisiz yoʻllarga qoʻshing:
```python
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView

from core.sitemaps import SITEMAPS

urlpatterns += [
    path("sitemap.xml", sitemap, {"sitemaps": SITEMAPS}, name="sitemap"),
    path("robots.txt", TemplateView.as_view(template_name="core/robots.txt", content_type="text/plain")),
]
```
`settings.py` da `Sitemap` mutlaq URL uchun `django.contrib.sites` kerak emas — Django `sitemap` view `request` dan domen oladi; testda `https://tttaudit.uz` boʻlishi uchun `test_sitemap_...` faqat yoʻlni tekshiradi (yuqoridagi test shunday).

- [ ] **Step 4: Tarjimalar**

```bash
cd /d/tttaudit && cp "/c/Users/Surface PC/reper/core/management/commands/maketranslations.py" core/management/commands/
mkdir -p locale && cp "/c/Users/Surface PC/reper/locale/translations.json" locale/
```
`maketranslations.py` da `collect_sources` roʻyxatini `("models.py", "views.py", "forms.py", "compliance.py")` qiling. Keyin:
```bash
PYTHONIOENCODING=utf-8 python manage.py maketranslations --report
```
Chiqishda boʻsh qolgan satrlar roʻyxati keladi (yangi shablonlardagi ~120 ta satr). `locale/translations.json` ni toʻldiring — har satr uchun `ru` va `en`. Qoidalar: rasmiy uslub, «Вы» shakli, «аудиторская организация» yozilmaydi (ru: «экспертная организация»), «Rahbariyat va mutaxassislar» → ru «Руководство и специалисты», en «Management and specialists»; «Bajarilgan ishlar reestri» → «Реестр выполненных работ» / «Registry of completed work»; «Maxsus imkoniyatlar» → «Специальные возможности» / «Accessibility»; «Murojaat yuborish» → «Отправить обращение» / «Send a request»; «Qonunchilik» → «Законодательство» / «Legislation»; «Hujjatlar» → «Документы» / «Documents»; «Reestr» → «Реестр» / «Registry»; «Tashkilot» → «Организация» / «Organisation»; «Yangiliklar» → «Новости» / «News»; «Aloqa» → «Контакты» / «Contact». Toʻldirgach:
```bash
PYTHONIOENCODING=utf-8 python manage.py maketranslations && PYTHONIOENCODING=utf-8 python manage.py maketranslations --report   # 0 ta boʻsh
```
Brauzerda `/ru/` va `/en/` ni ochib menyu, tugmalar, jadval sarlavhalari tarjima qilinganini tekshiring; DB kontenti (`_ru/_en`) seed va importdan keladi, boʻsh joylar UZ ga qaytadi.

- [ ] **Step 5: Test oʻtadi, qamrov, commit**

```bash
PYTHONIOENCODING=utf-8 pytest -q --cov=core --cov-report=term-missing   # TOTAL ≥ 80%
git add -A && git commit -m "feat: uch til tarjimalari, sitemap.xml, robots.txt, SEO tekshiruv testlari"
```

---

### Task 13: Deploy tayyorligi — Dockerfile, README, prod tekshiruvi

**Files:**
- Create: `Dockerfile`, `README.md`
- Modify: `.env.example` (allaqachon), `config/settings.py` (prod cache)
- Test: qoʻlda — `DJANGO_DEBUG=0` bilan `check --deploy` va `collectstatic`.

- [ ] **Step 1: settings — prod cache**

`settings.py` da `CACHES` ni almashtiring (chegara hisoblagichi ishchilar oʻrtasida umumiy boʻlsin):
```python
if os.environ.get("DATABASE_URL"):
    CACHES = {"default": {"BACKEND": "django.core.cache.backends.db.DatabaseCache", "LOCATION": "cache_table"}}
else:
    CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
```

- [ ] **Step 2: Dockerfile**

```dockerfile
# TTT Audit sayti: Node vidjetlarni yigʻadi, Python Django'ni xizmat qiladi.
FROM node:24-alpine AS widgets
WORKDIR /w
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.14-slim
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
COPY --from=widgets /w/dist ./frontend/dist
# Statika build bosqichida yigʻiladi; bazasiz ishlashi uchun oʻrinbosar qiymatlar.
RUN DJANGO_SECRET_KEY=build-only DJANGO_DEBUG=0 python manage.py collectstatic --noinput
CMD sh -c "python manage.py migrate --noinput && \
           python manage.py createcachetable && \
           python manage.py seed_content && python manage.py import_tttaudit && \
           gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 3 --timeout 120 --access-logfile -"
```
Eslatma: `seed_content` va `import_tttaudit` `--force`siz — mavjud yozuvlarni **oʻzgartirmaydi** (admin tahrirlari saqlanadi); `seed_content` esa `update_or_create` bilan tahririy matnni yangilaydi — mijoz admin panelda xizmat matnini tahrirlashni boshlagach, `seed_content` ni CMD dan olib tashlang (README da yozilgan).

- [ ] **Step 3: README.md**

```markdown
# TTT Audit — sayt (tttaudit.uz)

Energoaudit va qurilishda nazorat oʻlchovi boʻyicha ekspert tashkilotining rasmiy sayti.
Django 5.2 SSR + React vidjetlari (Vite). Uch til: /uz/ /ru/ /en/.

## Lokal ishga tushirish

```bash
python -m venv .venv && .venv/Scripts/activate
pip install -r requirements-dev.txt
python manage.py migrate
python manage.py seed_content        # tahririy kontent (yoʻnalish, xizmat, qonun, maqola)
python manage.py import_tttaudit     # mijoz faktlari: hujjatlar, 39 mutaxassis, 143 loyiha
python manage.py createsuperuser
cd frontend && npm install && npm run build && cd ..
python manage.py runserver
```
Sayt: http://127.0.0.1:8000/uz/ · Admin: /admin/ · Testlar: `pytest -q --cov=core`

## Tuzilma
- `core/models.py` — kontent modellari (`_uz/_ru/_en` maydonlar, `{{ obj|tr:"title" }}`).
- `core/compliance.py`, `core/energy.py` — talab qoidalari va A–G chegaralari (server va React uchun yagona manba).
- `core/templates/core/` — sahifalar; `core/static/core/css/site.css` — dizayn tizimi.
- `frontend/src/` — uchta React vidjet; `npm run build` → `frontend/dist/widgets/`.
- `data/tttaudit/` — mijoz byulletenlaridan ajratilgan JSON va skanlar.
- `tools/prepare_logo.py` — `logo/` dagi PNG'dan sayt logotiplari.

## Tarjima
Interfeys satrlari: `python manage.py maketranslations --report` → `locale/translations.json` → `maketranslations`.

## Prod
`.env.example` → muhit oʻzgaruvchilari. `Dockerfile` gunicorn + whitenoise. PostgreSQL `DATABASE_URL`.
Murojaat chegarasi cache orqali: prodda `DatabaseCache` (`createcachetable` CMD da).
Telegram: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`.
Mijoz admin panelda xizmat matnlarini tahrirlay boshlagach `seed_content` ni Dockerfile CMD dan olib tashlang.

## Kontent qoidalari
Faqat energoaudit va qurilishda nazorat oʻlchovi. Manbasiz raqam yoʻq. Qonun faqat `verified_on` bilan chiqadi.
```

- [ ] **Step 4: Prod rejimida tekshiruv**

```bash
cd /d/tttaudit && DJANGO_DEBUG=0 DJANGO_SECRET_KEY=x DJANGO_ALLOWED_HOSTS=localhost DJANGO_SSL_REDIRECT=0 python manage.py check --deploy
DJANGO_DEBUG=0 DJANGO_SECRET_KEY=x python manage.py collectstatic --noinput   # staticfiles/widgets/widgets.js bor
docker build -t tttaudit . && docker run --rm -p 8000:8000 -e DJANGO_SECRET_KEY=x -e DJANGO_ALLOWED_HOSTS=localhost -e DJANGO_SSL_REDIRECT=0 -e DJANGO_DEBUG=0 tttaudit
```
`http://localhost:8000/uz/` ochiladi, statika va vidjetlar ishlaydi. Docker yoʻq boʻlsa — `collectstatic` va `gunicorn config.wsgi` lokalda.

- [ ] **Step 5: Commit**

```bash
git add -A && git commit -m "chore: Dockerfile, README, prod cache va deploy tekshiruvi"
```

---

## Mijozga topshirishdan oldin (kod emas, tekshiruv roʻyxati)

- [ ] Logotip natijasi (`logo-mark.png`) mijozga koʻrsatiladi — 3D renderdan tekis belgi qilingani maʼqulmi.
- [ ] Reestrda buyurtmachi nomlari ochiq — mijoz tasdigʻi.
- [ ] Xodim ismlarining lotin yozuvi — mijoz tekshiradi (admin: Rahbariyat va mutaxassislar).
- [ ] Asosiy e-pochta (`tttaudit@mail.ru` / `info@tttaudit.uz`) va ish soatlari — admin panelda toʻldiriladi.
- [ ] `LegalAct` dagi `verified_on=None` hujjatlar (A–G toifalari, nazorat oʻlchovi tartibi) — lex.uz tekshiruvidan keyin sana qoʻyiladi.
- [ ] Domen: tttaudit.uz DNS → yangi server; eski sayt oʻchiriladi.
