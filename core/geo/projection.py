"""Kenglik va uzunlik → `uzmap.json` holsti koordinatalari.

Holst bmmaudit.uz dagi `tools/mkmap.py` bilan yigʻilgan: kenglik 41.3° ga tuzatilgan teng oraliqli
proyeksiya, boshlanish nuqtasi — manba maʼlumotlar ramkasining burchagi. Konstantalar `uzproj.js`
dagi bilan bir xil (20 ta shahar boʻyicha tiklangan, eng katta farq 0.07 birlik). 1 birlik ≈ 1.08 km.
"""
import math

LON0 = 55.975496
LAT1 = 45.558515
SCALE = 77.511465
KX = math.cos(math.radians(41.3))
WIDTH, HEIGHT = 1000, 649


def project(lat: float, lon: float) -> tuple[float, float]:
    """(lat, lon) → (x, y) holstda; y pastga qarab oʻsadi."""
    return (lon - LON0) * KX * SCALE, (LAT1 - lat) * SCALE
