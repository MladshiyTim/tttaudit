"""Barcha sahifalar serverda render qilinadi. React faqat [data-react] orollari uchun."""
import json

from django.conf import settings
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from . import compliance, energy
from .models import Credential, Direction, Instrument, LegalAct, Post, Project, Service, Stat


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


HOME_FAQ = [
    (_("Energoaudit kimga majburiy?"),
     _("ЗРУ-940 ga koʻra davriy energoaudit majburiy tartibda besh yilda kamida bir marta oʻtkaziladi. "
       "Davlat energetika reestriga kiritilgan korxonalar va davlat ishtirokidagi tashkilotlar uchun "
       "audit majburiy; boshqalar uchun ixtiyoriy.")),
    (_("Qaysi binolarga energosamaradorlik toifasi belgilanadi?"),
     _("Foydalaniladigan maydoni 200 m² dan katta bino va inshootlarga. Energopasport yangi, mavjud, "
       "rekonstruksiya va modernizatsiya qilinayotgan obyektlar uchun rasmiylashtiriladi.")),
    (_("Nazorat oʻlchovi uchun qurilishni toʻxtatish kerakmi?"),
     _("Yoʻq. Oʻlchov ish jarayoniga xalaqit bermaydi; yashirin ishlar yopilishidan oldin qayd etiladi.")),
    (_("Ishlab chiqarishni toʻxtatmasdan energoaudit qilsa boʻladimi?"),
     _("Ha — aksincha, oʻlchovlar real ish rejimida olinishi kerak.")),
    (_("Hujjatlarimiz uchinchi shaxsga beriladimi?"),
     _("Yoʻq. Hujjatlar faqat shartnoma doirasida ishlatiladi; axborot xavfsizligi tizimi ISO 27001:2022 "
       "boʻyicha sertifikatlangan.")),
]


def home(request):
    context = {
        "directions": Direction.objects.prefetch_related("services").all(),
        "stats": Stat.objects.all(),
        "hero_credentials": Credential.objects.filter(show_in_hero=True),
        "projects": Project.objects.select_related("direction").exclude(year__isnull=True)[:8],
        "posts": Post.objects.filter(is_published=True)[:3],
        "faq": [{"q": q, "a": a} for q, a in HOME_FAQ],
    }
    context.update(compliance_context())
    return page(request, "core/home.html", **context)


def services(request):
    return page(
        request, "core/services.html", nav="services",
        crumbs=[(_("Xizmatlar"), None)],
        directions=Direction.objects.prefetch_related("services").all(),
    )


def direction(request, direction_slug):
    obj = get_object_or_404(Direction.objects.prefetch_related("services", "legal_acts"), slug=direction_slug)
    is_energy = obj.accent == Direction.ACCENT_AMBER
    context = {
        "direction": obj,
        "is_energy": is_energy,
        "services": obj.services.all(),
        "legal_acts": obj.legal_acts.filter(verified_on__isnull=False),
        "projects": obj.projects.exclude(year__isnull=True)[:6],
        "instruments": Instrument.objects.all() if not is_energy else [],
        "project_total": obj.projects.count(),
    }
    if is_energy:
        context.update(compliance_context())
        context.update(energy_context())
    return page(
        request, "core/direction.html", nav="services",
        crumbs=[(_("Xizmatlar"), reverse("core:services")), (obj.tr("title"), None)],
        **context,
    )


def service(request, direction_slug, slug):
    obj = get_object_or_404(Service.objects.select_related("direction"), direction__slug=direction_slug, slug=slug)
    return page(
        request, "core/service.html", nav="services",
        crumbs=[(_("Xizmatlar"), reverse("core:services")),
                (obj.direction.tr("title"), obj.direction.get_absolute_url()), (obj.tr("title"), None)],
        service=obj, direction=obj.direction,
        siblings=obj.direction.services.exclude(pk=obj.pk),
        legal_acts=obj.direction.legal_acts.filter(verified_on__isnull=False),
    )
