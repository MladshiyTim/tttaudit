/* Sayt JS: menyu, «Maxsus imkoniyatlar» rejimi, skan koʻrgich. Vidjetlar alohida (widgets.js). */
(function () {
  "use strict";
  var root = document.documentElement;

  // --- Maxsus imkoniyatlar: katta shrift + kulrang rejim, localStorage'da saqlanadi
  var A11Y_KEY = "ttt-a11y";
  function applyA11y(on) {
    root.setAttribute("data-a11y", on ? "on" : "off");
    document.querySelectorAll("[data-a11y-toggle]").forEach(function (btn) {
      btn.setAttribute("aria-pressed", on ? "true" : "false");
    });
  }
  var saved = false;
  try { saved = localStorage.getItem(A11Y_KEY) === "on"; } catch (e) { saved = false; }
  applyA11y(saved);
  document.addEventListener("click", function (event) {
    var btn = event.target.closest("[data-a11y-toggle]");
    if (!btn) return;
    var on = root.getAttribute("data-a11y") !== "on";
    applyA11y(on);
    try { localStorage.setItem(A11Y_KEY, on ? "on" : "off"); } catch (e) { /* xususiy rejim */ }
  });

  // --- Mobil menyu
  document.addEventListener("click", function (event) {
    var toggle = event.target.closest("[data-nav-toggle]");
    if (!toggle) return;
    var nav = document.getElementById(toggle.getAttribute("aria-controls"));
    if (!nav) return;
    var open = nav.classList.toggle("is-open");
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
  });

  // --- Skan koʻrgich: <a data-lightbox data-alt="..." href="scan.png">
  var box = document.getElementById("lightbox");
  if (box && typeof box.showModal === "function") {
    var img = box.querySelector("img");
    document.addEventListener("click", function (event) {
      var link = event.target.closest("[data-lightbox]");
      if (link) {
        event.preventDefault();
        img.src = link.getAttribute("href");
        img.alt = link.getAttribute("data-alt") || "";
        box.showModal();
      } else if (event.target === box) {
        box.close();
      }
    });
  }
})();
