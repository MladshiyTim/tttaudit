"""Shablon filtrlari."""
from django import template

register = template.Library()


@register.filter(name="tr")
def translate_field(obj, field):
    """Joriy tildagi matn: {{ direction|tr:"title" }}"""
    getter = getattr(obj, "tr", None)
    if callable(getter):
        return getter(field)
    return getattr(obj, f"{field}_uz", "") or ""


@register.filter(name="tr_list")
def translate_list(obj, field):
    """JSON ro'yxatning joriy tildagi ko'rinishi: {{ service|tr_list:"process" }}"""
    getter = getattr(obj, "tr_list", None)
    if callable(getter):
        return getter(field)
    return []


from django.conf import settings
from django.urls import translate_url


@register.simple_tag
def alt_path(request, lang_code):
    """Joriy sahifaning boshqa tildagi nisbiy yoʻli (til almashtirgich)."""
    return translate_url(request.path, lang_code)


@register.simple_tag
def alt_url(request, lang_code):
    """hreflang uchun mutlaq manzil: SITE_URL + tarjima qilingan yoʻl (Host sarlavhasiga bogʻliq emas)."""
    return settings.SITE_URL + translate_url(request.path, lang_code)


@register.simple_tag(takes_context=True)
def qs_replace(context, **kwargs):
    """Joriy GET parametrlarini saqlab bittasini almashtiradi: {% qs_replace page=2 %}"""
    query = context["request"].GET.copy()
    for key, value in kwargs.items():
        if value in (None, ""):
            query.pop(key, None)
        else:
            query[key] = value
    encoded = query.urlencode()
    return f"?{encoded}" if encoded else "?"


NBSP = " "


@register.filter(name="groupnum")
def group_number(value, signed=""):
    """Jadval raqami: minglar boʻsh joy bilan, oʻnlik — joriy tilga mos («386,5» / "386.5").

    {{ row.diff|groupnum:"sign" }} musbat qiymatga «+» qoʻshadi.
    """
    from django.utils.translation import get_language

    try:
        number = float(value)
    except (TypeError, ValueError):
        return value
    decimal = "." if (get_language() or "uz").startswith("en") else ","
    text = f"{abs(number):,.1f}" if number % 1 else f"{abs(number):,.0f}"
    text = text.replace(",", NBSP).replace(".", decimal)
    if number < 0:
        return "−" + text
    if signed and number > 0:
        return "+" + text
    return text


@register.filter(name="svc_tag")
def service_tag(service):
    """Xizmat qatori oʻngidagi mono belgi: muddat, boʻlmasa qisqa tavsif."""
    from core.home import SERVICE_TAGS

    return service.tr("duration") or SERVICE_TAGS.get(service.slug, "")
