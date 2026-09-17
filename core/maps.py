"""Loyihalar xaritasi: hudud boʻyoqi, shahar belgilari, yon panel va JS uchun maʼlumot.

Xaritaga faqat ochiq (`is_public`) joylar chiqadi. Koordinatali joy — shahar belgisi; koordinatasiz joy
faqat hudud boʻyoqida hisoblanadi. Barcha sonlar — alohida loyihalar soni (bir loyiha bir necha
hududda boʻlsa, har birida bir marta).
"""
from dataclasses import dataclass, field

from django.urls import reverse
from django.utils.translation import get_language, gettext as _

from .geo.projection import HEIGHT, WIDTH, project
from .geo.regions import REGIONS, region_name, uzmap
from .models import Direction, Project, ProjectLocation

DEPT_ENERGY = "energy"
DEPT_CONSTRUCTION = "construction"
DEPT_ACCENTS = {Direction.ACCENT_AMBER: DEPT_ENERGY, Direction.ACCENT_STEEL: DEPT_CONSTRUCTION}
DEPTS = (DEPT_ENERGY, DEPT_CONSTRUCTION)
DEPT_PARAM = "yo"
REGION_PARAM = "hudud"

# Hudud boʻyoqining 3 pogʻonasi: loyihalar soni shu chegaradan boshlab (1-, 2-, 3-pogʻona)
SHADE_STEPS = (1, 3, 10)
TOP_REGIONS = 6
# Shu masofadan (holst birligi, ≈1 km) yaqin shaharlar bitta belgi: aks holda biri ikkinchisining tagida qoladi
MERGE_DISTANCE = 3

# Nomi yozib qoʻyiladigan shaharlar (viloyat markazlari); qolganlari — faqat tooltip'da
LABELLED_CITIES = {
    "Toshkent", "Fargʻona", "Andijon", "Namangan", "Samarqand", "Buxoro", "Navoiy", "Qarshi", "Termiz",
    "Jizzax", "Urganch", "Guliston", "Nukus", "Qoʻqon", "Margʻilon",
}
# Tor ekranda ham qoladigan yozuvlar (qolganlari u yerda yashiriladi — belgilar ustiga chiqadi)
NARROW_LABELS = {"Toshkent", "Fargʻona", "Samarqand", "Buxoro", "Urganch", "Qarshi", "Termiz", "Nukus"}
# Fargʻona vodiysi zich: yozuvlar belgilar ustiga chiqmasligi uchun qoʻlda siljitiladi.
# (dx, dy, anchor) holst birliklarida; standart — belgidan oʻngda.
LABEL_OFFSETS = {
    "Fargʻona": (0, 30, "middle"),
    "Qoʻqon": (-9, 14, "end"),
    "Margʻilon": (-9, -8, "end"),
    "Andijon": (0, -13, "middle"),
    "Namangan": (-9, -6, "end"),
    "Toshkent": (-9, -6, "end"),
    "Termiz": (9, -4, "start"),
}
DEFAULT_OFFSET = (9, 4, "start")


def shade_level(count: int) -> int:
    return sum(1 for step in SHADE_STEPS if count >= step)


def dept_of(project) -> str:
    return DEPT_ACCENTS.get(project.direction.accent, "") if project.direction_id else ""


@dataclass
class Marker:
    key: str
    name: str
    region: str
    x: float
    y: float
    ids: set = field(default_factory=set)


def _city_name(location) -> str:
    return location.tr("city") or location.city_uz


def _collect(queryset):
    """Ochiq joylardan: loyihalar, hudud → loyiha id'lari, shahar belgilari."""
    locations = (ProjectLocation.objects.filter(is_public=True, project__in=queryset, project__abroad=False)
                 .select_related("project__direction").order_by("project__order", "pk"))
    projects, regions, markers = {}, {key: set() for key in REGIONS}, {}
    for loc in locations:
        proj = loc.project
        projects[proj.pk] = proj
        regions.setdefault(loc.region, set()).add(proj.pk)
        if loc.lat is None or loc.lon is None:
            continue
        _marker_for(markers, loc).ids.add(proj.pk)
    return projects, regions, markers


def _marker_for(markers, loc):
    key = f"{loc.region}:{loc.city_uz}"
    if key in markers:
        return markers[key]
    x, y = project(loc.lat, loc.lon)
    for marker in markers.values():
        if marker.region == loc.region and max(abs(marker.x - x), abs(marker.y - y)) < MERGE_DISTANCE:
            name = _city_name(loc)
            if name not in marker.name.split(", "):
                marker.name = f"{marker.name}, {name}"
            return marker
    markers[key] = Marker(key=key, name=_city_name(loc), region=loc.region, x=round(x, 1), y=round(y, 1))
    return markers[key]


def _count(ids, projects, dept):
    return sum(1 for pk in ids if not dept or dept_of(projects[pk]) == dept)


def _region_rows(projects, region_ids, dept, selected):
    geometry = {r["key"]: r["d"] for r in uzmap()["regions"]}
    registry = reverse("core:registry")
    rows = []
    for key in REGIONS:
        count = _count(region_ids.get(key, ()), projects, dept)
        rows.append({
            "key": key, "d": geometry[key], "name": region_name(key), "count": count, "total": len(region_ids.get(key, ())),
            "level": shade_level(count), "selected": key == selected,
            "url": f"{registry}?{REGION_PARAM}={key}",
        })
    return rows


