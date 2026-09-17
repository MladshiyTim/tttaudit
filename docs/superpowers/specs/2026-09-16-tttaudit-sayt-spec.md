# TTT Audit sayti — spets (2026-09-16)

## Mijoz va vazifa

**«TTTaudit» MChJ** (Fargʻona, Yangiobod 5) — 1997-yildan ishlaydigan ekspert
tashkiloti: **energoaudit** (24 mutaxassis) va **qurilishda nazorat oʻlchovi /
texnik nazorat** (16 mutaxassis). Mavjud tttaudit.uz mijozga yoqmagan; **butunlay
yangi sayt** quriladi va eski domenga chiqadi.

Mijoz talabi: sayt **my.gov.uz / soliq.uz kabi jiddiy, rasmiy (davlat portali)
uslubida** boʻlsin. Andoza — Timur qurgan bmmaudit.uz tuzilmasi (bosh sahifa →
xizmatlar → hujjatlar → jamoa → reestr → aloqa), lekin TTT unga **oʻxshamasligi**
shart (BMM: toʻq siyoh + mis + serif; ikkalasi bir guruh, bir manzil).

Manbalar:
- Mijoz byulletenlari: `D:\tttaudit\mijozdan kelgan ma'lumot\*.docx` (2 ta, ru).
- Ulardan ajratilgan tuzilmali maʼlumot: `C:\Users\Surface PC\reper\data\tttaudit\`
  (`facts.json`, `staff.json` — 39 mutaxassis surat bilan, `projects.json` — 143
  loyiha, `clients.json`, `img/docs/*` — 8 ta hujjat skani).
- Yangi logotip: `D:\tttaudit\logo\*.png` (1254×1254, monoxrom 3D render, kulrang
  fonda — fonni ajratish kerak).
- Oldingi backend (Django 5.2, 12 model, energy/compliance mantiq, React vidjetlar):
  `C:\Users\Surface PC\reper` — **backend port qilinadi, front qaytadan yoziladi**.

## Kontent qoidalari (mijoz koʻrsatmalari)

1. Saytda **faqat energoaudit va qurilishda nazorat oʻlchovi**. Moliyaviy audit,
   MSFO, oʻquv markazi, eski auditorlar, Moliya vazirligi litsenziyasi — YOʻQ.
2. «auditorlik tashkiloti» iborasi ishlatilmaydi; tashkilot — «ekspert tashkiloti».
3. «Jamoa» emas — **«Rahbariyat va mutaxassislar»**. Filiallar boʻlimi yoʻq;
   Toshkent ofisi faqat aloqa sahifasida (byulletenda bor).
4. Manbasiz daʼvo yoʻq: muddat, narx, kafolat, ish soatlari — faqat mijoz bergan
   raqam. Qonun moddalari lex.uz bilan tekshirilgan (`verified_on`) boʻlsagina chiqadi.
5. Stok foto va generativ «sanʼat» yoʻq. Faqat mijozning hujjat skanlari va
   xodim suratlari. Surat boʻlmasa — blok suratsiz ishlaydi.
6. Brend nomi: **TTT Audit** (REPER nomi hech qayerda yoʻq).

## Axborot arxitekturasi (URL, uch tilda `/uz/ /ru/ /en/`)

```
/                         Bosh sahifa
/xizmatlar/               Xizmatlar (ikki yoʻnalish, 8 xizmat)
/xizmatlar/<yoʻnalish>/   Yoʻnalish: energoaudit | olchov-auditi
/xizmatlar/<yoʻnalish>/<xizmat>/
/reestr/                  Bajarilgan ishlar reestri (143 ta; filtr: yoʻnalish, yil, qidiruv; 25 tadan)
/hujjatlar/               Litsenziya, reestr, aʼzolik, ISO, sugʻurta — skanlar bilan
/qonunchilik/             Meʼyoriy hujjatlar jadvali (lex.uz havolalari)
/yangiliklar/ , /yangiliklar/<slug>/
/tashkilot/               Tashkilot haqida (1997, UZACE, hamkorlar, ISO, sugʻurta)
/tashkilot/mutaxassislar/ Rahbariyat va mutaxassislar (39 kishi, boʻlim boʻyicha)
/tashkilot/asboblar/      Oʻlchov asboblari va qiyoslash jadvali (5 ta)
/tashkilot/rekvizitlar/   Rekvizitlar
/aloqa/                   Aloqa (bosh ofis, Toshkent ofisi, xarita)
/murojaat/                Murojaat (soʻrov) formasi
/api/lead/  /api/compliance/  /api/energy-estimate/
/sitemap.xml  /robots.txt  (til prefiksisiz)
```

Interaktiv asboblar (React orollari, SSR sahifa ichida):
- **Talab tekshiruvchi** (`compliance-check`) — bosh sahifa va energoaudit yoʻnalishi.
- **Energiya toifasi baholagich** (`energy-estimator`) — energoaudit yoʻnalishi.
- **Murojaat formasi** (`lead-form`) — /murojaat/ va /aloqa/.

## Dizayn tizimi — «davlat portali»

- Fon `#F3F4F7`, oq kartalar `1px #D9DEE7` chegara, radius 8px, soyasiz.
- Brend koʻk `#27306E` (tugma, sarlavha urgʻusi, jadval sarlavhasi foni `#EEF0F8`),
  toʻqroq `#1E2556` (yuqori panel va futer), sariq `#FFC424` faqat: sarlavha ostidagi
  3px chiziq, faol menyu chizigʻi, «Diqqat» bloki chegarasi.
- Shrift: **Inter** (400/500/600/700), raqamlar `tabular-nums`. Serif yoʻq.
- Davlat portali belgilari: yuqori xizmat paneli (telefon, e-pochta, til, «Maxsus
  imkoniyatlar» — katta shrift + kulrang rejim), har ichki sahifada breadcrumbs,
  reestr jadvallari (№, sana, raqam), hujjat kartalari (skan + raqam + amal muddati),
  «Diqqat» axborot bloklari, marketing sifatlarisiz matn.
- Logotip: emblema qismi (TTT harflari ustidagi belgi) sarlavhada 44px, yonida
  «TTT AUDIT» matni; toʻliq logotip futerda oq rangda; favicon emblemadan.

## Texnik talablar

- Django 5.2 SSR (organik qidiruv asosiy kanal), React 19 + Vite 7 faqat vidjetlar.
- Python 3.14, Node 24. SQLite lokal, PostgreSQL prod (`DATABASE_URL`).
- Testlar: pytest-django, har sahifa uchun 200 + kalit matn testi, API testlar,
  import buyrugʻi testi. Qamrov ≥ 80% (`core/`).
- Murojaat: 5 ta/soat/IP chegara, Telegram bildirishnoma (env orqali), fayl ≤ 25 MB.
- SEO: `<title>`/description har sahifada, canonical, hreflang, sitemap.xml
  (uch til), robots.txt, JSON-LD (ProfessionalService), OG teglar.
- Deploy: Dockerfile (gunicorn + whitenoise), `.env.example`, README.

## Ochiq savollar (mijozdan; kodni toʻxtatmaydi)

- Ish soatlari (byulletenda yoʻq) — boʻsh qoldiriladi, kelganda admin panelda.
- Asosiy e-pochta: `tttaudit@mail.ru` (byulleten) yoki `info@tttaudit.uz`.
- Xodim ismlarining lotin yozuvi avtomatik oʻgirilgan — mijoz tekshiradi.
- Buyurtmachi nomlari reestrda ochiq koʻrsatiladi (byulletendagidek) — tasdiq kerak.
