# TTT Audit — sayt (tttaudit.uz)

Energoaudit va qurilishda nazorat oʻlchovi boʻyicha ekspert tashkilotining rasmiy sayti.
Django 5.2 SSR + React vidjetlari (Vite). Uch til: /uz/ /ru/ /en/.

## Lokal ishga tushirish

```bash
python -m venv .venv && .venv/Scripts/activate
pip install -r requirements-dev.txt
python manage.py migrate
python manage.py seed_content        # tahririy kontent (yoʻnalish, xizmat, qonun, maqola)
python manage.py import_tttaudit     # mijoz faktlari: hujjatlar, 38 mutaxassis, 143 loyiha
python manage.py createsuperuser
cd frontend && npm install && npm run build && cd ..
python manage.py runserver
```
Sayt: http://127.0.0.1:8000/uz/ · Admin: /admin/ · Testlar: `pytest -q --cov=core`

Testlardan oldin har doim `cd frontend && npm run build` bajaring — testlardan biri
(`core/tests/test_widgets_build.py`) yigʻilgan `frontend/dist/widgets/widgets.js` faylini tekshiradi.

## Tuzilma
- `core/models.py` — kontent modellari (`_uz/_ru/_en` maydonlar, `{{ obj|tr:"title" }}`).
- `core/compliance.py`, `core/energy.py` — talab qoidalari va A–G chegaralari (server va React uchun yagona manba).
- `core/templates/core/` — sahifalar; `core/static/core/css/site.css` — dizayn tizimi.
- `frontend/src/` — uchta React vidjet; `npm run build` → `frontend/dist/widgets/`.
- `data/tttaudit/` — mijoz byulletenlaridan ajratilgan JSON va skanlar (38 mutaxassis — 24 energetika / 14 qurilish,
  143 loyiha, 8 hujjat/sertifikat).
- `tools/prepare_logo.py` — `logo/` dagi PNG'dan sayt logotiplari (natija allaqachon commit qilingan; bu skript
  faqat logotip qayta yasalganda kerak, konteynerda ishlamaydi).

## Tarjima
Interfeys satrlari: `python manage.py maketranslations --report` (faqat oʻqish, hech narsa yozmaydi) →
`locale/translations.json` ni tahrirlash → `python manage.py maketranslations` (yozadi).
Oʻzbekcha interfeys matnini tahrirlagandan keyin shu buyruqni ishga tushirish va `frontend/src/i18n.js`
(vidjet matnlari, qoʻlda `locale/translations.json` bilan sinxron tutiladi) ni ham yangilash shart.

## Prod
`.env.example` → muhit oʻzgaruvchilari. `Dockerfile` gunicorn + whitenoise. PostgreSQL `DATABASE_URL`.
Murojaat chegarasi cache orqali: prodda `DatabaseCache` (`createcachetable` CMD da), lokal/testda `LocMemCache`.
Telegram: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`.
Mijoz admin panelda xizmat matnlarini tahrirlay boshlagach `seed_content` ni Dockerfile CMD dan olib tashlang.

### Prod: muhim
- **`DJANGO_DEBUG=0` majburiy.** Docker tashqarisida (masalan toʻgʻridan-toʻgʻri server yoki boshqa PaaS'da)
  joylashtirilganda ham bu oʻzgaruvchini aniq qoʻying — aks holda `media/` katalogidagi yuklangan fayllar
  (murojaat qildirilgan hujjatlar, xodim suratlari, kredential skanlari) **hammaga ochiq xizmat qilinadi**.
- **Teskari proksi orqasida ishlatiladi**, boʻlmasa Django yuklamani (`request body`) tekshirishdan oldin
  diskka/xotiraga toʻliq yozib oladi. Proksida soʻrov hajmini cheklang, masalan nginx'da:
  `client_max_body_size 30m;`.
- **`TRUST_X_REAL_IP=1` ni faqat** `X-Real-IP` sarlavhasini **oʻzi qayta yozadigan** teskari proksi ortida
  yoqing (Railway, toʻgʻri sozlangan nginx). Aks holda barcha tashrif buyuruvchilar bitta chegara
  hisoblagichini (`LEAD_RATE_LIMIT`) baham koʻradi, yoki sarlavha soxtalashtirilib chegara chetlab oʻtiladi.
- **`media/` uchun doimiy volume** biriktiring — kredential skanlari, xodim suratlari, murojaat qildirilgan
  fayllar shu yerda saqlanadi; konteyner qayta yaratilganda yoʻqolmasligi kerak.
- **`seed_content` ni CMD dan olib tashlash** — mijoz admin panelda yoʻnalish/xizmat/qonun/maqola matnlarini
  tahrirlay boshlagach, Dockerfile'dagi CMD'dan `python manage.py seed_content` qatorini olib tashlang.
- Oʻzbekcha interfeys matnini oʻzgartirgandan keyin `python manage.py maketranslations` ishga tushiring va
  `frontend/src/i18n.js` ni qoʻlda sinxron tutib boring (vidjet matnlari tarjima faylidan avtomatik olinmaydi).
- Testlardan oldin `cd frontend && npm run build` bajaring — bitta test yigʻilgan bundlni tekshiradi.

## Kontent qoidalari
Faqat energoaudit va qurilishda nazorat oʻlchovi. Manbasiz raqam yoʻq. Qonun faqat `verified_on` bilan chiqadi.
