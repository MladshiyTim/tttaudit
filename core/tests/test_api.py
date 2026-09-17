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
