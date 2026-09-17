from pathlib import Path

DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist" / "widgets"


def test_widget_bundle_is_built():
    assert (DIST / "widgets.js").exists(), "cd frontend && npm run build"
    assert (DIST / "style.css").exists()
    css = (DIST / "style.css").read_text(encoding="utf-8")
    for cls in (".check", ".est", ".form", ".reqs", ".ladder", ".field"):
        assert cls in css, cls


def test_widget_bundle_has_ru_and_en_strings():
    """React vidjetlari (ComplianceCheck/EnergyEstimator/LeadForm) ichidagi
    matnlar `frontend/src/i18n.js` orqali uch tilda — bundle uz bilan bir
    qatorda ru/en satrlarni ham o'z ichiga olishi kerak (aks holda vidjetlar
    /ru/ va /en/ sahifalarda o'zbekcha chiqib qoladi)."""
    js = (DIST / "widgets.js").read_text(encoding="utf-8")
    assert "Отправить заявку" in js  # LeadForm/ComplianceCheck submit tugmasi — ru
    assert "Send a request" in js  # LeadForm/ComplianceCheck submit tugmasi — en
    assert "Soʻrov yuborish" in js  # xuddi shu tugma — uz (fallback / default til)
