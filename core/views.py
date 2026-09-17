"""Barcha sahifalar serverda render qilinadi. React faqat [data-react] orollari uchun."""
import json

from django.conf import settings
from django.shortcuts import render

from . import compliance, energy
from .models import Direction


def page(request, template, nav="", crumbs=(), **context):
    """Umumiy render: `nav` — faol menyu kaliti, `crumbs` — [(sarlavha, url|None), ...]."""
    context.update({"nav": nav, "crumbs": list(crumbs)})
    return render(request, template, context)


def form_context():
    """Murojaat formasi vidjeti uchun umumiy kontekst."""
    directions = list(Direction.objects.all())
    return {
        "form_directions": directions,
        "form_directions_json": json.dumps(
            [{"id": d.pk, "title": d.tr("title"), "accent": d.accent, "slug": d.slug} for d in directions],
            ensure_ascii=False,
        ),
        "max_upload_mb": settings.LEAD_MAX_UPLOAD_BYTES // (1024 * 1024),
    }


def compliance_context():
    return {"compliance": {
        "passport_area": compliance.PASSPORT_AREA_M2,
        "registry_kwh": compliance.REGISTRY_KWH,
        "registry_gas": compliance.REGISTRY_GAS_M3,
        "periodic_years": compliance.PERIODIC_YEARS,
    }}


def energy_context():
    ladder = energy.ladder()
    return {
        "energy_ladder": ladder,
        "energy_ladder_json": json.dumps(ladder, ensure_ascii=False),
        "passport_threshold": energy.PASSPORT_AREA_THRESHOLD_M2,
    }


def home(request):
    return page(request, "core/base.html")
