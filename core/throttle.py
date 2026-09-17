"""Oddiy chegara: cache'da hisoblagich. Hisoblagich oʻzining tugash vaqtini (`expires_at`)
qiymat ichida saqlaydi, shu sababli har qanday cache backend (LocMem, DatabaseCache, Redis)
bilan toʻgʻri ishlaydi — `DatabaseCache.incr()` kabi backendlar `get`+`set` orqali ishlaydi va
`timeout`ni `DEFAULT_TIMEOUT`ga (300s) qaytarib qoʻyadi, agar oyna cache'ning oʻz timeout'iga
tayansa. `get`+`set` atomik emas, lekin murojaat formasi uchun bu yetarli."""
import time

from django.conf import settings
from django.core.cache import cache


def client_ip(request) -> str:
    """`settings.TRUST_X_REAL_IP` yoqilgan boʻlsa (faqat sarlavhani qayta yozadigan teskari
    proksi ortida xavfsiz) X-Real-IP (Railway/nginx), aks holda REMOTE_ADDR."""
    if settings.TRUST_X_REAL_IP:
        header_ip = (request.META.get("HTTP_X_REAL_IP") or "").strip()
        if header_ip:
            return header_ip
    return (request.META.get("REMOTE_ADDR") or "").strip()


def allow(key: str, limit: int, window: int) -> bool:
    """`window` soniya ichida `limit` tagacha ruxsat; oshsa False.

    Hisoblagich `(count, expires_at)` juftligini saqlaydi va har safar oʻzining qolgan
    muddatini `timeout` sifatida qayta yozadi — shuning uchun backend `incr()`ni qanday
    amalga oshirishidan qatʼi nazar oyna 3600s kabi uzoq boʻlib qoladi (masalan
    `DatabaseCache`da).
    """
    cache_key = f"throttle:{key}"
    now = time.time()
    stored = cache.get(cache_key)
    if stored is None or now >= stored[1]:
        count, expires_at = 0, now + window
    else:
        count, expires_at = stored
    count += 1
    cache.set(cache_key, (count, expires_at), timeout=max(1, int(expires_at - now)))
    return count <= limit
