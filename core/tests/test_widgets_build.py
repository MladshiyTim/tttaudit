from pathlib import Path

DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist" / "widgets"


def test_widget_bundle_is_built():
    assert (DIST / "widgets.js").exists(), "cd frontend && npm run build"
    assert (DIST / "style.css").exists()
    css = (DIST / "style.css").read_text(encoding="utf-8")
    for cls in (".check", ".est", ".form", ".reqs", ".ladder", ".field"):
        assert cls in css, cls
