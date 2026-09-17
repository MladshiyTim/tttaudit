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
    assert data["ok"] and data["estimated_fee"] == "15 000"
    assert data["requirements"][0]["service_url"].endswith("/xizmatlar/olchov-auditi/nazorat-olchovi/")


@pytest.mark.django_db
def test_energy_api(client):
    assert client.get("/uz/api/energy-estimate/", {"area": "1000", "kwh": "100000"}).json()["category"] == "D"
    assert client.get("/uz/api/energy-estimate/", {"area": "x"}).status_code == 400
