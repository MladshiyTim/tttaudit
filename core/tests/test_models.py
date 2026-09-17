import pytest
from django.utils import translation

from core import compliance, energy
from core.models import Direction, SiteSettings


@pytest.mark.django_db
def test_tr_falls_back_to_uz_when_translation_empty():
    d = Direction.objects.create(slug="tr-fallback-check", title_uz="Energoaudit", title_ru="", summary_uz="x")
    with translation.override("ru"):
        assert d.tr("title") == "Energoaudit"
    d.title_ru = "Энергоаудит"
    with translation.override("ru"):
        assert d.tr("title") == "Энергоаудит"


@pytest.mark.django_db
def test_site_settings_load_creates_single_row():
    # seed_content/import_tttaudit already create the singleton for the test session;
    # delete it here (inside this test's transaction, so it doesn't leak to other
    # tests) to exercise the "creates the row when the table is empty" branch.
    SiteSettings.objects.all().delete()
    assert SiteSettings.objects.count() == 0
    site = SiteSettings.load()
    assert site.org_name_uz == "«TTTaudit» MChJ"
    assert SiteSettings.load().pk == site.pk


def test_energy_category_bands():
    assert energy.category_for(30) == "A"
    assert energy.category_for(100) == "D"
    assert energy.category_for(500) == "G"
    assert energy.category_for(None) is None


def test_compliance_registry_threshold_triggers_mandatory_audit():
    result = compliance.evaluate(object_kind="industrial", annual_kwh=5_000_000)
    assert "mandatory_energy_audit" in [r.key for r in result.requirements]


def test_compliance_budget_construction_gives_fee_cap():
    result = compliance.evaluate(object_kind="construction", funding="budget", estimate_value="1000000")
    assert result.estimated_fee == "3 000"
