import pytest
from django.utils.html import escape

from core.models import SiteSettings

LAT, LON = "40.406844", "71.782245"
EMBED = f"https://yandex.uz/map-widget/v1/?ll={LON}%2C{LAT}&z=17&pt={LON},{LAT},pm2rdm&lang="
BUTTONS = (
    f"https://yandex.uz/maps/?ll={LON},{LAT}&z=17&pt={LON},{LAT},pm2rdm",
    f"https://yandex.uz/maps/?rtext=~{LAT},{LON}&rtt=auto",
    f"https://maps.google.com/maps?q={LAT},{LON}",
)


@pytest.mark.django_db
def test_import_sets_yandex_office_coordinates():
    site = SiteSettings.load()
    assert (site.map_lat, site.map_lng) == (40.406844, 71.782245)


@pytest.mark.django_db
@pytest.mark.parametrize("path", ["/uz/aloqa/", "/uz/"])
def test_office_map_iframe_and_buttons(client, path):
    html = client.get(path).content.decode()
    assert f'src="{escape(EMBED)}ru_RU"' in html
    assert 'loading="lazy"' in html and 'referrerpolicy="no-referrer-when-downgrade"' in html
    for url, label in zip(BUTTONS, ("Yandex Xarita", "Marshrut", "Google Xarita")):
        assert f'href="{escape(url)}" target="_blank" rel="noopener noreferrer">{label}</a>' in html
    assert "openstreetmap" not in html


@pytest.mark.django_db
def test_home_contact_section_lists_phone_once(client):
    html = client.get("/uz/").content.decode()
    start = html.index('id="aloqa"')
    section = html[start:html.index("</section>", start)]
    site = SiteSettings.load()
    assert section.count(f">{site.phone}<") == 1 and section.count(f">{site.email}<") == 1
    assert "Avisozlar" not in section


@pytest.mark.django_db
def test_office_map_english_and_russian_labels(client):
    en = client.get("/en/aloqa/").content.decode()
    assert f"{escape(EMBED)}en_US" in en and ">Yandex Maps<" in en and ">Route<" in en and ">Google Maps<" in en
    ru = client.get("/ru/aloqa/").content.decode()
    assert f"{escape(EMBED)}ru_RU" in ru and ">Яндекс Карты<" in ru and ">Маршрут<" in ru


@pytest.mark.django_db
def test_no_office_map_without_coordinates(client):
    site = SiteSettings.load()
    site.map_lat = site.map_lng = None
    site.save()
    for path in ("/uz/aloqa/", "/uz/"):
        html = client.get(path).content.decode()
        assert "map-widget" not in html and 'class="omap"' not in html
    assert "Yangiobod" in client.get("/uz/").content.decode()   # manzil baribir bor
