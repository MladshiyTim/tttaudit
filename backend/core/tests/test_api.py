import time

import pytest
from django.conf import settings
from django.core.cache import cache
from django.core.management import call_command
from django.test import RequestFactory, override_settings

from core import throttle
from core.models import Lead


def test_throttle_allows_up_to_limit_then_blocks():
    assert all(throttle.allow("t:1", limit=3, window=60) for _ in range(3))
    assert throttle.allow("t:1", limit=3, window=60) is False
    assert throttle.allow("t:2", limit=3, window=60) is True


def test_throttle_recovers_from_legacy_non_tuple_cache_value():
    """Eski formatdagi (yalang'och int) qiymat TypeError bilan yiqilmasin — yangi oyna sifatida olinsin."""
    cache.set("throttle:legacy:1", 3, timeout=3600)
    assert throttle.allow("legacy:1", limit=5, window=3600) is True
    stored = cache.get("throttle:legacy:1")
    assert isinstance(stored, tuple) and len(stored) == 2


@pytest.mark.django_db
def test_throttle_window_keeps_expiry_under_database_cache():
    """DatabaseCache'ning incr() fallback'i (get+set, DEFAULT_TIMEOUT=300s) oynani
    qisqartirmasligi kerak — hisoblagich oʻzining expires_at'ini saqlaydi."""
    with override_settings(CACHES={"default": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "test_cache_table",
    }}):
        call_command("createcachetable")
        from django.core.cache import cache

        window = 3600
        now = time.time()
        assert throttle.allow("dbcache:1", limit=3, window=window) is True
        assert throttle.allow("dbcache:1", limit=3, window=window) is True
        assert throttle.allow("dbcache:1", limit=3, window=window) is True
        assert throttle.allow("dbcache:1", limit=3, window=window) is False

        count, expires_at = cache.get("throttle:dbcache:1")
        assert count == 4
        assert expires_at >= now + window - 5


def test_client_ip_ignores_x_real_ip_by_default():
    request = RequestFactory().get("/", REMOTE_ADDR="127.0.0.1", HTTP_X_REAL_IP="203.0.113.5")
    assert throttle.client_ip(request) == "127.0.0.1"


def test_client_ip_uses_x_real_ip_header_when_trusted():
    request = RequestFactory().get("/", REMOTE_ADDR="127.0.0.1", HTTP_X_REAL_IP="203.0.113.5")
    with override_settings(TRUST_X_REAL_IP=True):
        assert throttle.client_ip(request) == "203.0.113.5"


@pytest.mark.django_db
def test_lead_post_creates_lead_and_returns_json(client, monkeypatch):
    sent = []
    monkeypatch.setattr("core.views.notify_telegram", lambda lead: sent.append(lead) or True)
    response = client.post("/uz/api/lead/", {"name": "Test", "phone": "+998901234567", "note": "Bino"},
                           HTTP_X_REQUESTED_WITH="XMLHttpRequest")
    assert response.status_code == 200 and response.json()["ok"] is True
    assert Lead.objects.count() == 1 and Lead.objects.get().language == "uz"
    assert len(sent) == 1
    assert sent[0].pk == Lead.objects.get().pk


