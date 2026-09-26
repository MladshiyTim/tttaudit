"""Soʻrov tanasi hajmini CSRF/forma tahlilidan oldin cheklaydi."""
from django.conf import settings
from django.http import HttpResponse

TOO_LARGE_MESSAGE = "Soʻrov hajmi juda katta."


class MaxBodySizeMiddleware:
    """`CONTENT_LENGTH` > `settings.MAX_REQUEST_BODY_BYTES` boʻlsa 413 qaytaradi.

    CsrfViewMiddleware POST tanasini oʻqiydi (va fayllarni diskka yozadi) — shu sababli
    tekshiruv SecurityMiddleware'dan keyin darhol turadi. Sarlavha yoʻq yoki notoʻgʻri
    boʻlsa soʻrov oʻtkaziladi: Django'ning oʻz chegaralari (DATA_UPLOAD_MAX_*) qoladi.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            length = int(request.META.get("CONTENT_LENGTH") or 0)
        except (TypeError, ValueError):
            length = 0
        if length > settings.MAX_REQUEST_BODY_BYTES:
            return HttpResponse(TOO_LARGE_MESSAGE, status=413, content_type="text/plain; charset=utf-8")
        return self.get_response(request)
