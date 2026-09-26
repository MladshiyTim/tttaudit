/**
 * React vidjetlari uchun minimal i18n.
 *
 * Til `document.documentElement.lang` dan olinadi (SSR `<html lang="...">`
 * atributi, `base.html` da allaqachon toʻgʻri qoʻyilgan). Faqat vidjet
 * ichidagi statik interfeys matnlari shu yerda tarjima qilinadi — serverdan
 * keladigan matnlar (API JSON javoblari, `data-directions` sarlavhalari)
 * allaqachon `core/*.py` tomonidan tarjima qilingan boʻladi, shu sababli
 * bu yerda takrorlanmaydi.
 */

import DICT from "./i18n.json";

// Admin paneldagi «Sayt matnlari» (vidjet) qayta yozuvlari: base.html dagi #site-texts JSON
let overrides;
function siteOverrides() {
  if (overrides === undefined) {
    const el = typeof document !== "undefined" && document.getElementById("site-texts");
    try {
      overrides = el ? JSON.parse(el.textContent) || {} : {};
    } catch {
      overrides = {};
    }
  }
  return overrides;
}


function currentLang() {
  const raw =
    (typeof document !== "undefined" && document.documentElement.lang) || "uz";
  const lang = raw.split("-")[0].toLowerCase();
  return DICT[lang] ? lang : "uz";
}

/**
 * `key` boʻyicha joriy tildagi matnni qaytaradi. `vars` berilsa,
 * `{varName}` oʻrniga qiymat qoʻyiladi (Python `%(name)s` ga oʻxshash,
 * lekin sof JS shablon — Django %-escaping bilan aloqasi yoʻq).
 */
export function t(key, vars) {
  const lang = currentLang();
  let text = siteOverrides()[key] || (DICT[lang][key] ?? DICT.uz[key] ?? key);
  if (vars) {
    for (const [name, value] of Object.entries(vars)) {
      text = text.split(`{${name}}`).join(String(value));
    }
  }
  return text;
}
