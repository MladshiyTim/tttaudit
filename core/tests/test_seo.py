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


@pytest.mark.django_db
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
    assert "uchun yetishmaydi" not in out, out
    for lang in ("ru", "en"):
        match = re.search(rf"{lang}: (\d+)/(\d+) tarjima qilingan", out)
        assert match, out
        done, total = match.groups()
        assert done == total, out


@pytest.mark.django_db
def test_ru_interface_is_translated_not_uzbek(client):
    ru_home = client.get("/ru/").content.decode()
    assert "Murojaat yuborish" not in ru_home
    assert "Отправить обращение" in ru_home

    en_home = client.get("/en/").content.decode()
    assert "Send a request" in en_home


@pytest.mark.django_db
def test_percent_sign_survives_translation(client, tmp_path):
    """`{% translate %}` ichidagi `%` Django tomonidan `%%` ga escape qilinadi —
    tarjima qiluvchi buni to'g'ri hisoblamasa, satr hech qachon topilmaydi va
    ru/en sahifada oʻzbekcha qolib ketadi. (Saytdagi yagona `%` li satr — 0,3% —
    olib tashlangan, shu sababli yigʻuvchi vaqtinchalik shablonda tekshiriladi.)"""
    from core.management.commands.maketranslations import extract

    templates = tmp_path / "core" / "templates"
    templates.mkdir(parents=True)
    (templates / "t.html").write_text(
        '{% translate "Chegara 5% gacha" %}{% blocktranslate with n=x %}{{ n }}% ulush{% endblocktranslate %}',
        encoding="utf-8",
    )
    found = extract(tmp_path)
    assert "Chegara 5%% gacha" in found and "%(n)s%% ulush" in found

    html = client.get("/ru/xizmatlar/energoaudit/").content.decode()
    assert "Byudjet mablagʻi hisobiga" not in html


@pytest.mark.django_db
def test_registry_ru_avoids_bad_number_agreement(client):
    """Oʻzgaruvchan sonlar otdan oldin turgan ruscha satrlar har qanday son
    uchun grammatik boʻlishi kerak — «Всего 143 работ» kabi kelishik xatosi
    boʻlmasin (143 -> genitiv birlik «работы» talab qiladi, koʻplik «работ» emas)."""
    html = client.get("/ru/reestr/").content.decode()
    assert "Всего 143 работ" not in html
    assert "Работ в реестре:" in html
    assert "Найдено:" in html
