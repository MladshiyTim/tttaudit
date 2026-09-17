"""Barcha sahifalar serverda render qilinadi. React faqat [data-react] orollari uchun."""
import json

from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import F, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST

from . import compliance, energy, throttle
from .forms import LeadForm
from .models import (
    Branch,
    Client,
    Credential,
    Direction,
    Instrument,
    LegalAct,
    Post,
    Project,
    Service,
    SiteSettings,
    Stat,
    TeamMember,
)
from .notify import notify_telegram


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
    obj = get_object_or_404(Direction.objects.prefetch_related("services"), slug=direction_slug)
    is_energy = obj.accent == Direction.ACCENT_AMBER
    context = {
        "direction": obj,
        "is_energy": is_energy,
        "services": obj.services.all(),
        "legal_acts": obj.legal_acts.filter(verified_on__isnull=False),
        "projects": obj.projects.exclude(year__isnull=True)[:6],
        "instruments": obj.instruments.all() if not is_energy else Instrument.objects.none(),
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


def credentials(request):
    return page(
        request, "core/credentials.html", nav="credentials",
        crumbs=[(_("Hujjatlar"), None)],
        credentials=Credential.objects.all(),
    )


def instruments(request):
    return page(
        request, "core/instruments.html", nav="company",
        crumbs=[(_("Tashkilot"), reverse("core:company")), (_("Oʻlchov asboblari"), None)],
        instruments=Instrument.objects.all(),
    )


def company(request):
    return page(
        request, "core/company.html", nav="company",
        crumbs=[(_("Tashkilot"), None)],
        credentials=Credential.objects.all(),
        stats=Stat.objects.all(),
        leadership=TeamMember.objects.filter(is_leadership=True)[:4],
        clients=Client.objects.filter(featured=True)[:12],
    )


def team(request):
    members = TeamMember.objects.all()
    return page(
        request, "core/team.html", nav="company",
        crumbs=[(_("Tashkilot"), reverse("core:company")), (_("Rahbariyat va mutaxassislar"), None)],
        leadership=members.filter(is_leadership=True),
        energy=members.filter(is_leadership=False, dept=TeamMember.DEPT_ENERGY),
        construction=members.filter(is_leadership=False, dept=TeamMember.DEPT_CONSTRUCTION),
        total=members.count(),
    )


def requisites(request):
    return page(
        request, "core/requisites.html", nav="company",
        crumbs=[(_("Tashkilot"), reverse("core:company")), (_("Rekvizitlar"), None)],
        branches=Branch.objects.all(),
    )


def legislation(request):
    return page(
        request, "core/legislation.html", nav="legislation",
        crumbs=[(_("Qonunchilik"), None)],
        acts=LegalAct.objects.filter(verified_on__isnull=False),
        posts=Post.objects.filter(is_published=True)[:4],
    )


def news(request):
    return page(
        request, "core/news.html", nav="news",
        crumbs=[(_("Yangiliklar"), None)],
        posts=Post.objects.filter(is_published=True).select_related("legal_act"),
    )


def post(request, slug):
    published = Post.objects.filter(is_published=True).select_related("legal_act")
    obj = get_object_or_404(published, slug=slug)
    return page(
        request, "core/post.html", nav="news",
        crumbs=[(_("Yangiliklar"), reverse("core:news")), (obj.tr("title"), None)],
        post=obj, others=published.exclude(pk=obj.pk)[:3],
    )


REGISTRY_PAGE_SIZE = 25


def registry(request):
    queryset = Project.objects.select_related("direction").order_by(F("year").desc(nulls_last=True), "order", "pk")
    direction_slug = request.GET.get("d", "")
    year = request.GET.get("y", "")
    year = year if year.isdigit() else ""
    query = request.GET.get("q", "").strip()
    if direction_slug:
        queryset = queryset.filter(direction__slug=direction_slug)
    if year:
        queryset = queryset.filter(year=int(year))
    if query:
        queryset = queryset.filter(Q(title_uz__icontains=query) | Q(title_ru__icontains=query) | Q(client__icontains=query))
    paginator = Paginator(queryset, REGISTRY_PAGE_SIZE)
    page_obj = paginator.get_page(request.GET.get("page"))
    return page(
        request, "core/registry.html", nav="registry",
        crumbs=[(_("Bajarilgan ishlar reestri"), None)],
        page_obj=page_obj, total=Project.objects.count(), found=paginator.count,
        directions=Direction.objects.all(),
        years=Project.objects.exclude(year__isnull=True).values_list("year", flat=True).distinct().order_by("-year"),
        active={"d": direction_slug, "y": year, "q": query},
        offset=page_obj.start_index() - 1,
    )


def _wants_json(request) -> bool:
    return request.headers.get("X-Requested-With") == "XMLHttpRequest" or "application/json" in request.headers.get("Accept", "")


def contact(request):
    site = SiteSettings.load()
    map_bbox = ""
    if site.map_lat and site.map_lng:
        map_bbox = f"{site.map_lng - 0.01:.5f},{site.map_lat - 0.006:.5f},{site.map_lng + 0.01:.5f},{site.map_lat + 0.006:.5f}"
    context = {"branches": Branch.objects.all(), "map_bbox": map_bbox}
    context.update(form_context())
    return page(request, "core/contact.html", nav="contact", crumbs=[(_("Aloqa"), None)], **context)


def request_page(request):
    context = {"hero_credentials": Credential.objects.filter(show_in_hero=True), "sent": request.GET.get("sent") == "1",
               "error": request.GET.get("error", "")}
    context.update(form_context())
    return page(request, "core/request.html", nav="contact", crumbs=[(_("Murojaat"), None)], **context)


@require_POST
def lead_create(request):
    """React formasi JSON kutadi; JS oʻchiq boʻlsa oddiy forma redirect oladi."""
    if not throttle.allow(f"lead:{throttle.client_ip(request)}", settings.LEAD_RATE_LIMIT, settings.LEAD_RATE_WINDOW_SECONDS):
        if _wants_json(request):
            return JsonResponse({"ok": False, "error": _("Juda koʻp soʻrov. Birozdan soʻng urinib koʻring yoki qoʻngʻiroq qiling.")}, status=429)
        return redirect(reverse("core:request") + "?error=limit")

    form = LeadForm(request.POST, request.FILES)
    if not form.is_valid():
        if _wants_json(request):
            return JsonResponse({"ok": False, "errors": form.errors}, status=400)
        return redirect(reverse("core:request") + "?error=1")

    lead = form.save(commit=False)
    lead.language = request.LANGUAGE_CODE
    lead.source = (request.META.get("HTTP_REFERER") or "")[:200]
    lead.save()
    notify_telegram(lead)

    message = _("Murojaat qabul qilindi. Bir ish kuni ichida muhandis bogʻlanadi.")
    if _wants_json(request):
        return JsonResponse({"ok": True, "message": message})
    return redirect(reverse("core:request") + "?sent=1")


def compliance_check(request):
    result = compliance.evaluate(
        object_kind=request.GET.get("object_kind", ""),
        area_m2=request.GET.get("area_m2"), annual_kwh=request.GET.get("annual_kwh"),
        annual_gas_m3=request.GET.get("annual_gas_m3"), estimate_value=request.GET.get("estimate_value"),
        funding=request.GET.get("funding", ""),
        has_dispute=request.GET.get("has_dispute") in ("1", "true", "on"),
    )
    payload = result.as_dict()
    slugs = {r["service_slug"] for r in payload["requirements"] if r["service_slug"]}
    urls = {s.slug: {"url": s.get_absolute_url(), "title": s.tr("title")}
            for s in Service.objects.select_related("direction").filter(slug__in=slugs)} if slugs else {}
    for item in payload["requirements"]:
        info = urls.get(item["service_slug"])
        if info:
            item["service_url"], item["service_title"] = info["url"], info["title"]
    return JsonResponse({"ok": True, **payload})


def energy_estimate(request):
    try:
        area = float(request.GET.get("area") or 0)
        kwh = float(request.GET.get("kwh") or 0)
    except (TypeError, ValueError):
        return JsonResponse({"ok": False, "error": _("Notoʻgʻri qiymat")}, status=400)
    value = energy.specific_consumption(kwh, area)
    return JsonResponse({
        "ok": True, "specific": round(value, 1) if value is not None else None,
        "category": energy.category_for(value),
        "passport_required": area >= energy.PASSPORT_AREA_THRESHOLD_M2,
        "threshold": energy.PASSPORT_AREA_THRESHOLD_M2,
    })
