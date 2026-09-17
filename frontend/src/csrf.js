/**
 * CSRF tokenini bir marta, React render qilishdan OLDIN oladi.
 * SSR formasidagi yashirin maydon React bilan almashtiriladi, shuning uchun
 * qiymat modul yuklanganda ushlab qolinadi; cookie zaxira sifatida qoladi.
 */
function fromCookie() {
  const match = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]*)/);
  return match ? decodeURIComponent(match[1]) : "";
}

function fromDom() {
  const input = document.querySelector("input[name='csrfmiddlewaretoken']");
  return input ? input.value : "";
}

const token = fromDom() || fromCookie();

export function csrfToken() {
  return token || fromCookie();
}
