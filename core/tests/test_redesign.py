"""v3 vizual tili: navigatsiya tartibi, faktlar tasmasi, hero tablari, suratlar, vedomost."""
import re

import pytest
from django.template import Context, Template
from django.utils import translation

from core import home
from core.models import Project, SiteSettings, Stat

NAV_ORDER = {
    "uz": ["Xizmatlar", "Reestr", "Hujjatlar", "Qonunchilik", "Tashkilot", "Jamoa", "Yangiliklar", "Aloqa"],
    "ru": ["Услуги", "Реестр", "Документы", "Законодательство", "Организация", "Команда", "Новости", "Контакты"],
    "en": ["Services", "Registry", "Documents", "Legislation", "Organisation", "Team", "News", "Contact"],
}


def _nav_labels(html):
    nav = re.search(r'<nav class="nav" id="nav"[^>]*>(.*?)</nav>', html, re.S).group(1)
    return re.findall(r'<a href="[^"]+"(?: aria-current="page")?>([^<]+)</a>', nav)


def _section(html, marker):
    start = html.index(marker)
    return html[start:html.index("</section>", start)]


@pytest.mark.django_db
@pytest.mark.parametrize("lang", ["uz", "ru", "en"])
def test_nav_has_team_right_after_organisation(client, lang):
    labels = _nav_labels(client.get(f"/{lang}/").content.decode())
    assert labels == NAV_ORDER[lang]
    assert labels.index(NAV_ORDER[lang][5]) == labels.index(NAV_ORDER[lang][4]) + 1


@pytest.mark.django_db
def test_team_link_points_to_team_page_and_footer_says_jamoa(client):
    html = client.get("/uz/").content.decode()
    assert '<a href="/uz/tashkilot/mutaxassislar/">Jamoa</a>' in html
    assert "Rahbariyat va mutaxassislar</a>" not in html          # futerda ham «Jamoa»
    assert html.count('class="nav-toggle"') == 1


@pytest.mark.django_db
def test_home_facts_band_uses_database_numbers(client):
    site = SiteSettings.load()
    site.founded_year, site.experience_years = 1996, 30
    site.staff_total, site.staff_energy, site.staff_supervision = 57, 26, 18
    site.save()
    Stat.objects.filter(value__icontains="mlrd").update(value="12 mlrd")

    facts = _section(client.get("/uz/").content.decode(), '<section class="facts"')
    assert '<b class="num">1996</b>' in facts and "30 yillik tajriba" in facts
    assert '<b class="num">57</b>' in facts and "26 energoaudit · 18 texnik nazorat" in facts
    assert f'<b class="num">{Project.objects.count()}</b>' in facts and "2019–2025" in facts
    assert '<b class="num">12 mlrd</b>' in facts

    en = _section(client.get("/en/").content.decode(), '<section class="facts"')
    assert '<b class="num">12 bn</b>' in en and "UZS professional liability insurance" in en


@pytest.mark.django_db
def test_insurance_fact_falls_back_when_stat_missing():
    Stat.objects.filter(value__icontains="mlrd").delete()
    assert home.facts(SiteSettings.load())["insurance_bn"] == home.INSURANCE_FALLBACK_BN


@pytest.mark.django_db
def test_hero_practice_tabs_work_without_js(client):
    hero = _section(client.get("/uz/").content.decode(), '<section class="hero"')
    assert hero.count('class="prac__tab"') == 2
    assert '<a class="prac__tab" href="#prac-energoaudit"' in hero and 'href="#prac-olchov-auditi"' in hero
    panels = re.findall(r'<div class="prac__panel" id="(prac-[a-z-]+)"([^>]*)>', hero)
    assert [p[0] for p in panels] == ["prac-energoaudit", "prac-olchov-auditi"]
    assert all("hidden" not in attrs for _, attrs in panels)          # ikkala panel JS'siz koʻrinadi
    assert "VM qarori № 673" in hero and "litsenziyasi № 518159" in hero
    assert "Energetik pasport" in hero and "Nazorat oʻlchovi dalolatnomasi" in hero