def _marker_rows(projects, markers, dept):
    rows = []
    for marker in markers.values():
        city_uz = marker.key.split(":", 1)[1]
        dx, dy, anchor = LABEL_OFFSETS.get(city_uz, DEFAULT_OFFSET)
        count = _count(marker.ids, projects, dept)
        rows.append({
            "key": marker.key, "name": marker.name, "region": marker.region, "x": marker.x, "y": marker.y,
            "count": count, "total": len(marker.ids), "hidden": count == 0, "places": len(marker.name.split(", ")),
            "label": city_uz in LABELLED_CITIES, "narrow": city_uz in NARROW_LABELS, "lx": round(marker.x + dx, 1), "ly": round(marker.y + dy, 1),
            "anchor": anchor,
        })
    # Koʻp loyihali belgi avval chiziladi: kichiklari ustida qoladi va ularni bosish oson
    rows.sort(key=lambda m: -m["total"])
    return rows


def _script_data(projects, region_ids, markers, labels, **state):
    """`json_script` uchun: JS filtrlash va tanlov paneli shu maʼlumotdan ishlaydi."""
    return {
        **state, "steps": SHADE_STEPS, "labels": labels, "top": TOP_REGIONS,
        "registry": reverse("core:registry"), "param": REGION_PARAM,
        "projects": {str(pk): {"t": proj.tr("title"), "c": proj.client, "y": proj.year, "d": dept_of(proj)}
                     for pk, proj in projects.items()},
        "regions": {key: {"name": region_name(key), "ids": sorted(ids)} for key, ids in region_ids.items() if ids},
        "markers": {m.key: {"name": m.name, "region": m.region, "ids": sorted(m.ids)} for m in markers.values()},
    }


def projects_map_context(queryset, dept=None, region=None, tab_url=None, live=True) -> dict:
    """Xarita va panel konteksti.

    `dept` — "energy" / "construction" / None; `region` — tanlangan hudud kaliti (reestr filtri).
    `tab_url(key)` — yoʻnalish havolasi (standart `?yo=`); `live` — JS sahifani qayta yuklamasdan filtrlaydimi.
    """
    dept = dept if dept in DEPTS else ""
    region = region if region in REGIONS else ""
    projects, region_ids, markers = _collect(queryset)
    tab_url = tab_url or (lambda key: f"?{DEPT_PARAM}={key}#xarita" if key else "?#xarita")
    regions = _region_rows(projects, region_ids, dept, region)
    marker_rows = _marker_rows(projects, markers, dept)
    labels = {DEPT_ENERGY: _("Energoaudit"), DEPT_CONSTRUCTION: _("Qurilishda nazorat oʻlchovi")}
    on_map = _count(projects, projects, dept)
    scope = {"": queryset.count()}
    scope.update({key: queryset.filter(direction__accent=_accent(key)).count() for key in DEPTS})
    return {
        "width": WIDTH, "height": HEIGHT, "regions": regions, "markers": marker_rows,
        "totals": {
            "projects": on_map,
            "regions": sum(1 for r in regions if r["count"]),
            "cities": sum(m["places"] for m in marker_rows if m["count"]),
            DEPT_ENERGY: _count(projects, projects, DEPT_ENERGY),
            DEPT_CONSTRUCTION: _count(projects, projects, DEPT_CONSTRUCTION),
        },
        "off_map": scope[dept] - on_map, "dept": dept, "region": region, "live": live,
        "tabs": [{"key": key, "label": label, "active": key == dept, "url": tab_url(key)}
                 for key, label in (("", _("Barchasi")), *labels.items())],
        "top_regions": sorted((r for r in regions if r["count"]), key=lambda r: -r["count"])[:TOP_REGIONS],
        "data": _script_data(projects, region_ids, markers, labels, dept=dept, region=region, live=live, scope=scope),
    }


def _accent(dept):
    return next(accent for accent, key in DEPT_ACCENTS.items() if key == dept)


def region_options():
    """Reestr filtri uchun (kalit, nom) — joriy tilda."""
    return [(key, region_name(key)) for key in REGIONS]


def registry_map_context(request, direction_slug, region):
    """Reestr xaritasi: yoʻnalish tugmalari jadvaldagi `d` filtrini almashtiradi (sahifa qayta yuklanadi)."""
    slugs = dict(Direction.objects.values_list("accent", "slug"))
    dept = next((key for accent, key in DEPT_ACCENTS.items() if direction_slug and slugs.get(accent) == direction_slug), None)

    def tab_url(key):
        query = request.GET.copy()
        query.pop("page", None)
        query.pop("d", None)
        if key:
            query["d"] = slugs.get(_accent(key), "")
        return f"?{query.urlencode()}#xarita" if query else "?#xarita"

    return projects_map_context(Project.objects.all(), dept=dept, region=region, tab_url=tab_url, live=False)



# Yandex vidjetida oʻzbek tili yoʻq — oʻzbekcha sahifada ruscha
YANDEX_LANG = {"uz": "ru_RU", "ru": "ru_RU", "en": "en_US"}


def office_map(site) -> dict | None:
    """Ofis xaritasi havolalari; koordinata boʻlmasa None (xarita bloki chiqmaydi).

    Yandex'da `ll` va `pt` — uzunlik,kenglik; `rtext` — kenglik,uzunlik.
    """
    if site.map_lat is None or site.map_lng is None:
        return None
    lat, lon = f"{site.map_lat:.6f}", f"{site.map_lng:.6f}"
    lang = YANDEX_LANG.get((get_language() or "uz").split("-")[0], "ru_RU")
    return {
        "embed": f"https://yandex.uz/map-widget/v1/?ll={lon}%2C{lat}&z=17&pt={lon},{lat},pm2rdm&lang={lang}",
        "yandex": f"https://yandex.uz/maps/?ll={lon},{lat}&z=17&pt={lon},{lat},pm2rdm",
        "route": f"https://yandex.uz/maps/?rtext=~{lat},{lon}&rtt=auto",
        "google": f"https://maps.google.com/maps?q={lat},{lon}",
    }
