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