@pytest.mark.django_db
def test_office_photos_have_dimensions_and_alt(client):
    html = client.get("/uz/").content.decode()
    images = re.findall(r'<img [^>]*office-(?:hero|entrance)[^>]*>', html)
    assert len(images) == 2
    for tag in images:
        assert re.search(r'width="\d+"', tag) and re.search(r'height="\d+"', tag), tag
        assert re.search(r'alt="[^"]{10,}"', tag), tag
        assert "srcset=" in tag and "sizes=" in tag and "loading=" in tag


@pytest.mark.django_db
def test_home_document_viewer_previews_first_and_links_to_credentials(client):
    docs = _section(client.get("/uz/").content.decode(), '<section class="sec sec--tint" id="hujjatlar"')
    panels = re.findall(r'<article class="dview" id="cred-\d+" data-doc-panel( hidden)?>', docs)
    assert len(panels) == 8 and panels[0] == "" and all(p == " hidden" for p in panels[1:])
    assert docs.count('href="/uz/hujjatlar/#cred-') == 8


@pytest.mark.django_db
def test_home_team_strip_starts_with_director(client):
    team = _section(client.get("/uz/").content.decode(), '<section class="sec" id="jamoa"')
    people = re.findall(r'data-person="([^"]+)"', team)
    assert people[0] == "director" and len(people) == home.TEAM_STRIP_SIZE + 1
    assert "Jami 50 xodim: 24 energoaudit, 16 texnik nazorat." in team


@pytest.mark.django_db
def test_home_keeps_content_rules(client):
    for lang in ("uz", "ru", "en"):
        html = client.get(f"/{lang}/").content.decode()
        assert "auditorlik tashkiloti" not in html.lower()
        assert "bepul" not in html and "0,3" not in html
        assert "Avisozlar" not in html                                   # Toshkent ofisi faqat aloqa sahifasida
        assert '<span class="badge">A</span>' not in html


def test_split_title_variants():
    assert home.split_title("Energoaudit va qurilishda nazorat oʻlchovi", "") == (
        "Energoaudit va", "qurilishda nazorat oʻlchovi")
    assert home.split_title("Энергоаудит и контрольный обмер в строительстве", "") == (
        "Энергоаудит и", "контрольный обмер в строительстве")
    assert home.split_title("Energy audit and construction control measurement", "")[1] == (
        "construction control measurement")
    assert home.split_title("Ekspertiza. Obyektda, asbob bilan.", "") == ("Ekspertiza.", "Obyektda, asbob bilan.")
    assert home.split_title("Energoaudit", "Obyektda.") == ("Energoaudit", "Obyektda.")
    assert home.split_title("Energoaudit", "") == ("Energoaudit", "")


@pytest.mark.django_db
def test_hero_accent_from_settings_is_used(client):
    site = SiteSettings.load()
    site.hero_accent_uz = "Obyektda, asbob bilan."
    site.save()
    html = client.get("/uz/").content.decode()
    assert "<em>Obyektda, asbob bilan.</em>" in html
    assert "<em>Obyektda, asbob bilan.</em>" not in client.get("/en/").content.decode()


def test_sample_sheet_totals_match_v3():
    sheet = home.sheet()
    assert len(sheet["rows"]) == 5
    assert [row.diff_sum for row in sheet["rows"]] == [-36_975_000, -15_300_000, 0, -15_010_000, 0]
    assert sheet["total"] == 67_285_000


def test_groupnum_filter_is_locale_aware():
    template = Template('{% load sitetags %}{{ a|groupnum }}|{{ b|groupnum:"sign" }}|{{ c|groupnum:"sign" }}|{{ d|groupnum }}')
    context = Context({"a": 1450000, "b": -25.5, "c": 3, "d": "x"})
    with translation.override("uz"):
        assert template.render(context) == "1 450 000|−25,5|+3|x"
    with translation.override("en"):
        assert template.render(context) == "1 450 000|−25.5|+3|x"


def test_nav_toggle_hidden_on_desktop_regardless_of_rule_order():
    from pathlib import Path

    css = (Path(__file__).resolve().parents[1] / "static" / "core" / "css" / "site.css").read_text(encoding="utf-8")
    assert ".hdr .nav-toggle{display:none" in css
    assert "Inter" not in css and "IBM Plex Sans Condensed" in css