@pytest.mark.django_db
def test_lead_post_invalid_phone_returns_400(client):
    response = client.post("/uz/api/lead/", {"name": "Test", "phone": "12"}, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
    assert response.status_code == 400 and "phone" in response.json()["errors"]


@pytest.mark.django_db
def test_lead_post_without_js_redirects(client):
    response = client.post("/uz/api/lead/", {"name": "Test", "phone": "+998901234567"})
    assert response.status_code == 302 and response["Location"].endswith("/uz/murojaat/?sent=1")


@pytest.mark.django_db
def test_lead_rate_limit(client, monkeypatch):
    monkeypatch.setattr("core.views.notify_telegram", lambda lead: True)
    for _ in range(settings.LEAD_RATE_LIMIT):
        response = client.post("/uz/api/lead/", {"name": "T", "phone": "+998901234567"}, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        assert response.status_code == 200
    response = client.post("/uz/api/lead/", {"name": "T", "phone": "+998901234567"}, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
    assert response.status_code == 429


@pytest.mark.django_db
def test_lead_rate_limit_ignores_spoofed_x_real_ip_by_default(client, monkeypatch):
    """TRUST_X_REAL_IP=0 (default) boʻlsa, har xil X-Real-IP yuborilsa ham bitta paket
    baham koʻriladi — chunki REMOTE_ADDR (test klientida doim bir xil) ishlatiladi."""
    monkeypatch.setattr("core.views.notify_telegram", lambda lead: True)
    for i in range(settings.LEAD_RATE_LIMIT):
        response = client.post(
            "/uz/api/lead/", {"name": "T", "phone": "+998901234567"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest", HTTP_X_REAL_IP=f"10.0.0.{i}",
        )
        assert response.status_code == 200
    response = client.post(
        "/uz/api/lead/", {"name": "T", "phone": "+998901234567"},
        HTTP_X_REQUESTED_WITH="XMLHttpRequest", HTTP_X_REAL_IP="10.0.0.99",
    )
    assert response.status_code == 429


@pytest.mark.django_db
def test_compliance_api_returns_requirements_with_service_links(client):
    response = client.get("/uz/api/compliance/", {"object_kind": "construction", "funding": "budget", "estimate_value": "5000000"})
    data = response.json()
    assert data["ok"] and data["estimated_fee"] is None     # 0,3% chegarasi tasdiqlanmagan
    assert all("0,3" not in item["note"] for item in data["requirements"])
    assert data["requirements"][0]["service_url"].endswith("/xizmatlar/olchov-auditi/nazorat-olchovi/")


@pytest.mark.django_db
def test_energy_api_hides_unverified_category(client):
    data = client.get("/uz/api/energy-estimate/", {"area": "1000", "kwh": "100000"}).json()
    assert data == {"ok": True, "specific": 100.0, "category": None, "passport_required": True, "threshold": 200}
    assert client.get("/uz/api/energy-estimate/", {"area": "x"}).status_code == 400


@pytest.mark.django_db
def test_energy_api_shows_category_once_bands_verified(client, monkeypatch):
    monkeypatch.setattr("core.energy.BANDS_VERIFIED", True)
    assert client.get("/uz/api/energy-estimate/", {"area": "1000", "kwh": "100000"}).json()["category"] == "D"


@pytest.mark.django_db
def test_energy_api_passport_threshold_is_strictly_greater(client):
    at = client.get("/uz/api/energy-estimate/", {"area": "200", "kwh": "10000"}).json()
    above = client.get("/uz/api/energy-estimate/", {"area": "201", "kwh": "10000"}).json()
    assert at["passport_required"] is False and above["passport_required"] is True


@pytest.mark.django_db
@pytest.mark.parametrize("params", [{"area": "1000", "kwh": "nan"}, {"area": "inf", "kwh": "1000"},
                                    {"area": "-5", "kwh": "1000"}, {"area": "1000", "kwh": "-1"}])
def test_energy_api_rejects_non_finite_or_negative(client, params):
    assert client.get("/uz/api/energy-estimate/", params).status_code == 400


def test_compliance_passport_threshold_and_hidden_category():
    from core import compliance

    at = compliance.evaluate(area_m2="200", annual_kwh="20000")
    above = compliance.evaluate(area_m2="201", annual_kwh="20000")
    assert "energy_passport" not in [r.key for r in at.requirements]
    assert "energy_passport" in [r.key for r in above.requirements]
    assert above.specific_kwh == 99.5 and above.energy_category is None


@pytest.mark.django_db
def test_lead_json_message_has_no_unsourced_promise(client, monkeypatch):
    monkeypatch.setattr("core.views.notify_telegram", lambda lead: True)
    message = client.post("/uz/api/lead/", {"name": "T", "phone": "+998901234567"},
                          HTTP_X_REQUESTED_WITH="XMLHttpRequest").json()["message"]
    assert message == "Murojaat qabul qilindi. Muhandis siz bilan bogʻlanadi."


def _upload(name, content=b"%PDF-1.4 test", content_type="application/pdf"):
    from django.core.files.uploadedfile import SimpleUploadedFile

    return SimpleUploadedFile(name, content, content_type=content_type)


@pytest.mark.django_db
def test_lead_rejects_disallowed_extension(client):
    response = client.post("/uz/api/lead/", {"name": "T", "phone": "+998901234567", "attachment": _upload("virus.exe")},
                           HTTP_X_REQUESTED_WITH="XMLHttpRequest")
    assert response.status_code == 400 and "attachment" in response.json()["errors"]
    assert Lead.objects.count() == 0


@pytest.mark.django_db
def test_lead_rejects_oversized_attachment(client, settings):
    settings.LEAD_MAX_UPLOAD_BYTES = 10
    response = client.post("/uz/api/lead/", {"name": "T", "phone": "+998901234567",
                                             "attachment": _upload("smeta.pdf", b"x" * 11)},
                           HTTP_X_REQUESTED_WITH="XMLHttpRequest")
    assert response.status_code == 400 and "attachment" in response.json()["errors"]


@pytest.mark.django_db
def test_lead_accepts_small_pdf_under_leads(client, monkeypatch):
    monkeypatch.setattr("core.views.notify_telegram", lambda lead: True)
    response = client.post("/uz/api/lead/", {"name": "T", "phone": "+998901234567", "attachment": _upload("smeta.pdf")},
                           HTTP_X_REQUESTED_WITH="XMLHttpRequest")
    assert response.status_code == 200
    lead = Lead.objects.get()
    assert lead.attachment.name.startswith("leads/") and lead.attachment.name.endswith(".pdf")
    assert str(settings.MEDIA_ROOT) in lead.attachment.path


@pytest.mark.django_db
def test_lead_invalid_post_without_js_redirects_with_error(client):
    response = client.post("/uz/api/lead/", {"name": "", "phone": "12"})
    assert response.status_code == 302 and response["Location"].endswith("/uz/murojaat/?error=1")


@pytest.mark.django_db
def test_lead_rate_limit_without_js_redirects(client, monkeypatch):
    monkeypatch.setattr("core.views.throttle.allow", lambda *args: False)
    response = client.post("/uz/api/lead/", {"name": "T", "phone": "+998901234567"})
    assert response.status_code == 302 and response["Location"].endswith("/uz/murojaat/?error=limit")


def _keys(client, **params):
    data = client.get("/uz/api/compliance/", params).json()
    return [r["key"] for r in data["requirements"]], data


@pytest.mark.django_db
def test_compliance_api_funding_and_dispute_branches(client):
    keys, data = _keys(client, object_kind="construction", funding="credit")
    assert keys == ["bank_measurement"] and data["requirements"][0]["severity"] == "likely"

    keys, data = _keys(client, object_kind="construction", funding="own")
    assert keys == ["voluntary_measurement"] and data["requirements"][0]["severity"] == "optional"

    keys, data = _keys(client, object_kind="building", has_dispute="1")
    assert keys == ["dispute_opinion"]
    assert data["requirements"][0]["service_url"].endswith("/xizmatlar/olchov-auditi/nizo/")


@pytest.mark.django_db
def test_compliance_api_notes_when_nothing_applies(client):
    keys, data = _keys(client, object_kind="building")
    assert keys == [] and len(data["notes"]) == 1
    assert "aniq majburiyat koʻrinmadi" in data["notes"][0]

    keys, data = _keys(client, object_kind="industrial", annual_kwh="1000")
    assert keys == [] and any("reestr mezonidan past" in note for note in data["notes"])
