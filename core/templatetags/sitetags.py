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


from django.urls import translate_url


@register.simple_tag
def alt_url(request, lang_code):
    """Joriy sahifaning boshqa tildagi mutlaq manzili (hreflang, til almashtirgich)."""
    return request.build_absolute_uri(translate_url(request.path, lang_code))


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
