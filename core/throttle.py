"""Oddiy chegara: cache'da hisoblagich. Prodda cache umumiy (DatabaseCache/Redis) boʻlishi kerak,
LocMem har gunicorn ishchisida alohida sanaydi — README da qayd etilgan."""
from django.core.cache import cache


def client_ip(request) -> str:
    """Teskari proksi ortida X-Real-IP (Railway/nginx), aks holda REMOTE_ADDR."""
    return (request.META.get("HTTP_X_REAL_IP") or request.META.get("REMOTE_ADDR") or "").strip()


def allow(key: str, limit: int, window: int) -> bool:
    """`window` soniya ichida `limit` tagacha ruxsat; oshsa False."""
    cache_key = f"throttle:{key}"
    cache.add(cache_key, 0, timeout=window)
    try:
        count = cache.incr(cache_key)
    except ValueError:  # kalit oynada oʻchib ketgan
        cache.set(cache_key, 1, timeout=window)
        count = 1
    return count <= limit
