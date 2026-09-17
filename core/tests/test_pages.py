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
def test_direction_headcount_comes_from_site_settings(client):
    from core.models import SiteSettings

    site = SiteSettings.load()
    site.staff_energy, site.staff_supervision = 31, 17
    site.save()
    energy = client.get("/uz/xizmatlar/energoaudit/").content.decode()
    construction = client.get("/uz/xizmatlar/olchov-auditi/").content.decode()
    assert "31 nafar energoaudit mutaxassisi" in energy and "24 mutaxassis" not in energy
    assert "17 nafar texnik nazorat xodimi" in construction and "16 mutaxassis" not in construction
    assert "Специалистов по энергоаудиту: 31" in client.get("/ru/xizmatlar/energoaudit/").content.decode()


@pytest.mark.django_db
def test_energy_direction_hides_unverified_bands_and_fee(client):
    html = client.get("/uz/xizmatlar/energoaudit/").content.decode()
    assert '<span class="badge">A</span>' not in html and '<span class="badge">G</span>' not in html
    assert 'data-ladder="[]"' in html
    assert "energopasport talabi hisoblanadi" in html
    assert "0,3" not in html


@pytest.mark.django_db
def test_energy_direction_shows_bands_once_verified(client, monkeypatch):
    monkeypatch.setattr("core.energy.BANDS_VERIFIED", True)
    html = client.get("/uz/xizmatlar/energoaudit/").content.decode()
    assert '<span class="badge">A</span>' in html and '<span class="badge">G</span>' in html


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


@pytest.mark.django_db
def test_company_page(client):
    html = client.get("/uz/tashkilot/").content.decode()
    assert "1997" in html and "UZACE" in html and "ISO 27001" in html
    assert "Botirov" in html
    assert "filial" not in html.lower()
    assert "Buyurtmachilar orasida" not in html          # eski saytdan — mijoz tasdiqlaguncha yoʻq


@pytest.mark.django_db
def test_team_page_groups_by_department(client):
    html = client.get("/uz/tashkilot/mutaxassislar/").content.decode()
    assert "Rahbariyat va mutaxassislar" in html
    assert html.count('class="card person"') == 39      # 38 mutaxassis (takror birlashtirilgan) + direktor kartasi
    assert "Jami 50 xodim" in html and "Roʻyxatda: 38" in html
    assert "Listed: 38" in client.get("/en/tashkilot/mutaxassislar/").content.decode()
    assert "Energoaudit" in html and "Qurilishda nazorat oʻlchovi" in html
    assert "Jamoa" not in html
    # "== 1" emas: fotosurati bor har bir xodim nomi img alt'da HAM <b> ichida
    # takrorlanadi (bitta karta ichida 2 marta) — shu sababli karta sonini
    # <b> yorlig'i orqali sanaymiz: bitta kishi = bitta karta = bitta <b>.
    assert html.count("<b>Xudayberdiev Otabek Talipovich</b>") == 1


@pytest.mark.django_db
def test_requisites_page(client):
    html = client.get("/uz/tashkilot/rekvizitlar/").content.decode()
    assert "202216926" in html and "«TTTaudit» MChJ" in html
    assert "filial" not in html.lower()
    assert "Avisozlar" not in html                          # spec 3-qoida: Toshkent ofisi faqat aloqa sahifasida


@pytest.mark.django_db
def test_contact_and_request_pages(client):
    contact = client.get("/uz/aloqa/").content.decode()
    assert "Toshkent" in contact and "Yangiobod" in contact and 'data-react="lead-form"' in contact
    assert "Avisozlar" in contact
    request_page = client.get("/uz/murojaat/").content.decode()
    assert 'name="csrfmiddlewaretoken"' in request_page and 'enctype="multipart/form-data"' in request_page
    sent = client.get("/uz/murojaat/?sent=1").content.decode()
    assert "Murojaat qabul qilindi. Muhandis siz bilan bogʻlanadi." in sent
    assert "ish kuni" not in sent and "bepul" not in sent
