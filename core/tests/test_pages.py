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
