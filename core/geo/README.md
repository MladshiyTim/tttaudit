# core/geo — Oʻzbekiston xaritasi geometriyasi

- `uzmap.json` — viloyatlar konturlari (SVG yoʻllari, holst 1000×649), `regions[].key`, `cx/cy` va
  `cities` (tekshiruv nuqtalari). Manba: **Natural Earth 10m admin-1, public domain**; bmmaudit.uz
  saytidagi `src/data/uzmap.js` dan (`tools/mkmap.py` natijasi) JS oʻrami olib tashlangan holda.
  Alohida mamlakat konturi faylda yoʻq — tashqi chiziq viloyat yoʻllarining oʻzidan chiziladi.
- `projection.py` — `project(lat, lon)` → holst koordinatalari (`uzproj.js` bilan bir xil konstantalar).
- `regions.py` — 14 hudud nomi uz/ru/en, kalitlari `uzmap.json` dagi bilan bir xil.

Qoʻlda tahrirlanmaydi: geometriya oʻzgarsa `uzmap.js` qayta yigʻiladi va shu fayl undan olinadi.
