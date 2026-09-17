"""Yangi murojaat haqida Telegram xabari. Xato soʻrovni yiqitmaydi: murojaat bazada, xabar ikkinchi darajali."""
import json
import logging
import urllib.request

from django.conf import settings

log = logging.getLogger(__name__)


def notify_telegram(lead) -> bool:
    token, chat = settings.TELEGRAM_BOT_TOKEN, settings.TELEGRAM_CHAT_ID
    if not token or not chat:
        return False
    lines = [
        "Saytdan yangi murojaat",
        f"Ism: {lead.name}",
        f"Telefon: {lead.phone}",
        f"E-pochta: {lead.email}" if lead.email else "",
        f"Yoʻnalish: {lead.direction.title_uz}" if lead.direction_id else "",
        f"Obyekt: {lead.object_type}" if lead.object_type else "",
        f"Izoh: {lead.note}" if lead.note else "",
        f"Sahifa: {lead.source}" if lead.source else "",
    ]
    payload = json.dumps({"chat_id": chat, "text": "\n".join(filter(None, lines)),
                          "disable_web_page_preview": True}).encode()
    request = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage", data=payload,
        headers={"Content-Type": "application/json"},
    )
    try:
        urllib.request.urlopen(request, timeout=8).read()
        return True
    except Exception as error:  # noqa: BLE001 — tarmoq xatosi turli sinflarda keladi
        log.warning("Telegram: yuborilmadi — %s", error)
        return False
