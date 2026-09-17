"""Bosh sahifa bloklari uchun maʼlumot: faktlar tasmasi, hero sarlavhasi, vedomost namunasi."""
import re
from dataclasses import dataclass

from django.db.models import Count, Max, Min
from django.utils.translation import gettext_lazy as _

from .models import Direction, Project, SiteSettings, Stat, TeamMember

TEAM_STRIP_SIZE = 5            # direktordan tashqari kartalar soni
INSURANCE_FALLBACK_BN = "10"   # Stat jadvalida sugʻurta raqami boʻlmasa

# Taqqoslash vedomosti — NAMUNA: hajm va narxlar shartli, sahifada shunday yoziladi.
SHEET_ROWS = (
    (_("Monolit beton B25, poydevor"), "m³", 412.0, 386.5, 1_450_000),
    (_("Sement-qum suvoq, ichki devorlar"), "m²", 2340, 2115, 68_000),
    (_("Armatura A500C"), _("t"), 38.6, 38.6, 11_800_000),
    (_("Gidroizolyatsiya, tom"), "m²", 860, 702, 95_000),
    (_("Plastik deraza bloklari"), "m²", 214, 214, 1_250_000),
)


@dataclass(frozen=True)
class SheetRow:
    title: str
    unit: str
    doc: float
    fact: float
    price: int

    @property
    def diff(self) -> float:
        return round(self.fact - self.doc, 3)

    @property
    def diff_sum(self) -> int:
        return round(self.diff * self.price)


def sheet() -> dict:
    rows = [SheetRow(*row) for row in SHEET_ROWS]
    overstated = sum(-row.diff_sum for row in rows if row.diff_sum < 0)
    return {"rows": rows, "total": overstated}


def split_title(title: str, accent: str) -> tuple[str, str]:
    """Hero sarlavhasini ikki qismga ajratadi: ikkinchisi indigo rangda.

    Tartib: `hero_accent` toʻldirilgan boʻlsa — u; sarlavhada nuqta boʻlsa — birinchi
    nuqtadan keyingi qism; aks holda birinchi bogʻlovchidan («va», «и», "and") keyingi qism.
    """
    title, accent = (title or "").strip(), (accent or "").strip()
    if accent:
        return title, accent
    head, dot, tail = title.partition(".")
    if dot and tail.strip():
        return head + dot, tail.strip()
    match = re.search(r"\s(va|и|and)\s", title)
    if match:
        return title[: match.end()].rstrip(), title[match.end():]
    return title, ""


def _insurance_bn() -> str:
    for stat in Stat.objects.all():
        if "mlrd" in stat.value.lower():
            digits = re.search(r"\d+(?:[.,]\d+)?", stat.value)
            if digits:
                return digits.group(0)
    return INSURANCE_FALLBACK_BN


def facts(site: SiteSettings) -> dict:
    years = Project.objects.aggregate(first=Min("year"), last=Max("year"))
    counts = dict(
        Direction.objects.annotate(n=Count("projects")).values_list("accent", "n")
    )
    return {
        "founded": site.founded_year,
        "experience": site.experience_years,
        "staff_total": site.staff_total,
        "staff_energy": site.staff_energy,
        "staff_supervision": site.staff_supervision,
        "projects": Project.objects.count(),
        "projects_energy": counts.get(Direction.ACCENT_AMBER, 0),
        "projects_construction": counts.get(Direction.ACCENT_STEEL, 0),
        "year_first": years["first"],
        "year_last": years["last"],
        "insurance_bn": _insurance_bn(),
    }


def team_strip():
    """Direktor (bazada birinchi) va yana TEAM_STRIP_SIZE kishi."""
    return TeamMember.objects.all()[:TEAM_STRIP_SIZE + 1]


# Xizmat qatoridagi qisqa mono belgi (xizmatda `duration` toʻldirilmagan boʻlsa)
SERVICE_TAGS = {
    "majburiy": _("reestr subyektlari"),
    "energopasport": _("200 m² dan katta bino"),
    "termografiya": _("issiqlik yoʻqotishlari"),
    "ekspress": _("dastlabki baho"),
    "nazorat-olchovi": _("obyektda, tomonlar bilan"),
    "smeta-auditi": _("obyektga chiqmasdan"),
    "texnik-nazorat": _("qurilish davomida"),
    "nizo": _("uchinchi tomon sifatida"),
}
