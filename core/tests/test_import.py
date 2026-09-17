import pytest
from django.core.management import call_command

from core.models import (
    Branch, Client, Credential, Direction, Instrument, Project, Service,
    SiteSettings, Stat, TeamMember,
)


@pytest.mark.django_db
def test_seed_content_creates_two_directions_and_eight_services():
    assert set(Direction.objects.values_list("slug", flat=True)) == {"energoaudit", "olchov-auditi"}
    assert Service.objects.count() == 8
    assert not Service.objects.filter(slug__in=["msfo", "konsalting", "malaka-oshirish"]).exists()


@pytest.mark.django_db
def test_import_loads_client_facts():
    site = SiteSettings.load()
    assert site.tin == "202216926"
    assert site.director_uz.startswith("Botirov")
    assert site.seo_title_uz == "Energoaudit va qurilishda nazorat oʻlchovi — TTT Audit, Fargʻona"
    assert Branch.objects.count() == 2
    assert Credential.objects.count() == 8
    assert Credential.objects.filter(kind="insurance").exists()
    assert Instrument.objects.count() == 5
    assert Stat.objects.count() == 4
    assert TeamMember.objects.count() == 38
    assert TeamMember.objects.filter(dept="energy").count() == 24
    assert TeamMember.objects.exclude(photo="").count() >= 30
    assert "filial" not in Branch.objects.get(is_head_office=False).address_uz.lower()
    assert Project.objects.count() == 143
    assert Project.objects.filter(direction__slug="olchov-auditi").count() == 95
    assert Client.objects.count() > 0


@pytest.mark.django_db
def test_import_is_idempotent_without_force():
    before = Project.objects.count()
    call_command("import_tttaudit")
    assert Project.objects.count() == before


@pytest.mark.django_db
def test_import_force_recreates_tables_with_same_counts():
    models = (Branch, Client, Credential, Instrument, Project, Stat, TeamMember)
    before = {model.__name__: model.objects.count() for model in models}
    call_command("import_tttaudit", "--force")
    assert {model.__name__: model.objects.count() for model in models} == before
    scans = Credential.objects.exclude(scan="")
    assert scans.exists() and all(c.scan.storage.exists(c.scan.name) for c in scans)
