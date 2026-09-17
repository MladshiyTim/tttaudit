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
    assert "Elektron mikrometr" in html
    assert 'data-react="energy-estimator"' not in html


@pytest.mark.django_db
def test_service_page_and_404(client):
    response = client.get("/uz/xizmatlar/olchov-auditi/nazorat-olchovi/")
    assert response.status_code == 200
    assert "Nazorat oʻlchovi".encode() in response.content
    assert client.get("/uz/xizmatlar/olchov-auditi/yoq-xizmat/").status_code == 404


@pytest.mark.django_db
def test_registry_paginates_and_filters(client):
    html = client.get("/uz/reestr/").content.decode()
    assert "143" in html                                   # jami soni sarlavhada
    assert html.count("<tr>") == 26                         # 1 sarlavha + 25 qator
    assert 'class="pager"' in html                          # sahifalash bloki
    assert '<span aria-current="page">1</span>' in html     # joriy sahifa pagerda
    assert "?page=2" in html                                 # keyingi sahifaga havola

    energy = client.get("/uz/reestr/?d=energoaudit").content.decode()
    assert "Topildi: 48 ta" in energy
    assert '<span class="badge">Qurilishda nazorat oʻlchovi</span>' not in energy

    year = client.get("/uz/reestr/?y=2023").content.decode()
    assert "Topildi: 20 ta" in year

    search = client.get("/uz/reestr/?q=AGROBANK").content.decode()
    assert "AGROBANK" in search and "Topildi: 1 ta" in search

    assert client.get("/uz/reestr/?page=999").status_code == 200   # oxirgi sahifaga tushadi

    assert "Tozalash" not in client.get("/uz/reestr/?y=abc").content.decode()
